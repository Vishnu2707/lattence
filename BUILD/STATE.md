# Current state

- Milestone: v1.0 phase 0 complete, awaiting review
- Last completed: T-110, distinguish finding correlations from structural paths
- Next task: scope phase 1 packaging and local install after phase 0 review
- Blockers: none
- Manual steps: branch protection and tag protection commands from the
  v0.1.0 release are still printed for review only, not run

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
