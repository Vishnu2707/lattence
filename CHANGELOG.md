# Changelog

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
Versions before 1.0 may include breaking changes in a minor release.

## [Unreleased]

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
