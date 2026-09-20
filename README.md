<p align="center">
  <img src="assets/brand/logo.svg" alt="Lattence" width="220">
</p>

<p align="center">AI security and post-quantum security assurance for agentic systems.</p>

<p align="center">
  <a href="https://github.com/Vishnu2707/lattence/actions/workflows/ci.yml"><img src="https://github.com/Vishnu2707/lattence/actions/workflows/ci.yml/badge.svg?branch=dev" alt="CI status"></a>
  <a href="https://pypi.org/project/lattence/"><img src="https://img.shields.io/pypi/v/lattence" alt="PyPI version"></a>
  <img src="https://img.shields.io/badge/license-Apache--2.0-blue" alt="License Apache-2.0">
</p>

Lattence scans an agentic codebase, builds a security graph of its agents,
tools, models, and data stores, and runs a native attack catalog against it
to find prompt injection, unsafe tool use, delegation risks, and quantum
vulnerable cryptography. It is for engineers who ship LLM agents and need
evidence of what an agent can reach, not a general code scanner.

## Demo

![Lattence scanning the vulnerable-agent fixture](assets/demo/scan.gif)

See it run an [attack](assets/demo/attack.gif) and open the
[terminal security view](assets/demo/tui.gif).

## Install

```bash
pip install lattence          # or: pipx install lattence
```

```bash
git clone https://github.com/Vishnu2707/lattence.git && cd lattence
LATTENCE_API_TOKEN=$(openssl rand -hex 32) docker compose up
```

## Quickstart

Lattence ships a deliberately vulnerable fixture so you can see real
findings without pointing it at your own code first:

```bash
cd examples/vulnerable-agent && lattence scan .
```

```
LATTENCE  scan  .

DISCOVERY
  Agents                3
  MCP servers           1
  Tools                 2
...
AI ATTACK SURFACE
  Excessive agency            HIGH
  Unsafe tool use             CRITICAL
...
CRYPTOGRAPHY
  Quantum vulnerable     4
  PQC readiness          21%

  Attack paths           92
  Findings               13

Report  lattence-report.html      Elapsed  0.0s
```

```bash
lattence attack .   # requires lattence.targets.yaml; the fixture has one
```

```
LATTENCE  attack  .

VULNERABLE  LT-AGENT-001  Excessive agency  agent:agents-sdk:app.py:12
VULNERABLE  LT-AI-001  Direct prompt injection  agent:agents-sdk:app.py:12
VULNERABLE  LT-AI-002  Indirect prompt injection  dataset:rag-pipeline:app.py:15
VULNERABLE  LT-MCP-002  Confused deputy  mcp_server:mcp.json:records
...
Findings  13
```

```bash
lattence graph chain . --offline --no-color   # correlate AI findings to crypto weaknesses
```

```
LATTENCE  graph chain  .

CROSS-LAYER  32 finding correlations across 9 distinct structural paths

VULNERABLE  1/32  LT-AGENT-001 -> LT-PQC-203
  START       agent:agents-sdk:app.py:12
  EDGE 1      key_exchange  forward
    STORED    agent:agents-sdk:app.py:12 -> crypto_algorithm:crypto_config.py:7:tls-1-2
  END         crypto_algorithm:crypto_config.py:7:tls-1-2
...
```

`lattence report lattence-report.json` rebuilds the HTML report from a
saved JSON report.

## What it finds

Lattence ships a native catalog of 15 attack rules. A sample:

| Category | Example finding | OWASP mapping |
| --- | --- | --- |
| Direct prompt injection | An agent's instructions can be overridden by untrusted user input. | LLM01 |
| Indirect prompt injection | A retrieval path feeds untrusted content into an agent's context. | LLM01 |
| Excessive agency | An agent can delegate actions to another execution context. | LLM06 |
| Confused deputy | An MCP server exposes a credentialed tool to any caller. | LLM06 |

Every finding carries an OWASP LLM Top 10 mapping, and most carry an OWASP
Agentic Security Initiative mapping and a CWE identifier where one applies.

## REST API, Docker, and CI

```bash
LATTENCE_API_TOKEN=$(openssl rand -hex 32) lattence serve   # start the API
```

```bash
LATTENCE_API_TOKEN=... docker compose up   # same, in a container
```

```bash
lattence scan . --json --fail-on high   # fail a CI build on findings
```

## Documentation

[Architecture](docs/architecture.md) · [Cross-layer analysis](docs/cross-layer-analysis.md) · [PQC and crypto assurance](docs/crypto-assurance.md) · [Deployment modes](docs/additional-info.md#deployment-modes) · [Extending the rule packs](docs/additional-info.md#extending-the-rule-packs) · [Full command reference and troubleshooting](docs/additional-info.md)

## Security and responsible use

Lattence is an offensive security tool. Point it only at projects you own
or are explicitly authorized to test. `attack` and `crypto chaos` refuse to
run without a `lattence.targets.yaml` declaration. Native workflows make no
network calls and execute none of the target project's code. See
[SECURITY.md](SECURITY.md) to report a vulnerability in Lattence itself.

## Contributing and license

See [CONTRIBUTING.md](CONTRIBUTING.md), [SECURITY.md](SECURITY.md), and
[LICENSE](LICENSE). Lattence is licensed under the Apache License,
Version 2.0.
