import json
import sys
from dataclasses import asdict, dataclass
from importlib.metadata import version
from pathlib import Path

from lattence.discovery import discover_dependency_manifests, inventory_project
from lattence.evidence import Report, build_report, normalize_crypto_findings
from lattence_crypto import crypto_discovery_files, discover_crypto
from lattence_crypto.agility import CryptoAgilityScore, score_crypto_agility
from lattence_crypto.chaos import (
    CryptoChaosObservation,
    DowngradeValidation,
    execute_key_exchange_downgrade,
    execute_signature_downgrade,
    plan_crypto_mutation,
    validate_downgrade_resistance,
)
from lattence_crypto.pqc import (
    CryptoDependencyGraph,
    MLDSAMigration,
    MLKEMMigration,
    QuantumVulnerablePath,
    assess_ml_dsa_migration,
    assess_ml_kem_migration,
    build_crypto_graph,
    find_quantum_vulnerable_paths,
)
from lattence_crypto.tls import HybridTLSValidation, validate_hybrid_tls

from .workflow import _crypto_output_exclusions, create_report


class CryptoWorkflowError(ValueError):
    pass


@dataclass(frozen=True)
class CryptoAssessment:
    report: Report
    crypto_graph: CryptoDependencyGraph
    vulnerable_paths: tuple[QuantumVulnerablePath, ...]
    ml_kem: MLKEMMigration
    ml_dsa: MLDSAMigration
    hybrid_tls: HybridTLSValidation
    agility: CryptoAgilityScore
    downgrade: DowngradeValidation


def _target_node_id(report: Report, graph: CryptoDependencyGraph) -> str:
    report_ids = {node.id for node in report.graph.nodes}
    for node in graph.nodes:
        if node.id in report_ids and node.kind in {"algorithm", "certificate"}:
            return node.id
    if report.graph.nodes:
        return report.graph.nodes[0].id
    raise CryptoWorkflowError("no graph target is available for crypto assessment")


def create_crypto_assessment(
    root: Path,
    downgrade: DowngradeValidation | None = None,
    output: Path | None = None,
) -> CryptoAssessment:
    report = create_report(root, output)
    inventory = inventory_project(root.resolve(strict=True))
    dependencies = discover_dependency_manifests(inventory.root, inventory.files)
    crypto_files = crypto_discovery_files(
        inventory.files, _crypto_output_exclusions(root, output)
    )
    discovery = discover_crypto(
        dependencies.dependencies, inventory.root, crypto_files
    )
    crypto_graph = build_crypto_graph(report.graph, discovery.libraries)
    vulnerable_paths = find_quantum_vulnerable_paths(crypto_graph)
    names = tuple(node.name for node in crypto_graph.nodes if node.kind == "algorithm")
    hybrid_supported = any("hybrid" in name.lower() for name in names)
    ml_kem = assess_ml_kem_migration(
        crypto_graph,
        supported_groups=names,
        hybrid_supported=hybrid_supported,
    )
    ml_dsa = assess_ml_dsa_migration(
        crypto_graph,
        supported_signatures=names,
        hybrid_supported=hybrid_supported,
    )
    hybrid_tls = validate_hybrid_tls(crypto_graph)
    downgrade_result = downgrade or validate_downgrade_resistance(())
    agility = score_crypto_agility(
        crypto_graph,
        vulnerable_paths=vulnerable_paths,
        ml_kem=ml_kem,
        ml_dsa=ml_dsa,
        hybrid_tls=hybrid_tls,
        downgrade_resistant=downgrade_result.resistant,
    )
    findings = normalize_crypto_findings(
        _target_node_id(report, crypto_graph),
        report.generated_at,
        ml_kem=ml_kem,
        ml_dsa=ml_dsa,
        agility=agility,
        downgrade=downgrade_result,
        tool_version=version("lattence"),
    )
    crypto_report = build_report(
        report.project,
        report.graph,
        list(findings),
        report.tool.version,
        report.summary.pqc_readiness,
    )
    return CryptoAssessment(
        report=crypto_report,
        crypto_graph=crypto_graph,
        vulnerable_paths=vulnerable_paths,
        ml_kem=ml_kem,
        ml_dsa=ml_dsa,
        hybrid_tls=hybrid_tls,
        agility=agility,
        downgrade=downgrade_result,
    )


def crypto_assessment_json(assessment: CryptoAssessment) -> str:
    payload = {
        "agility": asdict(assessment.agility),
        "crypto_graph": asdict(assessment.crypto_graph),
        "downgrade": asdict(assessment.downgrade),
        "findings": [
            finding.model_dump(mode="json") for finding in assessment.report.findings
        ],
        "hybrid_tls": asdict(assessment.hybrid_tls),
        "ml_dsa": asdict(assessment.ml_dsa),
        "ml_kem": asdict(assessment.ml_kem),
        "pqc_readiness": assessment.report.summary.pqc_readiness,
        "vulnerable_paths": [asdict(path) for path in assessment.vulnerable_paths],
    }
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


def _probe_command(target_path: str, classical_value: str) -> tuple[str, ...]:
    script = (
        "from pathlib import Path; import sys; "
        "text=Path(sys.argv[1]).read_text(); "
        "required=('require_pqc = true' in text.lower() or "
        "'require_pqc: true' in text.lower()); "
        "raise SystemExit(1 if required else (sys.argv[2] not in text))"
    )
    return (sys.executable, "-c", script, target_path, classical_value)


def _first_fragment(content: str, candidates: tuple[str, ...]) -> str | None:
    return next((candidate for candidate in candidates if candidate in content), None)


def run_crypto_chaos(
    root: Path,
    declared_paths: tuple[str, ...],
    output: Path | None = None,
) -> CryptoAssessment:
    observations: list[CryptoChaosObservation] = []
    for target_path in sorted(set(declared_paths)):
        target = root / target_path
        if not target.is_file():
            continue
        try:
            content = target.read_text(encoding="utf-8")
        except (OSError, UnicodeError):
            continue
        key_fragment = _first_fragment(
            content,
            ("X25519 + ML-KEM-768 hybrid", "ML-KEM-768", "Kyber"),
        )
        if key_fragment is not None:
            plan = plan_crypto_mutation(
                root,
                target_path,
                declared_paths=declared_paths,
                before_fragment=key_fragment,
                after_fragment="X25519",
                dry_run=False,
            )
            observations.append(
                execute_key_exchange_downgrade(
                    root,
                    plan,
                    probe_command=_probe_command(target_path, "X25519"),
                )
            )
        signature_fragment = _first_fragment(
            content,
            ("ECDSA + ML-DSA-65 hybrid", "ML-DSA-65", "Dilithium"),
        )
        if signature_fragment is not None:
            plan = plan_crypto_mutation(
                root,
                target_path,
                declared_paths=declared_paths,
                before_fragment=signature_fragment,
                after_fragment="ECDSA",
                dry_run=False,
            )
            observations.append(
                execute_signature_downgrade(
                    root,
                    plan,
                    probe_command=_probe_command(target_path, "ECDSA"),
                )
            )
    if not observations:
        raise CryptoWorkflowError(
            "declared files contain no supported PQC key exchange or signature"
        )
    return create_crypto_assessment(
        root, validate_downgrade_resistance(tuple(observations)), output
    )
