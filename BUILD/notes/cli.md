# CLI module

The root project builds the `lattence` distribution from `lattence-cli/src` and
installs the `lattence` binary. The command tree exposes all frozen v1 commands
and their seven common options. Commands are scaffolds that return internal
error code 3 until their owning implementation tasks wire behavior.

Public entry points are `lattence.cli:app`, `lattence.cli:main`, and
`python -m lattence.cli`. The current package version is `0.0.0`.

T-023 added strict loading for `lattence.targets.yaml`. Attack execution must
find a version 1 declaration, an `owned-or-authorized` acknowledgement, and an
explicit project-root target. Invalid declarations fail without echoing file
content. Project paths cannot escape the root and URL targets cannot embed
credentials.

T-039 wired scan, attack, PQC assessment, graph export, and report commands to
one offline workflow. The root wheel includes discovery rules, attack rules,
and the report schema. Scan writes JSON and HTML, attack enforces the owned
target declaration, and machine modes write only structured data to stdout.

T-041 added `examples/vulnerable-agent`, an offline fixture with agent
delegation, persistent memory, unclassified retrieval, a destructive local
tool, a credentialed MCP tool, and classical cryptography. CLI tests scan and
attack it without importing or executing its declared dependencies.

T-038 added plain and color terminal scan summaries under the installed
`lattence.cli.presentation` namespace. Plain output contains no terminal escape
sequences and reports discovery counts, attack findings, crypto inventory, PQC
readiness, graph relationships, output path, and elapsed time.

T-043 added the root `README.md`. It documents only the commands that are
wired today: `scan`, `attack`, `report`, `pqc assess`, and `graph export`.
`harden`, `verify`, `tui`, `crypto chaos`, `provider enable`, `provider list`,
and `policy check` stay scaffolds, so the README lists them under Roadmap
instead of Quickstart. There is no PyPI release and no Docker image yet, so
install instructions cover source and pipx-from-git only.

T-044 added a `types` CI job that runs `mypy --strict` against every
implemented package (`lattence-cli`, discovery, graph, `lattence-crypto`,
`lattence-evidence`, `lattence-mcp`, and the AI attack runner), matching the
per-role verification commands already used locally. `lattence-crypto/chaos`
and `lattence-ai/planner` are not part of v0.1 and stay out of the matrix.
The `test` job now runs with `pytest-cov` and a coverage gate configured in
`pyproject.toml` (85 percent, current total is about 91 percent). The
`provenance`, `prose`, and `lint` jobs, and the schema tests inside the full
suite, were already wired and needed no change.

T-045 found that the built wheel was missing every module outside
`lattence.cli`: `lattence.discovery`, `lattence.graph`, `lattence.evidence`,
`lattence.mcp`, `lattence_ai`, and `lattence_crypto` were absent, and the root
`dependencies` list named the workspace-only packages `lattence-ai`,
`lattence-core`, `lattence-crypto`, `lattence-evidence`, and `lattence-mcp` as
if they were installable distributions. A pip install of the wheel outside
the uv workspace failed to resolve those names, and even a forced install
would have hit `ModuleNotFoundError` on `scan`. The fix force-includes the
five packages' source into the wheel under their real import paths and
replaces the root dependency list with the actual third-party libraries
(`cryptography`, `jsonschema`, `packaging`, `pathspec`, `pydantic`, `pyyaml`,
plus `rich` and `typer`). A standalone venv install of the rebuilt wheel now
runs `scan`, `attack`, and `report` against `examples/vulnerable-agent` with
no workspace and no source checkout present. CI gained an `acceptance` job
that builds the wheel, installs it into a fresh venv, and runs that same
sequence on every push.

A later design-system pass changed three command behaviors: `--version` now
prints the block-character banner from `assets/brand/banner.txt` before the
version line (previously version-only, pinned by a test that now checks the
last line instead of the whole line), `tui` prints the same banner before
its pending-scaffold exit, and `attack` now honors `--no-color` and colors
`VULNERABLE` lines instead of ignoring the option entirely. See
`BUILD/notes/ux.md` for the design-token rationale.

T-048 wired `verify FINDING_ID` to `lattence_ai.attacks.verify_finding`
(T-047). `verify` takes no path argument, per the CLI contract; `--out`
names the directory (or file) holding the existing report to verify
against, the same convention `scan`/`attack`/`report` use for where they
write. Prints `VULNERABLE  ID  title  target` (still reproduces),
`PASS  ID  title  target` (no longer reproduces), or
`BLOCKED  ID  finding not found` (unknown id, exit 2). A `VULNERABLE`
outcome exits 1 only if the finding's own severity meets `--fail-on`,
reusing the same severity ordering as `exceeds_gate` through a new
`severity_meets_gate(severity, gate)`.

T-046 wired `--fail-on` to `scan` and `attack` exit codes, via a new
`exceeds_gate(summary, gate)` in `workflow.py`. This closes a gap where the
CLI contract's "exit 1 for findings at or above the gate" was not
implemented even though both commands were marked done in v0.1. Scope is
`scan` and `attack` only: `report` re-renders an already-scanned report,
and `pqc assess` / `graph export` do not carry finding-severity semantics,
so extending the gate to them is a separate decision, not folded into this
task. Existing tests that scanned the vulnerable fixture without disabling
the gate now pass `--fail-on none` explicitly, and so does the CI
acceptance job, which otherwise would have started failing on its own
expected findings.

T-049 added the frozen `SecurityProvider` runtime contract under
`lattence.providers`. Provider objects must implement all four contract
methods. Raw results are revalidated for matching test identifiers, named
providers, and ordered timestamps. Normalized findings are strictly validated,
must have unique identifiers, and must target the test node.

T-050 added the optional Garak adapter. It creates one deterministic Garak
test per graph model, invokes the external `garak` executable without importing
its package, reads the JSONL report, and normalizes failed evaluation rows into
provider-neutral findings. Missing executables and malformed reports remain
provider errors. Garak is not a Lattence package dependency.

T-051 added the optional PyRIT adapter. Graph model metadata selects a
registered scanner target and scenario. The adapter invokes `pyrit_scan` as an
external process, parses its JSON result, and normalizes successful objectives
into provider-neutral findings. Missing executables and malformed output remain
provider errors. PyRIT is not a Lattence package dependency.

T-052 added the optional Promptfoo adapter. It invokes `promptfoo redteam run`
for each graph model target, reads the documented JSON output envelope, and
normalizes failed red-team assertions into provider-neutral findings. Missing
executables and malformed output remain provider errors. Promptfoo is not a
Lattence package dependency.

T-053 wired `provider enable NAME` and `provider list`. State is a version 1
JSON document named `providers.json` under `--out`, which defaults to the
current directory. Enablement is independent of executable availability, so a
provider can be configured before its optional engine is installed. Text and
JSON listings report enabled and available states separately. The provider
command group moved out of `app.py`, returning that source below 300 lines.

T-054 added the external provider lifecycle to `attack`. Available enabled
providers may discover graph nodes, generate tests, execute them, and normalize
their results. Provider tests must target known nodes, and finding identifiers
must remain unique across native and external results. Normalized findings are
merged through the existing report builder. `--offline` skips all external
provider execution.

T-056 wired read-only `harden`. A report path or directory prints all
remediation plans. A finding identifier reads the report under `--out` and
prints only that plan. Text output contains the target, action, evidence, and
reproduction context. JSON output contains the complete structured plans.
Severity gates apply to the selected plans. Tests confirm that the command does
not modify the project or report.
