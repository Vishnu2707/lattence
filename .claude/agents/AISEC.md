# AISEC

## Scope
Implement native AI and agent security tests, rule execution, and attack packs.

## Owned paths
`lattence-ai/src/lattence_ai/attacks/`, `tests/ai/attacks/`, and
`lattence-packs/attacks/`.

## Contracts
Return contracted test cases, raw results, findings, and evidence. Do not alter
the planner, provider interface, policy authority, or target declaration gate.

## Definition of done
Each attack has positive and negative fixtures, deterministic replay data, a
declared target, and an OWASP mapping. Offline rule execution stays functional.

## Verification
1. `uv run pytest tests/ai/attacks`
2. `uv run ruff check lattence-ai/src/lattence_ai/attacks tests/ai/attacks`
3. `uv run mypy --strict lattence-ai/src/lattence_ai/attacks`
