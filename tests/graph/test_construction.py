from datetime import UTC, datetime

from lattence.graph import (
    Agent,
    Application,
    MCPServer,
    Project,
    SourceRef,
    Tool,
    build_security_graph,
)


def test_constructs_deterministic_relationship_edges() -> None:
    source = SourceRef(path="app.py", line=1)
    tool = Tool(
        id="tool:search",
        name="search",
        source=source,
        permissions={"read"},
    )
    agent = Agent(
        id="agent:primary",
        name="primary",
        source=source,
        tool_ids=[tool.id],
    )
    application = Application(
        id="application:fixture",
        name="fixture",
        source=source,
        entrypoints=["app.py"],
    )
    server = MCPServer(
        id="mcp_server:local",
        name="local",
        source=SourceRef(path="mcp.json"),
        transport="stdio",
        tool_ids=[tool.id],
    )
    project = Project(
        id="fixture",
        name="fixture",
        root=".",
        scanned_at=datetime(2026, 1, 1, tzinfo=UTC),
        nodes=[tool, server, agent, application],
    )

    graph = build_security_graph(project)

    relationships = {
        (edge.source_id, edge.type, edge.target_id) for edge in graph.edges
    }
    assert (application.id, "contains", agent.id) in relationships
    assert (application.id, "contains", tool.id) in relationships
    assert (agent.id, "calls", tool.id) in relationships
    assert (server.id, "contains", tool.id) in relationships
    call_edge = next(edge for edge in graph.edges if edge.source_id == agent.id)
    assert call_edge.permission == "read"
    assert graph.generated_at == project.scanned_at
    assert [node.id for node in graph.nodes] == sorted(node.id for node in graph.nodes)


def test_deduplicates_edges_supported_by_repeated_references() -> None:
    tool = Tool(id="tool:one", name="one")
    agent = Agent(id="agent:one", name="one", tool_ids=[tool.id, tool.id])
    project = Project(
        id="fixture",
        name="fixture",
        root=".",
        scanned_at=datetime(2026, 1, 1, tzinfo=UTC),
        nodes=[agent, tool],
    )

    graph = build_security_graph(project)

    assert len(graph.edges) == 1
