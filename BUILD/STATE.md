# Current state

- Milestone: v0.4.1 repair scoped; v0.4.0 confirmation withdrawn
- Last completed: T-084, report isolated vulnerable assets separately from traversable paths
- Next task: T-085, wire crypto assets into the trust graph with evidence
- Blockers: none
- Manual steps: branch protection and tag protection commands from the
  v0.1.0 release are still printed for review only, not run

## Repository state

- Branch: `dev`, `main` merged at the v0.1.0 release commit
- Remote: `origin/dev` up to date through T-081
- Tags: `v0.1.0`, `v0.2.0`, `v0.3.0`, and `v0.4.0`, annotated and pushed
- Contracts: frozen at version 1.0
- Design: frozen at version 1.0
- v0.1 tasks: 45 done
- v0.2 tasks: 3 done (T-046, T-047, T-048), 0 todo
- v0.3 tasks: 16 done (T-049 through T-064), 0 todo
- v0.4 tasks: 17 done (T-065 through T-081), 0 todo
- v0.4.1 tasks: 3 done, 4 todo (T-085 through T-088)

## v0.4 release gate

- Full suite: 260 passed, 90.59% coverage
- Lint and formatting: passed
- Strict typing: passed for all seven package targets
- Package build and Twine validation: passed
- Provenance and prose checks: passed
- Clean-wheel and fresh-clone crypto acceptance: passed with verified rollback
