# HANDOFF

Begin T-047. Read `BUILD/agents/AISEC.md`, `BUILD/notes/ai-security.md`, and
the T-047 design note in `BUILD/TASKS.md` first. The runner primitive it
builds on (`AttackRunner.observe`) is already deterministic; T-047 is new
code, not a redesign.

## Current state

- Milestone: v0.2, closing CLI-contract gaps left by v0.1 scaffolds
- Last completed: T-046, task commit
- Next task: T-047, deterministic single-finding replay verification
- Blockers: none
- Manual steps: branch protection and tag protection commands from the
  v0.1.0 release are still printed for review only, not run

## Repository state

- Branch: `dev`, `main` merged at the v0.1.0 release commit
- Remote: `origin/dev` up to date through T-046
- Tag: `v0.1.0`, annotated, pushed
- Contracts: frozen at version 1.0
- Design: frozen at version 1.0
- v0.1 tasks: 45 done
- v0.2 tasks: 1 done (T-046), 2 todo (T-047, T-048), 6 deferred pending a
  scoping decision (see BUILD/TASKS.md)
