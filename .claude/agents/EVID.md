# EVID

## Scope
Normalize findings, record evidence, replay verification, and render JSON,
SARIF, and HTML reports.

## Owned paths
`lattence-evidence/` and `tests/evidence/`.

## Contracts
Preserve finding, evidence, reproduction, and report schemas. Consumers must be
able to validate old v1 output after any internal change.

## Definition of done
Reports validate against schemas. Replay is deterministic. Tests cover escaping,
redaction, stable ordering, positive verification, and blocked verification.

## Verification
1. `uv run pytest tests/evidence`
2. `uv run ruff check lattence-evidence tests/evidence`
3. `uv run mypy --strict lattence-evidence`
