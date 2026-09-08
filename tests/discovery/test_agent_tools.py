from lattence.discovery import (
    detect_agents_and_tools,
    parse_javascript_source,
    parse_python_source,
)
from lattence.graph import Agent, Model


def test_detects_tools_permissions_delegation_and_memory() -> None:
    syntax = parse_python_source(
        """\
from framework import Agent, tool

agent = Agent()

@tool
def read_customer() -> str:
    return "data"

@tool()
def delete_customer() -> None:
    pass

delegate_to_worker(agent)
memory.save(agent)
""",
        "src/agent.py",
    )
    model = Model(
        id="model:test",
        name="test model",
        provider="test",
        model_name="fixture",
        source={"path": "src/agent.py", "line": 1},
    )

    result = detect_agents_and_tools((), (model,), (syntax,))

    assert len(result.agents) == 1
    agent = result.agents[0]
    assert agent.delegation_enabled
    assert agent.memory_enabled
    assert agent.model_ids == ["model:test"]
    assert len(agent.tool_ids) == 2
    tools = {tool.name: tool for tool in result.tools}
    assert tools["read_customer"].permissions == {"read"}
    assert not tools["read_customer"].side_effects
    assert tools["delete_customer"].permissions == {"delete"}
    assert tools["delete_customer"].side_effects


def test_enriches_existing_framework_agent_without_duplicates() -> None:
    syntax = parse_python_source("agent = Agent()\n", "agent.py")
    existing = Agent(
        id="agent:framework:agent.py:1",
        name="Agent",
        source={"path": "agent.py", "line": 1},
        framework="fixture",
    )

    result = detect_agents_and_tools((existing,), (), (syntax,))

    assert {agent.id for agent in result.agents} == {
        "agent:framework:agent.py:1",
        "agent:agent.py:1",
    }


def test_detects_javascript_agent_and_tool_calls() -> None:
    syntax = parse_javascript_source(
        "const agent = Agent();\nconst tool = defineTool({});\n", "agent.ts"
    )

    result = detect_agents_and_tools((), (), javascript_files=(syntax,))

    assert len(result.agents) == 1
    assert len(result.tools) == 1
    assert result.agents[0].tool_ids == [result.tools[0].id]


def test_unrelated_source_produces_no_agents_or_tools() -> None:
    syntax = parse_python_source("value = object()\n", "plain.py")

    result = detect_agents_and_tools((), (), (syntax,))

    assert result.agents == ()
    assert result.tools == ()
