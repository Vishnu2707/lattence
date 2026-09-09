# Changelog

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
Versions before 1.0 may include breaking changes in a minor release.

## [Unreleased]

### Fixed

- The built wheel now bundles the full runtime source (`discovery`,
  `graph`, `evidence`, `mcp`, `lattence_ai`, `lattence_crypto`) and depends
  on real third-party libraries instead of workspace-only package names.
  Previously, installing the wheel outside the uv workspace failed.

### Changed

- CI gained `types` (`mypy --strict` per package) and `acceptance`
  (clean-venv install, then `scan`, `attack`, `report` against
  `examples/vulnerable-agent`) jobs, alongside a coverage gate at 85
  percent.
- `.claude/`, a local coding-assistant mirror of `BUILD/agents/`, is no
  longer tracked.

### Added

- `README.md`, `SECURITY.md`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`,
  `GOVERNANCE.md`, `MAINTAINERS.md`, `SUPPORT.md`, `ROADMAP.md`, and this
  changelog.

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
