from typing import Literal, Self

from pydantic import Field, model_validator

from .common import ContractModel, JsonValue, NodeId, UtcDateTime
from .nodes import Node

type EdgeType = Literal[
    "calls",
    "accesses",
    "trusts",
    "authenticated_by",
    "protected_by",
    "key_exchange",
    "contains",
    "delegates_to",
]
type TrustLevel = Literal["untrusted", "low", "medium", "high", "system", "unknown"]


def _duplicates(values: list[str]) -> set[str]:
    seen: set[str] = set()
    duplicates: set[str] = set()
    for value in values:
        if value in seen:
            duplicates.add(value)
        seen.add(value)
    return duplicates


class Edge(ContractModel):
    id: str
    source_id: NodeId
    target_id: NodeId
    type: EdgeType
    permission: str | None = None
    auth_method: str | None = None
    transport: str | None = None
    algorithm: str | None = None
    trust_level: TrustLevel = "unknown"
    evidence_refs: list[str] = Field(default_factory=list)
    metadata: dict[str, JsonValue] = Field(default_factory=dict)


class Project(ContractModel):
    id: str
    name: str
    root: str
    version: str = "1"
    scanned_at: UtcDateTime
    source_revision: str | None = None
    nodes: list[Node] = Field(default_factory=list)
    metadata: dict[str, JsonValue] = Field(default_factory=dict)

    @model_validator(mode="after")
    def node_ids_are_unique(self) -> Self:
        duplicate_ids = _duplicates([node.id for node in self.nodes])
        if duplicate_ids:
            raise ValueError(f"duplicate node id: {sorted(duplicate_ids)[0]}")
        return self


class SecurityGraph(ContractModel):
    version: Literal["1"] = "1"
    project_id: str
    nodes: list[Node]
    edges: list[Edge]
    generated_at: UtcDateTime

    @model_validator(mode="after")
    def references_are_valid(self) -> Self:
        node_ids = [node.id for node in self.nodes]
        duplicate_nodes = _duplicates(node_ids)
        if duplicate_nodes:
            raise ValueError(f"duplicate node id: {sorted(duplicate_nodes)[0]}")

        duplicate_edges = _duplicates([edge.id for edge in self.edges])
        if duplicate_edges:
            raise ValueError(f"duplicate edge id: {sorted(duplicate_edges)[0]}")

        known_nodes = set(node_ids)
        for edge in self.edges:
            for endpoint in (edge.source_id, edge.target_id):
                if endpoint not in known_nodes:
                    raise ValueError(
                        f"edge {edge.id} references unknown node {endpoint}"
                    )
        return self
