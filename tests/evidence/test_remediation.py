import pytest
from lattence.evidence import RemediationError, remediation_plans

from .test_reporting import _report


def test_remediation_plan_contains_finding_target_and_reproduction() -> None:
    report = _report()

    plans = remediation_plans(report)

    assert len(plans) == 1
    assert plans[0].finding_id == "LT-AI-001"
    assert plans[0].remediation == "Fix the fixture."
    assert plans[0].target.id == "agent:one"
    assert plans[0].target.type == "agent"
    assert plans[0].reproduction == report.findings[0].reproduction
    assert plans[0].evidence_id == report.findings[0].evidence.id


def test_remediation_plan_filters_by_finding_id() -> None:
    plans = remediation_plans(_report(), "LT-AI-001")

    assert [plan.finding_id for plan in plans] == ["LT-AI-001"]


def test_remediation_plan_rejects_unknown_finding() -> None:
    with pytest.raises(RemediationError, match="finding not found"):
        remediation_plans(_report(), "LT-AI-999")


def test_remediation_plan_rejects_missing_target_node() -> None:
    report = _report()
    invalid = report.model_copy(
        update={
            "findings": [
                report.findings[0].model_copy(
                    update={"target_node_id": "agent:missing"}
                )
            ]
        }
    )

    with pytest.raises(RemediationError, match="target node not found"):
        remediation_plans(invalid)
