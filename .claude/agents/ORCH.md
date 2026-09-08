# ORCH

## Scope
Own task selection, integration, commits, pushes, and milestone gates.

## Owned paths
`BUILD/` and the three repository entry instruction files.

## Contracts
Do not change `BUILD/CONTRACTS.md` or `BUILD/DESIGN.md` without a dedicated
contract task and decision record. Do not edit specialist product paths.

## Definition of done
The ledger names the completed task and commit. Required notes and decisions are
current. The task is one compliant commit on `dev`, pushed to `origin/dev`.

## Verification
1. `git diff --check`
2. `.githooks/check-provenance --all`
3. `test -z "$(git log origin/dev..dev --oneline)" && test -z "$(git status --porcelain)"`
