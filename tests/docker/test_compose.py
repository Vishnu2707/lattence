import os
import shutil
import subprocess
from pathlib import Path

import pytest
import yaml

_ROOT = Path(__file__).resolve().parents[2]

pytestmark = pytest.mark.skipif(
    shutil.which("docker") is None, reason="docker is not available"
)


def _env(**overrides: str) -> dict[str, str]:
    base = {
        key: value
        for key, value in os.environ.items()
        if key not in {"LATTENCE_API_TOKEN", "LATTENCE_PROJECT_DIR"}
    }
    return {**base, **overrides}


def test_compose_config_is_valid() -> None:
    result = subprocess.run(
        ["docker", "compose", "config"],
        cwd=_ROOT,
        capture_output=True,
        text=True,
        env=_env(LATTENCE_API_TOKEN="test-token"),
        timeout=30,
    )
    assert result.returncode == 0, result.stderr
    config = yaml.safe_load(result.stdout)
    service = config["services"]["lattence-api"]
    assert service["environment"]["LATTENCE_API_TOKEN"] == "test-token"
    assert service["ports"][0]["target"] == 8000
    assert service["volumes"][0]["read_only"] is True


def test_compose_requires_token_when_unset() -> None:
    result = subprocess.run(
        ["docker", "compose", "config"],
        cwd=_ROOT,
        capture_output=True,
        text=True,
        env=_env(),
        timeout=30,
    )
    assert result.returncode != 0
    assert "LATTENCE_API_TOKEN" in result.stderr
