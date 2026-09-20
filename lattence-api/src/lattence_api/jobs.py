import threading
import uuid
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from pathlib import Path
from typing import Any

from lattence.cli.presentation_workflow import create_security_presentation
from lattence.cli.workflow import create_attack_report, create_report
from lattence.evidence import Report, SecurityPresentation
from lattence.governance import AuditLog, Role, default_audit_db_path


class JobOperation(StrEnum):
    SCAN = "scan"
    ATTACK = "attack"
    CHAIN = "chain"


class JobStatus(StrEnum):
    QUEUED = "queued"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


_ROLE_FOR_OPERATION = {
    JobOperation.SCAN: Role.RUN_SCANS,
    JobOperation.ATTACK: Role.RUN_ATTACKS,
    JobOperation.CHAIN: Role.READ_FINDINGS,
}


def role_for_operation(operation: JobOperation) -> Role:
    return _ROLE_FOR_OPERATION[operation]


def _now() -> str:
    return datetime.now(UTC).isoformat()


@dataclass
class Job:
    id: str
    operation: JobOperation
    project_source: str
    caller_id: str
    status: JobStatus = JobStatus.QUEUED
    submitted_at: str = field(default_factory=_now)
    started_at: str | None = None
    finished_at: str | None = None
    result: dict[str, Any] | None = None
    error: str | None = None


class JobController:
    """A single controller coordinating a fixed pool of in-process workers.

    This is the realistic scope for a single-host deployment: one process
    submits jobs to a thread pool, each worker calls the same deterministic
    workflow functions the direct API routes already call, and every state
    transition is audited. It deliberately does not attempt multi-host
    worker registration, a message broker, or short-lived per-job worker
    credentials; see docs/enterprise-deployment-design.md for what those
    would need and why they are Phase 5's realistic stopping point, not
    this controller's.
    """

    def __init__(self, worker_count: int = 2, audit_db: Path | None = None) -> None:
        self._jobs: dict[str, Job] = {}
        self._lock = threading.Lock()
        self._executor = ThreadPoolExecutor(max_workers=worker_count)
        self._audit = AuditLog(audit_db or default_audit_db_path())

    def submit(
        self, operation: JobOperation, project_source: str, caller_id: str
    ) -> Job:
        job = Job(
            id=str(uuid.uuid4()),
            operation=operation,
            project_source=project_source,
            caller_id=caller_id,
        )
        with self._lock:
            self._jobs[job.id] = job
        self._audit.record(
            actor=caller_id,
            action=f"job_submit:{operation.value}",
            target=project_source,
            result="queued",
            details={"job_id": job.id},
        )
        self._executor.submit(self._run, job.id)
        return job

    def _run(self, job_id: str) -> None:
        with self._lock:
            job = self._jobs[job_id]
            job.status = JobStatus.RUNNING
            job.started_at = _now()
        source = Path(job.project_source)
        result: Report | SecurityPresentation
        try:
            if job.operation is JobOperation.SCAN:
                result = create_report(source)
            elif job.operation is JobOperation.ATTACK:
                result = create_attack_report(source, source, True, source)
            else:
                result = create_security_presentation(source)
        except Exception as error:
            with self._lock:
                job.status = JobStatus.FAILED
                job.error = str(error)
                job.finished_at = _now()
            self._audit.record(
                actor=job.caller_id,
                action=f"job_complete:{job.operation.value}",
                target=job.project_source,
                result="failed",
                details={"job_id": job.id, "error": str(error)},
            )
            return
        with self._lock:
            job.status = JobStatus.SUCCEEDED
            job.result = result.model_dump(mode="json")
            job.finished_at = _now()
        self._audit.record(
            actor=job.caller_id,
            action=f"job_complete:{job.operation.value}",
            target=job.project_source,
            result="succeeded",
            details={"job_id": job.id},
        )

    def get(self, job_id: str) -> Job | None:
        with self._lock:
            return self._jobs.get(job_id)

    def list_jobs(self, caller_id: str | None = None) -> tuple[Job, ...]:
        with self._lock:
            jobs = tuple(self._jobs.values())
        if caller_id is None:
            return jobs
        return tuple(job for job in jobs if job.caller_id == caller_id)
