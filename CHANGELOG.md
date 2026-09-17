# Changelog

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
Versions before 1.0 may include breaking changes in a minor release.

## [Unreleased]

### Added

- Deterministic cross-layer correlation from AI, agent, and MCP findings to
  concrete cryptographic findings over genuine graph edges.
- A shared version 1 presentation document that preserves stored and traversal
  direction for every hop and carries evidence references into both views.
- A fixed-navigation terminal view and browser dashboard with dense tables,
  filtering, sorting, selected-path details, and JSON copy and export.
- A cross-layer architecture diagram and deterministic terminal demonstration.

## [0.4.1] - 2026-09-16

### Fixed

- Crypto discovery no longer scans Lattence's own JSON, HTML, graph, or
  provider artifacts, including every file below a configured output path.
  Consecutive assessments therefore produce identical inventory counts.
- Quantum-vulnerable singleton nodes are reported as isolated assets instead
  of zero-edge paths. Traversable paths now require at least two nodes and one
  relationship in terminal, structured JSON, and HTML output.
- Applications, agents, tools, and MCP servers now connect to algorithms and
  certificates through evidence-backed `key_exchange` and `protected_by`
  relationships. Dependency imports and configuration references are retained
  as traversal evidence.
- The shared crypto presentation identifies the command that ran, so
  `pqc assess` is no longer mislabeled as `crypto`.

### Compatibility

- Report schema v1 adds optional `quantum_vulnerable_assets` and
  `quantum_vulnerable_paths` summary fields. Existing v1 reports remain valid
  and default both fields to zero.
- v0.4.0 was tagged with output self-contamination, mislabeled singleton
  exposure records, and incomplete trust-graph wiring. v0.4.1 supersedes that
  release without changing the frozen graph or report schema versions.

## [0.4.0] - 2026-09-15

### Added

- Deterministic crypto dependency graph projections and direct and transitive
  quantum-vulnerable dependency paths.
- ML-KEM-768 and ML-DSA-65 migration tests, hybrid TLS validation, and a
  five-component crypto agility score with explicit limiting factors.
- Consent-gated, bounded, reversible key-exchange and signature downgrade
  experiments with deterministic evidence and rollback verification.
- A complete cryptographic assurance guide and architecture and safety
  diagrams.

### Changed

- `pqc assess` now emits the full crypto assessment and normalized findings.
- `crypto chaos` is implemented and requires an exact declared configuration
  file in addition to project-root consent.

## [0.3.0] - 2026-09-15

### Added

- Optional Garak, PyRIT, and Promptfoo adapters behind persistent provider
  enablement. External results normalize into the existing finding schema.
- Read-only `harden` output for one finding or a complete report.
- `policy check` validation of report target nodes against a versioned declared
  scope, with non-zero exit on out-of-scope access.
- An explicit usage error for the reserved `--planner llm` mode.

### Changed

- Clean-wheel acceptance now covers an optional external adapter, hardening,
  and scope policy validation.

## [0.2.0] - 2026-09-10

### Added

- Deterministic single-finding replay through `verify FINDING_ID`.

### Changed

- `scan`, `attack`, and `verify` apply the configured finding severity gate to
  their exit codes.

## [0.1.0] - 2026-09-08

Initial foundation release.

### Added

- Discovery engine: agents, tools, MCP servers, model providers, data
  stores, external services, infrastructure and CI configuration, and
  cryptographic usage, from Python and JavaScript/TypeScript source,
  dependency manifests, and configuration files.
- A security graph built from discovery evidence, with attack path
  traversal and deterministic JSON export.
- A native catalog of 15 attack checks covering prompt injection,
  instruction extraction and override, unsafe output handling and data
  disclosure, excessive agency and unsafe tool use, tool argument
  injection and confused deputy, RAG poisoning, insecure delegation and
  memory poisoning, and resource exhaustion, each with an OWASP LLM
  Top 10 mapping.
- Cryptography and TLS discovery, quantum-vulnerable and post-quantum
  algorithm classification, and a deterministic PQC readiness score.
- Schema-valid JSON reports and self-contained dense HTML reports.
- Terminal scan summaries in plain and color modes.
- The `scan`, `attack`, `pqc assess`, `graph export`, and `report`
  commands, wired to one offline workflow. `harden`, `verify`, `tui`,
  `crypto chaos`, and the `provider` and `policy` commands are scaffolded
  but not yet implemented.
- A deliberately vulnerable reference application at
  `examples/vulnerable-agent`, producing a real cross-layer finding chain
  from indirect prompt injection through to tool argument injection.
- A brand and logo system, and a deterministic scan demonstration GIF.
- CI enforcing lint, strict types, test coverage, schema validity,
  commit and file provenance, prose standards, and a clean-install
  acceptance run.
