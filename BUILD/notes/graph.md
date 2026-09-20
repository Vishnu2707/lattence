# Graph module

The graph module defines frozen Pydantic models for every project node, graph
edge, project inventory, and serialized security graph. It normalizes contracted
timestamps to UTC and rejects extra fields, duplicate identifiers, absolute
source paths, and edges that reference missing nodes. Parallel edges remain
valid when their identifiers differ.

Public imports come from `lattence.graph`. They include every concrete node,
`Node`, `NodeType`, `NodeId`, `SourceRef`, `Edge`, `EdgeType`, `TrustLevel`,
`Project`, `SecurityGraph`, `JsonValue`, and `UtcDateTime`.

T-020 added deterministic graph construction. It links application ownership,
agent calls, server tools, data access, credentials, and cryptographic
protection from explicit identifiers and shared source evidence. Duplicate edge
candidates collapse by stable edge id.
T-021 added cycle-safe reachability and bounded simple-path queries. Both APIs
validate node identifiers, support edge-type filters, and return stable sorted
results. Parallel edges remain distinct in returned paths.
T-022 added stable JSON serialization and file export. Node, edge, set-like,
reference, and relationship lists are ordered before serialization. The output
uses sorted keys, UTF-8 text, and a final newline.

T-085 connects applications, agents, tools, and MCP servers to algorithms and
certificates with the existing `key_exchange` and `protected_by` relationships.
Bindings choose exact source, application entrypoint, explicit config/source
reference, or same-module proximity in that order. Every edge records its
binding reason and source evidence; unrelated modules and algorithm-name-only
matches remain disconnected.

T-090 adds bounded topology traversal without changing directed graph edges.
Each hop retains the edge identifier, stored endpoints, relationship type,
evidence, traversal endpoints, and explicit forward or reverse orientation.
Results contain only shortest simple paths per source and target pair, retain
parallel edges, reject unknown nodes, and use stable ordering.
