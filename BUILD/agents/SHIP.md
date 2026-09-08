# SHIP

## Scope
Own packaging, commands, API delivery, CI, containers, documentation, community
files, release automation, and milestone shipping.

## Owned paths
`lattence-cli/` except `src/lattence_cli/presentation/`, `lattence-api/`,
`.github/`, root configuration and governance files, `docs/` except
`docs/architecture/`, `examples/`, and `integrations/`.

## Contracts
Expose the frozen command and report contracts. Do not change specialist
internals, design tokens, or schemas without an orchestrator contract task.

## Definition of done
Packages build and install from wheels. CI uses pinned actions and least
privilege. Smoke tests use only the bundled declared target.

## Verification
1. `uv run pytest tests/cli tests/api`
2. `uv run ruff check lattence-cli lattence-api tests/cli tests/api`
3. `uv build && uv run twine check dist/*`
