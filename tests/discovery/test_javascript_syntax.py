from pathlib import Path

import pytest
from lattence.discovery import (
    JavaScriptSyntaxError,
    parse_javascript_file,
    parse_javascript_source,
)

SOURCE = """\
import client from "framework";
import { tool as defineTool, Agent } from "agent-kit";
import * as protocol from "protocol-kit";
import "side-effects";
const helper = require("helper-kit");

const text = "hidden.call(secret)";
// comment.call()
const agent = client.create({ token: "not-recorded" });
defineTool(agent);
protocol.connect();
"""


def test_parser_records_imports_and_calls_in_source_order() -> None:
    result = parse_javascript_source(SOURCE, "agent.ts")

    assert [(item.module, item.bindings, item.kind) for item in result.imports] == [
        ("framework", ("client",), "import"),
        ("agent-kit", ("tool as defineTool", "Agent"), "import"),
        ("protocol-kit", ("protocol",), "import"),
        ("side-effects", (), "import"),
        ("helper-kit", (), "require"),
    ]
    assert [item.function for item in result.calls] == [
        "client.create",
        "defineTool",
        "protocol.connect",
    ]


def test_parser_does_not_record_strings_or_comments_as_calls() -> None:
    result = parse_javascript_source(SOURCE)
    rendered = repr(result)

    assert "hidden.call" not in rendered
    assert "comment.call" not in rendered
    assert "not-recorded" not in rendered


def test_parser_rejects_unterminated_source_without_echoing_content() -> None:
    with pytest.raises(JavaScriptSyntaxError, match="unterminated string") as captured:
        parse_javascript_source("const secret = 'sensitive")

    assert "sensitive" not in str(captured.value)


def test_file_parser_uses_project_relative_path(tmp_path: Path) -> None:
    source = tmp_path / "src" / "agent.tsx"
    source.parent.mkdir()
    source.write_text("connect();\n", encoding="utf-8")

    result = parse_javascript_file(source, tmp_path)

    assert result.path == "src/agent.tsx"
