from datetime import UTC, datetime

from lattence.graph import (
    Agent,
    Application,
    CryptoAlgorithm,
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


def test_wires_crypto_to_ai_components_by_bounded_module_proximity() -> None:
    application = Application(
        id="application:fixture",
        name="fixture",
        source=SourceRef(path="src/app.py"),
        entrypoints=["src/app.py"],
    )
    agent = Agent(id="agent:fixture", name="agent", source=application.source)
    tool = Tool(id="tool:fixture", name="tool", source=application.source)
    server = MCPServer(
        id="mcp_server:fixture",
        name="server",
        source=SourceRef(path="src/mcp.json"),
        transport="stdio",
    )
    algorithm = CryptoAlgorithm(
        id="crypto_algorithm:src/crypto.py:1:x25519",
        name="X25519",
        source=SourceRef(path="src/crypto.py", line=1),
        algorithm="X25519",
        purpose="key exchange",
        quantum_status="vulnerable",
    )
    project = Project(
        id="fixture",
        name="fixture",
        root=".",
        scanned_at=datetime(2026, 1, 1, tzinfo=UTC),
        nodes=[application, agent, tool, server, algorithm],
    )

    graph = build_security_graph(project)
    crypto_edges = [edge for edge in graph.edges if edge.target_id == algorithm.id]

    assert {edge.source_id for edge in crypto_edges} == {
        application.id,
        agent.id,
        tool.id,
        server.id,
    }
    assert {edge.type for edge in crypto_edges} == {"key_exchange"}
    assert {edge.metadata["binding_reason"] for edge in crypto_edges} == {
        "module-proximity"
    }
    assert all("src/crypto.py" in edge.evidence_refs for edge in crypto_edges)


def test_prefers_explicit_config_reference_and_does_not_link_unrelated_modules() -> (
    None
):
    application = Application(
        id="application:fixture",
        name="fixture",
        source=SourceRef(path="src/app.py"),
    )
    unrelated = Tool(
        id="tool:unrelated",
        name="unrelated",
        source=SourceRef(path="other/tool.py"),
    )
    algorithm = CryptoAlgorithm(
        id="crypto_algorithm:config/tls.yaml:1:ecdsa",
        name="ECDSA",
        source=SourceRef(path="config/tls.yaml", line=1),
        algorithm="ECDSA",
        purpose="signature",
        quantum_status="vulnerable",
        metadata={"referenced_by": ["src/app.py"]},
    )
    project = Project(
        id="fixture",
        name="fixture",
        root=".",
        scanned_at=datetime(2026, 1, 1, tzinfo=UTC),
        nodes=[application, unrelated, algorithm],
    )

    graph = build_security_graph(project)
    crypto_edges = [edge for edge in graph.edges if edge.target_id == algorithm.id]

    assert len(crypto_edges) == 1
    assert crypto_edges[0].source_id == application.id
    assert crypto_edges[0].type == "protected_by"
    assert crypto_edges[0].metadata == {"binding_reason": "config-reference"}
    assert crypto_edges[0].evidence_refs == ["config/tls.yaml", "src/app.py"]
