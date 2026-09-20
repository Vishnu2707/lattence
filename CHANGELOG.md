# Changelog

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
Versions before 1.0 may include breaking changes in a minor release.

## [1.0.0] - 2026-09-20

### Added

- Public package publication: `lattence` and `lattence[api]` on PyPI,
  verified with an isolated `pipx install lattence`.
- A REST API (`lattence serve`, `lattence-api`): `GET /v1/scan`,
  `POST /v1/attack`, and `GET /v1/chain`, returning the same frozen report
  and presentation models the CLI already serializes.
- A plugin SDK guide documenting the `SecurityProvider` interface against
  the shipped Garak, PyRIT, and Promptfoo adapters.
- Bearer token authentication for the API, with role-based access control
  (`read_findings`, `run_scans`, `run_attacks`, `manage_policy`) issued
  through `lattence rbac create-key/list/revoke`, layered on top of the
  static team token without breaking it.
- An OIDC-compatible SSO extension point (`SSOProvider`), with a shipped
  mock reference provider.
- Durable, queryable audit logging for every `scan`, `attack`, and
  `policy check`, on both the CLI and the API.
- A single-controller-multi-worker job queue (`POST /v1/jobs`,
  `GET /v1/jobs/{id}`, `GET /v1/jobs`), backed by an in-process thread
  pool, RBAC-gated and audited.
- A Docker image and `docker-compose.yml` for a single-container team
  deployment, verified offline against a mounted project with no network
  calls beyond the published port.
- SARIF 2.1.0 output (`lattence sarif`), validated against the real OASIS
  schema, plus a GitHub Action and a self-scan workflow uploading results
  to GitHub code scanning.
- The startup banner now also prints on a bare `lattence` invocation and
  at the top of `lattence tui`, not only `--version`.

### Changed

- The README was cut from 359 lines to a real quickstart; the full
  architecture, cross-layer analysis, PQC, deployment mode, and rule pack
  extension material moved into `docs/`, with a new `docs/architecture.md`
  and `docs/additional-info.md`.
- The controller/worker enterprise deployment design
  (`docs/enterprise-deployment-design.md`), written before RBAC and audit
  logging existed, was updated to distinguish the real single-host job
  queue that shipped from the multi-host case that is still only a
  design.

### Fixed

- Cross-layer output now distinguishes 32 finding correlations from 9 distinct
  structural edge paths in the bundled example. Each finding pairing remains
  visible, but terminal, JSON, and dashboard HTML summaries no longer imply
  32 independent routes.
- The API returned `500` for a server missing `LATTENCE_API_TOKEN`; a
  missing configuration is a service-unavailable condition, not an
  internal error, so it now returns `503`.
- A job submission was audited twice, once by the job controller and once
  by the route handler; fixed to log the submission once.

## [0.5.1] - 2026-09-18

### Fixed

- `lattence graph chain PATH` now prints every discovered cross-layer
  correlation with both finding identifiers, stored and traversal edge
  directions, edge types, and evidence references.
- Enter on a correlated TUI finding now opens the real chain produced by the
  shared correlator, and `[` and `]` select its real graph hops.
- Integration coverage now calls the correlator directly with findings and the
  graph discovered from `examples/vulnerable-agent`.

## [0.5.0] - 2026-09-17

### Added

- Deterministic cross-layer correlation from AI, agent, and MCP findings to
  concrete cryptographic findings over genuine graph edges.
- A shared version 1 presentation document that preserves stored and traversal
  direction for every hop and carries evidence references into both views.
- A fixed-navigation terminal view and browser dashboard with dense tables,
  filtering, sorting, selected-path details, and JSON copy and export.
- A cross-layer architecture diagram and deterministic terminal demonstration.

### Changed

- `lattence tui PATH` now renders the shared terminal view and writes the same
  version 1 data to `presentation.json` for the static dashboard.
- Clean-wheel acceptance now validates the terminal output, byte-identical
  dashboard data, dashboard assets, real edge orientation, and evidence.

### Known limitation

- The graph and presentation data contained genuine cross-layer chains, but
  v0.5.0 did not provide a dedicated command that printed them. Its terminal
  command rendered only the initial overview and did not run an interactive
  key loop. v0.5.1 adds both human-facing paths.

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
