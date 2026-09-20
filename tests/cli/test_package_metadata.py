import tomllib
from pathlib import Path

ROOT = Path(__file__).parents[2]


def test_public_project_metadata_matches_repo_and_license() -> None:
    project = tomllib.loads((ROOT / "pyproject.toml").read_text())["project"]

    assert project["name"] == "lattence"
    assert project["version"] == "0.5.2"
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
