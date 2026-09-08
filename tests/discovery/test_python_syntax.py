from pathlib import Path

import pytest
from lattence.discovery import PythonSyntaxError, parse_python_file, parse_python_source

SOURCE = """\
import framework as fw
from package.tools import action as run_action

client = fw.Client(token="not-recorded")
typed: object = client

@fw.tool(scope="write")
def execute(value: str) -> None:
    run_action(value, mode="safe")
"""


def test_parser_records_imports_calls_decorators_and_assignments() -> None:
    result = parse_python_source(SOURCE, "agent.py")

    assert [(item.module, item.name, item.alias) for item in result.imports] == [
        ("framework", None, "fw"),
        ("package.tools", "action", "run_action"),
    ]
    assert [item.function for item in result.calls] == [
        "fw.Client",
        "fw.tool",
        "run_action",
    ]
    assert result.calls[0].keyword_names == ("token",)
    assert result.calls[0].argument_kinds == ()
    assert result.decorators[0].target == "execute"
    assert result.decorators[0].decorator == "fw.tool()"
    assert [(item.target, item.value_kind) for item in result.assignments] == [
        ("client", "fw.Client()"),
        ("typed", "client"),
    ]


def test_parser_does_not_store_literal_values() -> None:
    result = parse_python_source("secret = 'sensitive-value'\n")

    assert result.assignments[0].value_kind == "<str>"
    assert "sensitive-value" not in repr(result)


def test_parser_reports_location_without_source_content() -> None:
    with pytest.raises(PythonSyntaxError, match=r"broken.py at 1:9") as captured:
        parse_python_source("def bad(:\n", "broken.py")

    assert "def bad" not in str(captured.value)


def test_file_parser_uses_project_relative_posix_path(tmp_path: Path) -> None:
    source = tmp_path / "src" / "agent.py"
    source.parent.mkdir()
    source.write_text("import framework\n", encoding="utf-8")

    result = parse_python_file(source, tmp_path)

    assert result.path == "src/agent.py"
