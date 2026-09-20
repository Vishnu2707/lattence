import getpass
import json
from collections.abc import Iterable
from dataclasses import dataclass
from importlib.metadata import version
from pathlib import Path

from lattence.discovery import (
    discover_dependency_manifests,
    discover_project,
    inventory_project,
)
from lattence.evidence import (
    Report,
    ReportSummary,
    build_report,
    normalize_rule_finding,
    report_json,
    sarif_json,
    write_html_report,
    write_json_report,
)
from lattence.graph import (
    CryptoAlgorithm,
    JsonValue,
    Node,
    build_security_graph,
    security_graph_json,
)
from lattence.mcp import discover_mcp_configs
from lattence.providers import (
    ProviderValidationError,
    SecurityProvider,
    enabled_providers,
    normalize_provider_result,
    validate_provider,
)
from lattence_ai.attacks import (
    AttackRunner,
    ObservationResult,
    VerificationOutcome,
    load_native_attack_catalog,
    verify_finding,
)
from lattence_crypto import (
    annotate_crypto_references,
    assess_readiness,
    classify_graph,
    crypto_discovery_files,
    discover_crypto,
    discover_tls,
)

from .options import SeverityGate


@dataclass(frozen=True)
class ArtifactPaths:
    json: Path
    html: Path


_SEVERITY_ORDER = ("critical", "high", "medium", "low", "info")


def exceeds_gate(summary: ReportSummary, gate: SeverityGate) -> bool:
    if gate == SeverityGate.NONE:
        return False
    index = _SEVERITY_ORDER.index(gate.value)
    return any(getattr(summary, level) > 0 for level in _SEVERITY_ORDER[: index + 1])


def severity_meets_gate(severity: str, gate: SeverityGate) -> bool:
    if gate == SeverityGate.NONE:
        return False
    return _SEVERITY_ORDER.index(severity) <= _SEVERITY_ORDER.index(gate.value)


def _data_root() -> Path:
    for parent in Path(__file__).resolve().parents:
        candidate = parent / "lattence-packs"
        if candidate.is_dir():
            return candidate
    installed = Path(__file__).resolve().parents[1] / "packs"
    if installed.is_dir():
        return installed
    raise RuntimeError("cannot locate bundled rule packs")


def _schema_path() -> Path:
    for parent in Path(__file__).resolve().parents:
        candidate = parent / "docs" / "schemas" / "report.v1.json"
        if candidate.is_file():
            return candidate
    installed = Path(__file__).resolve().parents[1] / "schemas" / "report.v1.json"
    if installed.is_file():
        return installed
    raise RuntimeError("cannot locate bundled report schema")


def _crypto_output_exclusions(root: Path, output: Path | None) -> tuple[str, ...]:
    if output is None:
        return ()
    resolved_root = root.resolve()
    resolved_output = output.resolve()
    try:
        relative = resolved_output.relative_to(resolved_root).as_posix()
    except ValueError:
        return ()
    if relative == ".":
        return ()
    if output.suffix.lower() in {".html", ".json"}:
        paths = artifact_paths(output)
        return tuple(
            sorted(
                path.resolve().relative_to(resolved_root).as_posix()
                for path in (paths.html, paths.json)
            )
        )
    return (f"{relative.rstrip('/')}/",)


def _extra_nodes(root: Path, output: Path | None = None) -> tuple[Node, ...]:
    inventory = inventory_project(root)
    dependencies = discover_dependency_manifests(inventory.root, inventory.files)
    excluded_paths = _crypto_output_exclusions(root, output)
    crypto_files = crypto_discovery_files(inventory.files, excluded_paths)
    tls = discover_tls(inventory.root, crypto_files)
    crypto = discover_crypto(
        dependencies.dependencies,
        inventory.root,
        crypto_files,
    )
    mcp = discover_mcp_configs(inventory.root, inventory.files)
    crypto_assets = annotate_crypto_references(
        inventory.root,
        crypto_files,
        (*tls.certificates, *tls.algorithms, *crypto.algorithms),
    )
    return (
        *crypto_assets,
        *mcp.servers,
        *mcp.tools,
    )


def create_report(root: Path, output: Path | None = None) -> Report:
    resolved = root.resolve(strict=True)
    data_root = _data_root()
    discovery = discover_project(
        resolved, data_root / "discovery", _extra_nodes(resolved, output)
    )
    graph = classify_graph(build_security_graph(discovery.project))
    project = discovery.project.model_copy(update={"nodes": graph.nodes})
    readiness = assess_readiness(graph)
    catalog = load_native_attack_catalog(data_root / "attacks")
    runner = AttackRunner(graph, catalog.rules)
    tests = {test.id: test for test in runner.generate_tests()}
    rules = {rule.id: rule for rule in catalog.rules}
    matched: dict[str, ObservationResult] = {}
    for observation in runner.run():
        if observation.matched:
            matched.setdefault(observation.rule_id, observation)
    findings = [
        normalize_rule_finding(
            rules[rule_id],
            observation.target_node_id,
            observation.observed_at,
            tests[observation.test_id].replay_seed,
            tool_version=version("lattence"),
        )
        for rule_id, observation in sorted(matched.items())
    ]
    return build_report(
        project, graph, findings, version("lattence"), readiness.score_percent
    )


def run_external_providers(
    report: Report, providers: Iterable[SecurityProvider]
) -> Report:
    project = report.project
    graph = report.graph
    findings = list(report.findings)
    finding_ids = {finding.id for finding in findings}
    for provider in providers:
        checked = validate_provider(provider)
        discovered = checked.discover(project)
        if discovered:
            nodes = [*graph.nodes, *discovered]
            node_ids = [node.id for node in nodes]
            if len(node_ids) != len(set(node_ids)):
                raise ProviderValidationError("provider discovered a duplicate node")
            project = project.model_copy(update={"nodes": nodes})
            graph = graph.model_copy(update={"nodes": nodes})
        known_nodes = {node.id for node in graph.nodes}
        for test in checked.generate_tests(graph):
            if test.target_node_id not in known_nodes:
                raise ProviderValidationError(
                    f"provider test targets unknown node: {test.target_node_id}"
                )
            raw = checked.execute(test)
            for finding in normalize_provider_result(checked, test, raw):
                if finding.id in finding_ids:
                    raise ProviderValidationError(
                        f"duplicate finding id across providers: {finding.id}"
                    )
                finding_ids.add(finding.id)
                findings.append(finding)
    return build_report(
        project,
        graph,
        findings,
        report.tool.version,
        report.summary.pqc_readiness,
    )


def create_attack_report(
    root: Path, provider_directory: Path, offline: bool, output: Path | None = None
) -> Report:
    report = create_report(root, output)
    if offline:
        return report
    return run_external_providers(report, enabled_providers(provider_directory))


def artifact_paths(output: Path) -> ArtifactPaths:
    if output.suffix.lower() in {".html", ".json"}:
        base = output.with_suffix("")
        return ArtifactPaths(base.with_suffix(".json"), base.with_suffix(".html"))
    return ArtifactPaths(
        output / "lattence-report.json", output / "lattence-report.html"
    )


def write_report_artifacts(report: Report, output: Path) -> ArtifactPaths:
    paths = artifact_paths(output)
    write_json_report(report, paths.json, _schema_path())
    write_html_report(report, paths.html)
    return paths


def load_report(input_path: Path) -> Report:
    source = input_path / "lattence-report.json" if input_path.is_dir() else input_path
    return Report.model_validate_json(source.read_text(encoding="utf-8"))


def write_graph(report: Report, output: Path) -> Path:
    destination = output / "lattence-graph.json" if output.is_dir() else output
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(security_graph_json(report.graph), encoding="utf-8")
    return destination


def write_sarif(report: Report, output: Path) -> Path:
    destination = output / "lattence.sarif.json" if output.is_dir() else output
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(sarif_json(report), encoding="utf-8")
    return destination


def attack_text(report: Report, target: Path) -> str:
    lines = [f"LATTENCE  attack  {target}", ""]
    for finding in report.findings:
        lines.append(
            f"VULNERABLE  {finding.id}  {finding.title}  {finding.target_node_id}"
        )
    indirect = next((item for item in report.findings if item.id == "LT-AI-002"), None)
    tool = next(
        (
            node
            for node in report.graph.nodes
            if node.type == "tool" and node.server_id is not None
        ),
        None,
    )
    if indirect is not None and tool is not None:
        lines.extend(("", f"Indirect chain  {indirect.target_node_id} -> {tool.id}"))
    lines.extend(("", f"Findings  {report.summary.total}"))
    return "\n".join(lines) + "\n"


@dataclass(frozen=True)
class VerificationResult:
    outcome: VerificationOutcome
    finding_id: str
    title: str | None
    target_node_id: str | None
    severity: str | None


def verify_report(report_path: Path, finding_id: str) -> VerificationResult:
    report = load_report(report_path)
    rules = load_native_attack_catalog(_data_root() / "attacks").rules
    outcome = verify_finding(report, finding_id, rules)
    finding = next((item for item in report.findings if item.id == finding_id), None)
    return VerificationResult(
        outcome=outcome,
        finding_id=finding_id,
        title=finding.title if finding else None,
        target_node_id=finding.target_node_id if finding else None,
        severity=finding.severity if finding else None,
    )


def verify_text(result: VerificationResult) -> str:
    if result.outcome is VerificationOutcome.NOT_FOUND:
        return f"BLOCKED  {result.finding_id}  finding not found\n"
    word = "VULNERABLE" if result.outcome is VerificationOutcome.VULNERABLE else "PASS"
    return f"{word}  {result.finding_id}  {result.title}  {result.target_node_id}\n"


def verify_json(result: VerificationResult) -> str:
    payload = {
        "finding_id": result.finding_id,
        "outcome": result.outcome.value,
        "severity": result.severity,
        "target_node_id": result.target_node_id,
        "title": result.title,
    }
    return json.dumps(payload, sort_keys=True) + "\n"


def readiness_json(report: Report) -> str:
    algorithms = [
        node for node in report.graph.nodes if isinstance(node, CryptoAlgorithm)
    ]
    payload = {
        "algorithms": len(algorithms),
        "pqc_readiness": report.summary.pqc_readiness,
        "quantum_vulnerable": sum(
            node.quantum_status == "vulnerable" for node in algorithms
        ),
    }
    return json.dumps(payload, sort_keys=True) + "\n"


def machine_report(report: Report) -> str:
    return report_json(report, _schema_path())


def record_cli_audit_event(
    *,
    action: str,
    target: Path,
    result: str,
    out: Path,
    details: dict[str, JsonValue],
) -> None:
    from lattence.governance import AuditLog, default_audit_db_path

    log = AuditLog(default_audit_db_path(out))
    try:
        actor = getpass.getuser()
    except OSError:
        actor = "unknown"
    log.record(
        actor=actor,
        action=action,
        target=str(target),
        result=result,
        details=details,
    )
