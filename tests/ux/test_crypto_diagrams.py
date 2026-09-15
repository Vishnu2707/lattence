from pathlib import Path
from xml.etree import ElementTree

DIAGRAMS = Path(__file__).parents[2] / "docs" / "architecture"


def test_crypto_diagrams_are_accessible_clean_svgs() -> None:
    names = {"crypto-assurance-pipeline.svg", "crypto-chaos-safety.svg"}

    for name in names:
        source = (DIAGRAMS / name).read_text(encoding="utf-8")
        root = ElementTree.fromstring(source)
        assert root.attrib["width"] == "1200"
        assert root.attrib["height"] == "680"
        assert "aria-labelledby" in root.attrib
        assert "<title" in source and "<desc" in source
        assert "metadata" not in source.lower()
        assert "generator" not in source.lower()
        assert "#0B0D10" in source
        assert "#4C8DFF" in source


def test_diagrams_cover_assurance_and_safety_flows() -> None:
    assurance = (DIAGRAMS / "crypto-assurance-pipeline.svg").read_text()
    chaos = (DIAGRAMS / "crypto-chaos-safety.svg").read_text()

    for label in ("CRYPTO GRAPH", "ML-KEM TEST", "ML-DSA TEST", "AGILITY SCORE"):
        assert label in assurance
    for label in ("CONSENT GATE", "DOWNGRADE", "RESTORE ORIGINAL BYTES", "EVIDENCE"):
        assert label in chaos
