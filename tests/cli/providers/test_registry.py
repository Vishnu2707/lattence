import json
from pathlib import Path

import pytest
from lattence.providers.registry import (
    ProviderRegistryError,
    enable_provider,
    enabled_providers,
    list_providers,
)


def test_registry_enables_known_provider_and_preserves_optional_state(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr("lattence.providers.registry.which", lambda name: None)

    enabled = enable_provider("garak", tmp_path)
    providers = list_providers(tmp_path)

    assert enabled.name == "garak"
    assert enabled.enabled
    assert not enabled.available
    assert [item.name for item in providers] == ["garak", "promptfoo", "pyrit"]
    assert json.loads((tmp_path / "providers.json").read_text()) == {
        "enabled": ["garak"],
        "version": "1",
    }


def test_registry_rejects_unknown_provider(tmp_path: Path) -> None:
    with pytest.raises(ProviderRegistryError, match="unknown provider"):
        enable_provider("unknown", tmp_path)


def test_registry_rejects_invalid_state(tmp_path: Path) -> None:
    (tmp_path / "providers.json").write_text('{"version":"2","enabled":[]}')

    with pytest.raises(ProviderRegistryError, match="version"):
        list_providers(tmp_path)


def test_registry_builds_only_enabled_available_providers(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    enable_provider("garak", tmp_path)
    enable_provider("pyrit", tmp_path)
    monkeypatch.setattr(
        "lattence.providers.registry.which",
        lambda name: f"/bin/{name}" if name == "garak" else None,
    )

    providers = enabled_providers(tmp_path)

    assert [type(provider).__name__ for provider in providers] == ["GarakProvider"]
