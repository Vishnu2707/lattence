# UX

## Scope
Own terminal presentation, dashboard presentation, brand assets, diagrams, and
deterministic demonstrations.

## Owned paths
`lattence-ui/`, `assets/`, `docs/architecture/`,
`lattence-cli/src/lattence_cli/presentation/`, and `tests/ux/`.

## Contracts
Follow `BUILD/DESIGN.md` exactly. Do not change command behavior, data models,
report schemas, or severity semantics.

## Definition of done
Views work without color and by keyboard. Assets contain no generator metadata.
Visual output is checked at required sizes and against deterministic fixtures.

## Verification
1. `uv run pytest tests/ux`
2. `uv run ruff check lattence-cli/src/lattence_cli/presentation tests/ux`
3. `npm --prefix lattence-ui test -- --run`
