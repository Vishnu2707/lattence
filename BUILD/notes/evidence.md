# Evidence module

The evidence module defines frozen finding, evidence, policy decision,
environment, transcript, telemetry, and reproduction models. It validates
finding and digest formats, orders timestamps in UTC, rejects reversed time
ranges, and requires unique ordered transcript sequence numbers.

Public imports come from `lattence.evidence`. The primary types are `Finding`,
`EvidenceBundle`, `EvidenceInput`, `TranscriptEntry`, `TelemetrySpan`,
`PolicyDecision`, `EnvironmentFingerprint`, and `ReproductionRecipe`.

T-036 added deterministic rule-finding normalization and JSON report models.
Reports sort identifiers and set-like fields, include severity and PQC summary
counts, validate against the v1 JSON Schema when requested, and end with a
newline.
T-037 added a self-contained HTML renderer with the frozen dark palette, dense
summary metrics, finding and graph tables, embedded report JSON, responsive
layout, and HTML escaping. It does not load external assets.

T-055 added deterministic read-only remediation plans. Each plan contains the
finding identifier, title, severity, existing remediation text, full target
node, evidence identifier, and existing reproduction recipe. Plans may cover a
whole report or one finding identifier. Unknown findings and missing graph
targets fail explicitly.

T-075 normalizes blocked ML-KEM and ML-DSA migrations, limited agility,
accepted downgrades, and incomplete downgrade validation into stable
`LT-PQC-2xx` findings. Evidence contains deterministic summaries and hashes,
never mutated file content.

T-084 adds optional v1 summary counts for isolated quantum-vulnerable assets
and traversable quantum-vulnerable paths. Older v1 documents remain valid and
default both counts to zero; JSON and HTML writers emit and label both counts.

T-091 replaces the single fallback target used by every crypto finding with
explicit ML-KEM, ML-DSA, agility, and downgrade targets. Migration findings
prefer their affected algorithms, partial hybrid TLS agility prefers the
concrete non-TLS-1.3 transport node, and downgrade findings prefer the mutated
source. The vulnerable example now targets both `LT-PQC-203` and `LT-PQC-205`
at its discovered TLS 1.2 node.

T-093 adds strict version 1 presentation models shared by TUI and dashboard.
Cross-layer chains copy every graph edge's stored endpoints and type, retain
traversal orientation and evidence, and receive a stable content-derived
identifier. Presentation validation rejects unknown finding targets, synthetic
or altered edges, broken orientation, cycles, missing crypto relationships,
and endpoint mismatches. Stable JSON serialization ends with one newline.

T-110 adds a computed cross-layer summary to presentation JSON without changing
the version 1 input contract. A structural path is the ordered sequence of
graph edge identifiers and traversal directions, regardless of finding ids.
The vulnerable example has 32 finding correlations but 9 such paths.
