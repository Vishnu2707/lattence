# Graph module

The graph module defines frozen Pydantic models for every project node, graph
edge, project inventory, and serialized security graph. It normalizes contracted
timestamps to UTC and rejects extra fields, duplicate identifiers, absolute
source paths, and edges that reference missing nodes. Parallel edges remain
valid when their identifiers differ.

Public imports come from `lattence.graph`. They include every concrete node,
`Node`, `NodeType`, `NodeId`, `SourceRef`, `Edge`, `EdgeType`, `TrustLevel`,
`Project`, `SecurityGraph`, `JsonValue`, and `UtcDateTime`.
