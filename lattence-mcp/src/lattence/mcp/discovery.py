import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit, urlunsplit

import yaml
from lattence.discovery import ProjectFile
from lattence.graph import MCPServer, SourceRef, Tool
from yaml import YAMLError


class MCPDiscoveryError(ValueError):
    pass


@dataclass(frozen=True)
class MCPDiscovery:
    servers: tuple[MCPServer, ...]
    tools: tuple[Tool, ...]
    configs: tuple[str, ...]


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-") or "server"


def _safe_url(value: object) -> str | None:
    if not isinstance(value, str):
        return None
    parsed = urlsplit(value)
    if not parsed.scheme or not parsed.hostname:
        return None
    host = parsed.hostname
    if parsed.port:
        host = f"{host}:{parsed.port}"
    return urlunsplit((parsed.scheme, host, parsed.path, "", ""))


def _read_config(path: Path, relative: str) -> dict[str, Any]:
    try:
        text = path.read_text(encoding="utf-8")
        value: object = (
            yaml.safe_load(text)
            if path.suffix.lower() in {".yaml", ".yml"}
            else json.loads(text)
        )
    except (OSError, UnicodeError, json.JSONDecodeError, YAMLError) as error:
        raise MCPDiscoveryError(f"cannot parse MCP config {relative}") from error
    if not isinstance(value, dict):
        raise MCPDiscoveryError(f"MCP config {relative} must contain an object")
    return value


def _tool(
    value: object, server_id: str, source: SourceRef, position: int
) -> Tool | None:
    if isinstance(value, str):
        name = value
        config: dict[str, Any] = {}
    elif isinstance(value, dict) and isinstance(value.get("name"), str):
        name = value["name"]
        config = value
    else:
        return None
    permissions = {
        item for item in config.get("permissions", []) if isinstance(item, str)
    }
    schema = config.get("inputSchema", {})
    if not isinstance(schema, dict):
        schema = {}
    return Tool(
        id=f"tool:{server_id}:{_slug(name)}:{position}",
        name=name,
        source=source,
        description=(
            config.get("description")
            if isinstance(config.get("description"), str)
            else None
        ),
        input_schema=schema,
        side_effects=config.get("sideEffects") is True,
        permissions=permissions,
        server_id=server_id,
    )


def _server(
    name: str, config: object, relative: str
) -> tuple[MCPServer, tuple[Tool, ...]] | None:
    if not isinstance(config, dict):
        return None
    server_id = f"mcp_server:{relative}:{_slug(name)}"
    source = SourceRef(path=relative)
    url = _safe_url(config.get("url"))
    command = config.get("command")
    command = command if isinstance(command, str) else None
    transport = config.get("transport")
    if not isinstance(transport, str):
        transport = "http" if url else "stdio"
    auth_method = None
    if config.get("headers") or config.get("auth"):
        auth_method = "configured"
    configured_tools = config.get("tools", [])
    if not isinstance(configured_tools, list):
        configured_tools = []
    tools = tuple(
        tool
        for position, value in enumerate(configured_tools, start=1)
        if (tool := _tool(value, server_id, source, position)) is not None
    )
    return (
        MCPServer(
            id=server_id,
            name=name,
            source=source,
            transport=transport,
            command=command,
            url=url,
            auth_method=auth_method,
            tool_ids=[tool.id for tool in tools],
        ),
        tools,
    )


def discover_mcp_configs(root: Path, files: tuple[ProjectFile, ...]) -> MCPDiscovery:
    servers: list[MCPServer] = []
    tools: list[Tool] = []
    configs: list[str] = []
    for project_file in files:
        relative = project_file.path
        if Path(relative).name.lower() not in {
            ".mcp.json",
            "mcp.json",
            "mcp.yaml",
            "mcp.yml",
        }:
            continue
        document = _read_config(root / relative, relative)
        values = document.get("mcpServers", document.get("servers", {}))
        if not isinstance(values, dict):
            raise MCPDiscoveryError(f"MCP config {relative} has invalid servers")
        configs.append(relative)
        for name, config in sorted(values.items()):
            if not isinstance(name, str):
                continue
            discovered = _server(name, config, relative)
            if discovered:
                server, server_tools = discovered
                servers.append(server)
                tools.extend(server_tools)
    return MCPDiscovery(tuple(servers), tuple(tools), tuple(sorted(configs)))
