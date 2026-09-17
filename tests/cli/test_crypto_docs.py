from pathlib import Path

ROOT = Path(__file__).parents[2]


def test_crypto_guide_covers_flagship_scope_and_links_existing_diagrams() -> None:
    guide = (ROOT / "docs" / "crypto-assurance.md").read_text(encoding="utf-8")

    for term in (
        "Crypto dependency graph",
        "Quantum-vulnerable dependencies",
        "ML-KEM migration test",
        "ML-DSA migration test",
        "Hybrid TLS validation",
        "Crypto agility score",
        "Crypto chaos and downgrade validation",
        "Safety boundary",
    ):
        assert term in guide
    for name in ("crypto-assurance-pipeline.svg", "crypto-chaos-safety.svg"):
        assert name in guide
        assert (ROOT / "docs" / "architecture" / name).is_file()


def test_roadmap_no_longer_lists_completed_commands_as_scaffolded() -> None:
    roadmap = (ROOT / "ROADMAP.md").read_text(encoding="utf-8")

    assert "crypto chaos` remains scheduled" not in roadmap
    assert "The `tui` command exists" not in roadmap
