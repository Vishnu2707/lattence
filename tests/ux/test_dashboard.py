from pathlib import Path

ROOT = Path(__file__).parents[2] / "lattence-ui"


def test_dashboard_shell_has_fixed_rail_table_toolbar_and_side_panel() -> None:
    html = (ROOT / "index.html").read_text(encoding="utf-8")
    css = (ROOT / "src" / "dashboard.css").read_text(encoding="utf-8")

    assert 'id="navigation"' in html
    assert 'id="filter"' in html
    assert 'id="save-view"' in html
    assert 'id="copy-json"' in html
    assert 'id="export-json"' in html
    assert 'id="detail-panel"' in html
    assert "position: sticky" in css
    assert "height: 32px" in css
    assert "grid-template-columns: 208px minmax(480px, 1fr) 360px" in css
    assert "dialog" not in html


def test_dashboard_implements_keyboard_filter_sort_virtualization_and_export() -> None:
    source = (ROOT / "src" / "dashboard.mjs").read_text(encoding="utf-8")

    assert 'event.key === "ArrowDown"' in source
    assert 'event.key === "ArrowUp"' in source
    assert "filterRows(" in source
    assert "sortRows(" in source
    assert "visibleRows(" in source
    assert 'localStorage.setItem("lattence.saved-view"' in source
    assert "navigator.clipboard.writeText" in source
    assert 'link.download = "lattence-presentation.json"' in source
