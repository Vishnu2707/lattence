import json
from pathlib import Path

from lattence.cli import app
from typer.testing import CliRunner

runner = CliRunner()
EXAMPLE = Path(__file__).parents[2] / "examples" / "vulnerable-agent"


def test_tui_renders_and_exports_shared_dashboard_data(tmp_path: Path) -> None:
    result = runner.invoke(
        app,
        [
            "tui",
            str(EXAMPLE),
            "--offline",
            "--no-color",
            "--out",
            str(tmp_path),
        ],
    )

    assert result.exit_code == 0, result.output
    assert "LATTENCE" in result.stdout
    assert "Attack Graph" in result.stdout
    payload = json.loads((tmp_path / "presentation.json").read_text())
    assert payload["version"] == "1"
    assert payload["cross_layer_chains"]


def test_tui_json_stdout_matches_dashboard_export(tmp_path: Path) -> None:
    result = runner.invoke(
        app,
        ["tui", str(EXAMPLE), "--offline", "--json", "--out", str(tmp_path)],
    )

    assert result.exit_code == 0, result.output
    exported = (tmp_path / "presentation.json").read_text(encoding="utf-8")
    assert json.loads(result.stdout) == json.loads(exported)
