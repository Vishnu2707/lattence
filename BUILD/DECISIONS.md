# Decision log

Append decisions as three lines: date and identifier, decision, and rationale.
Do not rewrite earlier entries.

2026-09-08 D-001
Decision: Core models use a shared namespace package with graph-owned schemas.
Rationale: Separate workspace packages can extend one public Python namespace.

2026-09-08 D-002
Decision: The documented rule schema is bundled with the discovery package.
Rationale: Installed wheels validate offline, while a test prevents schema drift.

2026-09-08 D-003
Decision: The root project builds the public package from `lattence-cli/src`.
Rationale: One distribution owns the binary while workspace libraries stay separate.
## 2026-09-08, T-038, installed presentation namespace
Decision: Place terminal presentation code under `lattence.cli.presentation`.
Consequence: The frozen `lattence` namespace remains importable from the wheel.

2026-09-08 D-004
Decision: Duplicate bare test module names broke full-suite collection, so every test directory is now a package.
Rationale: Scoped runs never loaded both names; package markers preserve predictable dotted imports as the tree grows.

2026-09-08 D-005
Decision: CI coverage gate is set to 85 percent through `pytest-cov`, against a current total near 91 percent.
Rationale: The threshold catches real regressions without pinning to the exact current number and breaking on small, legitimate drops.

2026-09-08 D-006
Decision: The wheel force-includes the source of every workspace package it needs, and root dependencies list real third-party libraries instead of the workspace package names.
Rationale: A wheel built with the workspace names as dependencies cannot be installed outside the uv workspace, and was missing most of the runtime import surface.

2026-09-09 D-007
Decision: `--version` now prints the frozen ASCII banner before the version line, changing its previously exact-match output contract.
Rationale: BUILD/DESIGN.md allows a banner on the version command and at TUI start; the existing test pinned a narrower contract than the design system called for, so the test was widened to check the version line specifically rather than the whole output.

2026-09-10 D-008
Decision: v0.2 scopes to CLI-contract gaps with a precise existing spec (the fail-on exit gate, finding replay verification), and defers harden, tui, crypto chaos, provider, policy, and the llm planner pending a scoping decision for each.
Rationale: BUILD/CONTRACTS.md names these commands but does not specify their behavior in enough detail to implement without inventing product decisions unilaterally.

2026-09-15 D-009
Decision: v0.3 adds optional Garak, PyRIT, and Promptfoo adapters, read-only harden output, and declared-scope policy checks. TUI moves to v0.5, crypto chaos stays in v0.4, and the LLM planner moves to v0.4 or later with an explicit v0.3 not-implemented error.
Rationale: This scope preserves frozen interfaces, keeps external engines optional, and separates read-only guidance and policy enforcement from mutation and model-backed planning.

2026-09-15 D-010
Decision: The SecurityProvider runtime and external adapters live under the SHIP-owned `lattence.providers` namespace.
Rationale: External engines are integrations, while the AISEC role owns native attack rules and explicitly excludes the provider interface.

2026-09-15 D-011
Decision: Provider enablement is stored in a version 1 `providers.json` file under the command's `--out` directory, and availability is detected independently.
Rationale: Project-local state is deterministic and testable, while separate availability lets optional engines remain absent without invalidating configuration.

2026-09-15 D-012
Decision: Attack runs execute only providers that are both enabled and available, and `--offline` skips every external provider.
Rationale: This preserves optional installation and gives the existing offline flag a strict no-external-execution guarantee.

2026-09-15 D-013
Decision: `harden INPUT` treats an `LT-` value as a finding identifier resolved from the report under `--out`; every other value is a report path or directory.
Rationale: The frozen command has one positional argument, so this preserves that contract while supporting both requested read-only input forms.

2026-09-15 D-014
Decision: Policy checks define touched nodes as unique `Finding.target_node_id` values recorded in a report, with remote non-offline reproductions requiring matching URL scope.
Rationale: Findings record the targets actually exercised, while requiring URL declarations prevents project source authorization from implicitly authorizing external endpoint attacks.

2026-09-15 D-015
Decision: `policy check` auto-loads `lattence.targets.yaml` beside the report and accepts `--scope PATH` for an equivalent declaration file.
Rationale: Automatic lookup covers the standard project-local workflow, while the explicit option supports renamed or separately stored scope declarations.

2026-09-15 D-016
Decision: The combined wheel carries a root PEP 561 marker, and strict type checking uses `lattence-cli/src` as an explicit package base.
Rationale: The project uses a namespace package in source and a combined wheel at distribution time, so both contexts need one canonical `lattence.providers` module path.

2026-09-15 D-017
Decision: v0.4 is the flagship cryptography release: crypto graph projections, direct and transitive quantum-vulnerable dependency detection, separate ML-KEM and ML-DSA migration tests, hybrid TLS validation, deterministic crypto agility scoring, consent-gated reversible crypto chaos, downgrade validation, and a complete documentation section with diagrams.
Rationale: This preserves the frozen graph and report contracts while connecting the existing cryptographic inventory to actionable migration and safely contained resilience testing; the model-backed LLM planner remains deferred.

2026-09-16 D-018
Decision: Report schema v1 gains optional `quantum_vulnerable_assets` and `quantum_vulnerable_paths` summary counts, and a path requires at least one relationship while an isolated vulnerable node is reported only as an asset.
Rationale: v0.4.0 incorrectly labeled singleton zero-edge records as paths; optional defaulted fields preserve validation and deserialization of existing v1 reports while making the distinction explicit for every output format.

2026-09-16 D-019
Decision: Crypto ownership uses existing `key_exchange` and `protected_by` edges, selecting exact source, application entrypoint, explicit source/config reference, or same-module evidence in that order; dependency imports remain explicit library `implements` edges in the crypto projection.
Rationale: These bounded signals connect applications, agents, tools, and MCP servers to crypto assets without changing the frozen graph vocabulary or creating name-based and project-wide Cartesian links.

2026-09-16 D-020
Decision: v0.5 adds deterministic cross-layer AI-to-crypto topology chains plus a TUI and dashboard with one shared presentation contract; the model-backed planner remains deferred.
Rationale: The vulnerable fixture has genuine connecting edges but requires mixed-orientation traversal from an affected dataset through its accessing tool to crypto protection, so every hop must retain stored and traversal direction instead of being mislabeled as an all-forward path.

2026-09-16 D-021
Decision: Cross-layer chains use bounded shortest topology walks over existing edges, retain stored and traversal direction per hop, and live in a separate version 1 presentation model consumed by both TUI and dashboard.
Rationale: This permits honest resource-to-owner traversal and shared interaction data without mutating the directed graph or changing backward-compatible report schema v1.

2026-09-17 D-022
Decision: Shared presentation generation limits cross-layer correlation to four graph hops.
Rationale: The accepted fixture needs two hops, while an eight-hop all-path search expands excessively on the current graph before shortest-path filtering.
