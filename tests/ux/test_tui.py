from datetime import UTC, datetime

from lattence.cli.presentation import TuiState, handle_tui_key, render_tui
from lattence.evidence import CrossLayerChain, CrossLayerHop, SecurityPresentation
from lattence.graph import Dataset, Project, SecurityGraph, Tool


def _presentation() -> SecurityPresentation:
    generated_at = datetime(2026, 1, 1, tzinfo=UTC)
    dataset = Dataset(id="dataset:rag", name="RAG")
    tool = Tool(id="tool:retrieval", name="retrieval")
    graph = SecurityGraph(
        project_id="fixture",
        nodes=[dataset, tool],
        edges=[],
        generated_at=generated_at,
    )
    project = Project(
        id="fixture",
        name="fixture",
        root=".",
        scanned_at=generated_at,
        nodes=[dataset, tool],
    )
    chain = CrossLayerChain.model_construct(
        id="cross-layer:fixture",
        source_finding_id="LT-AI-002",
        crypto_finding_id="LT-PQC-203",
        start_node_id=dataset.id,
        end_node_id=tool.id,
        hops=[CrossLayerHop.model_construct(edge_id="edge:fixture")],
        explanation="LT-AI-002 reaches TLS 1.2 through real graph edges.",
        evidence_refs=["app.py", "crypto_config.py"],
    )
    return SecurityPresentation.model_construct(
        project=project,
        graph=graph,
        findings=[],
        cross_layer_chains=[chain],
        generated_at=generated_at,
    )


def test_tui_renders_fixed_navigation_without_terminal_escapes() -> None:
    rendered = render_tui(_presentation(), width=120, color=False)

    for label in (
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
    ):
        assert label in rendered
    assert "\x1b[" not in rendered
    assert "? help" in rendered


def test_tui_keyboard_navigation_opens_chain_detail_and_help() -> None:
    state = TuiState()
    for _ in range(8):
        state = handle_tui_key(state, "right", row_count=1)
    assert state.section_index == 8

    state = handle_tui_key(state, "enter", row_count=1)
    rendered = render_tui(_presentation(), state, width=160, color=False)

    assert state.detail_open is True
    assert "LT-AI-002 reaches TLS 1.2" in rendered
    assert "DETAIL" in rendered
    help_state = handle_tui_key(state, "?", row_count=1)
    assert "HELP" in render_tui(_presentation(), help_state, width=160)
    assert handle_tui_key(help_state, "q", row_count=1).quit_requested is True
