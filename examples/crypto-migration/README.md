# Crypto migration fixture

This offline fixture declares TLS 1.3, hybrid X25519 plus ML-KEM-768 key
exchange, hybrid ECDSA plus ML-DSA-65 signatures, and an independent
`require_pqc` downgrade control. It is safe to use with both v0.4 commands:

```bash
lattence pqc assess . --offline --fail-on none
lattence crypto chaos . --offline --fail-on none
```

The target declaration authorizes only the project root and `tls.conf`. Crypto
chaos restores the file and verifies its original digest before it exits.
