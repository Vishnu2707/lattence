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
