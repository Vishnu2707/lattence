# Contributing

## Local setup

Lattence is a uv workspace of several packages under one root project.

```bash
git clone https://github.com/Vishnu2707/lattence.git
cd lattence
uv sync --all-packages --dev
uv run pytest
```

`uv sync --all-packages --dev` installs every workspace package
(`lattence-cli`, `lattence-core`, `lattence-crypto`, `lattence-evidence`,
`lattence-mcp`, `lattence-ai`, `lattence-api`, `lattence-packs`) into one
shared environment, plus the dev tools (`pytest`, `pytest-cov`, `ruff`,
`mypy`, `twine`). Use this command, not a plain `uv sync`: a plain sync
skips installing sibling workspace packages as editable, which makes
`mypy --strict` report spurious `import-untyped` errors.

## What CI checks

Every push and pull request runs seven jobs, defined in
`.github/workflows/ci.yml`:

- `lint`: `ruff check` and `ruff format --check` across the repository.
- `test`: the full `pytest` suite with `pytest-cov`. Coverage must stay at
  or above 85 percent, configured in `pyproject.toml`.
- `types`: `mypy --strict` against every implemented package.
- `acceptance`: builds the wheel, installs it into a clean virtual
  environment with no workspace present, and runs `scan`, `attack`, and
  `report` against `examples/vulnerable-agent`.
- `provenance`: `.githooks/check-provenance --all`, scanning tracked
  content and the full commit history.
- `prose`: `.githooks/check-prose`, scanning Markdown files.
- `action-smoke`: exercises `action.yml`, the GitHub Action, end to end
  against this checkout and asserts it produces a real SARIF file.

`action-smoke` is not yet in `main`'s required status checks list; the
other six are.

Run the relevant ones locally before pushing. For a change scoped to one
package, the per-package commands in `BUILD/agents/*.md` are faster than the
full suite.

## Adding a detection or attack rule

Detection, attack, and policy rules are YAML files, not Python. They are
validated against `docs/schemas/rule-pack.v1.json`. See the example in
[`docs/additional-info.md`](docs/additional-info.md#extending-the-rule-packs).
A new rule needs:

- A unique `id` matching `LT-[A-Z][A-Z0-9]*-[0-9]{3}`.
- `kind` of `detection`, `attack`, or `policy`.
- A `match` block (`paths`, `dependencies`, `syntax`, `config`, or `graph`).
- A `finding` block with `message` and `remediation`, and `owasp_llm`,
  `owasp_agentic`, or `cwe` mappings where they apply.

Place the file under `lattence-packs/discovery/` or
`lattence-packs/attacks/`, in a subdirectory grouped by topic, matching the
existing layout. It loads automatically; no code change is needed unless
the rule needs a new match capability. `tests/discovery/test_rules.py`
checks that the bundled schema copy matches the documented one.

## Commit convention

Use conventional commit messages: a short imperative summary, and a body
explaining why when the change is not self-evident. Do not add
authorship trailers, generation notices, assistance notices, or tool,
model, or vendor names to a commit message or to tracked file content. The
local provenance hook checks this on every commit; the same check runs in
CI against the full history.

Set `core.hooksPath` to `.githooks` after cloning, if it is not already
set:

```bash
git config core.hooksPath .githooks
```

There is no DCO sign-off requirement on this repository today.

## Pull request checklist

- [ ] `uv run pytest` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run mypy --strict` passes for every package you touched.
- [ ] New or changed behavior has tests, including negative cases for
      anything security-relevant.
- [ ] Markdown changes pass `.githooks/check-prose`: no em dash, no
      promotional language, and claims match what the code does today.
- [ ] The commit message has no attribution trailers or vendor names.

Open an issue to discuss a nontrivial change before sending a pull request.
