from pathlib import Path

from lattence.discovery import (
    Dependency,
    DependencyInventory,
    RulePack,
    detect_services,
    load_rule_packs,
    parse_python_source,
)


def rules() -> tuple[RulePack, ...]:
    root = Path(__file__).parents[2]
    return tuple(load_rule_packs(root / "lattence-packs/discovery/services"))


def test_detects_api_database_cache_and_external_operation() -> None:
    syntax = parse_python_source(
        """\
from fastapi import FastAPI
import psycopg
import httpx
app = FastAPI()
app.get('/items')
psycopg.connect()
httpx.post('https://example.test')
""",
        "src/api.py",
    )
    dependencies = DependencyInventory(
        tuple(
            Dependency("python", name, "", "runtime", "pyproject.toml")
            for name in ("fastapi", "psycopg", "httpx", "redis")
        ),
        ("pyproject.toml",),
    )

    nodes = detect_services(rules(), dependencies, (syntax,))

    assert {node.name for node in nodes if node.type == "api"} == {"FastAPI"}
    assert {node.name for node in nodes if node.type == "database"} == {
        "PostgreSQL",
        "Redis",
    }
    external = [node for node in nodes if node.type == "external_service"]
    assert len(external) == 2
    assert all(node.host is None for node in external)


def test_detects_next_dependency() -> None:
    dependencies = DependencyInventory(
        (Dependency("node", "next", "^18", "runtime", "package.json"),),
        ("package.json",),
    )

    nodes = detect_services(rules(), dependencies)

    assert len(nodes) == 1
    assert nodes[0].name == "Next.js"


def test_unrelated_project_produces_no_service_nodes() -> None:
    assert detect_services(rules(), DependencyInventory((), ())) == ()
