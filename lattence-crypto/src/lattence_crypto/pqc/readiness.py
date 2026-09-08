from dataclasses import dataclass

from lattence.graph import CryptoAlgorithm, SecurityGraph

from .classification import classify_graph


@dataclass(frozen=True)
class PQCReadiness:
    total: int
    safe: int
    hybrid: int
    vulnerable: int
    unknown: int
    score_percent: int


def assess_readiness(graph: SecurityGraph) -> PQCReadiness:
    classified = classify_graph(graph)
    algorithms = [
        node for node in classified.nodes if isinstance(node, CryptoAlgorithm)
    ]
    counts = {
        status: sum(node.quantum_status == status for node in algorithms)
        for status in ("safe", "hybrid", "vulnerable", "unknown")
    }
    total = len(algorithms)
    weighted_points = counts["safe"] * 100 + counts["hybrid"] * 50
    score = int(weighted_points / total + 0.5) if total else 0
    return PQCReadiness(
        total=total,
        safe=counts["safe"],
        hybrid=counts["hybrid"],
        vulnerable=counts["vulnerable"],
        unknown=counts["unknown"],
        score_percent=score,
    )
