from pathlib import Path

DEMO = Path(__file__).parents[2] / "assets" / "demo"


def test_scan_tape_uses_frozen_demonstration_settings() -> None:
    source = (DEMO / "scan.tape").read_text(encoding="utf-8")

    assert "Set Width 1000" in source
    assert "Set Height 600" in source
    assert "Set TypingSpeed 40ms" in source
    assert "Set CursorBlink false" in source
    assert '"background": "#0B0D10"' in source
    assert "--offline" in source
    assert "--no-color" in source


def test_scan_gif_is_valid_and_below_release_limit() -> None:
    rendered = DEMO / "scan.gif"

    assert rendered.read_bytes().startswith(b"GIF")
    assert rendered.stat().st_size < 2 * 1024 * 1024
