# HANDOFF

v0.2 is complete as scoped: T-046, T-047, and T-048 close the CLI-contract
gaps that had a precise existing spec. Everything else on the v0.2 list is
deferred pending a scoping decision (see BUILD/TASKS.md) and needs
direction before it can become a task. Do not start v0.3 without
confirmation.

## Current state

- Milestone: v0.2, CLI-contract gaps closed
- Last completed: T-048, task commit
- Next task: none defined; v0.3 scope needs a decision on harden, tui,
  crypto chaos, provider, policy, and the llm planner
- Blockers: none
- Manual steps: branch protection and tag protection commands from the
  v0.1.0 release are still printed for review only, not run

## Repository state

- Branch: `dev`, `main` merged at the v0.1.0 release commit
- Remote: `origin/dev` up to date through T-048
- Tag: `v0.1.0`, annotated, pushed
- Contracts: frozen at version 1.0
- Design: frozen at version 1.0
- v0.1 tasks: 45 done
- v0.2 tasks: 3 done (T-046, T-047, T-048), 0 todo, 6 deferred pending a
  scoping decision
