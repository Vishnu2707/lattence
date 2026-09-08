import json
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
    build_report,
    normalize_rule_finding,
    report_json,
    write_html_report,
    write_json_report,
)
from lattence.graph import (
    CryptoAlgorithm,
    Node,
    build_security_graph,
    security_graph_json,
)
from lattence.mcp import discover_mcp_configs
from lattence_ai.attacks import (
    AttackRunner,
    ObservationResult,
    load_native_attack_catalog,
)
from lattence_crypto import (
    assess_readiness,
    classify_graph,
    discover_crypto,
    discover_tls,
)


@dataclass(frozen=True)
class ArtifactPaths:
    json: Path
    html: Path


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


def _extra_nodes(root: Path) -> tuple[Node, ...]:
    inventory = inventory_project(root)
    dependencies = discover_dependency_manifests(inventory.root, inventory.files)
    tls = discover_tls(inventory.root, inventory.files)
    crypto = discover_crypto(dependencies.dependencies, inventory.root, inventory.files)
    mcp = discover_mcp_configs(inventory.root, inventory.files)
    return (
        *tls.certificates,
        *tls.algorithms,
        *crypto.algorithms,
        *mcp.servers,
        *mcp.tools,
    )


def create_report(root: Path) -> Report:
    resolved = root.resolve(strict=True)
    data_root = _data_root()
    discovery = discover_project(
        resolved, data_root / "discovery", _extra_nodes(resolved)
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
