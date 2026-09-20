# Architecture

The native Lattence workflow runs three stages against a project on disk,
offline.

**Discovery** parses source, configuration, and dependency manifests into
agents, tools, models, MCP servers, data stores, and cryptographic usage.
Every discovered item becomes a graph node with a stable identifier, so the
same project produces the same graph on repeated runs.

**Graph construction** turns discovery output into a directed security
graph. Edges record how components reach each other: calls, data access,
trust relationships, authentication, cryptographic protection, key
exchange, containment, and delegation. Parallel edges are allowed when
distinct evidence supports the same relationship.

**Attack execution and reporting** walks the graph and evaluates the native
rule pack catalog against it, producing findings with replayable evidence.
Evidence rendering then writes a schema-valid JSON report
(`docs/schemas/report.v1.json`) and a self-contained HTML report.

## Cross-layer correlation

A separate stage correlates AI, agent, and MCP findings with concrete
cryptographic findings over the same security graph, without adding edges
or changing the graph or report schema. See
[cross-layer analysis](cross-layer-analysis.md) for the traversal and
evidence model.

## Package layout

Lattence is a uv workspace of focused packages, each independently
type-checked in strict mode:

| Package | Contents |
| --- | --- |
| `lattence-core` | Discovery and graph models |
| `lattence-evidence` | Finding, report, and presentation schemas |
| `lattence-ai` | Native attack catalog and cross-layer correlation |
| `lattence-crypto` | PQC discovery, migration testing, and crypto chaos |
| `lattence-mcp` | MCP server and tool discovery |
| `lattence-cli` | The `lattence` command and its workflows |
| `lattence-api` | The REST API server (`lattence serve`) |
| `lattence-packs` | Bundled discovery and attack rule packs |

## Deployment surfaces

The same deterministic workflow functions back every surface: the CLI, the
REST API, and the Docker team-mode container all call the same
`create_report`, `create_attack_report`, and `create_security_presentation`
functions. See [deployment modes](additional-info.md#deployment-modes) for
how the surfaces compare.
