from pathlib import Path

import pytest

DEMO = Path(__file__).parents[2] / "assets" / "demo"
TAPES = ["scan", "attack", "tui"]


@pytest.mark.parametrize("name", TAPES)
def test_tape_uses_frozen_demonstration_settings(name: str) -> None:
    source = (DEMO / f"{name}.tape").read_text(encoding="utf-8")

    assert "Set Width 1000" in source
    assert "Set Height 600" in source
    assert "Set TypingSpeed 40ms" in source
    assert "Set CursorBlink false" in source
    assert '"background": "#0B0D10"' in source
    assert "--offline" in source
    assert "--no-color" in source
    assert f"lattence {name} ." in source


@pytest.mark.parametrize("name", TAPES)
def test_gif_is_valid_and_below_release_limit(name: str) -> None:
    rendered = DEMO / f"{name}.gif"

    assert rendered.read_bytes().startswith(b"GIF")
    assert rendered.stat().st_size < 2 * 1024 * 1024
