from dataclasses import dataclass

from lattence.evidence import Finding
from lattence.graph import SecurityGraph, TopologyPath, find_topology_paths

_AI_DOMAINS = ("LT-AGENT-", "LT-AI-", "LT-MCP-")
_CRYPTO_DOMAINS = ("LT-CRYPTO-", "LT-PQC-")
_CRYPTO_EDGES = frozenset({"key_exchange", "protected_by"})


class CrossLayerAnalysisError(ValueError):
    pass


@dataclass(frozen=True, order=True)
class CrossLayerCorrelation:
    source_finding_id: str
    crypto_finding_id: str
    path: TopologyPath
    explanation: str
    evidence_refs: tuple[str, ...]


def _explanation(source: Finding, crypto: Finding, path: TopologyPath) -> str:
    hops = ", then ".join(
        f"{hop.traversal} {hop.edge_type} via {hop.edge_id} "
        f"from {hop.from_node_id} to {hop.to_node_id}"
        for hop in path.hops
    )
    return (
        f"{source.id} at {path.node_ids[0]} reaches {crypto.id} at "
        f"{path.node_ids[-1]}: {hops}."
    )


def correlate_cross_layer_findings(
    graph: SecurityGraph,
    findings: tuple[Finding, ...],
    *,
    max_depth: int = 8,
) -> tuple[CrossLayerCorrelation, ...]:
    """Correlate AI-layer and crypto findings over genuine graph edges."""
    known = {node.id for node in graph.nodes}
    unknown = next(
        (
            finding.target_node_id
            for finding in findings
            if finding.target_node_id not in known
        ),
        None,
    )
    if unknown is not None:
        raise CrossLayerAnalysisError(f"unknown finding target: {unknown}")

    ai_findings = tuple(
        sorted(
            (finding for finding in findings if finding.id.startswith(_AI_DOMAINS)),
            key=lambda finding: finding.id,
        )
    )
    crypto_findings = tuple(
        sorted(
            (finding for finding in findings if finding.id.startswith(_CRYPTO_DOMAINS)),
            key=lambda finding: finding.id,
        )
    )
    correlations: list[CrossLayerCorrelation] = []
    for source in ai_findings:
        for crypto in crypto_findings:
            paths = find_topology_paths(
                graph,
                (source.target_node_id,),
                (crypto.target_node_id,),
                max_depth=max_depth,
            )
            for path in paths:
                if not any(hop.edge_type in _CRYPTO_EDGES for hop in path.hops):
                    continue
                evidence_refs = tuple(
                    sorted(
                        {
                            source.evidence.id,
                            crypto.evidence.id,
                            *(
                                reference
                                for hop in path.hops
                                for reference in hop.evidence_refs
                            ),
                        }
                    )
                )
                correlations.append(
                    CrossLayerCorrelation(
                        source_finding_id=source.id,
                        crypto_finding_id=crypto.id,
                        path=path,
                        explanation=_explanation(source, crypto, path),
                        evidence_refs=evidence_refs,
                    )
                )
    return tuple(sorted(correlations, key=lambda item: (len(item.path.hops), item)))
