import json
from pathlib import Path

from lattence.cli import app
from typer.testing import CliRunner

runner = CliRunner()


def _project(root: Path) -> None:
    (root / "app.py").write_text(
        "from crewai import Agent\nagent = Agent()\n",
        encoding="utf-8",
    )
    (root / "pyproject.toml").write_text(
        '[project]\nname="fixture"\nversion="1"\ndependencies=["crewai"]\n',
        encoding="utf-8",
    )
    _scope(root / "lattence.targets.yaml", ".")


def _scope(path: Path, value: str) -> None:
    path.write_text(
        f"""\
version: "1"
authorization: owned-or-authorized
targets:
  - kind: project
    value: {value}
""",
        encoding="utf-8",
    )


def _scan(root: Path) -> None:
    result = runner.invoke(
        app,
        ["scan", str(root), "--out", str(root), "--fail-on", "none", "--quiet"],
    )
    assert result.exit_code == 0, result.output


def test_policy_check_passes_for_declared_targets(tmp_path: Path) -> None:
    _project(tmp_path)
    _scan(tmp_path)

    result = runner.invoke(app, ["policy", "check", str(tmp_path)])

    assert result.exit_code == 0, result.output
    assert result.stdout.startswith("PASS  policy.scope")


def test_policy_check_exits_nonzero_and_lists_out_of_scope_nodes(
    tmp_path: Path,
) -> None:
    _project(tmp_path)
    _scan(tmp_path)
    _scope(tmp_path / "lattence.targets.yaml", "tests")

    result = runner.invoke(app, ["policy", "check", str(tmp_path)])

    assert result.exit_code == 1, result.output
    assert "FAIL  policy.scope" in result.stdout
    assert "OUT-OF-SCOPE  agent:" in result.stdout


def test_policy_check_accepts_equivalent_scope_file_and_json(tmp_path: Path) -> None:
    _project(tmp_path)
    _scan(tmp_path)
    scope = tmp_path / "declared-scope.yaml"
    _scope(scope, ".")

    result = runner.invoke(
        app,
        ["policy", "check", str(tmp_path), "--scope", str(scope), "--json"],
    )

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["allowed"] is True
    assert payload["touched_node_ids"]
