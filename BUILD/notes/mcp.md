# MCP module

MCP discovery reads JSON and YAML server configuration without network access.
It emits server and tool nodes with source paths, transport, executable name,
sanitized URL, configured-auth state, tool schemas, permissions, and side-effect
flags. It removes URL credentials, queries, fragments, header values, and other
secret-bearing configuration from results and errors.

Public imports are `discover_mcp_configs`, `MCPDiscovery`, and
`MCPDiscoveryError` from `lattence.mcp`.
