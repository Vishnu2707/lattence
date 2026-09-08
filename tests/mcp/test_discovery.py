from pathlib import Path

import pytest
from lattence.discovery import inventory_project
from lattence.mcp import MCPDiscoveryError, discover_mcp_configs


def test_discovers_stdio_http_servers_and_configured_tools(tmp_path: Path) -> None:
    (tmp_path / "mcp.json").write_text(
        """{
  "mcpServers": {
    "files": {
      "command": "safe-server",
      "tools": [
        {
          "name": "read_file",
          "description": "Read a declared fixture.",
          "permissions": ["read"],
          "inputSchema": {"type": "object"}
        }
      ]
    },
    "remote": {
      "url": "https://user:secret@example.test/mcp?token=secret",
      "headers": {"Authorization": "secret"}
    }
  }
}
""",
        encoding="utf-8",
    )
    inventory = inventory_project(tmp_path)

    result = discover_mcp_configs(tmp_path, inventory.files)

    assert [server.name for server in result.servers] == ["files", "remote"]
    assert result.servers[0].transport == "stdio"
    assert result.servers[0].command == "safe-server"
    assert result.servers[0].tool_ids == [result.tools[0].id]
    assert result.tools[0].permissions == {"read"}
    assert result.servers[1].transport == "http"
    assert result.servers[1].url == "https://example.test/mcp"
    assert result.servers[1].auth_method == "configured"
    assert "secret" not in repr(result)


def test_discovers_yaml_server_format(tmp_path: Path) -> None:
    (tmp_path / "mcp.yaml").write_text(
        """\
servers:
  local:
    transport: stdio
    command: local-server
    tools: [search]
""",
        encoding="utf-8",
    )
    inventory = inventory_project(tmp_path)

    result = discover_mcp_configs(tmp_path, inventory.files)

    assert result.configs == ("mcp.yaml",)
    assert result.tools[0].name == "search"


def test_invalid_config_error_does_not_echo_content(tmp_path: Path) -> None:
    (tmp_path / "mcp.json").write_text('{"secret":', encoding="utf-8")
    inventory = inventory_project(tmp_path)

    with pytest.raises(MCPDiscoveryError) as captured:
        discover_mcp_configs(tmp_path, inventory.files)

    assert "secret" not in str(captured.value)


def test_ignores_unrelated_json(tmp_path: Path) -> None:
    (tmp_path / "config.json").write_text("not json", encoding="utf-8")
    inventory = inventory_project(tmp_path)

    result = discover_mcp_configs(tmp_path, inventory.files)

    assert result.servers == ()
    assert result.tools == ()
