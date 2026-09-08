# CHAOS

## Scope
Mutate declared cryptographic configuration and measure contained blast radius.

## Owned paths
`lattence-crypto/src/lattence_crypto/chaos/` and `tests/crypto/chaos/`.

## Contracts
Require explicit owned targets. Preserve the crypto node model, evidence model,
and command exit codes. Never mutate a live target without declaration.

## Definition of done
Mutations are reversible and bounded. Tests prove rollback, timeout, refusal,
evidence capture, and deterministic dry runs.

## Verification
1. `uv run pytest tests/crypto/chaos`
2. `uv run ruff check lattence-crypto/src/lattence_crypto/chaos tests/crypto/chaos`
3. `uv run mypy --strict lattence-crypto/src/lattence_crypto/chaos`
