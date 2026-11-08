import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).parents[2]
SCRIPT = ROOT / "scripts" / "verify-release.sh"


def test_release_verification_script_is_runnable_and_documented() -> None:
    assert SCRIPT.is_file()
    assert os.access(SCRIPT, os.X_OK)
    subprocess.run(["sh", "-n", str(SCRIPT)], check=True)

    source = SCRIPT.read_text(encoding="utf-8")
    assert "expected_tests=" in source
    assert "expected_coverage=" in source
    assert "Attack paths           92" in source
    assert "32 finding correlations across 9 distinct structural paths" in source

    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "Verify these claims yourself" in readme
    assert "scripts/verify-release.sh" in readme
