import json
from dataclasses import asdict, dataclass
from pathlib import Path
from shutil import which
from typing import cast

from lattence.graph import JsonValue

from .runtime import SecurityProvider

_EXECUTABLES = {
    "garak": "garak",
    "promptfoo": "promptfoo",
    "pyrit": "pyrit_scan",
}
_STATE_FILE = "providers.json"


class ProviderRegistryError(ValueError):
    pass


@dataclass(frozen=True)
class ProviderState:
    name: str
    enabled: bool
    available: bool
    executable: str

    def as_json(self) -> dict[str, JsonValue]:
        return cast(dict[str, JsonValue], asdict(self))


def _read_enabled(directory: Path) -> set[str]:
    path = directory / _STATE_FILE
    if not path.exists():
        return set()
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ProviderRegistryError(f"invalid provider state: {error}") from error
    if not isinstance(value, dict) or value.get("version") != "1":
        raise ProviderRegistryError("provider state version must be 1")
    enabled = value.get("enabled")
    if not isinstance(enabled, list) or any(
        not isinstance(item, str) or item not in _EXECUTABLES for item in enabled
    ):
        raise ProviderRegistryError("provider state has invalid enabled providers")
    if len(enabled) != len(set(enabled)):
        raise ProviderRegistryError("provider state has duplicate enabled providers")
    return set(enabled)


def _state(name: str, enabled: set[str]) -> ProviderState:
    executable = _EXECUTABLES[name]
    return ProviderState(
        name=name,
        enabled=name in enabled,
        available=which(executable) is not None,
        executable=executable,
    )


def list_providers(directory: Path) -> tuple[ProviderState, ...]:
    enabled = _read_enabled(directory)
    return tuple(_state(name, enabled) for name in sorted(_EXECUTABLES))


def enable_provider(name: str, directory: Path) -> ProviderState:
    normalized = name.strip().lower()
    if normalized not in _EXECUTABLES:
        choices = ", ".join(sorted(_EXECUTABLES))
        raise ProviderRegistryError(
            f"unknown provider {name!r}; expected one of: {choices}"
        )
    enabled = _read_enabled(directory)
    enabled.add(normalized)
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / _STATE_FILE
    temporary = path.with_suffix(".json.tmp")
    temporary.write_text(
        json.dumps({"enabled": sorted(enabled), "version": "1"}, indent=2) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)
    return _state(normalized, enabled)


def enabled_providers(directory: Path) -> tuple[SecurityProvider, ...]:
    from .garak import GarakProvider
    from .promptfoo import PromptfooProvider
    from .pyrit import PyritProvider

    factories = {
        "garak": GarakProvider,
        "promptfoo": PromptfooProvider,
        "pyrit": PyritProvider,
    }
    return tuple(
        factories[state.name]()
        for state in list_providers(directory)
        if state.enabled and state.available
    )
