from pathlib import Path

import pytest
from lattence.discovery import (
    DependencyManifestError,
    discover_dependency_manifests,
    inventory_project,
)


def test_discovers_python_and_node_dependencies(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text(
        """\
[project]
name = "fixture"
version = "1.0"
dependencies = ["pydantic>=2", "local @ https://invalid.test/archive.whl"]

[project.optional-dependencies]
test = ["pytest>=8"]

[dependency-groups]
dev = ["ruff>=0.11"]
""",
        encoding="utf-8",
    )
    (tmp_path / "requirements-prod.txt").write_text(
        "httpx>=0.28\n-r other.txt\n# comment\n", encoding="utf-8"
    )
    web = tmp_path / "web"
    web.mkdir()
    (web / "package.json").write_text(
        """{
  "dependencies": {"react": "^18.0.0"},
  "devDependencies": {"vitest": "^3.0.0"}
}
""",
        encoding="utf-8",
    )

    inventory = inventory_project(tmp_path)
    result = discover_dependency_manifests(tmp_path, inventory.files)

    assert result.manifests == (
        "pyproject.toml",
        "requirements-prod.txt",
        "web/package.json",
    )
    assert {
        (item.ecosystem, item.name, item.group) for item in result.dependencies
    } == {
        ("python", "httpx", "requirements"),
        ("python", "local", "runtime"),
        ("python", "pydantic", "runtime"),
        ("python", "pytest", "optional:test"),
        ("python", "ruff", "group:dev"),
        ("node", "react", "runtime"),
        ("node", "vitest", "development"),
    }
    local = next(item for item in result.dependencies if item.name == "local")
    assert local.specifier == "direct-reference"


def test_invalid_manifest_error_does_not_echo_content(tmp_path: Path) -> None:
    (tmp_path / "package.json").write_text(
        '{"dependencies": "sensitive-value"', encoding="utf-8"
    )
    inventory = inventory_project(tmp_path)

    with pytest.raises(DependencyManifestError) as captured:
        discover_dependency_manifests(tmp_path, inventory.files)

    assert "sensitive-value" not in str(captured.value)


def test_unknown_files_are_not_read_as_manifests(tmp_path: Path) -> None:
    (tmp_path / "dependencies.json").write_text("not-json", encoding="utf-8")
    inventory = inventory_project(tmp_path)

    result = discover_dependency_manifests(tmp_path, inventory.files)

    assert result.dependencies == ()
    assert result.manifests == ()
