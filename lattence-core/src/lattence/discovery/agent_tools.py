import re
from dataclasses import dataclass

from lattence.graph import Agent, Model, Node, SourceRef, Tool

from .javascript_syntax import JavaScriptSyntax
from .python_syntax import PythonSyntax

_AGENT_CALLS = ("agent", "agentexecutor", "assistantagent", "stategraph")
_TOOL_CALLS = ("tool", "definetool", "structuredtool")
_DELEGATION_TERMS = ("delegate", "handoff", "route_to", "transfer_to")
_MEMORY_TERMS = ("memory", "checkpoint", "history", "state_store")
_PERMISSION_TERMS = {
    "read": ("get", "list", "read", "search", "view"),
    "write": ("create", "send", "update", "write"),
    "delete": ("delete", "remove"),
    "execute": ("exec", "run", "shell"),
}


@dataclass(frozen=True)
class AgentToolDiscovery:
    agents: tuple[Agent, ...]
    tools: tuple[Tool, ...]


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-") or "unnamed"


def _ends_with(value: str, terms: tuple[str, ...]) -> bool:
    normalized = value.lower().removesuffix("()")
    return any(normalized.rsplit(".", 1)[-1] == term for term in terms)


def _contains(value: str, terms: tuple[str, ...]) -> bool:
    normalized = value.lower()
    return any(term in normalized for term in terms)


def _permissions(name: str) -> set[str]:
    tokens = set(
        re.findall(r"[a-z]+", re.sub(r"([a-z])([A-Z])", r"\1 \2", name).lower())
    )
    return {
        permission
        for permission, terms in _PERMISSION_TERMS.items()
        if tokens.intersection(terms)
    }


def _python_tools(syntax: PythonSyntax) -> list[Tool]:
    tools: list[Tool] = []
    for decorator in syntax.decorators:
        if not _contains(decorator.decorator, ("tool", "function")):
            continue
        permissions = _permissions(decorator.target)
        tools.append(
            Tool(
                id=f"tool:{syntax.path}:{decorator.target}",
                name=decorator.target,
                source=SourceRef(path=syntax.path, line=decorator.location.line),
                side_effects=bool(permissions - {"read"}),
                permissions=permissions,
                metadata={"declaration": "decorator"},
            )
        )
    return tools


def _javascript_tools(syntax: JavaScriptSyntax) -> list[Tool]:
    tools: list[Tool] = []
    for call in syntax.calls:
        if not _ends_with(call.function, _TOOL_CALLS):
            continue
        name = f"tool at line {call.location.line}"
        tools.append(
            Tool(
                id=f"tool:{syntax.path}:{call.location.line}",
                name=name,
                source=SourceRef(path=syntax.path, line=call.location.line),
                metadata={"declaration": "call"},
            )
        )
    return tools


def _generic_agents(
    python_files: tuple[PythonSyntax, ...],
    javascript_files: tuple[JavaScriptSyntax, ...],
) -> list[Agent]:
    agents: list[Agent] = []
    for python_syntax in python_files:
        for assignment in python_syntax.assignments:
            if not _ends_with(assignment.value_kind, _AGENT_CALLS):
                continue
            agents.append(
                Agent(
                    id=f"agent:{python_syntax.path}:{assignment.location.line}",
                    name=assignment.target.rsplit(".", 1)[-1],
                    source=SourceRef(
                        path=python_syntax.path, line=assignment.location.line
                    ),
                )
            )
    for javascript_syntax in javascript_files:
        for call in javascript_syntax.calls:
            if not _ends_with(call.function, _AGENT_CALLS):
                continue
            agents.append(
                Agent(
                    id=f"agent:{javascript_syntax.path}:{call.location.line}",
                    name=f"agent at line {call.location.line}",
                    source=SourceRef(
                        path=javascript_syntax.path, line=call.location.line
                    ),
                )
            )
    return agents


def _path_flags(
    path: str,
    python_files: tuple[PythonSyntax, ...],
    javascript_files: tuple[JavaScriptSyntax, ...],
) -> tuple[bool, bool]:
    functions = [
        call.function
        for syntax in python_files
        if syntax.path == path
        for call in syntax.calls
    ]
    functions.extend(
        call.function
        for syntax in javascript_files
        if syntax.path == path
        for call in syntax.calls
    )
    return (
        any(_contains(function, _DELEGATION_TERMS) for function in functions),
        any(_contains(function, _MEMORY_TERMS) for function in functions),
    )


def detect_agents_and_tools(
    framework_nodes: tuple[Node, ...],
    model_nodes: tuple[Model, ...],
    python_files: tuple[PythonSyntax, ...] = (),
    javascript_files: tuple[JavaScriptSyntax, ...] = (),
) -> AgentToolDiscovery:
    tools = [
        *(tool for syntax in python_files for tool in _python_tools(syntax)),
        *(tool for syntax in javascript_files for tool in _javascript_tools(syntax)),
    ]
    known_agents = [node for node in framework_nodes if isinstance(node, Agent)]
    agents = [*known_agents, *_generic_agents(python_files, javascript_files)]
    unique_tools = {tool.id: tool for tool in tools}
    unique_agents = {agent.id: agent for agent in agents}

    enriched: list[Agent] = []
    for agent in unique_agents.values():
        path = agent.source.path if agent.source else ""
        tool_ids = sorted(
            tool.id
            for tool in unique_tools.values()
            if tool.source and tool.source.path == path
        )
        model_ids = sorted(
            model.id
            for model in model_nodes
            if model.source and model.source.path == path
        )
        delegation, memory = _path_flags(path, python_files, javascript_files)
        enriched.append(
            agent.model_copy(
                update={
                    "tool_ids": tool_ids,
                    "model_ids": model_ids,
                    "delegation_enabled": delegation,
                    "memory_enabled": memory,
                }
            )
        )
    return AgentToolDiscovery(
        agents=tuple(sorted(enriched, key=lambda item: item.id)),
        tools=tuple(unique_tools[key] for key in sorted(unique_tools)),
    )
