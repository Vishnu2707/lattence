from pathlib import Path

import yaml

ROOT = Path(__file__).parents[2]


def test_gitlab_template_is_well_formed() -> None:
    template = yaml.safe_load(
        (ROOT / "templates" / "gitlab-ci.yml").read_text(encoding="utf-8")
    )

    job = template["lattence-scan"]
    assert job["stage"] == "test"
    assert job["image"].startswith("python:")

    script = "\n".join(job["script"])
    assert "lattence scan" in script
    assert "lattence attack" in script
    assert "lattence sarif" in script
    assert "exit $EXIT_CODE" in script

    variables = template["variables"]
    assert variables["LATTENCE_FAIL_ON"] == "high"
    assert variables["LATTENCE_SOURCE"] == "pypi"

    artifacts = job["artifacts"]["paths"]
    assert "lattence-scan/lattence.sarif.json" in artifacts
    assert "lattence-scan/lattence-report.json" in artifacts


def test_gitlab_template_propagates_severity_gate_before_sarif() -> None:
    """A real bug this guards against: if the scan step aborts the shell on
    a nonzero exit before capturing it (GitLab's default script execution
    behaves like `set -e`), the SARIF conversion step never runs and the
    job fails with no artifact. The template must disable that, capture the
    real exit code, then re-enable it before the next command."""
    template = yaml.safe_load(
        (ROOT / "templates" / "gitlab-ci.yml").read_text(encoding="utf-8")
    )
    script = "\n".join(template["lattence-scan"]["script"])

    assert "set +e" in script
    assert "EXIT_CODE=$?" in script
    assert "set -e" in script
    assert script.index("set +e") < script.index("EXIT_CODE=$?")
    assert script.index("EXIT_CODE=$?") < script.index("lattence sarif")
