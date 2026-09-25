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

2026-09-18 D-023
Decision: v0.5.1 validates correlation directly against a discovered project graph and adds dedicated CLI and TUI chain access before any v1.0 work.
Rationale: v0.5 contained real chain data, but its direct correlator coverage used a synthetic graph and no dedicated command printed the chain for a human.

2026-09-20 D-024
Decision: Count a structural cross-layer path by its ordered graph edge identifiers and traversal directions, while retaining every finding-to-path correlation.
Rationale: The bundled example yields 32 valid finding correlations over 9 distinct structural paths; reporting both avoids implying 32 independent routes.

2026-09-20 D-025
Decision: Prepare version 0.5.2 for the first public package-index upload and reserve 1.0.0 for the final milestone.
Rationale: Phase 1 must verify a public pipx install before API and enterprise phases are complete, so publishing 1.0.0 now would misstate completion.

2026-09-20 D-026
Decision: Add a CLI `serve` command that starts lattence-api and takes only --host and --port, outside the universal scan/attack option set, with fastapi and uvicorn imported lazily so the core CLI install stays dependency-light.
Rationale: A long-running server process has no single JSON, out, offline, or fail-on gate semantics, and most CLI users never need the API surface installed.

2026-09-20 D-027
Decision: Phase 3 documents the controller/worker enterprise deployment mode design but implements none of it; Phase 5 builds it against that document once RBAC and audit groundwork exist.
Rationale: A controller/worker runtime needs per-caller identity and an audit trail to be safe at all, and building an ad hoc version now would mean rebuilding the authorization layer correctly in Phase 5 anyway.

2026-09-20 D-028
Decision: Add a `sarif [INPUT]` CLI command that loads a saved report the same way `report` does and writes a schema-validated SARIF 2.1.0 document, rather than adding a `--sarif` flag to every existing command.
Rationale: `report` and `graph export` already establish the pattern of a dedicated INPUT-based command per output format; a new flag on every command would need to be threaded through scan, attack, and report alike for no benefit over one small command.

2026-09-20 D-029
Decision: RBAC is additive to the Phase 2 static bearer token, not a replacement; a request may authenticate with either a per-caller RBAC API key or the legacy team token, and route handlers require a specific Role rather than any router-level dependency.
Rationale: Phase 3's Docker team mode already ships and is already tested against the static token; breaking it to force RBAC adoption would regress a shipped deployment mode for no user benefit, and per-route role requirements are what let the resolved caller reach the audit logging Phase 5 also adds.

2026-09-20 D-030
Decision: Ship SSO as a code-level extension point (an `SSOProvider` protocol plus a `MockSSOProvider` reference implementation), not a real OIDC client library integration.
Rationale: The brief explicitly says full provider integration is not required; a real OIDC client needs JWKS fetching, signature verification, and issuer and audience validation, all genuinely new network-dependent surface that the mock proves the seam for without taking on.

2026-09-20 D-031
Decision: Implement the controller/worker job queue as one in-process controller with a ThreadPoolExecutor worker pool, not a multi-host system, and let /v1/jobs accept the same RBAC-or-legacy-token authentication the direct routes already use.
Rationale: A correct single-host queue is real, testable, and immediately useful; a multi-host queue needs a message broker and worker registration this phase has no basis to choose, and restricting job submission to RBAC-only while the direct routes still accept the legacy token would make the queue strictly worse than calling /v1/scan directly for team-mode users.

2026-09-25 D-032
Decision: Native attack rules whose finding claims untrusted data reaches a
sink (LT-AI-002, LT-AI-007, LT-AI-008) now require a real graph path from an
agent to the target node via `match.requires_path`, checked by
`AttackRunner` using the existing `lattence.graph.traversal.find_attack_paths`
function. Rules that check an intrinsic property of the node itself, not a
data-flow claim, are left as single-node field predicates.
Rationale: A self-scan false positive at workflow.py:208 showed the bug
class directly: a plain f-string was discovered as a `dataset` node with
`sensitivity: unknown`, and LT-AI-002/LT-AI-008 fired on that field shape
alone, with no check that any agent ever reached the node. Requiring a real
path reuses the existing traversal rather than building a second mechanism,
and only changes rules that make a reachability claim in their finding text.

## Milestone A audit: native rule taint/data-flow soundness

Full audit of every native rule pack (attacks: kind=attack, 15 rules; and
the AI attack discovery catalog: kind=detection, 23 rules) for the bug class
found at lattence-cli/src/lattence/cli/workflow.py:208: a rule that matches
on a node's field shape without checking whether untrusted data genuinely
reaches that node through the security graph.

Method: for each attack rule, read its finding message for a reachability or
data-flow claim ("enters the workflow", "reaches an agent", "can propagate
... into agent context") versus a claim about an intrinsic node property
("has delete permission", "has no bounded instruction source"). A rule that
claims reachability but checks only a single node's field is the bug class.
Detection rules (kind=detection) only ever assert "this dependency and this
syntax pattern were found in this file"; they make no reachability claim, so
they are out of scope for this class by construction and are listed for
completeness only.

Attack rules (kind=attack, native runner in lattence-ai/src/lattence_ai/attacks):

- LT-AGENT-001 (excessive agency, `delegation_enabled: true` on agent):
  SOUND. Claims a property of the agent itself, not a flow.
- LT-AGENT-002 (unsafe tool use, `permissions` contains `delete` on tool):
  SOUND. Intrinsic tool property.
- LT-AGENT-003 (insecure delegation, `delegation_enabled: true` on agent):
  SOUND. Same as LT-AGENT-001, different finding framing.
- LT-AGENT-004 (memory poisoning, `memory_enabled: true` on agent):
  SOUND. Intrinsic agent property; the finding names a risk class, not a
  claim that poisoned content already reached this agent.
- LT-AI-001 (direct prompt injection, `instructions_source` absent on agent):
  SOUND. Intrinsic property: the agent has no bounded source at all.
- LT-AI-002 (indirect prompt injection, `sensitivity: unknown` on dataset):
  NEEDED A FIX. Finding text claims unclassified context "can carry hostile
  instructions" into the workflow; this is exactly the bug found at
  workflow.py:208, a discovery artifact with no agent ever wired to it.
  Fixed: added `requires_path` (agent to dataset via calls/accesses,
  max_depth 4).
- LT-AI-003 (sourced system instructions, `instructions_source` exists on
  agent): SOUND. Intrinsic property, informational framing.
- LT-AI-004 (system instruction override, `delegation_enabled: true` on
  agent): SOUND. Intrinsic property.
- LT-AI-005 (unsafe output handling, `side_effects: true` on tool): SOUND.
  Intrinsic tool property; no claim that a specific untrusted input reached
  the tool, only that the tool itself is side-effecting.
- LT-AI-006 (secret exposure, `exposed_value: true` on secret): SOUND.
  Intrinsic secret property.
- LT-AI-007 (retrieval corpus poisoning, `metadata.vector_store: true` on
  database): NEEDED A FIX. Finding text claims the store "can propagate
  poisoned content into agent context," a reachability claim with the same
  shape-only match as LT-AI-002. Fixed: added the same `requires_path`.
- LT-AI-008 (untrusted retrieved context, `sensitivity: unknown` on
  dataset): NEEDED A FIX. Same rule shape and same finding text pattern
  ("enters the workflow ... reaches an agent") as LT-AI-002, same fixture
  collision observed live in the self-scan (both rules fired on the same
  workflow.py:208 node). Fixed: added the same `requires_path`.
- LT-AI-009 (resource exhaustion, `metadata.resource_limits` absent on
  application): SOUND. Intrinsic property: the application has no
  configured limit at all.
- LT-MCP-001 (tool argument injection, `input_schema: {}` on tool): SOUND.
  Intrinsic property: the tool has no schema to validate arguments against.
- LT-MCP-002 (confused deputy, `auth_method: configured` on mcp_server):
  SOUND. Intrinsic property of the server's own configuration.

Detection rules (kind=detection, 20 rules across
lattence-packs/discovery/{frameworks,providers,data,services}): all match on
`dependencies` and `syntax` (import/call patterns) within a single file.
None claims that data from one node reaches another; they report "this
framework/library is present," which is discovery, not an attack finding.
Listed for completeness, no fix needed: LT-AI-101 through LT-AI-106
(frameworks, 6 rules), LT-AI-201 through LT-AI-206 (providers, 6 rules),
LT-AI-301 through LT-AI-305 (data/retrieval, 5 rules), LT-AI-401 through
LT-AI-406 (services, 6 rules).

2026-09-25 D-033
Decision: The self-contained dashboard HTML embeds cross-layer chain data by
having `write_report_artifacts` look for a `presentation.json` file already
sitting next to its output directory, rather than adding a new CLI flag or
having `report` run fresh discovery itself.
Rationale: `report [INPUT]` is contractually a re-render of an already-saved
report and does not run discovery; `tui`/`graph chain` already write
`presentation.json` as a side effect (T-096, T-098). Reusing that file keeps
`report`'s option surface exactly as documented in `BUILD/CONTRACTS.md`, adds
no new data format, and degrades to an explicit empty chain state when no
presentation file is present instead of failing.
