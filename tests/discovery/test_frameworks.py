from pathlib import Path

from lattence.discovery import (
    Dependency,
    DependencyInventory,
    RulePack,
    detect_frameworks,
    load_rule_packs,
    parse_javascript_source,
    parse_python_source,
)


def rules() -> tuple[RulePack, ...]:
    root = Path(__file__).parents[2]
    return tuple(load_rule_packs(root / "lattence-packs/discovery/frameworks"))


def test_detects_application_and_agent_from_python_syntax() -> None:
    syntax = parse_python_source(
        "from langgraph.graph import StateGraph\ngraph = StateGraph(State)\n",
        "src/agent.py",
    )
    dependencies = DependencyInventory(
        dependencies=(
            Dependency("python", "langgraph", ">=1", "runtime", "pyproject.toml"),
        ),
        manifests=("pyproject.toml",),
    )

    nodes = detect_frameworks(rules(), dependencies, python_files=(syntax,))

    framework_nodes = [node for node in nodes if node.name == "LangGraph"]
    assert len(framework_nodes) == 1
    agents = [node for node in nodes if node.type == "agent"]
    assert len(agents) == 1
    assert agents[0].source is not None
    assert agents[0].source.path == "src/agent.py"


def test_detects_each_supported_framework_from_dependency() -> None:
    dependencies = DependencyInventory(
        dependencies=tuple(
            Dependency("python", name, "", "runtime", "pyproject.toml")
            for name in (
                "agents",
                "autogen-agentchat",
                "crewai",
                "langchain",
                "langgraph",
                "semantic-kernel",
            )
        ),
        manifests=("pyproject.toml",),
    )

    nodes = detect_frameworks(rules(), dependencies)

    applications = {node.name for node in nodes if node.type == "application"}
    assert applications == {
        "Agents SDK",
        "AutoGen",
        "CrewAI",
        "LangChain",
        "LangGraph",
        "Semantic Kernel",
    }


def test_detects_node_import_without_dependency_manifest() -> None:
    syntax = parse_javascript_source(
        'import { Agent } from "agents";\nconst agent = Agent();\n', "src/agent.ts"
    )
    empty = DependencyInventory((), ())

    nodes = detect_frameworks(rules(), empty, javascript_files=(syntax,))

    assert {node.type for node in nodes} == {"application", "agent"}


def test_unrelated_project_produces_no_framework_nodes() -> None:
    syntax = parse_python_source("import pathlib\npathlib.Path('.')\n", "app.py")

    nodes = detect_frameworks(rules(), DependencyInventory((), ()), (syntax,))

    assert nodes == ()
