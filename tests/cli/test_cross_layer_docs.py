from pathlib import Path

ROOT = Path(__file__).parents[2]


def test_cross_layer_guide_covers_orientation_views_and_evidence() -> None:
    guide = (ROOT / "docs" / "cross-layer-analysis.md").read_text(encoding="utf-8")

    for term in (
        "source_id",
        "target_id",
        "from_node_id",
        "to_node_id",
        "Attack Graph",
        "presentation.json",
        "Evidence review",
        "lattence graph chain",
    ):
        assert term in guide
    assert "cross-layer-chain.svg" in guide
    assert (ROOT / "assets" / "diagrams" / "cross-layer-chain.svg").is_file()


def test_readme_links_shared_presentation_guide_and_demo() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")

    assert "docs/cross-layer-analysis.md" in readme
    assert "assets/demo/tui.gif" in readme
    assert "lattence graph chain" in readme
