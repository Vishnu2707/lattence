# PLAN

## Scope
Implement the opt-in dynamic attack planner, mutation loop, judge, caching, and
provider-neutral model adapters.

## Owned paths
`lattence-ai/src/lattence_ai/planner/`, `lattence-ai/src/lattence_ai/judge/`,
`lattence-ai/src/lattence_ai/providers/`, and `tests/ai/planner/`.

## Contracts
Rules remain the default. Cache by prompt hash. Validate strict response models,
retry once, then fall back to rules. The planner never decides security status.

## Definition of done
Tests cover cache hits, invalid output, retry, fallback, budget limits, and an
offline run with no model request.

## Verification
1. `uv run pytest tests/ai/planner`
2. `uv run ruff check lattence-ai/src/lattence_ai tests/ai/planner`
3. `uv run mypy --strict lattence-ai/src/lattence_ai/planner`
