from dataclasses import dataclass
from typing import Literal

from lattence_crypto.pqc import CryptoDependencyGraph, CryptoGraphNode

type HybridTLSStatus = Literal["invalid", "partial", "valid"]


@dataclass(frozen=True)
class HybridTLSValidation:
    status: HybridTLSStatus
    tls_13: bool
    hybrid_key_exchange: bool
    hybrid_signature: bool
    node_ids: tuple[str, ...]
    issues: tuple[str, ...]


def _is_hybrid(nodes: tuple[CryptoGraphNode, ...]) -> bool:
    statuses = {node.quantum_status for node in nodes}
    return "hybrid" in statuses or {"safe", "vulnerable"}.issubset(statuses)


def validate_hybrid_tls(graph: CryptoDependencyGraph) -> HybridTLSValidation:
    """Validate a TLS 1.3 configuration with hybrid KEM and signatures."""
    transports = tuple(
        node for node in graph.nodes if node.kind == "tls_configuration"
    )
    key_exchange = tuple(
        node for node in graph.nodes if node.purpose == "key exchange"
    )
    signatures = tuple(node for node in graph.nodes if node.purpose == "signature")
    tls_13 = any("tls 1.3" in node.name.lower() for node in transports)
    hybrid_key_exchange = _is_hybrid(key_exchange)
    hybrid_signature = _is_hybrid(signatures)

    issues: list[str] = []
    if not tls_13:
        issues.append("TLS 1.3 configuration not discovered")
    if not hybrid_key_exchange:
        issues.append("classical + post-quantum key exchange not configured")
    if not hybrid_signature:
        issues.append("classical + post-quantum signatures not configured")

    completed = sum((tls_13, hybrid_key_exchange, hybrid_signature))
    status: HybridTLSStatus
    if completed == 3:
        status = "valid"
    elif completed:
        status = "partial"
    else:
        status = "invalid"
    relevant = (*transports, *key_exchange, *signatures)
    return HybridTLSValidation(
        status=status,
        tls_13=tls_13,
        hybrid_key_exchange=hybrid_key_exchange,
        hybrid_signature=hybrid_signature,
        node_ids=tuple(sorted({node.id for node in relevant})),
        issues=tuple(issues),
    )
