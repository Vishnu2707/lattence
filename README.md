<p align="center">
  <img src="assets/brand/logo.svg" alt="Lattence" width="220">
</p>

<p align="center">AI security and post-quantum security assurance for agentic systems.</p>

<p align="center">
  <a href="https://github.com/Vishnu2707/lattence/actions/workflows/ci.yml"><img src="https://github.com/Vishnu2707/lattence/actions/workflows/ci.yml/badge.svg?branch=dev" alt="CI status"></a>
  <img src="https://img.shields.io/badge/python-3.12%2B-blue" alt="Python 3.12+">
  <img src="https://img.shields.io/badge/license-Apache--2.0-blue" alt="License Apache-2.0">
</p>

Lattence scans an agentic codebase, builds a security graph of its agents,
tools, models, and data stores, and runs a native attack catalog against that
graph to find prompt injection, unsafe tool use, and delegation risks. It also
inventories cryptographic usage and scores post-quantum readiness. It is built
for engineers who ship LLM agents and need evidence of what an agent can
reach, not a general code scanner. Everything below runs offline, against a
project you already own.

## Demo

![Lattence scanning the vulnerable-agent fixture](assets/demo/scan.gif)

## Install

Lattence is not yet published to PyPI. Install it from source.

```bash
git clone https://github.com/Vishnu2707/lattence.git
cd lattence && uv sync --all-packages && uv run lattence --version
```

Or with pipx, directly from the repository:

```bash
pipx install "git+https://github.com/Vishnu2707/lattence.git#subdirectory=lattence-cli"
lattence --version
```

## Quickstart

Lattence ships a deliberately vulnerable fixture at
`examples/vulnerable-agent` so you can see real findings without pointing it
at your own code first.

```bash
cd examples/vulnerable-agent
lattence scan .
```

```
LATTENCE  scan  .

DISCOVERY
  Agents                3
  MCP servers           1
  Tools                 2
  External APIs         1
  Data stores           2

AI ATTACK SURFACE
  Excessive agency            HIGH
  Unsafe tool use             CRITICAL
  Insecure delegation         HIGH
  Memory poisoning            HIGH
  Direct prompt injection     HIGH

CRYPTOGRAPHY
  RSA                   2
  TLS 1.2               1
  X25519                1
  Quantum vulnerable    3
  PQC readiness         0%

  Attack paths           29
  Findings               13

Report  lattence-report.html      Elapsed  0.0s
```

`attack` requires a `lattence.targets.yaml` declaration in the project root
that names the target and acknowledges ownership. The fixture already has
one:

```bash
lattence attack .
```

```
LATTENCE  attack  .

VULNERABLE  LT-AGENT-001  Excessive agency  agent:agents-sdk:app.py:12
VULNERABLE  LT-AGENT-002  Unsafe tool use  tool:app.py:delete_customer_record
VULNERABLE  LT-AGENT-003  Insecure delegation  agent:agents-sdk:app.py:12
VULNERABLE  LT-AGENT-004  Memory poisoning  agent:agents-sdk:app.py:12
VULNERABLE  LT-AI-001  Direct prompt injection  agent:agents-sdk:app.py:12
VULNERABLE  LT-AI-002  Indirect prompt injection  dataset:rag-pipeline:app.py:15
VULNERABLE  LT-AI-004  System instruction override  agent:agents-sdk:app.py:12
VULNERABLE  LT-AI-005  Unsafe output handling  tool:app.py:delete_customer_record
VULNERABLE  LT-AI-007  Retrieval corpus poisoning  database:chroma
VULNERABLE  LT-AI-008  Untrusted retrieved context  dataset:rag-pipeline:app.py:15
VULNERABLE  LT-AI-009  Resource exhaustion boundary  application:agents-sdk
VULNERABLE  LT-MCP-001  Tool argument injection  tool:app.py:delete_customer_record
VULNERABLE  LT-MCP-002  Confused deputy  mcp_server:mcp.json:records

Indirect chain  dataset:rag-pipeline:app.py:15 -> tool:mcp_server:mcp.json:records:send-retrieved-context:1

Findings  13
```

`report` turns a saved JSON report back into the HTML report:

```bash
lattence report lattence-report.json
```

```
Report  lattence-report.html
```

## What it finds

Lattence ships a native catalog of 15 attack rules. A sample:

| Category | Example finding | OWASP mapping |
| --- | --- | --- |
| Direct prompt injection | An agent's instructions can be overridden by untrusted user input. | LLM01 |
| Indirect prompt injection | A retrieval path feeds untrusted content into an agent's context. | LLM01 |
| Excessive agency | An agent can delegate actions to another execution context. | LLM06 |
| Unsafe tool use | A tool call can trigger a destructive action without a policy check. | LLM06 |
| Memory poisoning | Persistent agent memory has no integrity check on write. | LLM04 |
| Retrieval corpus poisoning | A vector store accepts writes from an untrusted path. | LLM03 |
| Tool argument injection | A tool accepts arguments without a declared input schema. | LLM05 |
| Confused deputy | An MCP server exposes a credentialed tool to any caller. | LLM06 |
| Sensitive data disclosure | An agent's output path has no redaction step. | LLM02 |
| Resource exhaustion boundary | An agent has no bound on delegated call depth or count. | LLM10 |

Every finding carries an OWASP LLM Top 10 mapping, and most carry an OWASP
Agentic Security Initiative mapping and a CWE identifier where one applies.

## Architecture

Lattence runs three stages against a project on disk, offline. Discovery
parses source, config, and dependency manifests into agents, tools, models,
MCP servers, data stores, and cryptographic usage. Graph construction turns
that discovery output into a directed security graph with stable node
identifiers, so the same project produces the same graph. The attack runner
walks the graph and evaluates the rule pack catalog against it, producing
findings with replayable evidence, then evidence rendering writes a
schema-valid JSON report and a self-contained HTML report.

## PQC assurance

Lattence classifies discovered cryptographic usage as quantum-vulnerable or
post-quantum and computes a deterministic readiness percentage.

```bash
lattence pqc assess examples/vulnerable-agent
```

```
PQC readiness  0%
```

## CI integration

Run a scan on every push and fail the build on findings at or above a
severity threshold.

```yaml
- name: Lattence scan
  run: |
    pipx install "git+https://github.com/Vishnu2707/lattence.git#subdirectory=lattence-cli"
    lattence scan . --json --fail-on high
```

## Deployment modes

Today, Lattence runs as a local CLI against a project checkout, and as a step
in a CI pipeline using the same binary. Both modes are offline: scan, attack,
and report never make a network call. There is no hosted service or API
server yet.

## Extending it

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
and it loads on the next run.

## Roadmap

There is no `ROADMAP.md` yet. Commands scaffolded but not yet implemented:
`harden`, `verify`, `tui`, `crypto chaos`, `provider enable`, `provider list`,
and `policy check`. They currently exit with an internal error and no
behavior. Also planned: an `llm` planner mode alongside the default
deterministic rules planner, and a published PyPI package.

## Security and responsible use

Lattence is an offensive security tool. Point it only at projects you own or
are explicitly authorized to test.

- `attack` refuses to run without a `lattence.targets.yaml` declaration in
  the project root that names the target and acknowledges
  `owned-or-authorized`. Project targets cannot resolve outside the
  declared root, and URL targets cannot embed credentials.
- Scan, attack, and report make no network calls and execute none of the
  target project's code. Detection and attack rules match on parsed source,
  configuration, and graph structure.
- Reports include file paths and matched code locations. Treat generated
  reports as sensitive and store them with the same access controls as the
  scanned project.
- The bundled `examples/vulnerable-agent` fixture is intentionally unsafe.
  Do not deploy it or connect it to real credentials, tools, or data.

There is no `SECURITY.md` yet. To report a vulnerability in Lattence itself,
open an issue in this repository.

## Contributing and license

This project does not yet have a contributing guide. Open an issue to
discuss a change before sending a pull request.

Lattence is licensed under the Apache License, Version 2.0. See
[LICENSE](LICENSE).
