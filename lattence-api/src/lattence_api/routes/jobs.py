from typing import Annotated, Any

from fastapi import APIRouter, Depends, Header, HTTPException, Request
from lattence.governance import Role
from pydantic import BaseModel

from ..audit import record_api_audit_event
from ..auth import AuthenticatedCaller, require_access
from ..jobs import Job, JobController, JobOperation, JobStatus, role_for_operation

router = APIRouter()


class JobResponse(BaseModel):
    id: str
    operation: JobOperation
    project_source: str
    caller_id: str
    status: JobStatus
    submitted_at: str
    started_at: str | None
    finished_at: str | None
    result: dict[str, Any] | None
    error: str | None


def _to_response(job: Job) -> JobResponse:
    return JobResponse(
        id=job.id,
        operation=job.operation,
        project_source=job.project_source,
        caller_id=job.caller_id,
        status=job.status,
        submitted_at=job.submitted_at,
        started_at=job.started_at,
        finished_at=job.finished_at,
        result=job.result,
        error=job.error,
    )


def require_job_submitter(
    operation: JobOperation,
    authorization: str | None = Header(default=None),
) -> AuthenticatedCaller:
    return require_access(role_for_operation(operation))(authorization)


@router.post("/v1/jobs", response_model=JobResponse)
def submit_job(
    request: Request,
    caller: Annotated[AuthenticatedCaller, Depends(require_job_submitter)],
    operation: JobOperation,
    path: str = ".",
) -> JobResponse:
    controller: JobController = request.app.state.job_controller
    job = controller.submit(operation, path, caller.caller_id)
    record_api_audit_event(
        caller_id=caller.caller_id,
        action=f"job_submit:{operation.value}",
        target=path,
        result="queued",
        details={"job_id": job.id},
    )
    return _to_response(job)


@router.get("/v1/jobs/{job_id}", response_model=JobResponse)
def get_job(
    request: Request,
    job_id: str,
    caller: Annotated[AuthenticatedCaller, Depends(require_access(Role.READ_FINDINGS))],
) -> JobResponse:
    del caller
    controller: JobController = request.app.state.job_controller
    job = controller.get(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail=f"unknown job: {job_id}")
    return _to_response(job)


@router.get("/v1/jobs", response_model=list[JobResponse])
def list_jobs(
    request: Request,
    caller: Annotated[AuthenticatedCaller, Depends(require_access(Role.READ_FINDINGS))],
) -> list[JobResponse]:
    del caller
    controller: JobController = request.app.state.job_controller
    return [_to_response(job) for job in controller.list_jobs()]
