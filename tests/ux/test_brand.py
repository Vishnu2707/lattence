import struct
from pathlib import Path

BRAND = Path(__file__).parents[2] / "assets" / "brand"


def _png_dimensions(path: Path) -> tuple[int, int]:
    data = path.read_bytes()
    assert data[:8] == b"\x89PNG\r\n\x1a\n"
    return struct.unpack(">II", data[16:24])


def test_required_svg_assets_are_clean_and_geometric() -> None:
    names = {
        "logo.svg",
        "mark.svg",
        "mark-mono.svg",
        "logo-light.svg",
        "logo-dark.svg",
        "favicon.svg",
    }

    for name in names:
        source = (BRAND / name).read_text(encoding="utf-8")
        assert "<svg" in source
        assert "metadata" not in source.lower()
        assert "generator" not in source.lower()
        assert 'stroke-linecap="square"' in source
        assert " C" not in source and " Q" not in source


def test_raster_assets_have_required_dimensions() -> None:
    assert _png_dimensions(BRAND / "mark-32.png") == (32, 32)
    assert _png_dimensions(BRAND / "mark-64.png") == (64, 64)
    assert _png_dimensions(BRAND / "mark-256.png") == (256, 256)
    assert _png_dimensions(BRAND / "mark-512.png") == (512, 512)
    assert _png_dimensions(BRAND / "social-card.png") == (1280, 640)
