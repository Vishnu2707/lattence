import json
from pathlib import Path

ROOT = Path(__file__).parents[2]
GRAMMAR = ROOT / "lattence-ui" / "src" / "visual-grammar.json"
TOKENS = ROOT / "lattence-ui" / "src" / "tokens.css"


def test_shared_visual_grammar_matches_frozen_navigation_and_geometry() -> None:
    grammar = json.loads(GRAMMAR.read_text(encoding="utf-8"))

    assert grammar["navigation"] == [
        "Overview",
        "Applications",
        "Attack Surface",
        "AI Security",
        "Agent Security",
        "MCP",
        "Cryptography",
        "PQC Readiness",
        "Attack Graph",
        "Findings",
        "Verification",
        "Reports",
    ]
    assert grammar["geometry"] == {
        "spacing": [4, 8, 12, 16, 20, 24, 32],
        "rowHeight": 32,
        "controlHeights": [28, 32],
        "borderWidth": 1,
        "cornerRadius": 2,
        "focusWidth": 2,
        "focusOffset": 1,
    }
    assert grammar["detail"]["placement"] == "right-side-panel"
    assert grammar["detail"]["modal"] is False
    assert all(grammar["table"].values())


def test_css_exposes_every_frozen_color_without_forbidden_effects() -> None:
    grammar = json.loads(GRAMMAR.read_text(encoding="utf-8"))
    css = TOKENS.read_text(encoding="utf-8")

    assert all(value in css for value in grammar["colors"].values())
    assert "gradient" not in css.lower()
    assert "box-shadow" not in css.lower()
    assert "--radius: 2px" in css
    assert "border-radius: var(--radius)" in css
