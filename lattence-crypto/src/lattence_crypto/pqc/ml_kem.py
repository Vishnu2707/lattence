import re
from dataclasses import dataclass
from typing import Literal

from .graph import CryptoDependencyGraph

type MLKEMMigrationStatus = Literal[
    "already_migrated", "blocked", "direct_ready", "hybrid_ready"
]


@dataclass(frozen=True)
class MLKEMMigration:
    target: str
    status: MLKEMMigrationStatus
    compatible: bool
    affected_node_ids: tuple[str, ...]
    required_changes: tuple[str, ...]
    blocking_factors: tuple[str, ...]


def _normalized(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def assess_ml_kem_migration(
    graph: CryptoDependencyGraph,
    *,
    supported_groups: tuple[str, ...] = (),
    hybrid_supported: bool = False,
    target: str = "ML-KEM-768",
) -> MLKEMMigration:
    """Assess whether discovered key exchange can migrate to an ML-KEM group."""
    key_exchange = tuple(
        sorted(
            node
            for node in graph.nodes
            if node.kind == "algorithm" and node.purpose == "key exchange"
        )
    )
    affected = tuple(
        node.id for node in key_exchange if node.quantum_status == "vulnerable"
    )
    target_name = _normalized(target)
    if any(target_name in _normalized(node.name) for node in key_exchange):
        return MLKEMMigration(
            target=target,
            status="already_migrated",
            compatible=True,
            affected_node_ids=affected,
            required_changes=(),
            blocking_factors=(),
        )

    if not key_exchange:
        return MLKEMMigration(
            target=target,
            status="blocked",
            compatible=False,
            affected_node_ids=(),
            required_changes=(),
            blocking_factors=("no key-exchange assets discovered",),
        )

    normalized_groups = {_normalized(group) for group in supported_groups}
    if target_name not in normalized_groups:
        return MLKEMMigration(
            target=target,
            status="blocked",
            compatible=False,
            affected_node_ids=affected,
            required_changes=(),
            blocking_factors=(f"runtime does not advertise {target}",),
        )

    if hybrid_supported and affected:
        return MLKEMMigration(
            target=target,
            status="hybrid_ready",
            compatible=True,
            affected_node_ids=affected,
            required_changes=(
                f"configure a classical + {target} hybrid key-exchange group",
                "retain the classical group until every peer accepts the hybrid group",
            ),
            blocking_factors=(),
        )
    return MLKEMMigration(
        target=target,
        status="direct_ready",
        compatible=True,
        affected_node_ids=affected,
        required_changes=(f"replace discovered key exchange with {target}",),
        blocking_factors=(),
    )
