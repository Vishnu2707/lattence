import tomllib
from pathlib import Path

ROOT = Path(__file__).parents[2]
RELEASE_VERSION = "1.1.0"


def test_public_project_metadata_matches_repo_and_license() -> None:
    project = tomllib.loads((ROOT / "pyproject.toml").read_text())["project"]

    assert project["name"] == "lattence"
    assert project["version"] == RELEASE_VERSION
    assert project["readme"] == {
        "file": "README.md",
        "content-type": "text/markdown",
    }
    assert project["license"] == "Apache-2.0"
    assert project["license-files"] == ["LICENSE"]
    assert (ROOT / "LICENSE").read_text().lstrip().startswith("Apache License")
    assert project["urls"]["Repository"] == "https://github.com/Vishnu2707/lattence"
    assert "Programming Language :: Python :: 3.12" in project["classifiers"]
    assert all(not item.startswith("License ::") for item in project["classifiers"])


def test_every_workspace_project_uses_the_release_version() -> None:
    root_config = tomllib.loads((ROOT / "pyproject.toml").read_text())
    members = root_config["tool"]["uv"]["workspace"]["members"]

    declared = {
        member: tomllib.loads(
            (ROOT / member / "pyproject.toml").read_text(encoding="utf-8")
        )["project"]["version"]
        for member in members
    }
    assert declared == dict.fromkeys(members, RELEASE_VERSION)
