# Current state

- Milestone: v0.5 scoped; v0.4.1 confirmed
- Last completed: T-091, target crypto findings at concrete supporting nodes
- Next task: T-092, correlate AI and crypto findings through genuine paths
- Blockers: none
- Manual steps: branch protection and tag protection commands from the
  v0.1.0 release are still printed for review only, not run

## Repository state

- Branch: `dev`, `main` merged at the v0.1.0 release commit
- Remote: `origin/dev` up to date through T-088
- Tags: `v0.1.0`, `v0.2.0`, `v0.3.0`, `v0.4.0`, and `v0.4.1`, annotated and pushed
- Contracts: frozen at version 1.0
- Design: frozen at version 1.0
- v0.1 tasks: 45 done
- v0.2 tasks: 3 done (T-046, T-047, T-048), 0 todo
- v0.3 tasks: 16 done (T-049 through T-064), 0 todo
- v0.4 tasks: 17 done (T-065 through T-081), 0 todo
- v0.4.1 tasks: 7 done (T-082 through T-088), 0 todo
- v0.5 tasks: 3 done, 12 todo (T-092 through T-103)

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
