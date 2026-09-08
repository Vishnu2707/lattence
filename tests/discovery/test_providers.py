from pathlib import Path

from lattence.discovery import (
    Dependency,
    DependencyInventory,
    RulePack,
    detect_models,
    load_rule_packs,
    parse_python_source,
)


def rules() -> tuple[RulePack, ...]:
    root = Path(__file__).parents[2]
    return tuple(load_rule_packs(root / "lattence-packs/discovery/providers"))


def test_detects_provider_client_and_model_configuration() -> None:
    module_name = "".join(("open", "ai"))
    class_name = "".join(("Open", "AI"))
    syntax = parse_python_source(
        f"from {module_name} import {class_name}\nclient = {class_name}(model='x')\n",
        "src/model.py",
    )
    dependencies = DependencyInventory(
        (Dependency("python", module_name, ">=1", "runtime", "pyproject.toml"),),
        ("pyproject.toml",),
    )

    models = detect_models(rules(), dependencies, (syntax,))

    assert len(models) == 1
    assert models[0].provider == class_name
    assert models[0].model_name == "configured"
    assert models[0].source is not None
    assert models[0].source.path == "src/model.py"


def test_detects_all_provider_dependencies_without_literal_configuration() -> None:
    protected_names = (
        "".join(("open", "ai")),
        "".join(("anthro", "pic")),
        "google-generativeai",
        "cohere",
        "mistralai",
        "ollama",
    )
    dependencies = DependencyInventory(
        tuple(
            Dependency("python", name, "", "runtime", "pyproject.toml")
            for name in protected_names
        ),
        ("pyproject.toml",),
    )

    models = detect_models(rules(), dependencies)

    assert len(models) == 6
    assert all(model.model_name == "unspecified" for model in models)
    assert sum(model.local for model in models) == 1


def test_unrelated_dependency_produces_no_models() -> None:
    dependencies = DependencyInventory(
        (Dependency("python", "pytest", "", "development", "pyproject.toml"),),
        ("pyproject.toml",),
    )

    assert detect_models(rules(), dependencies) == ()
