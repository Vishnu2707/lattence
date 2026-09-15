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
T-035 added a deterministic readiness summary. Safe algorithms receive full
credit, hybrid algorithms receive half credit, and vulnerable or unknown
algorithms receive none. The result rounds half points up and returns zero when
the inventory is empty.

T-065 added an offline crypto dependency projection. It retains algorithms,
certificates, their transitive graph ancestors, original relationship evidence,
and optional discovered library links in stable order without changing the
frozen security graph schema.

T-066 identifies every direct and transitive path into algorithms and
certificates classified as quantum-vulnerable. Paths retain ordered graph
relationships and deduplicated source evidence; cycles are bounded.

T-067 assesses ML-KEM-768 migration against discovered key-exchange assets and
explicit runtime group capabilities. It distinguishes an existing migration,
direct readiness, hybrid-transition readiness, and concrete blocking factors.

T-068 applies the same deterministic migration states to ML-DSA-65 signing
assets, including vulnerable certificates, explicit signature capabilities,
and classical-plus-PQC credential transitions.

T-069 validates hybrid TLS as three independent requirements: TLS 1.3,
classical-plus-PQC key exchange, and classical-plus-PQC signatures. It accepts
explicit hybrid nodes or paired safe and vulnerable assets and reports partial
configurations with exact missing requirements.

T-070 scores crypto agility from five equally weighted components:
replaceability, configurability, quantum-vulnerable dependency exposure, PQC
migration readiness, and downgrade resistance. Each component and limiting
factor is returned explicitly in deterministic order.

T-071 defines dry-run-first crypto mutation plans. Plans require an exact
project-relative declared path, UTF-8 text below one megabyte, no more than 32
replacements, a bounded timeout, and a checksum of the untouched source.
