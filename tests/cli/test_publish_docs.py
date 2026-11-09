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


def test_v110_changelog_records_only_verified_release_claims() -> None:
    changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    release = changelog.split("## [1.1.0] - 2026-11-09", 1)[1].split(
        "## [1.0.0]", 1
    )[0]
    normalized = " ".join(release.split())

    for verified in (
        "13 findings",
        "92 attack paths",
        "32 cross-layer correlations across 9 structural paths",
        "21 percent PQC readiness",
        "101,851 bytes",
        "111,834 bytes",
        "394 tests at 92.47 percent coverage",
    ):
        assert verified in normalized

    assert "2,312-node" not in release
    assert "20,684-edge" not in release


def test_v110_release_commands_cover_each_manual_release_action() -> None:
    commands = (ROOT / "BUILD" / "RELEASE-1.1.0.md").read_text(encoding="utf-8")

    for required in (
        "git tag -a v1.1.0",
        "gh pr create --base main --head dev",
        "gh pr merge --merge",
        "uv build --package lattence",
        "uv build --package lattence-api",
        "twine upload --non-interactive",
        "gh release create v1.1.0",
    ):
        assert required in commands
