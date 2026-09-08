# Crypto module note

T-016 added offline discovery for certificate files, configured TLS versions,
and named key-exchange algorithms. Certificate parse errors contain only the
project-relative path. Algorithm classification remains unknown until T-034.

The `lattence-crypto` distribution owns the `lattence_crypto` package and is a
runtime dependency of the root command distribution.
