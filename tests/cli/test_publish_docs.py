from pathlib import Path

ROOT = Path(__file__).parents[2]


def test_publish_guide_uses_isolated_artifacts_and_public_pipx() -> None:
    guide = (ROOT / "docs" / "publishing.md").read_text()

    for required in (
        "uv build --out-dir",
        "uv run twine check",
        "TWINE_USERNAME=__token__",
        "twine upload --non-interactive",
        "pipx install --python python3.12 lattence",
        "PIP_INDEX_URL=https://pypi.org/simple",
        "check_distribution.py",
    ):
        assert required in guide
    assert "pipx install dist/" not in guide
