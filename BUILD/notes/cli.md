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

T-057 added declared-scope evaluation for completed reports. Finding target
identifiers define the graph nodes touched by a run. Project declarations match
project-relative source paths. URL declarations match remote node endpoints by
origin and path boundary. A non-offline reproduction against a remote node
requires URL scope rather than source-file scope. Scope files use the existing
version 1 target declaration schema and may have any filename.

T-058 wired `policy check INPUT`. It reads a report file or directory and uses
the target declaration beside the report by default. `--scope PATH` selects an
equivalent declaration file explicitly. Plain and JSON output list the touched
and out-of-scope node identifiers. Any out-of-scope node exits 1 regardless of
the finding severity gate. Invalid reports or declarations exit 2.

T-059 made the shared `--planner llm` parser fail with usage exit code 2 and a
clear not-implemented message. The callback applies to all 12 commands. Rules
remain the default, and no command can silently discard an explicit LLM planner
request.

T-060 updated the README, roadmap, and changelog for v0.3 behavior. The README
now documents read-only hardening, scope checks, optional provider enablement,
external execution boundaries, and explicit LLM planner rejection. The roadmap
keeps crypto chaos in v0.4, moves the TUI to v0.5 with the dashboard, and leaves
model-backed planning for v0.4 or later.

T-061 extended clean-wheel acceptance with an executable Garak fixture. The
installed wheel lists and enables the optional adapter, merges its normalized
findings into an attack report, renders read-only hardening guidance, and passes
declared-scope policy validation. The acceptance path uses no external engine
package or network service.

T-062 applied the repository formatter to six v0.3 Python files identified by
the milestone gate. The CLI tests, lint, format check, build, and package checks
pass after the mechanical changes.

T-063 added the PEP 561 marker for the combined `lattence` wheel and configured
the source root for strict type checking. Provider modules now resolve as
`lattence.providers` instead of appearing under two module names. Runtime
method validation uses the built-in callable check. The complete CLI type
command passes.

T-064 recorded the v0.3 release gate. The full suite passes 215 tests at 89.84
percent coverage, lint, formatting, seven strict type targets, package build
and validation, provenance, and prose checks. The annotated v0.3.0 tag is
pushed on `dev`, followed by clean-clone acceptance from the tag.

T-076 wires the complete PQC assessment and crypto chaos workflows. Assessment
builds the crypto projection, migration checks, hybrid TLS validation, agility
score, and normalized findings. Chaos requires both project-root consent and
an explicitly declared configuration file, runs local bounded downgrade probes,
verifies restoration, writes report artifacts, and applies the severity gate.

T-079 adds the complete cryptographic assurance guide, links the flagship
pipeline and safety diagrams, expands the README's PQC section, removes crypto
chaos from the scaffold roadmap, and records the v0.4 feature set under the
unreleased changelog.

T-080 adds an isolated crypto migration fixture and extends clean-wheel
acceptance to assert ML-KEM, ML-DSA, hybrid TLS, resistant key-exchange and
signature downgrade probes, report generation, and byte-for-byte rollback.

T-081 recorded the v0.4 release gate. The full suite passes 260 tests at 90.59
percent coverage, lint, formatting, seven strict type targets, package build
and validation, provenance, prose, and fresh-clone crypto acceptance with
byte-for-byte rollback verification.

T-087 makes the bundled vulnerable-agent fixture a direct acceptance target
for every repaired v0.4 workflow. It retains classical RSA, X25519, TLS 1.2,
and ECDSA exposure while adding enforced hybrid ML-KEM and ML-DSA configuration
for reversible chaos probes. Its declaration explicitly authorizes only that
configuration file, and tests require stable repeated assessment plus
byte-for-byte rollback.

T-098 wires `lattence tui PATH` to the shared version 1 presentation workflow.
The command combines native AI findings with crypto assessment findings,
correlates them over real graph edges, renders the TUI, and writes the same
payload to `presentation.json` for the dashboard. `--json` writes that exact
payload to standard output. The wheel now carries the shared visual grammar.

T-100 documents cross-layer orientation, the version 1 presentation fields,
the accepted example chain, terminal and dashboard navigation, local dashboard
serving, and the six-step evidence review. README links the TUI recording,
diagram, and guide. The changelog records the v0.5 surface, and the roadmap no
longer lists the implemented terminal view as a scaffold.

T-101 pins the vulnerable example's real `LT-AI-002` correlation. The test
requires a reverse traversal over the stored tool-to-dataset `accesses` edge,
then a forward traversal over the tool-to-TLS-1.2 `key_exchange` edge targeted
by `LT-PQC-203`. Every hop must match an existing graph edge, and the chain
must retain both source files as evidence.

T-102 extends clean-wheel acceptance with plain and JSON TUI runs. It requires
the JSON stream and dashboard file to match byte-for-byte, checks the exact
oriented example chain against stored graph edges, and verifies the complete
static dashboard asset set in a fresh checkout. The same checks passed locally
with packaged modules from a newly built wheel.

T-103 closes v0.5 at 293 tests and 91.14 percent coverage. Lint, formatting,
seven strict type targets, package validation, dashboard tests, provenance,
prose, and clean-wheel acceptance all pass. The annotated `v0.5.0` tag is the
review boundary before any v1.0 scope.

T-106 adds `lattence graph chain PATH`. It builds the shared presentation from
fresh project discovery and crypto assessment, then prints every correlation
with both finding identifiers, each stored and traversed edge, its type and
orientation, and edge and aggregate evidence references. JSON mode emits the
same presentation document written for the dashboard.

T-108 corrects the v0.5.0 notes to distinguish genuine graph and presentation
data from the missing dedicated command and interactive terminal loop. CI now
runs `graph chain` from the clean wheel and checks the accepted finding pair,
both edge types and orientations, and evidence. A new local environment passed
the same offline command against a copied vulnerable-agent checkout.

T-109 closes v0.5.1 at 299 tests and 90.60 percent coverage. Lint, formatting,
seven strict type targets, package validation, UX tests, provenance, prose, and
fresh-wheel chain acceptance pass. The chain acceptance uses a separate output
directory so its new timestamp does not overwrite the dashboard document being
compared. The annotated `v0.5.1` tag is the review boundary before v1.0.

T-110 changes `graph chain`'s bare count heading to report both finding
correlations and distinct structural paths. The bundled example has 32 and 9,
respectively. Its own generated report and presentation files are ignored by
the example's discovery inventory to keep repeated counts stable.

T-111 prepares public package metadata at version 0.5.2. It declares the
Apache-2.0 SPDX expression and license file, README Markdown long description,
classifiers, keywords, and repository, issue, changelog, and documentation
links. The final 1.0.0 version remains reserved for the completed milestone.
