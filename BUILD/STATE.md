# HANDOFF

Begin T-048. Read `BUILD/agents/SHIP.md`, `BUILD/notes/cli.md`, and the T-047
entry in `BUILD/notes/ai-security.md` first. `verify_finding` and
`AttackRunner.replay` already exist in `lattence_ai.attacks`; T-048 is CLI
wiring, not new verification logic. The T-047 design note in
`BUILD/TASKS.md` gives the command's intended shape: `verify FINDING_ID`
reads the existing report from `--out` (no path argument, per the CLI
contract), and prints `VULNERABLE`, `PASS`, or `BLOCKED`.

Also note: if this session edits `lattence-ai`, `lattence-core`,
`lattence-crypto`, `lattence-evidence`, or `lattence-mcp` source, run
`uv sync --all-packages --dev --reinstall-package lattence` before trusting
a test run. See the dated note in `BUILD/notes/ux.md` for why.

## Current state

- Milestone: v0.2, closing CLI-contract gaps left by v0.1 scaffolds
- Last completed: T-047, task commit
- Next task: T-048, wire the verify command to replay verification
- Blockers: none
- Manual steps: branch protection and tag protection commands from the
  v0.1.0 release are still printed for review only, not run

## Repository state

- Branch: `dev`, `main` merged at the v0.1.0 release commit
- Remote: `origin/dev` up to date through T-047
- Tag: `v0.1.0`, annotated, pushed
- Contracts: frozen at version 1.0
- Design: frozen at version 1.0
- v0.1 tasks: 45 done
- v0.2 tasks: 2 done (T-046, T-047), 1 todo (T-048), 6 deferred pending a
  scoping decision (see BUILD/TASKS.md)
