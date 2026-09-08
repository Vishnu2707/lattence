from pathlib import Path

from lattence.discovery import (
    Dependency,
    DependencyInventory,
    RulePack,
    detect_data_paths,
    load_rule_packs,
    parse_python_source,
)


def rules() -> tuple[RulePack, ...]:
    root = Path(__file__).parents[2]
    return tuple(load_rule_packs(root / "lattence-packs/discovery/data"))


def test_detects_vector_store_and_rag_dataset() -> None:
    syntax = parse_python_source(
        "import chromadb\ncollection.add(items)\nretriever.retrieve(query)\n",
        "src/rag.py",
    )
    dependencies = DependencyInventory(
        (Dependency("python", "chromadb", "", "runtime", "pyproject.toml"),),
        ("pyproject.toml",),
    )

    nodes = detect_data_paths(rules(), dependencies, (syntax,))

    databases = [node for node in nodes if node.type == "database"]
    datasets = [node for node in nodes if node.type == "dataset"]
    assert len(databases) == 1
    assert databases[0].engine == "chroma"
    assert len(datasets) == 2
    assert all(dataset.vectorized for dataset in datasets)
    assert {dataset.source.path for dataset in datasets if dataset.source} == {
        "src/rag.py"
    }


def test_detects_supported_vector_dependencies() -> None:
    dependencies = DependencyInventory(
        tuple(
            Dependency("python", name, "", "runtime", "pyproject.toml")
            for name in ("pinecone", "weaviate-client", "chromadb", "redisvl")
        ),
        ("pyproject.toml",),
    )

    nodes = detect_data_paths(rules(), dependencies)

    assert {node.name for node in nodes} == {
        "Chroma",
        "Pinecone",
        "Redis Vector",
        "Weaviate",
    }


def test_unrelated_project_has_no_data_path_nodes() -> None:
    syntax = parse_python_source("print('plain')\n", "plain.py")

    assert detect_data_paths(rules(), DependencyInventory((), ()), (syntax,)) == ()
