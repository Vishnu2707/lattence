# Crypto module note

T-016 added offline discovery for certificate files, configured TLS versions,
and named key-exchange algorithms. Certificate parse errors contain only the
project-relative path. Algorithm classification remains unknown until T-034.

The `lattence-crypto` distribution owns the `lattence_crypto` package and is a
runtime dependency of the root command distribution.

T-017 added dependency-based cryptographic library discovery and deterministic
source matching for encryption, signature, public-key, and hash algorithms.
Key sizes are retained when they occur near the algorithm declaration.

T-034 added deterministic post-quantum classification. Public-key and classical
key-exchange algorithms are vulnerable, named post-quantum and strong symmetric
algorithms are safe, mixed constructions are hybrid, and unmatched algorithms
remain unknown.
