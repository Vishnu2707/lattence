from dataclasses import dataclass

from lattence_crypto.pqc import (
    CryptoDependencyGraph,
    MLDSAMigration,
    MLKEMMigration,
    QuantumExposure,
)
from lattence_crypto.tls import HybridTLSValidation


@dataclass(frozen=True, order=True)
class AgilityComponent:
    name: str
    score: int
    limiting_factor: str | None = None


@dataclass(frozen=True)
class CryptoAgilityScore:
    percentage: int
    components: tuple[AgilityComponent, ...]
    limiting_factors: tuple[str, ...]


def _replaceability(graph: CryptoDependencyGraph) -> AgilityComponent:
    assets = tuple(
        node for node in graph.nodes if node.kind in {"algorithm", "certificate"}
    )
    if not assets:
        return AgilityComponent("replaceability", 0, "no crypto assets discovered")
    replaceable = sum(
        node.source_path is not None or node.implementation is not None
        for node in assets
    )
    score = replaceable * 100 // len(assets)
    factor = None if score == 100 else "some crypto assets lack a source location"
    return AgilityComponent("replaceability", score, factor)


def _configurability(graph: CryptoDependencyGraph) -> AgilityComponent:
    algorithms = tuple(node for node in graph.nodes if node.kind == "algorithm")
    explicit = sum(
        node.source_path is not None or node.implementation is not None
        for node in algorithms
    )
    has_tls_configuration = any(
        node.kind == "tls_configuration" for node in graph.nodes
    )
    if not algorithms:
        score = 0
    else:
        score = (explicit * 80 // len(algorithms)) + (
            20 if has_tls_configuration else 0
        )
    factor = None if score == 100 else "crypto choices are not fully configurable"
    return AgilityComponent("configurability", score, factor)


def _exposure(exposure: QuantumExposure) -> AgilityComponent:
    vulnerable_targets = {
        *(asset.target_id for asset in exposure.isolated_assets),
        *(path.target_id for path in exposure.paths),
    }
    score = max(0, 100 - (25 * len(vulnerable_targets)))
    factor = (
        None
        if score == 100
        else f"{len(vulnerable_targets)} quantum-vulnerable asset(s) remain"
    )
    return AgilityComponent("dependency_exposure", score, factor)


def _migration(
    kem: MLKEMMigration,
    dsa: MLDSAMigration,
    hybrid: HybridTLSValidation,
) -> AgilityComponent:
    checks = (kem.compatible, dsa.compatible, hybrid.status == "valid")
    score = sum(checks) * 100 // len(checks)
    factor = None if score == 100 else "PQC migration checks are incomplete"
    return AgilityComponent("migration_readiness", score, factor)


def _downgrade(resistant: bool | None) -> AgilityComponent:
    if resistant is True:
        return AgilityComponent("downgrade_resistance", 100)
    if resistant is False:
        return AgilityComponent(
            "downgrade_resistance", 0, "downgrade resistance failed"
        )
    return AgilityComponent(
        "downgrade_resistance", 0, "downgrade resistance is untested"
    )


def score_crypto_agility(
    graph: CryptoDependencyGraph,
    *,
    quantum_exposure: QuantumExposure,
    ml_kem: MLKEMMigration,
    ml_dsa: MLDSAMigration,
    hybrid_tls: HybridTLSValidation,
    downgrade_resistant: bool | None = None,
) -> CryptoAgilityScore:
    components = tuple(
        sorted(
            (
                _replaceability(graph),
                _configurability(graph),
                _exposure(quantum_exposure),
                _migration(ml_kem, ml_dsa, hybrid_tls),
                _downgrade(downgrade_resistant),
            )
        )
    )
    return CryptoAgilityScore(
        percentage=sum(component.score for component in components) // len(components),
        components=components,
        limiting_factors=tuple(
            component.limiting_factor
            for component in components
            if component.limiting_factor is not None
        ),
    )
