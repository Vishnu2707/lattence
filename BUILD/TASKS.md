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
