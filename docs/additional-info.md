# Additional information

Command reference, plugin SDK pointers, deployment mode comparison, rule
pack authoring, and install troubleshooting. The [README](../README.md)
covers the common path; this document covers the rest.

## Command reference

Every command below accepts `--json` (machine output to stdout),
`--out PATH` (report and export destination, default `.`), `--offline`
(skip external engines), `--no-color`, `--quiet`, `--planner [rules|llm]`
(`llm` is reserved and exits with a usage error), and
`--fail-on [critical|high|medium|low|info|none]` (default `high`). Exit
codes: 0 clean, 1 findings at or above the gate, 2 usage error, 3 internal
error.

| Command | Purpose |
| --- | --- |
| `scan [PATH]` | Discover and build the security graph, write JSON and HTML reports. |
| `attack [PATH]` | Run the native attack catalog and any enabled external providers. Requires `lattence.targets.yaml`. |
| `harden [PATH or FINDING_ID]` | Print structured remediation for a report or a single finding. Read-only. |
| `verify FINDING_ID` | Re-observe a single finding from a saved report and print `VULNERABLE`, `PASS`, or `BLOCKED`. |
| `report [INPUT]` | Rebuild the HTML report from a saved JSON report. |
| `sarif [INPUT]` | Convert a saved JSON report into a schema-validated SARIF 2.1.0 document. |
| `tui [INPUT]` | Open the full-screen terminal view, or write the shared presentation document with `--json`. |
| `pqc assess [PATH]` | Build the crypto dependency graph, migration tests, hybrid TLS validation, and agility score. |
| `crypto chaos [PATH]` | Run bounded, reversible key-exchange and signature downgrade probes. Requires `lattence.targets.yaml`. |
| `provider enable NAME` | Enable a built-in external provider (`garak`, `pyrit`, `promptfoo`). |
| `provider list` | Show enablement and executable availability per provider. |
| `graph export [INPUT]` | Write the deterministic security graph JSON. |
| `graph chain [INPUT]` | Print or export cross-layer finding chains and their evidence. |
| `policy check [INPUT]` | Exit non-zero if any report target node falls outside a declared scope file. |
| `serve` | Start the REST API (`--host`, default `127.0.0.1`; `--port`, default `8000`). Requires the `api` extra. |
| `rbac create-key CALLER_ID --role ROLE...` | Issue an RBAC API key with one or more roles. Prints the plaintext key once. Requires `LATTENCE_RBAC_DB`. |
| `rbac list` | List every RBAC caller id and its roles. |
| `rbac revoke CALLER_ID` | Delete every key for a caller id. |

`serve` and `rbac` do not accept the common option set above: a
long-running server and identity management each have their own narrower
argument shape. `sarif` does accept it, following the same `report` and
`graph export` pattern. See [API authentication](api-authentication.md)
for RBAC and SSO in detail.

## Plugin SDK

See the [plugin SDK guide](plugin-sdk.md) for the full `SecurityProvider`
interface, the `discover`/`generate_tests`/`execute`/`normalize_results`
contract, and the Garak, PyRIT, and Promptfoo adapters as worked reference
implementations.

## Extending the rule packs

Detection, attack, and policy rules are YAML files validated against
`docs/schemas/rule-pack.v1.json`. A minimal detection rule:

```yaml
version: "1"
id: LT-AI-210
kind: detection
title: Example provider
description: Detects the example model provider client.
severity: info
confidence: high
applies_to: [model]
match:
  dependencies: [example-provider-sdk]
  syntax: ["import:example_provider*", "call:*ExampleClient"]
finding:
  message: Example provider model client detected.
  remediation: Review model data flow and credentials.
```

Drop the file under `lattence-packs/discovery/` or `lattence-packs/attacks/`
and it loads on the next run. Rules use declarative path, dependency,
syntax, configuration, and graph predicates; a new deterministic detection
or attack belongs in YAML when the schema can express it.

## Deployment modes

| Mode | What it is | When to use it |
| --- | --- | --- |
| CLI | `lattence` run locally or in a CI step against a project checkout. | Local development, one-off scans, CI gates. |
| REST API | `lattence serve`, a single `lattence-api` process behind a static team token, per-caller RBAC keys, or an SSO extension point. See [API authentication](api-authentication.md). | Calling scan/attack/chain results from another service or UI. |
| Docker team mode | `docker compose up`, one container, one bearer token, a project bind-mounted read-only. | A team that wants the API without managing a Python environment. |
| Job queue (single-host) | `POST /v1/jobs` on the same API process, backed by an in-process thread pool, RBAC-gated and audited. | Submitting a scan or attack and polling for the result instead of holding the HTTP connection open. |
| Controller/worker (multi-host) | Not implemented. See [enterprise deployment design](enterprise-deployment-design.md) for the design and what a real distributed version still needs. | Organizations running many scans across many teams' projects at a scale one host cannot serve. |

All API-backed modes call the same deterministic workflow functions a
direct CLI run does. A report produced through the CLI, the API, the job
queue, or the container is byte-identical for the same project and code
revision.

## Troubleshooting install issues

**`pipx install lattence` reports "already on your PATH".** This happens
when a `lattence` binary from an active virtual environment shadows the one
pipx just installed. It is a warning, not a failure; run
`which lattence` to see which one resolves first, or use
`pipx run lattence` to bypass PATH resolution entirely.

**`lattence serve` fails with an import error.** The `api` extra is not
installed. Run `pip install "lattence[api]"` or `pipx inject lattence
fastapi uvicorn`.

**`attack` or `crypto chaos` refuses to run.** Both require a
`lattence.targets.yaml` declaration in the project root naming the target
and acknowledging `owned-or-authorized`. See the
[security and responsible use](../README.md#security-and-responsible-use)
section of the README.

**Docker build is slow on first run.** The builder stage downloads and
builds both wheels from source; subsequent builds reuse Docker layer cache
unless `pyproject.toml` or source files changed.

**`mypy --strict` reports `import-untyped` errors locally.** Use
`uv sync --all-packages --dev`, not a plain `uv sync`. A plain sync does not
install every workspace member as an editable package, which makes mypy
unable to see their `py.typed` markers.
