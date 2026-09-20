import hashlib
import json
from collections.abc import Iterable
from typing import Literal, Self

from lattence.graph import (
    EdgeType,
    NodeId,
    Project,
    SecurityGraph,
    TopologyPath,
    TraversalDirection,
    UtcDateTime,
)
from pydantic import Field, computed_field, model_validator

from .models import Finding
from .reporting import ReportModel


class CrossLayerHop(ReportModel):
    edge_id: str
    source_id: NodeId
    target_id: NodeId
    edge_type: EdgeType
    traversal: TraversalDirection
    from_node_id: NodeId
    to_node_id: NodeId
    evidence_refs: list[str] = Field(default_factory=list)


class CrossLayerChain(ReportModel):
    id: str
    source_finding_id: str
    crypto_finding_id: str
    start_node_id: NodeId
    end_node_id: NodeId
    hops: list[CrossLayerHop] = Field(min_length=1)
    explanation: str
    evidence_refs: list[str] = Field(default_factory=list)


class CrossLayerSummary(ReportModel):
    finding_correlations: int = Field(ge=0)
    distinct_structural_paths: int = Field(ge=0)


def summarize_cross_layer_chains(
    chains: Iterable[CrossLayerChain],
) -> CrossLayerSummary:
    chain_list = list(chains)
    structural_paths = {
        tuple((hop.edge_id, hop.traversal) for hop in chain.hops)
        for chain in chain_list
    }
    return CrossLayerSummary(
        finding_correlations=len(chain_list),
        distinct_structural_paths=len(structural_paths),
    )


class SecurityPresentation(ReportModel):
    version: Literal["1"] = "1"
    project: Project
    graph: SecurityGraph
    findings: list[Finding]
    cross_layer_chains: list[CrossLayerChain]
    generated_at: UtcDateTime

    @computed_field  # type: ignore[prop-decorator]
    @property
    def cross_layer_summary(self) -> CrossLayerSummary:
        return summarize_cross_layer_chains(self.cross_layer_chains)

    @model_validator(mode="after")
    def references_are_valid(self) -> Self:
        nodes = {node.id for node in self.graph.nodes}
        edges = {edge.id: edge for edge in self.graph.edges}
        findings = {finding.id: finding for finding in self.findings}
        for finding in self.findings:
            if finding.target_node_id not in nodes:
                raise ValueError(f"unknown finding target: {finding.target_node_id}")
        for chain in self.cross_layer_chains:
            source = findings.get(chain.source_finding_id)
            crypto = findings.get(chain.crypto_finding_id)
            if source is None or crypto is None:
                raise ValueError(f"unknown chain finding: {chain.id}")
            if source.target_node_id != chain.start_node_id:
                raise ValueError(f"invalid chain start: {chain.id}")
            if crypto.target_node_id != chain.end_node_id:
                raise ValueError(f"invalid chain end: {chain.id}")
            visited = {chain.start_node_id}
            current = chain.start_node_id
            has_crypto_edge = False
            for hop in chain.hops:
                edge = edges.get(hop.edge_id)
                if edge is None:
                    raise ValueError(f"unknown chain edge: {hop.edge_id}")
                if (hop.source_id, hop.target_id, hop.edge_type) != (
                    edge.source_id,
                    edge.target_id,
                    edge.type,
                ):
                    raise ValueError(f"altered chain edge: {hop.edge_id}")
                expected = (
                    (edge.source_id, edge.target_id)
                    if hop.traversal == "forward"
                    else (edge.target_id, edge.source_id)
                )
                if (hop.from_node_id, hop.to_node_id) != expected:
                    raise ValueError(f"invalid hop orientation: {hop.edge_id}")
                if hop.from_node_id != current or hop.to_node_id in visited:
                    raise ValueError(f"non-simple chain: {chain.id}")
                visited.add(hop.to_node_id)
                current = hop.to_node_id
                has_crypto_edge |= hop.edge_type in {"key_exchange", "protected_by"}
            if current != chain.end_node_id or not has_crypto_edge:
                raise ValueError(f"invalid chain endpoint: {chain.id}")
        return self


def build_cross_layer_chain(
    source_finding_id: str,
    crypto_finding_id: str,
    path: TopologyPath,
    explanation: str,
    evidence_refs: tuple[str, ...],
) -> CrossLayerChain:
    fingerprint = json.dumps(
        [
            source_finding_id,
            crypto_finding_id,
            *(f"{hop.edge_id}:{hop.traversal}" for hop in path.hops),
        ],
        separators=(",", ":"),
    )
    suffix = hashlib.sha256(fingerprint.encode()).hexdigest()[:16]
    return CrossLayerChain(
        id=f"cross-layer:{source_finding_id}:{crypto_finding_id}:{suffix}",
        source_finding_id=source_finding_id,
        crypto_finding_id=crypto_finding_id,
        start_node_id=path.node_ids[0],
        end_node_id=path.node_ids[-1],
        hops=[
            CrossLayerHop(
                edge_id=hop.edge_id,
                source_id=hop.source_id,
                target_id=hop.target_id,
                edge_type=hop.edge_type,
                traversal=hop.traversal,
                from_node_id=hop.from_node_id,
                to_node_id=hop.to_node_id,
                evidence_refs=list(hop.evidence_refs),
            )
            for hop in path.hops
        ],
        explanation=explanation,
        evidence_refs=sorted(set(evidence_refs)),
    )


def build_security_presentation(
    project: Project,
    graph: SecurityGraph,
    findings: Iterable[Finding],
    chains: Iterable[CrossLayerChain],
) -> SecurityPresentation:
    return SecurityPresentation(
        project=project,
        graph=graph,
        findings=sorted(findings, key=lambda finding: finding.id),
        cross_layer_chains=sorted(
            chains,
            key=lambda chain: (
                len(chain.hops),
                chain.source_finding_id,
                chain.crypto_finding_id,
                chain.id,
            ),
        ),
        generated_at=graph.generated_at,
    )


def presentation_json(presentation: SecurityPresentation) -> str:
    return (
        json.dumps(
            presentation.model_dump(mode="json"),
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
        + "\n"
    )
