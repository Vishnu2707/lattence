# Build protocol

This file is the contract for every coding agent working on Lattence. The three
repository entry paths are conventional files that coding tools read when they
open the project.

## Authorship and provenance

- Every commit must be authored by Vishnu2707.
- Use conventional commit messages that are plain and factual.
- Never add authorship trailers, generation notices, assistance notices, tool
  names, model names, vendor names, or signatures to a commit.
- Do not put tool, model, or vendor names in source, comments, docstrings,
  documentation, templates, configuration, workflows, or asset metadata.
- `.githooks/provenance-pattern.txt` is the sole pattern definition. It is the
  only path omitted when repository content is checked against that pattern.
- The commit message hook checks every message. The pre-commit hook checks all
  staged file content. CI checks the working tree and full commit history.
- Before the first commit, set `core.hooksPath` to `.githooks`.
- After every commit, inspect `git log -1 --format='%an|%ae|%s|%b'` and confirm
  that the author and message comply with this section.

## Prose

- Write like a senior engineer. Use short declarative sentences and concrete
  nouns. Use real numbers where they add useful precision.
- Do not use the em dash character. Use a comma, full stop, or colon.
- Avoid promotional filler, vague transformation claims, and claims that a
  feature is effortless, industry-leading, or uniquely powerful.
- Do not use emoji in documentation, command output, source, or commits.
- README claims must describe behavior implemented today. Put planned work in
  the Roadmap section and mark it planned.
- CI checks Markdown for prohibited prose and the em dash character.

## Build discipline

- The ledger in `BUILD/` is the only source of task state.
- Read `BUILD/STATE.md`, `BUILD/TASKS.md`, the owning role file, and notes for
  the named module. Read no unrelated files.
- Search with `rg`. Inspect only the required ranges of large files.
- Do not reread a file already summarized in `BUILD/notes/`.
- Keep every source file below 300 lines. Split it before it reaches the limit.
- Write large command output to `BUILD/logs/`, then search the log.
- Run tests scoped to the module changed. Run the full suite only before a tag.
- Do not perform unrelated refactors. Edit only files named by the task.
- Complete one task through code, test, commit, push, and ledger update before
  starting another task.

## Runtime discipline

- Prefer deterministic parsing, rules, configuration, and graph traversal.
- Model-backed planning is opt in through `--planner llm`. Rules are the
  default through `--planner rules`.
- Cache every planner request on disk by prompt hash.
- Parse every planner response into a strict Pydantic model. Retry once after
  invalid output, then fall back to the rules planner.
- The planner proposes tests. Execution, telemetry, policy, and evidence decide
  the result.

## Git workflow

- Perform build work on `dev`. Confirm the branch before every task.
- Use one task and one conventional commit. Push immediately to `origin/dev`.
- Never batch tasks. Never finish a session with unpushed commits.
- At a milestone, run the full suite and create an annotated tag on `dev`.
- Open a pull request from `dev` to `main` with the release title and changelog
  body. Use a merge commit so task history remains intact.
- After the milestone merge, run `git checkout dev` and merge `main` with
  `git merge main --ff-only`.
- Never commit directly to `main`. It receives milestone merges only.
- Before stopping, require a clean worktree and no output from
  `git log origin/dev..dev`.

## Orchestrator loop

1. Read `BUILD/STATE.md`. Select the next todo task whose dependencies are done.
2. Read only its role file and notes for modules named by the task.
3. Mark the task doing. Write tests first where behavior can be tested.
4. Implement the task and run its three role verification commands.
5. If verification fails, fix it. After two failed attempts, mark the task
   blocked, record the cause in `BUILD/STATE.md`, and select another unblocked
   task.
6. Update `BUILD/TASKS.md`, `BUILD/STATE.md`, and the module note. Append a
   three-line entry to `BUILD/DECISIONS.md` when a decision was made.
7. Commit the task and ledger together. Push to `origin/dev` immediately.
8. Confirm authorship, repository cleanliness, and remote synchronization.
9. Stop, then begin the next task as a separate unit of work.

Independent specialists may work concurrently only when their tasks have no
shared dependency and touch disjoint owned directories. The orchestrator must
land each result as a separate task commit.

## Session boundaries

- Never leave a task doing. Finish and commit it, or revert its task changes,
  return it to todo, and record a note.
- After every completed task, rewrite `BUILD/STATE.md` with the milestone, last
  completed task and commit, next task, blockers, and required manual steps.
- When context or execution budget is low, finish the current task and stop.
  Add a `HANDOFF` section at the top of `BUILD/STATE.md` that states the first
  action for the next coding agent.

## Definition of done

A task is done only when all of the following are true:

- The implementation matches its acceptance criteria and frozen contracts.
- Behavior changes have focused tests, including positive and negative cases
  where security behavior is involved.
- The owning role's three verification commands pass.
- Changed source files remain below 300 lines.
- Human-readable text passes the prose standard.
- Staged content and the commit message pass provenance checks.
- Module notes, decisions, task status, and state are current.
- The commit has one task scope, is authored by Vishnu2707, and is pushed to
  `origin/dev`.
- The worktree is clean and the local branch has no commits ahead of its remote.
