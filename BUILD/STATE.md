# Current state

- Milestone: v0.5 scoped; v0.4.1 confirmed
- Last completed: T-102, pass clean-wheel and fresh-clone TUI, dashboard, and
  cross-layer acceptance
- Next task: T-103, record the v0.5 release gate, changelog, and annotated tag
- Blockers: none
- Manual steps: branch protection and tag protection commands from the
  v0.1.0 release are still printed for review only, not run

## Repository state

- Branch: `dev`, `main` merged at the v0.1.0 release commit
- Remote: `origin/dev` up to date through T-102 after the task push
- Tags: `v0.1.0`, `v0.2.0`, `v0.3.0`, `v0.4.0`, and `v0.4.1`, annotated and pushed
- Contracts: frozen at version 1.0
- Design: frozen at version 1.0
- v0.1 tasks: 45 done
- v0.2 tasks: 3 done (T-046, T-047, T-048), 0 todo
- v0.3 tasks: 16 done (T-049 through T-064), 0 todo
- v0.4 tasks: 17 done (T-065 through T-081), 0 todo
- v0.4.1 tasks: 7 done (T-082 through T-088), 0 todo
- v0.5 tasks: 14 done, 1 todo (T-103)

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
