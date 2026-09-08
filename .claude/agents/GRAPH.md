# GRAPH

## Scope
Build, serialize, query, and traverse the directed security multigraph.

## Owned paths
`lattence-core/src/lattence/graph/` and `tests/graph/`.

## Contracts
Use the frozen node and edge types. Preserve stable identifiers and report
serialization. Do not change discovery, policy, or command interfaces.

## Definition of done
Graph construction is deterministic. Tests cover duplicate edges, broken
references, path traversal, trust metadata, and JSON round trips.

## Verification
1. `uv run pytest tests/graph`
2. `uv run ruff check lattence-core/src/lattence/graph tests/graph`
3. `uv run mypy --strict lattence-core/src/lattence/graph`
