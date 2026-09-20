import shutil
import subprocess
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[2]

pytestmark = pytest.mark.skipif(
    shutil.which("docker") is None, reason="docker is not available"
)


def test_dockerfile_builds() -> None:
    result = subprocess.run(
        ["docker", "build", "-t", "lattence-api:pytest", "."],
        cwd=_ROOT,
        capture_output=True,
        text=True,
        timeout=600,
    )
    assert result.returncode == 0, result.stderr
