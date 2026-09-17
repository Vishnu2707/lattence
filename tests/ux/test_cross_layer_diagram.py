from pathlib import Path
from xml.etree import ElementTree

ROOT = Path(__file__).parents[2]
SOURCE = ROOT / "docs" / "architecture" / "cross-layer-chain.mmd"
RENDERED = ROOT / "assets" / "diagrams" / "cross-layer-chain.svg"


def test_cross_layer_diagram_source_records_real_edge_orientation() -> None:
    source = SOURCE.read_text(encoding="utf-8")

    for label in (
        "LT-AI-002",
        "untrusted retrieval",
        "delete_customer_record",
        "X25519",
        "REVERSE traversal",
        "FORWARD key_exchange",
    ):
        assert label in source


def test_cross_layer_diagram_is_accessible_and_uses_frozen_tokens() -> None:
    source = RENDERED.read_text(encoding="utf-8")
    root = ElementTree.fromstring(source)

    assert root.tag.endswith("svg")
    assert "<title" in source and "<desc" in source
    assert "#0B0D10" in source
    assert "#4C8DFF" in source
    assert "#E5484D" in source
    assert "linearGradient" not in source
    assert "drop-shadow" not in source
    assert "generator" not in source.lower()
