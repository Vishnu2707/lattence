from pathlib import Path

import yaml

ROOT = Path(__file__).parents[2]


def test_action_yml_is_well_formed_composite_action() -> None:
    action = yaml.safe_load((ROOT / "action.yml").read_text(encoding="utf-8"))

    assert action["runs"]["using"] == "composite"
    step_ids = {step.get("id") for step in action["runs"]["steps"] if step.get("id")}
    assert {"run", "sarif"} <= step_ids
    upload_step = next(
        step
        for step in action["runs"]["steps"]
        if str(step.get("uses", "")).startswith("github/codeql-action/upload-sarif")
    )
    assert "@" in upload_step["uses"]
    assert upload_step["with"]["sarif_file"] == "${{ steps.sarif.outputs.path }}"


def test_self_scan_workflow_uses_local_action_and_uploads_findings() -> None:
    workflow = yaml.safe_load(
        (ROOT / ".github" / "workflows" / "lattence-scan.yml").read_text(
            encoding="utf-8"
        )
    )

    assert workflow["permissions"]["security-events"] == "write"
    steps = workflow["jobs"]["self-scan"]["steps"]
    assert any(step.get("uses") == "./" for step in steps)


def test_workflow_actions_are_pinned_to_a_commit_sha() -> None:
    workflow = yaml.safe_load(
        (ROOT / ".github" / "workflows" / "lattence-scan.yml").read_text(
            encoding="utf-8"
        )
    )
    action = yaml.safe_load((ROOT / "action.yml").read_text(encoding="utf-8"))

    for steps in (workflow["jobs"]["self-scan"]["steps"], action["runs"]["steps"]):
        for step in steps:
            uses = step.get("uses")
            if uses is None or uses == "./":
                continue
            ref = uses.rsplit("@", 1)[-1]
            assert len(ref) == 40 and all(
                character in "0123456789abcdef" for character in ref
            ), f"{uses} is not pinned to a full commit SHA"
