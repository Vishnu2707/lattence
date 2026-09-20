# Enterprise deployment mode: controller/worker design

This document scoped the controller/worker deployment mode for large
organizations running many scans across many projects, written in Phase 3
as a design only, before Phase 5's RBAC and audit groundwork existed.

## What Phase 5 actually implemented

Phase 5 (`lattence_api.jobs.JobController`, `POST /v1/jobs`,
`GET /v1/jobs/{id}`, `GET /v1/jobs`) implements a single-controller,
multi-worker job queue: one API process holds an in-process thread pool
(`concurrent.futures.ThreadPoolExecutor`), submitting a job returns
immediately with a queued `Job` record, and a caller polls
`GET /v1/jobs/{id}` for status and, once `succeeded`, the same `Report` or
`SecurityPresentation` body the direct `/v1/scan`/`/v1/attack`/`/v1/chain`
routes would have returned. Every job submission and completion is an
audited event (`job_submit:<operation>` / `job_complete:<operation>`),
naming the RBAC caller, matching the audit trail section below. Submitting
a job requires the same role the equivalent direct route requires
(`run_scans`, `run_attacks`, `read_findings`), enforced through the same
`require_access` dependency Phase 5's RBAC already added.

This is the realistic scope named in the Phase 5 brief: a correct
single-controller-multi-worker queue, not a distributed system. What it
does not do, deliberately:

- No multi-host workers. All workers are threads in the one process that
  also serves the HTTP API; there is no worker registration protocol.
- No message broker. The queue is `ThreadPoolExecutor`'s own internal
  queue, in memory, lost on process restart. A `Job` record does not
  survive the controller process dying mid-run.
- No short-lived per-job worker credentials, since a worker is a thread in
  the same process and trust boundary as the controller, not a separate
  process the controller must authenticate to.

Reaching genuine multi-host distribution needs the infrastructure choices
this phase has no basis to make on its own: a real message queue or
broker, worker registration and heartbeating, and a decision about where
job state persists across a controller restart. The roles, job model, and
audit trail described below are unchanged by this scope; a future
multi-host implementation should keep this same `Job` shape and audit
event naming, replacing only the in-process queue with a real one.

## The design (Phase 3, written before Phase 5)

## Why this differs from team mode

Team mode (Phase 3, shipped) is one `lattence-api` container, one shared
bearer token, one project mounted at a time. It fits a single team running
its own scans against its own repositories. It does not fit an organization
that needs to run many scans across many teams' projects, know who
requested each run, enforce that a caller can only see findings for
projects they are authorized to see, and retain an audit trail of every
scan and attack execution for compliance. That is what controller/worker
mode is for.

## Roles

**Controller.** The only component that terminates client authentication. It
accepts job submissions, checks the caller's identity and role against
Phase 5's RBAC store, records an audit entry for the request, and enqueues
accepted jobs. It never runs `scan`, `attack`, or `graph chain` itself. It
holds no project source code and no scan results longer than serving them
back to an authorized caller; results live in whatever store Phase 5
chooses (the shape here does not need to know).

**Worker.** A pool of stateless processes, each running the same
`create_report` / `create_attack_report` / `create_security_presentation`
functions Phase 2's API already calls directly. A worker pulls one job at a
time, fetches or receives the project source named by the job, runs the
existing deterministic workflow, and returns the `Report` or
`SecurityPresentation` to the controller. A worker holds no long-lived
credential: it authenticates to the controller with a short-lived, per-job
token the controller issues when it dispatches the job, scoped to that job
alone.

This split is a trust boundary, not a performance optimization: the
controller is the only thing that needs to know who a caller is and what
they are allowed to see, so it is the only thing that carries that risk. A
worker that only ever sees one job's source and returns one job's result
cannot leak a different caller's data even if compromised.

## Job model

A `Job` carries: an id, the requesting caller's identity (from Phase 5
RBAC), a project source reference (a path or a fetchable location, not
inline source, since jobs may be large), the requested operation (`scan`,
`attack`, or `chain`, matching the existing `/v1/scan`, `/v1/attack`,
`/v1/chain` operations), a status (`queued`, `running`, `succeeded`,
`failed`), timestamps, and, on completion, the same `Report` or
`SecurityPresentation` model the existing API already returns. No new
result schema: a controller/worker run produces exactly what a direct
`/v1/scan` call produces today, so a caller migrating from team mode to
enterprise mode parses the same JSON.

## Controller API surface (as implemented)

Additive to the existing `/v1/scan`, `/v1/attack`, `/v1/chain` routes, not a
replacement:

- `POST /v1/jobs?operation=scan|attack|chain&path=...` submits a job.
  Accepts either an RBAC API key with the operation's required role, or the
  legacy Phase 2 static team token, the same as the direct routes; the
  static token was not restricted out of this surface, since doing so would
  make the job queue unusable from team mode for no stated benefit.
- `GET /v1/jobs/{id}` returns job status and, once `succeeded`, the same
  `Report` or `SecurityPresentation` body `/v1/scan` etc. would have
  returned directly. Requires `read_findings`.
- `GET /v1/jobs` lists every job the controller knows about. Requires
  `read_findings`. It does not yet filter to the caller's own jobs; see
  deferred items above.

## Audit trail (as implemented)

Every job submission and completion is an `AuditLog` record (actor,
action, target, result, and a JSON details blob carrying the job id),
using the same `lattence.governance.AuditLog` SQLite store Phase 5's CLI
and direct-route audit wiring already write to, not a separate format.
A dispatch-to-worker transition is not separately recorded, since in the
current in-process design dispatch is immediate and uninteresting; a
future multi-host implementation that adds real network dispatch latency
should add that transition back.

## What is still open for a real multi-host implementation

- The concrete queue or message broker between controller and remote
  workers.
- Worker registration, heartbeating, and failure handling.
- Job state persistence across a controller restart.
- Per-caller job listing and cancellation.
- Short-lived worker credentials, once workers are a separate process or
  host from the controller and need their own scoped access instead of
  running in the controller's own trust boundary.
