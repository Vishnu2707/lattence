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

## Deferred pending a design decision

These CLI-contract commands remain scaffolds. Each needs a scoping decision
before it can become a task, because the contracts name the command but not
its behavior in enough detail to implement without inventing it:

- `harden`: no spec for what it changes or how a change is proposed, applied,
  or reverted.
- `tui`: `BUILD/DESIGN.md` specifies the dashboard information architecture
  in detail; this is the most ready of the deferred items, but is a large
  unit of work (a full-screen keyboard-driven view, not a small task).
- `crypto chaos`: `BUILD/agents/CHAOS.md` requires mutations to be reversible
  and bounded, but no task has defined what gets mutated or how.
- `provider enable` / `provider list`: unclear whether "provider" means the
  `SecurityProvider` plugin interface in `BUILD/CONTRACTS.md`, or enabling
  model-provider detection rules already in `lattence-packs/discovery/providers/`.
- `policy check`: `PolicyDecision` already exists per-finding in evidence;
  unclear what a standalone policy check command evaluates that `scan` does
  not already produce.
- `--planner llm`: `BUILD/agents/PLAN.md` specifies caching, retry, and
  fallback behavior, but bringing in a real model provider call is a larger
  and riskier unit of work than the other items here.

## Milestone gate

After the last v0.2 task, run the full suite, create the annotated `v0.2` tag
on `dev`, and hold for review before opening a pull request to `main` or
starting v0.3.
