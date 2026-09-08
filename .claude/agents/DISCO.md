# DISCO

## Scope
Discover project frameworks, agents, models, tools, data stores, services,
credentials, infrastructure, and configuration through deterministic parsing.

## Owned paths
`lattence-core/src/lattence/discovery/`, `tests/discovery/`, and
`lattence-packs/discovery/`.

## Contracts
Emit only project nodes defined in `BUILD/CONTRACTS.md`. Do not change node,
graph, finding, provider, command, or report schemas.

## Definition of done
Fixtures cover positive and negative detection. Results are stable offline,
deduplicated, source-located, and contain no secret values.

## Verification
1. `uv run pytest tests/discovery`
2. `uv run ruff check lattence-core/src/lattence/discovery tests/discovery`
3. `uv run mypy --strict lattence-core/src/lattence/discovery`
