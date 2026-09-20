from datetime import UTC, datetime
from pathlib import Path

from lattence.cli.presentation import (
    TuiState,
    handle_presentation_key,
    handle_tui_key,
    render_tui,
)
from lattence.cli.presentation_workflow import create_security_presentation
from lattence.evidence import CrossLayerChain, CrossLayerHop, SecurityPresentation
from lattence.graph import Dataset, Project, SecurityGraph, Tool

EXAMPLE = Path(__file__).parents[2] / "examples" / "vulnerable-agent"


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
        hops=[
            CrossLayerHop.model_construct(
                edge_id="edge:fixture",
                source_id=tool.id,
                target_id=dataset.id,
                edge_type="reads_from",
                traversal="reverse",
                from_node_id=dataset.id,
                to_node_id=tool.id,
                evidence_refs=["app.py:15"],
            )
        ],
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
    assert "REVERSE" in rendered
    assert "dataset:rag -> tool:retrieval" in rendered
    assert "app.py:15" in rendered
    next_hop = handle_tui_key(state, "]", row_count=1, hop_count=2)
    assert next_hop.path_hop_index == 1
    assert handle_tui_key(next_hop, "[", row_count=1, hop_count=2).path_hop_index == 0
    help_state = handle_tui_key(state, "?", row_count=1)
    assert "HELP" in render_tui(_presentation(), help_state, width=160)
    assert handle_tui_key(help_state, "q", row_count=1).quit_requested is True


def test_real_finding_row_opens_correlation_and_navigates_hops() -> None:
    presentation = create_security_presentation(EXAMPLE)
    graph_view = render_tui(
        presentation,
        TuiState(section_index=8),
        width=160,
        height=24,
    )
    assert "32 finding correlations / 9 structural paths" in graph_view
    ai_finding_ids = [
        finding.id
        for finding in presentation.findings
        if finding.id.startswith("LT-AI-")
    ]
    state = TuiState(
        section_index=3,
        row_index=ai_finding_ids.index("LT-AI-002"),
    )

    state = handle_presentation_key(presentation, state, "enter")
    first_hop = render_tui(presentation, state, width=240, height=40)

    assert state.detail_open is True
    assert "LT-AI-002" in first_hop
    assert "LT-PQC-203" in first_hop
    assert "HOP 1  ACCESSES  REVERSE" in first_hop
    assert "app.py" in first_hop

    state = handle_presentation_key(presentation, state, "]")
    second_hop = render_tui(presentation, state, width=240, height=40)

    assert state.path_hop_index == 1
    assert "HOP 2  KEY_EXCHANGE  FORWARD" in second_hop
    assert "crypto_config.py" in second_hop
