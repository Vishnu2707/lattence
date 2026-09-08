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
