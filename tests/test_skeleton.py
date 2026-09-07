from pathlib import Path

WORKSPACE_MEMBERS = (
    "lattence-ai",
    "lattence-api",
    "lattence-cli",
    "lattence-core",
    "lattence-crypto",
    "lattence-evidence",
    "lattence-mcp",
    "lattence-packs",
)


def test_workspace_members_have_project_metadata() -> None:
    root = Path(__file__).parents[1]

    for member in WORKSPACE_MEMBERS:
        assert (root / member / "pyproject.toml").is_file()
