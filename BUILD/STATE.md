# Current state

## 2026-09-26: Milestone 4 (overnight run) closed, overnight run complete

Published the false-positive audit methodology and rate directly in
`README.md` (new "False positive methodology" section), not only in
`docs/false-positive-methodology.md`. Checked `SECURITY.md`,
`CONTRIBUTING.md`, and `README.md` against everything shipped tonight
(T-158 through T-161): `SECURITY.md` needed no change; `CONTRIBUTING.md`
was already stale before tonight (said CI runs "six jobs," actually seven
since `action-smoke` was added earlier and never reflected there), fixed.
Also found and fixed one real prose-check violation already pushed in
T-161's commit (60248dd): a banned promotional word in `BUILD/TASKS.md`,
matched by `.githooks/prose-pattern.txt`. The local pre-commit hook only runs
`check-provenance`, not `check-prose`, so it slipped past every commit
tonight until caught here by running `check-prose` with no arguments
(whole tracked tree) as part of this task's own verification; CI's
`prose` job would have caught it on the next push regardless. Updated
`CHANGELOG.md` with an `[Unreleased]` section listing every milestone
completed tonight. Task T-162. Full suite: 384 passed, same 2 pre-existing
Docker exclusions. Prose check clean across the whole tracked tree.

This closes the overnight run: Milestones 0 through 4 all completed and
gated green, tasks T-158 through T-162, commits 750c5bd, 9506b50, bff4954,
60248dd, and this task's commit, all on `dev`, all pushed. No release
tagged, no PR opened to main, per instruction.

## 2026-09-26: Milestone 3 (overnight run) closed

Chose GitLab CI integration over a second discovery language (Go/Java) for
this run's coverage-broadening milestone: it reuses the existing `lattence
scan`/`attack`/`sarif` commands with no new discovery or detection logic,
while a second language needs new rules, fixtures, and catalog entries
across three packages. Proposal in `BUILD/DECISIONS.md` D-037. Added
`templates/gitlab-ci.yml` (mirrors `action.yml`: install, scan or attack,
convert to SARIF, publish artifacts, exit on the severity gate) and
`docs/gitlab-ci.md`. Verified the template's exact shell commands locally
against `examples/vulnerable-agent`: real scan output, a valid SARIF file
with 13 results matching the 13 findings, and the severity-gate exit code
(1, `high` gate met) correctly surviving past the SARIF conversion step.
Honest scope note: this does not integrate with GitLab's Security
Dashboard, which needs GitLab's own report schema, not SARIF; it publishes
a downloadable SARIF artifact and fails the pipeline on the gate, matching
what the GitHub Action already does. Task T-161. Full suite: 384 passed,
same 2 pre-existing Docker exclusions.

## 2026-09-26: Milestone 2 (overnight run) closed

Audited `lattence_ai/attacks/cross_layer.py` for the combinatorial-artifact
bug class v0.5.1 fixed ("32 correlations vs 9 distinct paths"). Found no
bug: every correlation requires a real graph path with a real crypto edge,
and the finding-correlations vs distinct-structural-paths dedup from
v0.5.1 is still in place and shared by every renderer (terminal, TUI, HTML,
API) through one `CrossLayerSummary` computed once in `presentation.py`.
Full audit in `BUILD/DECISIONS.md` D-036. Added a real worked example to
`README.md` ("The differentiator: a real cross-layer chain") showing the
actual `LT-AI-002 -> LT-PQC-203` chain from `examples/vulnerable-agent`,
re-verified live immediately before committing (caught and corrected one
factual error in an earlier draft: `TLS 1.2` in this fixture has
`quantum_status: unknown`, not `vulnerable`, and `LT-PQC-203` is limited
cryptographic agility, not a TLS-specific finding). Task T-160. Full suite:
382 passed, same 2 pre-existing Docker exclusions.

## 2026-09-26: Milestone 1 (overnight run) closed

Root-caused the other half of the original bug report: the 14MB HTML file
was largely caused by `render_html_report` embedding the entire report
JSON a second time, verbatim, in an inline `<pre>` block, with no cap on
the findings or graph node tables. Fixed: both tables now cap at 200 rows
(most severe first, with a note pointing at the full JSON for the rest),
and the inline JSON dump is skipped above 500,000 bytes with the same
pointer. Added a synthetic 250-row regression test and a real-fixture size
ceiling test (1MB, justified in `BUILD/DECISIONS.md` D-035 since each
finding legitimately carries full evidence data). Real current sizes for
`examples/vulnerable-agent`: about 100KB JSON, about 112KB HTML. Task
T-159. Full suite: 382 passed, same 2 pre-existing Docker exclusions.

Tooling note for future agents: hit a stale, non-editable copy of the
`lattence` namespace package physically present under
`.venv/lib/python3.12/site-packages/lattence`, which shadowed the editable
`lattence-evidence` source and served old code even after
`uv sync --all-packages --dev --reinstall-package <pkg>`. Fix: delete that
directory, then run plain `uv sync --all-packages --dev` again. Check for
this first if a source change does not seem to take effect.

## 2026-09-26: Milestone 0 (overnight run) closed

A bug report described `lattence scan` against `examples/vulnerable-agent`
producing 2,312 graph nodes, 20,684 edges, 20,684 attack paths, and a
contradictory 100 percent PQC readiness. Bisected at a14d7ba (pre-Milestone
A), b4224cb (Milestone A), and 34b891d (Milestone B): a fresh `scan` at
every one of the three commits, including repeated runs into the same
output directory, produced identical stable numbers (24 nodes, 92 edges,
92 attack paths, 21 percent PQC readiness). No commit on `dev` reproduces
the explosion. The bad numbers traced to a stale, gitignored
`examples/vulnerable-agent/lattence-report.json`/`.html` pair left over
from an earlier, unrelated broken run, now deleted. Full evidence in
`BUILD/DECISIONS.md` D-034.

A second, real bug was found and fixed: `create_report` never computed
`quantum_vulnerable_assets`/`quantum_vulnerable_paths` for `scan`/`attack`,
so the JSON summary always showed 0 for both regardless of the graph's
real crypto topology, while the terminal's "Quantum vulnerable" row was
always correct. Fixed by having `create_report` run the same
`assess_quantum_exposure` computation the `pqc` command already runs.
Verified against `examples/vulnerable-agent` (real, current numbers,
independently confirmed by reading the generated JSON, not just the
terminal output): 24 graph nodes, 92 edges, 92 attack paths, 13 findings,
PQC readiness 21 percent, `quantum_vulnerable_paths` 140,
`quantum_vulnerable_assets` 0 (correctly, since none of this fixture's
vulnerable crypto nodes are isolated per the contract's definition).
Regression test added:
`tests/cli/test_workflow.py::test_scan_vulnerable_agent_graph_and_pqc_summary_stay_sane`.
Full suite: 380 passed, 2 pre-existing Docker daemon tests excluded
(unrelated, no daemon in this environment). Task T-158, commit follows
this state update. Milestones 1 through 4 from the overnight run plan were
not started in this pass; see HANDOFF below if this run stops before they
are picked up.

- Milestone: v1.0.0 shipped. Repository is public. Milestone A (detection
  precision hardening) done. Milestone B (web dashboard, minimum viable)
  done; holding per instruction before Milestone C.
- Last completed: T-157, extended the self-contained `lattence-report.html`
  (already written by `scan`/`attack`/`report`) into a minimum-viable
  dashboard: a click-to-sort-by-severity findings table, the existing PQC
  readiness metric, and a new cross-layer chain section reusing the
  existing version 1 `presentation.json` data contract, embedded inline
  (not fetched) so the page works fully offline from `file://`. Added
  `GET /v1/dashboard` to `lattence-api`, a small addition mirroring the
  existing `/v1/chain` route. Full detail in `BUILD/DECISIONS.md` D-033 and
  `BUILD/TASKS.md` T-157.
- Verified against `examples/vulnerable-agent`: `graph chain` then `scan`
  then `report` into the same `--out` directory produced
  `lattence-report.html` containing "32 finding correlations across 9
  distinct structural paths" and the real `LT-AI-002 -> LT-PQC-203` chain
  with its `key_exchange` hop, the same accepted fixture numbers already
  pinned in `tests/cli/test_graph_chain_command.py`. `GET /v1/dashboard`
  against the same example returned identical chain data as HTML. Checked
  offline: no `http://`, `https://`, `fetch(`, `<link `, or `cdn.` anywhere
  in the rendered output; the extracted `<script>` parses with a real JS
  engine (Node `new Function()`).
- Previously completed: T-156, audited all native attack and detection
  rules for matching on node field shape without a real data-flow path (the
  bug class found live at workflow.py:208), fixed the three rules that make
  a reachability claim (LT-AI-002, LT-AI-007, LT-AI-008) by requiring a real
  graph path via the existing `lattence.graph.traversal` machinery, and
  added a distinct regression test module. Full detail in
  `BUILD/DECISIONS.md` D-032 and `BUILD/TASKS.md` T-156.
- Self-scan (`lattence scan .` against this repository): 13 findings before
  the fix, 13 after. Unchanged in count because the workflow.py:208 false
  positive and a real missed finding on examples/vulnerable-agent's RAG
  dataset were colliding on the same rule ids; after the fix LT-AI-002 and
  LT-AI-008 correctly target `dataset:rag-pipeline:examples/vulnerable-agent/app.py:15`
  instead of the spurious `dataset:chroma:lattence-cli/src/lattence/cli/workflow.py:208`
  node. All deliberate findings in examples/vulnerable-agent still fire
  (verified via `lattence graph export examples/vulnerable-agent --offline`
  and the CLI attack fixture test).
- Next task: none selected. Hold for review before scoping Milestone C.
- Blockers: none for Milestone B. Noted but not fixed, out of this
  milestone's scope: `lattence-cli/src/lattence/cli/workflow.py` was
  already over the 300-line module guideline (364 lines) before this
  milestone and is now 379 lines after the minimal `_sibling_presentation`
  addition; splitting it is a separate task. Also carried over from
  Milestone A, unchanged: the provenance hook (`.githooks/check-provenance --all`)
  fails against full commit history because of a pre-existing dependabot
  merge commit (`a14d7ba`, already on `origin/dev` before this milestone
  started) whose commit body includes an attribution trailer that dependabot
  itself adds, matching the provenance pattern. This predates and is
  unrelated to Milestone A's commits; each commit made in this milestone
  passes the hook on its own diff and message. Also noted but pre-existing
  and unrelated: `tests/docker/` has 2 failing tests in this environment
  because no Docker daemon is running locally (confirmed by running them
  against the unmodified branch before starting Milestone A).
- Note: local verification uses `uv sync --all-packages --dev`, matching CI.
  A plain `uv sync` does not install every workspace member editable and
  produces spurious mypy import-untyped errors across packages. Also: after
  changing a bundled non-Python data file (e.g. `rule-pack.v1.json`), the
  editable install in `.venv` does not pick up the change from
  `uv sync --all-packages --dev` alone; use
  `uv sync --all-packages --dev --reinstall-package lattence-core` (and any
  other affected package) to force the rebuild.
- Branch protection: applied on `main` via `gh api` (verified live,
  2026-09-20): required status checks `lint`, `test`, `types`,
  `acceptance`, `provenance`, `prose` (the original six CI jobs; the new
  `action-smoke` job is not yet in this required list), `enforce_admins`
  true, `required_linear_history` true, force pushes and deletions
  disallowed. `dev` intentionally has no required PR review, matching
  `BUILD/PROTOCOL.md`'s direct-push-per-task workflow; force pushes and
  deletions are still disallowed there.
- Tag protection: not applied. GitHub's classic tag protection API
  (`POST /repos/{owner}/{repo}/tags/protection`) requires an
  organization-owned repository; this repository is on a personal
  account, and the endpoint returns 404 here. A ruleset-based tag
  protection (`POST /repos/{owner}/{repo}/rulesets` with a `tag` target)
  is available on personal accounts and is the option to revisit if tag
  protection is wanted.

## Repository state

- Branch: `dev`, `main` merged at the v0.1.0 release commit
- Remote: `origin/dev` up to date through T-103 after the task push
- Tags: `v0.1.0`, `v0.2.0`, `v0.3.0`, `v0.4.0`, `v0.4.1`, `v0.5.0`, and
  `v0.5.1`, annotated and pushed
- Contracts: frozen at version 1.0
- Design: frozen at version 1.0
- v0.1 tasks: 45 done
- v0.2 tasks: 3 done (T-046, T-047, T-048), 0 todo
- v0.3 tasks: 16 done (T-049 through T-064), 0 todo
- v0.4 tasks: 17 done (T-065 through T-081), 0 todo
- v0.4.1 tasks: 7 done (T-082 through T-088), 0 todo
- v0.5 tasks: 15 done, 0 todo
- v0.5.1 tasks: 6 done, 0 todo
- v1.0 phase 0 tasks: 1 done, 0 todo
- v1.0 phase 1 tasks: 5 done, 0 todo
- v1.0 phase 2 tasks: 13 done, 0 todo
- v1.0 phase 3 tasks: 6 done, 0 todo
- v1.0 fixes (banner, README): 2 done, 0 todo
- v1.0 phase 4 tasks: 5 done, 0 todo
- v1.0 phase 5 tasks: 7 done, 0 todo
- v1.0 phase 6 tasks: 6 done, 0 todo

## v1.0 phase 5 progress

- Full suite: 366 passed, 92.37 percent coverage.
- Lint and formatting: passed across the tree.
- Strict typing: passed for all nine package targets (governance is new)
  plus tests/docker and tests/ci.
- Provenance and prose: passed.
- RBAC, SSO extension point, durable audit logging, and a real
  single-controller-multi-worker job queue shipped. A duplicate
  `job_submit` audit event was caught live during the gate demonstration
  (not by an existing test) and fixed before the gate closed; the test
  that should have caught it was also strengthened.

## v1.0 phase 4 progress

- Full suite: 337 passed, 91.42 percent coverage.
- Lint and formatting: passed across the tree.
- Strict typing: passed for all eight package targets plus tests/docker
  and tests/ci.
- Provenance and prose: passed.
- SARIF conversion validated against the real OASIS SARIF 2.1.0 schema.
  GitHub Action and self-scan workflow added, with every third-party
  action reference pinned to a commit SHA verified live via `gh api`
  rather than guessed.

## v1.0 phase 3 progress

- Full suite: 325 passed, 91.43 percent coverage.
- Lint and formatting: passed across the full tree, including tests/docker.
- Strict typing: passed for all eight package targets plus tests/docker.
- Provenance and prose: full tracked tree and commit history passed.
- Main package wheel and source archive still build and pass twine check;
  the Dockerfile and compose file do not affect the published `lattence`
  distribution's contents.

## v1.0 phase 2 progress

- Full suite: 321 passed, 91.43 percent coverage.
- Lint and formatting: passed across the full tree, including the new
  lattence-api package.
- Strict typing: passed for all seven original package targets plus
  lattence-api/src/lattence_api.
- Provenance and prose: full tracked tree and commit history passed.
- lattence serve added to the CLI, lazily importing fastapi, uvicorn, and
  lattence_api so the core `lattence` wheel stays dependency-light. Main
  wheel and source archive still build and pass twine check with lattence-api
  as an optional extra, not force-included.

## v1.0 phase 1 progress

- Version 0.5.2 wheel and source archive pass metadata and package validation.
- A fresh Python 3.12 environment installed the local wheel. Its version,
  root help, and all 13 command help screens match the source build exactly.
- Publication instructions in `docs/publishing.md` use an isolated artifact
  directory, a hidden API-token prompt, and a public-index pipx installation.
- Package `lattence` 0.5.2 is live on the public PyPI index. Two independent
  `pipx install lattence` runs against isolated pipx homes both installed
  0.5.2 from the public index and printed the correct banner and version.
  The phase gate is closed.

## v1.0 phase 0 gate

- The real vulnerable-agent export has 32 finding correlations across 9
  distinct structural edge paths. Path group sizes are 10, 2, 2, 6, 2, 2, 2,
  2, and 4 finding pairs.
- Terminal, presentation JSON, TUI Attack Graph, and dashboard HTML now label
  both counts. Each finding-to-path correlation remains visible.
- The bundled example ignores generated presentation and report files during
  discovery, so repeated local output does not change the graph being analyzed.
- Full suite: 300 passed, 90.64 percent coverage. Lint, formatting, all seven
  strict typing targets, UX tests, provenance, and prose checks passed.

## v0.5.1 acceptance before release gate

- A new Python 3.12 environment installed only the built wheel and its declared
  dependencies, then analyzed a copied vulnerable-agent checkout.
- `graph chain` ran offline and printed 32 real correlations.
- The accepted `LT-AI-002` to `LT-PQC-203` chain printed the reverse `accesses`
  hop, forward `key_exchange` hop, stored endpoints, and evidence from
  `app.py` and `crypto_config.py`.

## v0.5.1 release gate

- Full suite: 299 passed, 90.60 percent coverage.
- Lint and formatting: passed across 222 files.
- Strict typing: passed for all seven package targets.
- Package build and validation: source archive and wheel passed.
- Terminal and dashboard checks: all 26 UX tests passed.
- Provenance and prose: full tracked tree and commit history passed.
- Clean-wheel acceptance prints and checks the real `LT-AI-002` to
  `LT-PQC-203` chain without overwriting dashboard acceptance data.

## v0.5 acceptance before release gate

- A fresh local clone built the wheel and loaded only its packaged Lattence
  modules against the cached dependency environment.
- Plain TUI output exposed all twelve navigation sections with no color
  escapes, and JSON output matched the dashboard `presentation.json`
  byte-for-byte.
- The acceptance check found the real two-hop `LT-AI-002` to `LT-PQC-203`
  chain, matched both hops to stored graph edges, retained evidence from
  `app.py` and `crypto_config.py`, and found every dashboard asset.
- CI now repeats the presentation checks from its clean wheel environment.

## v0.5 release gate

- Full suite: 293 passed, 91.14 percent coverage.
- Lint and formatting: passed across 218 files.
- Strict typing: passed for all seven package targets.
- Package build and validation: source archive and wheel passed.
- Terminal and dashboard checks: dependency-free dashboard tests and all 25 UX
  tests passed.
- Provenance and prose: full tracked tree and commit history passed.
- Clean-wheel acceptance: CI run 35227054663 passed all jobs, including the
  oriented `LT-AI-002` cross-layer chain and dashboard export.

## v0.4 release gate

- Full suite: 260 passed, 90.59% coverage
- Lint and formatting: passed
- Strict typing: passed for all seven package targets
- Package build and Twine validation: passed
- Provenance and prose checks: passed
- Clean-wheel and fresh-clone crypto acceptance: passed with verified rollback

## v0.4.1 release gate

- Full suite: 269 passed, 90.59% coverage
- Lint and formatting: passed
- Strict typing: passed for all seven package targets
- Package build and Twine validation: passed
- Provenance and prose checks: passed
- Pre-tag fresh-clone acceptance: two assessments both returned 17 nodes,
  86 relationships, 0 isolated vulnerable assets, and 140 traversable paths;
  attack returned 13 findings at exit 1; two crypto-chaos probes returned
  resistant and restored the target SHA-256 byte-for-byte
