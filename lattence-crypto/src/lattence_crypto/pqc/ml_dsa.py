import re
from dataclasses import dataclass
from typing import Literal

from .graph import CryptoDependencyGraph

type MLDSAMigrationStatus = Literal[
    "already_migrated", "blocked", "direct_ready", "hybrid_ready"
]


@dataclass(frozen=True)
class MLDSAMigration:
    target: str
    status: MLDSAMigrationStatus
    compatible: bool
    affected_node_ids: tuple[str, ...]
    required_changes: tuple[str, ...]
    blocking_factors: tuple[str, ...]


def _normalized(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def assess_ml_dsa_migration(
    graph: CryptoDependencyGraph,
    *,
    supported_signatures: tuple[str, ...] = (),
    hybrid_supported: bool = False,
    target: str = "ML-DSA-65",
) -> MLDSAMigration:
    """Assess whether discovered signing assets can migrate to ML-DSA."""
    signatures = tuple(
        sorted(
            node
            for node in graph.nodes
            if node.purpose == "signature"
            and node.kind in {"algorithm", "certificate"}
        )
    )
    affected = tuple(
        node.id for node in signatures if node.quantum_status == "vulnerable"
    )
    target_name = _normalized(target)
    if any(target_name in _normalized(node.name) for node in signatures):
        return MLDSAMigration(
            target=target,
            status="already_migrated",
            compatible=True,
            affected_node_ids=affected,
            required_changes=(),
            blocking_factors=(),
        )

    if not signatures:
        return MLDSAMigration(
            target=target,
            status="blocked",
            compatible=False,
            affected_node_ids=(),
            required_changes=(),
            blocking_factors=("no signing assets discovered",),
        )

    normalized_signatures = {
        _normalized(signature) for signature in supported_signatures
    }
    if target_name not in normalized_signatures:
        return MLDSAMigration(
            target=target,
            status="blocked",
            compatible=False,
            affected_node_ids=affected,
            required_changes=(),
            blocking_factors=(f"runtime does not advertise {target}",),
        )

    if hybrid_supported and affected:
        return MLDSAMigration(
            target=target,
            status="hybrid_ready",
            compatible=True,
            affected_node_ids=affected,
            required_changes=(
                f"issue classical + {target} hybrid credentials",
                "retain classical verification until every peer accepts ML-DSA",
            ),
            blocking_factors=(),
        )
    return MLDSAMigration(
        target=target,
        status="direct_ready",
        compatible=True,
        affected_node_ids=affected,
        required_changes=(f"replace discovered signing assets with {target}",),
        blocking_factors=(),
    )
