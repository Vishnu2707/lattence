# CRYPTO

## Scope
Discover cryptography, assess post-quantum readiness, validate TLS, and score
cryptographic agility.

## Owned paths
`lattence-crypto/src/lattence_crypto/discovery/`,
`lattence-crypto/src/lattence_crypto/pqc/`,
`lattence-crypto/src/lattence_crypto/tls/`,
`lattence-crypto/src/lattence_crypto/agility/`, and `tests/crypto/` except chaos.

## Contracts
Emit contracted crypto and certificate nodes. Preserve readiness score and
report field semantics. Do not change chaos behavior or command definitions.

## Definition of done
Tests cover safe, vulnerable, hybrid, and unknown states. Checks work offline,
never contact undeclared hosts, and cite source locations.

## Verification
1. `uv run pytest tests/crypto --ignore=tests/crypto/chaos`
2. `uv run ruff check lattence-crypto/src/lattence_crypto tests/crypto`
3. `uv run mypy --strict lattence-crypto/src/lattence_crypto`
