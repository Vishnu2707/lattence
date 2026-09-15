from dataclasses import dataclass
from typing import Literal

from .execution import CryptoChaosObservation

type DowngradeStatus = Literal["blocked", "resistant", "vulnerable"]


@dataclass(frozen=True, order=True)
class DowngradeEvidence:
    experiment: str
    target_path: str
    outcome: str
    probe_returncode: int | None
    original_sha256: str
    mutated_sha256: str | None
    rollback_verified: bool


@dataclass(frozen=True)
class DowngradeValidation:
    status: DowngradeStatus
    resistant: bool | None
    evidence: tuple[DowngradeEvidence, ...]
    blocking_reasons: tuple[str, ...]


def _evidence(observation: CryptoChaosObservation) -> DowngradeEvidence:
    if not observation.executed:
        outcome = "dry-run"
    elif observation.timed_out:
        outcome = "timeout"
    elif observation.error:
        outcome = "error"
    elif observation.downgrade_accepted:
        outcome = "accepted"
    else:
        outcome = "rejected"
    return DowngradeEvidence(
        experiment=observation.experiment,
        target_path=observation.target_path,
        outcome=outcome,
        probe_returncode=observation.probe_returncode,
        original_sha256=observation.original_sha256,
        mutated_sha256=observation.mutated_sha256,
        rollback_verified=observation.rollback_verified,
    )


def validate_downgrade_resistance(
    observations: tuple[CryptoChaosObservation, ...],
) -> DowngradeValidation:
    evidence = tuple(sorted(_evidence(item) for item in observations))
    reasons: list[str] = []
    if not observations:
        reasons.append("no downgrade experiments were supplied")
    if any(not item.rollback_verified for item in observations):
        reasons.append("one or more mutation targets were not restored")
    if any(not item.executed for item in observations):
        reasons.append("one or more experiments were dry runs")
    if any(item.timed_out for item in observations):
        reasons.append("one or more probes timed out")
    if any(item.error is not None for item in observations):
        reasons.append("one or more probes could not run")
    if any(item.downgrade_accepted is None for item in observations):
        reasons.append("one or more experiments produced no acceptance result")
    if reasons:
        return DowngradeValidation(
            status="blocked",
            resistant=None,
            evidence=evidence,
            blocking_reasons=tuple(sorted(set(reasons))),
        )
    if any(item.downgrade_accepted for item in observations):
        return DowngradeValidation(
            status="vulnerable",
            resistant=False,
            evidence=evidence,
            blocking_reasons=(),
        )
    return DowngradeValidation(
        status="resistant",
        resistant=True,
        evidence=evidence,
        blocking_reasons=(),
    )
