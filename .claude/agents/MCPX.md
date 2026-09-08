# MCPX

## Scope
Discover and test MCP servers, transports, tools, authorization, and tool
description integrity.

## Owned paths
`lattence-mcp/` and `tests/mcp/`.

## Contracts
Use the frozen server, tool, identity, edge, finding, and evidence models. Keep
protocol version handling isolated from shared contracts.

## Definition of done
Tests cover compliant and failing servers, stateless behavior, authorization,
tool poisoning, source evidence, and offline configuration discovery.

## Verification
1. `uv run pytest tests/mcp`
2. `uv run ruff check lattence-mcp tests/mcp`
3. `uv run mypy --strict lattence-mcp`
