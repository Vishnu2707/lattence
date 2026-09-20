# v0.1 task ledger

Each line is one commit unit. Status values are `todo`, `doing`, `done`, and
`blocked`. A task may start only when every dependency is done.

[T-001] [v0.1] [GRAPH] implement project, node, edge, and graph models | deps: none | status: done | commit: self
[T-002] [v0.1] [EVID] implement finding, evidence, and replay models | deps: T-001 | status: done | commit: self
[T-003] [v0.1] [DISCO] implement versioned YAML rule pack loader and validation | deps: T-001 | status: done | commit: self
[T-004] [v0.1] [SHIP] create installable package and command scaffold | deps: T-001,T-002 | status: done | commit: self
[T-005] [v0.1] [DISCO] inventory project files with ignore and size controls | deps: T-001 | status: done | commit: self
[T-006] [v0.1] [DISCO] parse Python imports, calls, decorators, and assignments | deps: T-005 | status: done | commit: self
[T-007] [v0.1] [DISCO] parse JavaScript and TypeScript imports and calls | deps: T-005 | status: done | commit: self
[T-008] [v0.1] [DISCO] discover Python and Node dependency manifests | deps: T-005 | status: done | commit: self
[T-009] [v0.1] [DISCO] detect agent framework applications and definitions | deps: T-003,T-006,T-007,T-008 | status: done | commit: self
[T-010] [v0.1] [DISCO] detect model provider clients and model configuration | deps: T-003,T-006,T-007,T-008 | status: done | commit: self
[T-011] [v0.1] [DISCO] detect agents, tools, permissions, and delegation | deps: T-009,T-010 | status: done | commit: self
[T-012] [v0.1] [MCPX] discover MCP server configuration and exposed tools | deps: T-001,T-005 | status: done | commit: self
[T-013] [v0.1] [DISCO] detect RAG pipelines, datasets, and vector stores | deps: T-003,T-006,T-007,T-008 | status: done | commit: self
[T-014] [v0.1] [DISCO] detect APIs, databases, caches, and external services | deps: T-003,T-006,T-007,T-008 | status: done | commit: self
[T-015] [v0.1] [DISCO] detect credential references, OAuth, JWT, and identities | deps: T-003,T-006,T-007 | status: done | commit: self
[T-016] [v0.1] [CRYPTO] discover TLS settings, certificates, and key exchange | deps: T-001,T-005 | status: done | commit: self
[T-017] [v0.1] [CRYPTO] discover cryptographic libraries and algorithms | deps: T-001,T-005,T-008 | status: done | commit: self
[T-018] [v0.1] [DISCO] discover container, cluster, infrastructure, and CI configuration | deps: T-003,T-005 | status: done | commit: self
[T-019] [v0.1] [DISCO] aggregate discovery with stable identifiers and deduplication | deps: T-011,T-012,T-013,T-014,T-015,T-016,T-017,T-018 | status: done | commit: self
[T-020] [v0.1] [GRAPH] construct security graph edges from discovery evidence | deps: T-001,T-019 | status: done | commit: self
[T-021] [v0.1] [GRAPH] implement graph traversal and attack path queries | deps: T-020 | status: done | commit: self
[T-022] [v0.1] [GRAPH] export deterministic security graph JSON | deps: T-020 | status: done | commit: self
[T-023] [v0.1] [SHIP] validate owned target declarations before attack execution | deps: T-004 | status: done | commit: self
[T-024] [v0.1] [AISEC] implement attack rule runner and observation result | deps: T-002,T-003,T-020,T-023 | status: done | commit: self
[T-025] [v0.1] [AISEC] add direct and indirect prompt injection tests | deps: T-024 | status: done | commit: self
[T-026] [v0.1] [AISEC] add system instruction extraction and override tests | deps: T-024 | status: done | commit: self
[T-027] [v0.1] [AISEC] add unsafe output handling and data disclosure tests | deps: T-024 | status: done | commit: self
[T-028] [v0.1] [AISEC] add excessive agency and unsafe tool use tests | deps: T-024 | status: done | commit: self
[T-029] [v0.1] [AISEC] add tool argument injection and confused deputy tests | deps: T-024,T-012 | status: done | commit: self
[T-030] [v0.1] [AISEC] add RAG poisoning and untrusted context tests | deps: T-024,T-013 | status: done | commit: self
[T-031] [v0.1] [AISEC] add insecure delegation and memory poisoning tests | deps: T-024,T-011 | status: done | commit: self
[T-032] [v0.1] [AISEC] add denial, resource exhaustion, and boundary tests | deps: T-024 | status: done | commit: self
[T-033] [v0.1] [AISEC] assemble 15-test native attack catalog | deps: T-025,T-026,T-027,T-028,T-029,T-030,T-031,T-032 | status: done | commit: self
[T-034] [v0.1] [CRYPTO] classify quantum-vulnerable and post-quantum algorithms | deps: T-016,T-017,T-020 | status: done | commit: self
[T-035] [v0.1] [CRYPTO] calculate deterministic PQC readiness percentage | deps: T-034 | status: done | commit: self
[T-036] [v0.1] [EVID] normalize findings and write schema-valid JSON reports | deps: T-002,T-022,T-033,T-035 | status: done | commit: self
[T-037] [v0.1] [EVID] render self-contained dense HTML reports | deps: T-036 | status: done | commit: self
[T-038] [v0.1] [UX] implement terminal scan summary and plain output modes | deps: T-004,T-019,T-021,T-035,T-036 | status: done | commit: self
[T-039] [v0.1] [SHIP] wire scan, attack, PQC, graph, and report commands | deps: T-022,T-023,T-033,T-035,T-037,T-038 | status: done | commit: self
[T-040] [v0.1] [UX] create logo system and raster brand assets | deps: none | status: done | commit: self
[T-041] [v0.1] [SHIP] build deliberately vulnerable reference application | deps: T-012,T-025,T-029,T-039 | status: done | commit: self
[T-042] [v0.1] [UX] author deterministic scan demonstration tape and GIF | deps: T-038,T-040,T-041 | status: done | commit: self
[T-043] [v0.1] [SHIP] write accurate README and responsible-use guidance | deps: T-039,T-040,T-041,T-042 | status: done | commit: self
[T-044] [v0.1] [SHIP] enforce lint, strict types, coverage, schemas, provenance, and prose in CI | deps: T-036,T-039,T-043 | status: done | commit: self
[T-045] [v0.1] [SHIP] pass clean-clone scan, attack, and HTML report acceptance | deps: T-041,T-042,T-043,T-044 | status: done | commit: self

## Milestone gate

After T-045, run the full suite, create the annotated `v0.1` tag on `dev`, open
the milestone pull request to `main`, merge with a merge commit, then fast-forward
`dev` to `main`.

v0.1.0 shipped 2026-09-08. `dev` and `main` are both at the release commit.

# v0.2 task ledger

v0.2 closes CLI-contract gaps left by v0.1's scaffolded commands, favoring
tasks whose behavior `BUILD/CONTRACTS.md` and `BUILD/DESIGN.md` already
specify precisely, over inventing product behavior for commands the
contracts name but do not describe (see "Deferred" below).

[T-046] [v0.2] [SHIP] wire the --fail-on severity gate to scan and attack exit codes | deps: none | status: done | commit: self
[T-047] [v0.2] [AISEC] implement deterministic single-finding replay verification | deps: T-024 | status: done | commit: self
[T-048] [v0.2] [SHIP] wire the verify command to replay verification | deps: T-047 | status: done | commit: self

## T-047 design note

`AttackRunner.observe(test)` in `lattence-ai/src/lattence_ai/attacks/runner.py`
is already a pure function of `(rule_id, target_node_id)` against a graph. A
`Finding`'s `id` and `target_node_id`, together with the `SecurityGraph`
already embedded in a `Report`, are enough to rebuild the same `TestCase` and
re-observe it without rescanning the project. T-047 adds a function that
takes a `Report` and a finding id, rebuilds the runner from the report's own
graph and the loaded native attack catalog, re-observes the one test, and
returns whether it still matches. T-048 wires `verify FINDING_ID` to it,
reading the existing report from `--out` (there is no path argument on
`verify` in the CLI contract), and prints `VULNERABLE` if it still matches,
`PASS` if it no longer does, or `BLOCKED` if the finding id or report is not
found, per the valid state words in `BUILD/DESIGN.md`.

## Milestone gate

After the last v0.2 task, run the full suite, create the annotated `v0.2` tag
on `dev`, and hold for review before opening a pull request to `main` or
starting v0.3.

# v0.3 task ledger

v0.3 adds optional external security engines, read-only remediation output,
and declared-scope policy validation. External engines are never hard
dependencies. Their results normalize into the frozen `Finding` schema through
the frozen `SecurityProvider` interface.

[T-049] [v0.3] [SHIP] implement the SecurityProvider runtime and strict provider result validation | deps: T-002,T-024 | status: done | commit: self
[T-050] [v0.3] [SHIP] add an optional Garak SecurityProvider adapter | deps: T-049 | status: done | commit: self
[T-051] [v0.3] [SHIP] add an optional PyRIT SecurityProvider adapter | deps: T-049 | status: done | commit: self
[T-052] [v0.3] [SHIP] add an optional Promptfoo SecurityProvider adapter | deps: T-049 | status: done | commit: self
[T-053] [v0.3] [SHIP] persist provider enablement and wire provider enable and list | deps: T-049 | status: done | commit: self
[T-054] [v0.3] [SHIP] execute enabled external providers and merge normalized findings into attack reports | deps: T-050,T-051,T-052,T-053 | status: done | commit: self
[T-055] [v0.3] [EVID] build structured read-only remediation plans from report findings and evidence | deps: T-036 | status: done | commit: self
[T-056] [v0.3] [SHIP] wire harden for a finding id or scan report without modifying project files | deps: T-055 | status: done | commit: self
[T-057] [v0.3] [SHIP] validate report target nodes against a versioned declared-scope file | deps: T-023,T-036 | status: done | commit: self
[T-058] [v0.3] [SHIP] wire policy check with non-zero exit on every out-of-scope target node | deps: T-057 | status: done | commit: self
[T-059] [v0.3] [SHIP] reject --planner llm with a clear not-implemented error | deps: T-004 | status: done | commit: self
[T-060] [v0.3] [SHIP] document v0.3 commands and optional external engine setup | deps: T-054,T-056,T-058,T-059 | status: done | commit: self
[T-061] [v0.3] [SHIP] pass clean-clone external provider, harden, and policy acceptance | deps: T-060 | status: done | commit: self
[T-062] [v0.3] [SHIP] satisfy the milestone formatting gate for v0.3 changes | deps: T-061 | status: done | commit: self
[T-063] [v0.3] [SHIP] satisfy the milestone strict typing gate for provider modules | deps: T-062 | status: done | commit: self
[T-064] [v0.3] [ORCH] record the v0.3 release gate and changelog | deps: T-063 | status: done | commit: self

## v0.3 scope notes

- `harden` is read-only. It prints a structured remediation list per finding
  from `Finding.remediation`, the target node, and reproduction context in the
  evidence bundle. It has no patch or file-modification mode.
- `provider enable` and `provider list` manage Garak, PyRIT, and Promptfoo
  adapters. Missing external engines produce an unavailable provider state,
  not an installation failure for Lattence.
- `policy check` reads a scan or attack report and a
  `lattence.targets.yaml` or equivalent versioned scope declaration. It checks
  the actual target nodes recorded in the report graph and exits non-zero when
  any touched node is outside the declaration.
- `--planner llm` remains recognized but not implemented. It fails clearly and
  never falls back silently.

## Deferred after v0.3

- `tui` moves to v0.5 with the dashboard so both use one visual grammar.
- `crypto chaos` remains in v0.4 as originally scheduled.
- The model-backed LLM planner moves to v0.4 or later.

## v0.3 milestone gate

After T-064, run the full suite, create and push the annotated `v0.3.0` tag on
`dev`, then run acceptance from a fresh clean clone. Hold at the tag for review
before opening a milestone pull request or starting v0.4.

# v0.4 task ledger

v0.4 is the flagship post-quantum release. It turns discovered cryptography
into a dependency graph, identifies quantum-vulnerable dependency paths,
tests ML-KEM and ML-DSA migration readiness, validates hybrid TLS, scores
crypto agility, and runs bounded reversible downgrade chaos only against
explicitly declared targets. The release includes a complete documentation
section and diagrams for the end-to-end workflow.

[T-065] [v0.4] [CRYPTO] build deterministic cryptographic dependency graph projections | deps: T-020,T-034 | status: done | commit: self
[T-066] [v0.4] [CRYPTO] detect quantum-vulnerable direct and transitive dependency paths | deps: T-065 | status: done | commit: self
[T-067] [v0.4] [CRYPTO] test ML-KEM migration compatibility and readiness | deps: T-065,T-066 | status: done | commit: self
[T-068] [v0.4] [CRYPTO] test ML-DSA migration compatibility and readiness | deps: T-065,T-066 | status: done | commit: self
[T-069] [v0.4] [CRYPTO] validate hybrid TLS key exchange and signature configurations | deps: T-067,T-068 | status: done | commit: self
[T-070] [v0.4] [CRYPTO] calculate deterministic crypto agility scores and limiting factors | deps: T-066,T-067,T-068,T-069 | status: done | commit: self
[T-071] [v0.4] [CHAOS] define bounded reversible crypto mutation plans and safety guards | deps: T-023,T-065 | status: done | commit: self
[T-072] [v0.4] [CHAOS] execute contained key-exchange downgrade experiments with rollback | deps: T-067,T-069,T-071 | status: done | commit: self
[T-073] [v0.4] [CHAOS] execute contained signature downgrade experiments with rollback | deps: T-068,T-069,T-071 | status: done | commit: self
[T-074] [v0.4] [CHAOS] validate downgrade resistance with deterministic evidence capture | deps: T-072,T-073 | status: done | commit: self
[T-075] [v0.4] [EVID] normalize migration, agility, and downgrade results into findings | deps: T-070,T-074 | status: done | commit: self
[T-076] [v0.4] [SHIP] wire PQC assessment and consent-gated crypto chaos workflows | deps: T-023,T-075 | status: done | commit: self
[T-077] [v0.4] [UX] render crypto graph, migration, agility, and downgrade terminal output | deps: T-070,T-075,T-076 | status: done | commit: self
[T-078] [v0.4] [UX] create flagship crypto architecture and migration workflow diagrams | deps: T-077 | status: done | commit: self
[T-079] [v0.4] [SHIP] author the complete v0.4 cryptography documentation section | deps: T-076,T-078 | status: done | commit: self
[T-080] [v0.4] [SHIP] pass clean-clone crypto assessment, chaos, and downgrade acceptance | deps: T-079 | status: done | commit: self
[T-081] [v0.4] [ORCH] record the v0.4 release gate and changelog | deps: T-080 | status: done | commit: self

## v0.4 scope notes

- The crypto graph is an offline deterministic projection of the existing
  security graph and discovery evidence. It includes algorithms, libraries,
  certificates, TLS configuration, and the dependency paths that connect
  them, without changing frozen graph or report schemas.
- Quantum-vulnerable dependency detection covers direct and transitive paths.
  Migration testing separately evaluates ML-KEM key establishment and ML-DSA
  signatures, then validates classical-plus-PQC hybrid TLS configurations.
- Crypto agility is a deterministic score with explicit limiting factors,
  derived from replaceability, configurability, dependency exposure,
  migration readiness, and downgrade resistance.
- Crypto chaos requires an owned-target declaration, operates only on bounded
  local configuration targets, records deterministic dry runs and evidence,
  and restores every mutation on success, failure, or timeout.
- `--planner llm` remains recognized but not implemented in v0.4. It continues
  to fail clearly instead of falling back to the rules planner.

## v0.4 milestone gate

After T-081, run the full suite, create and push the annotated `v0.4.0` tag on
`dev`, then run crypto assessment, consent-gated chaos, downgrade validation,
and documentation acceptance from a fresh clean clone. Hold at the tag for
review before opening a milestone pull request or starting v0.5.

# v0.4.1 repair task ledger

v0.4.1 corrects the v0.4 crypto assessment before any v0.5 work begins. The
repair prevents generated-output self-ingestion, separates isolated vulnerable
assets from traversable paths, connects crypto assets to the main trust graph
using evidence-backed ownership and reference relationships, and corrects the
PQC command heading.

[T-082] [v0.4.1] [CRYPTO] exclude generated and configured output artifacts from crypto discovery | deps: T-081 | status: done | commit: self
[T-083] [v0.4.1] [ORCH] define isolated crypto asset and traversable path report semantics | deps: T-082 | status: done | commit: self
[T-084] [v0.4.1] [EVID] report isolated vulnerable assets separately from traversable paths in JSON HTML and terminal output | deps: T-083 | status: done | commit: self
[T-085] [v0.4.1] [GRAPH] wire crypto assets into the trust graph through ownership proximity dependency and config-reference evidence | deps: T-084 | status: done | commit: self
[T-086] [v0.4.1] [UX] render command-specific PQC assessment and crypto chaos headings | deps: T-085 | status: done | commit: self
[T-087] [v0.4.1] [SHIP] pass repeated-assessment attack and crypto-chaos clean-clone acceptance | deps: T-086 | status: done | commit: self
[T-088] [v0.4.1] [ORCH] record the v0.4.1 release gate changelog and tag | deps: T-087 | status: done | commit: self

## v0.4.1 relationship design

- Keep the frozen `key_exchange` and `protected_by` relationship types.
  `key_exchange` connects an owning component to transport or key-exchange
  configuration. `protected_by` connects an owning component to encryption,
  signature, hash, certificate, and other cryptographic protection assets.
- Resolve ownership by strongest available evidence in order: exact source,
  explicit application entrypoint, a source/config file reference from a
  component source, then the nearest common project module directory. Do not
  create a project-wide Cartesian product or infer relationships from an
  algorithm name alone.
- Preserve evidence paths and record the binding reason in edge metadata so a
  cross-layer traversal is explainable and deterministic.

## v0.4.1 milestone gate

After T-088, run the full suite, create and push annotated tag `v0.4.1` on
`dev`, then perform acceptance from a fresh clone of that tag. Run `pqc assess`
twice and require identical node, relationship, isolated-asset, and path counts;
also run `attack` and `crypto chaos` against the bundled examples. Hold for
review before proposing v0.5 scope.

# v0.5 task ledger

v0.5 adds deterministic cross-layer AI-to-crypto analysis and two presentation
surfaces over one shared information architecture. It uses only real security
graph edges, records the stored direction and traversal direction of every hop,
and exposes evidence without introducing a model-backed planner.

[T-089] [v0.5] [ORCH] define cross-layer chain semantics and the shared TUI and dashboard data contract | deps: T-088 | status: done | commit: self
[T-090] [v0.5] [GRAPH] implement deterministic orientation-aware cross-layer topology traversal | deps: T-089 | status: done | commit: self
[T-091] [v0.5] [EVID] target crypto findings at the concrete algorithm certificate or TLS nodes that support them | deps: T-084,T-090 | status: done | commit: self
[T-092] [v0.5] [AISEC] correlate AI findings to crypto findings through genuine graph paths with stable explanations | deps: T-090,T-091 | status: done | commit: self
[T-093] [v0.5] [EVID] serialize cross-layer chains and evidence drill-down into a strict presentation data model | deps: T-092 | status: done | commit: self
[T-094] [v0.5] [UX] implement shared visual tokens navigation labels tables and detail-panel grammar | deps: T-089,T-093 | status: done | commit: self
[T-095] [v0.5] [UX] implement the keyboard-driven TUI shell with the fixed twelve-section navigation | deps: T-094 | status: done | commit: self
[T-096] [v0.5] [UX] implement the dashboard shell with fixed rail dense tables filters and side-panel details | deps: T-094 | status: done | commit: self
[T-097] [v0.5] [UX] implement interactive attack-graph path selection and cross-layer evidence drill-down | deps: T-095,T-096 | status: done | commit: self
[T-098] [v0.5] [SHIP] wire lattence tui and dashboard data export to the shared cross-layer workflow | deps: T-093,T-097 | status: done | commit: self
[T-099] [v0.5] [UX] add the cross-layer chain diagram and deterministic TUI demonstration assets | deps: T-097,T-098 | status: done | commit: self
[T-100] [v0.5] [SHIP] document cross-layer analysis TUI dashboard traversal and evidence workflows | deps: T-098,T-099 | status: done | commit: self
[T-101] [v0.5] [SHIP] verify vulnerable-agent exposes LT-AI-002 through real edges to a concrete crypto weakness | deps: T-091,T-092,T-098 | status: done | commit: self
[T-102] [v0.5] [SHIP] pass clean-wheel and fresh-clone TUI dashboard and cross-layer acceptance | deps: T-100,T-101 | status: done | commit: self
[T-103] [v0.5] [ORCH] record the v0.5 release gate changelog and annotated tag | deps: T-102 | status: done | commit: self

## v0.5 cross-layer semantics

- A cross-layer chain starts at an AI, agent, or MCP finding target and ends at
  a concrete crypto finding target. Every hop must be an existing graph edge.
- Traversal may follow an edge forward or backward to move from an affected
  resource to its owning or accessing component. Output records both the edge's
  stored direction and the traversal direction. It never calls a mixed-
  orientation topology chain an all-forward directed path.
- The acceptance fixture must expose `LT-AI-002` at
  `dataset:rag-pipeline:app.py:15` through genuine edges to a vulnerable crypto
  node that explains TLS 1.2 or partial hybrid TLS. The current graph already
  contains the two-edge topology chain from that dataset through
  `tool:app.py:delete_customer_record` to vulnerable X25519.
- The TUI and dashboard use the fixed twelve-entry navigation from
  `BUILD/DESIGN.md`. Dense tables, keyboard navigation, filters, side-panel
  details, path highlighting, JSON copy, and export share one data contract and
  visual grammar.
- `--planner llm` remains recognized and not implemented. Cross-layer analysis
  is deterministic graph traversal.

## v0.5 milestone gate

After T-103, run the full suite, create and push annotated tag `v0.5.0` on
`dev`, then run acceptance from a fresh clone of the tag. Acceptance must print
one real end-to-end `LT-AI-002` cross-layer chain with every stored graph edge,
orientation, crypto endpoint, and evidence reference. Hold for review before
v1.0.

# v0.5.1 repair task ledger

v0.5.1 closes the validation and human-surfacing gaps in v0.5 without changing
the real graph data or cross-layer correlation semantics.

[T-104] [v0.5.1] [ORCH] scope the real-graph validation and chain-surfacing repair | deps: T-103 | status: done | commit: self
[T-105] [v0.5.1] [AISEC] test cross-layer correlation directly against the discovered vulnerable-agent graph | deps: T-104 | status: done | commit: self
[T-106] [v0.5.1] [SHIP] expose real cross-layer findings through the graph chain command | deps: T-105 | status: done | commit: self
[T-107] [v0.5.1] [UX] wire TUI finding detail and hop navigation to real cross-layer correlations | deps: T-106 | status: done | commit: self
[T-108] [v0.5.1] [SHIP] correct release documentation and pass fresh chain acceptance | deps: T-107 | status: done | commit: self
[T-109] [v0.5.1] [ORCH] record the v0.5.1 release gate and annotated tag | deps: T-108 | status: done | commit: self

## v0.5.1 milestone gate

After T-109, run the full suite, create and push annotated tag `v0.5.1` on
`dev`, then run `graph chain` against `examples/vulnerable-agent` from a fresh
checkout. The literal command output must show both finding identifiers, both
real edge types, their orientation, and every evidence reference. Hold at the
tag for review. Do not start v1.0.

# v1.0 phase 0 gate

[T-110] [v1.0 phase 0] [ORCH] distinguish finding correlations from structural paths across terminal JSON and dashboard output | deps: T-109 | status: done | commit: self

The remaining phases are scoped only after this gate is reviewed. Phase 1 is
packaging and local install, Phase 2 is API and plugin SDK, Phase 3 is Docker
deployment, Phase 4 is SARIF and CI, Phase 5 is enterprise controls and workers,
and Phase 6 is final documentation. Do not start the next phase before review.

# v1.0 phase 1 task ledger

Phase 1 prepares a public pre-v1 package, validates both distribution formats,
then requires a real package-index upload and clean public pipx install before
the gate. The distribution version is `0.5.2`; `1.0.0` is reserved for the
final milestone.

[T-111] [v1.0 phase 1] [SHIP] finalize public package metadata and version | deps: T-110 | status: done | commit: self
[T-112] [v1.0 phase 1] [SHIP] validate wheel and source archive metadata and clean command parity | deps: T-111 | status: done | commit: self
[T-113] [v1.0 phase 1] [SHIP] prepare exact package-index upload and clean pipx verification procedure | deps: T-112 | status: done | commit: self
[T-114] [v1.0 phase 1] [SHIP] publish package and verify public pipx installation | deps: T-113 | status: done | commit: self
[T-115] [v1.0 phase 1] [ORCH] run full phase gate and record acceptance | deps: T-114 | status: done | commit: self

## v1.0 phase 1 milestone gate

Package `lattence` 0.5.2 is published on the real public PyPI index
(`https://pypi.org/pypi/lattence/json` lists release `0.5.2` with wheel and
sdist uploaded 2026-09-20). Two independent `pipx install lattence` runs
against an isolated `PIPX_HOME`/`PIPX_BIN_DIR` against the public index both
installed version 0.5.2 and printed the correct banner and version string
from the isolated bin path. Phase 1 gate closed. Hold for review before
scoping Phase 2.

# v1.0 phase 2 task ledger

Phase 2 exposes scan, attack, and cross-layer chain results over HTTP and
documents the plugin SDK. The API is additive: it reuses the frozen
`lattence.graph`, `lattence.evidence`, and presentation Pydantic models from
`BUILD/CONTRACTS.md` without redefining them, and does not change CLI
behavior, report schema, or graph or finding contracts. `lattence-api` is an
existing empty workspace member; this phase fills it in. Authentication is
static bearer token only for v1.0. RBAC, SSO, and multi-tenant access control
are explicitly deferred to Phase 5.

[T-116] [v1.0 phase 2] [API] scaffold the lattence-api application and dependency wiring | deps: T-115 | status: done | commit: self
[T-117] [v1.0 phase 2] [API] wire GET /v1/scan to the existing scan workflow and Project and SecurityGraph models | deps: T-116 | status: done | commit: self
[T-118] [v1.0 phase 2] [API] wire POST /v1/attack to the existing attack workflow and Finding and EvidenceBundle models | deps: T-116 | status: done | commit: self
[T-119] [v1.0 phase 2] [API] wire GET /v1/chain to the existing graph chain workflow and CrossLayerChain models | deps: T-116 | status: done | commit: self
[T-120] [v1.0 phase 2] [API] add bearer token authentication for all v1 routes | deps: T-117,T-118,T-119 | status: done | commit: self
[T-121] [v1.0 phase 2] [API] validate every API response against report.v1.json and the SecurityPresentation model | deps: T-120 | status: done | commit: self
[T-122] [v1.0 phase 2] [SHIP] document the plugin SDK for third-party SecurityProvider adapters using the Garak, PyRIT, and Promptfoo adapters as the reference implementation | deps: T-116 | status: done | commit: self
[T-123] [v1.0 phase 2] [SHIP] document API authentication and record RBAC and SSO as deferred to Phase 5 | deps: T-120 | status: done | commit: self
[T-124] [v1.0 phase 2] [SHIP] add live-instance API integration tests against examples/vulnerable-agent asserting report schema conformance | deps: T-121 | status: done | commit: self
[T-125] [v1.0 phase 2] [SHIP] wire lattence-api into the package build, add a CLI serve command, and finalize workspace metadata | deps: T-124,T-122,T-123 | status: done | commit: self
[T-126] [v1.0 phase 2] [SHIP] satisfy the full-suite lint typing and prose gate for phase 2 changes | deps: T-125 | status: done | commit: self
[T-127] [v1.0 phase 2] [ORCH] record the v1.0 phase 2 release gate and annotated tag | deps: T-126 | status: done | commit: self

## v1.0 phase 2 scope notes

- The API layer is a thin HTTP surface over the existing deterministic
  workflows (`lattence.cli.workflow`, `graph_chain_command`, and the provider
  runtime). It does not reimplement scan, attack, or chain logic.
- `GET /v1/scan`, `POST /v1/attack`, and `GET /v1/chain` accept a project path
  or an existing report path, mirroring the CLI contract's `[PATH]` and
  `[INPUT]` arguments, and return the same Pydantic models the CLI already
  serializes, so responses validate against `docs/schemas/report.v1.json` and
  the `SecurityPresentation` model without a parallel schema.
- Authentication is a single static bearer token read from environment
  configuration, checked on every v1 route. No user store, roles, or session
  management ships in Phase 2. `BUILD/notes/` for the API module records this
  explicitly so Phase 5 RBAC and SSO work does not assume more exists today.
- The plugin SDK doc explains `discover`, `generate_tests`, `execute`, and
  `normalize_results` from the frozen `SecurityProvider` protocol using the
  real `garak.py`, `pyrit.py`, and `promptfoo.py` adapters as worked examples,
  not a new tutorial provider.
- Integration tests start a real running instance of the API, issue actual
  HTTP requests against `examples/vulnerable-agent`, and assert the JSON
  response against the frozen report and presentation schemas. They are not
  mocked at the HTTP layer.

## v1.0 phase 2 milestone gate

After T-127, run the full suite, create and push annotated tag `v1.0-phase2`
on `dev`, then show literal `curl` output from a real running `lattence-api`
instance for `/v1/scan`, `/v1/attack`, and `/v1/chain` against
`examples/vulnerable-agent`, including the bearer token requirement. Hold for
review before scoping Phase 3.

Gate closed 2026-09-20. `lattence serve --port 8099` ran as a real background
process with `LATTENCE_API_TOKEN` set. Literal results: a request to
`/v1/scan` with no `Authorization` header returned `401
{"detail":"missing bearer token"}`; a request with the wrong token returned
`401 {"detail":"invalid bearer token"}`; with the correct bearer token,
`GET /v1/scan?path=examples/vulnerable-agent` returned `200` with
`schema_version "1"` and 13 findings, `POST
/v1/attack?path=examples/vulnerable-agent&offline=true` returned `200` with
the same 13 findings, and `GET
/v1/chain?path=examples/vulnerable-agent` returned `200` with 32
`cross_layer_chains` and `cross_layer_summary
{"finding_correlations": 32, "distinct_structural_paths": 9}`, matching the
v0.5.1 acceptance numbers. The full suite passed at 321 tests and 91.43
percent coverage, lint and formatting passed across the tree, all eight
strict typing targets passed (the original seven plus
`lattence-api/src/lattence_api`), and provenance and prose checks passed.

[T-128] [v1.0 phase 2] [API] correct unconfigured-token response to 503 and add a regression test | deps: T-127 | status: done | commit: self

`require_bearer_token` returned 500 for a missing `LATTENCE_API_TOKEN`. A
missing server configuration is a service-unavailable condition, not an
internal server error caused by the request, so it now returns 503. Added
`test_v1_route_without_token_configured_returns_503` asserting the specific
status code, not just any error response, so this does not silently regress
back to 500.

# v1.0 phase 3 task ledger

Phase 3 adds a Docker deployment path for the team mode (one container
running `lattence-api`, offline, no network dependency beyond what the
package already declares) and documents, without building, the
controller/worker enterprise mode. Distributed execution across workers
depends on the RBAC and audit groundwork Phase 5 owns; building a
controller/worker runtime now would mean building authorization twice, so
Phase 3 stops at the design document and Phase 5 implements it against that
design.

[T-129] [v1.0 phase 3] [SHIP] write a Dockerfile for lattence-api built from the published wheel | deps: T-128 | status: done | commit: self
[T-130] [v1.0 phase 3] [SHIP] write docker-compose.yml for the team deployment mode with a mounted project volume | deps: T-129 | status: done | commit: self
[T-131] [v1.0 phase 3] [SHIP] confirm container build, run, and an offline scan against a mounted project directory produce correct output | deps: T-130 | status: done | commit: self
[T-132] [v1.0 phase 3] [ORCH] document the controller/worker enterprise deployment mode design | deps: T-131 | status: todo | commit: self
[T-133] [v1.0 phase 3] [SHIP] satisfy the full-suite lint typing and prose gate for phase 3 changes | deps: T-132 | status: todo | commit: self
[T-134] [v1.0 phase 3] [ORCH] record the v1.0 phase 3 release gate and annotated tag | deps: T-133 | status: todo | commit: self

## v1.0 phase 3 scope notes

- The team deployment mode is one `lattence-api` container per team,
  authenticated by the same static bearer token from Phase 2, reading a
  project mounted as a read-only volume. It performs no network access
  beyond what `pyproject.toml` already declares as dependencies; the
  container never reaches out to an external security engine unless one is
  explicitly enabled, matching the existing `--offline` CLI contract.
- The Dockerfile builds from the published wheel (or a local build in CI),
  not from a fat, from-source image, keeping the image close to what a real
  `pip install lattence[api]` user gets.
- The controller/worker design document scopes a control plane that
  schedules `scan`/`attack` runs across multiple workers with per-run
  identity and audit trail. It explicitly depends on Phase 5 RBAC and audit
  logging; Phase 3 does not implement scheduling, worker registration, or a
  message queue. It records enough of the design that Phase 5 can build
  against it without re-deciding the shape.

## v1.0 phase 3 milestone gate

After T-134, run the full suite, create and push annotated tag
`v1.0-phase3` on `dev`, then show literal `docker compose` output for
building the image, starting the team-mode service, and running a scan
against `examples/vulnerable-agent` mounted into the container, confirming
the result matches the CLI's own output and that no network call outside
the container's declared dependencies occurred. Hold for review before
scoping Phase 4.
