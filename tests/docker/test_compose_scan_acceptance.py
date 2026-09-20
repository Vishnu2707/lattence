import json
import shutil
import subprocess
import time
import urllib.error
import urllib.request
from pathlib import Path

import pytest
from lattence.cli.workflow import create_report
from lattence.evidence import report_json

_ROOT = Path(__file__).resolve().parents[2]
_TOKEN = "acceptance-test-token"

pytestmark = pytest.mark.skipif(
    shutil.which("docker") is None, reason="docker is not available"
)


def _compose(*args: str) -> None:
    docker = shutil.which("docker")
    assert docker is not None
    subprocess.run(
        [docker, "compose", *args],
        cwd=_ROOT,
        env={"LATTENCE_API_TOKEN": _TOKEN, "PATH": str(Path(docker).parent)},
        check=True,
        capture_output=True,
        text=True,
        timeout=180,
    )


def _wait_for_health(deadline: float) -> None:
    while time.monotonic() < deadline:
        try:
            urllib.request.urlopen("http://127.0.0.1:8000/health", timeout=1)
            return
        except (urllib.error.URLError, ConnectionError):
            time.sleep(0.5)
    raise TimeoutError("container did not become healthy in time")


def test_compose_scan_against_mounted_project_matches_cli() -> None:
    _compose("up", "-d", "--build")
    try:
        _wait_for_health(time.monotonic() + 60)
        request = urllib.request.Request(
            "http://127.0.0.1:8000/v1/scan?path=/data",
            headers={"Authorization": f"Bearer {_TOKEN}"},
        )
        with urllib.request.urlopen(request, timeout=30) as response:
            container_body = json.loads(response.read())
    finally:
        _compose("down")

    expected = json.loads(
        report_json(
            create_report(_ROOT / "examples" / "vulnerable-agent"),
            _ROOT / "docs" / "schemas" / "report.v1.json",
        )
    )
    assert container_body["summary"] == expected["summary"]
    assert [finding["id"] for finding in container_body["findings"]] == [
        finding["id"] for finding in expected["findings"]
    ]
