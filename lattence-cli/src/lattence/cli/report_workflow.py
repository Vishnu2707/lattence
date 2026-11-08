from collections.abc import Iterable
from importlib.metadata import version
from pathlib import Path

from lattence.discovery import (
    discover_dependency_manifests,
    discover_project,
    inventory_project,
)
from lattence.evidence import Report, build_report, normalize_rule_finding
from lattence.graph import Node, SecurityGraph, build_security_graph
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
    load_native_attack_catalog,
)
from lattence_crypto import (
    CryptoDiscovery,
    annotate_crypto_references,
    assess_readiness,
    classify_graph,
    crypto_discovery_files,
    discover_crypto,
    discover_tls,
)
from lattence_crypto.pqc import assess_quantum_exposure, build_crypto_graph

from .artifact_workflow import artifact_paths


def data_root() -> Path:
    for parent in Path(__file__).resolve().parents:
        candidate = parent / "lattence-packs"
        if candidate.is_dir():
            return candidate
    installed = Path(__file__).resolve().parents[1] / "packs"
    if installed.is_dir():
        return installed
    raise RuntimeError("cannot locate bundled rule packs")


def crypto_output_exclusions(root: Path, output: Path | None) -> tuple[str, ...]:
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


def _extra_nodes(
    root: Path, output: Path | None = None
) -> tuple[tuple[Node, ...], CryptoDiscovery]:
    inventory = inventory_project(root)
    dependencies = discover_dependency_manifests(inventory.root, inventory.files)
    crypto_files = crypto_discovery_files(
        inventory.files, crypto_output_exclusions(root, output)
    )
    tls = discover_tls(inventory.root, crypto_files)
    crypto = discover_crypto(dependencies.dependencies, inventory.root, crypto_files)
    mcp = discover_mcp_configs(inventory.root, inventory.files)
    crypto_assets = annotate_crypto_references(
        inventory.root,
        crypto_files,
        (*tls.certificates, *tls.algorithms, *crypto.algorithms),
    )
    return ((*crypto_assets, *mcp.servers, *mcp.tools), crypto)


def _quantum_exposure_counts(
    graph: SecurityGraph, crypto: CryptoDiscovery
) -> tuple[int, int]:
    exposure = assess_quantum_exposure(build_crypto_graph(graph, crypto.libraries))
    return len(exposure.isolated_assets), len(exposure.paths)


def create_report(root: Path, output: Path | None = None) -> Report:
    resolved = root.resolve(strict=True)
    root_data = data_root()
    extra_nodes, crypto = _extra_nodes(resolved, output)
    discovery = discover_project(resolved, root_data / "discovery", extra_nodes)
    graph = classify_graph(build_security_graph(discovery.project))
    project = discovery.project.model_copy(update={"nodes": graph.nodes})
    readiness = assess_readiness(graph)
    catalog = load_native_attack_catalog(root_data / "attacks")
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
    vulnerable_assets, vulnerable_paths = _quantum_exposure_counts(graph, crypto)
    return build_report(
        project,
        graph,
        findings,
        version("lattence"),
        readiness.score_percent,
        quantum_vulnerable_assets=vulnerable_assets,
        quantum_vulnerable_paths=vulnerable_paths,
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
        project, graph, findings, report.tool.version, report.summary.pqc_readiness
    )


def create_attack_report(
    root: Path, provider_directory: Path, offline: bool, output: Path | None = None
) -> Report:
    report = create_report(root, output)
    if offline:
        return report
    return run_external_providers(report, enabled_providers(provider_directory))
