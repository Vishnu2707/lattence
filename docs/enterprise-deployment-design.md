# Enterprise deployment mode: controller/worker design

This document scopes the controller/worker deployment mode for large
organizations running many scans across many projects. It is a design only.
Nothing in this document is implemented in Phase 3. Implementation is Phase
5's job, once the RBAC and audit groundwork that mode depends on exists.
Building scheduling, worker registration, or a job queue before that
groundwork exists would mean building an authorization layer twice: once
ad hoc here, once correctly in Phase 5. This document exists so Phase 5 can
build the runtime against an agreed shape instead of re-deciding it.

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

## Controller API surface

Additive to the existing `/v1/scan`, `/v1/attack`, `/v1/chain` routes, not a
replacement:

- `POST /v1/jobs` submits a job (operation, project source reference).
  Requires the caller's RBAC-issued credential, not the Phase 2 static
  bearer token; the static token model is team mode only and does not
  extend to this mode.
- `GET /v1/jobs/{id}` returns job status and, once `succeeded`, the same
  `Report` or `SecurityPresentation` body `/v1/scan` etc. would have
  returned directly.
- `GET /v1/jobs` lists jobs visible to the caller under RBAC, for audit and
  monitoring.

## Audit trail

Every state transition a job goes through, submitted, dispatched to a
worker, completed or failed, is an audit record: who, what operation, what
project reference, when, and the outcome. This reuses the same shape as
`PolicyDecision` and `EnvironmentFingerprint` already defined in
`BUILD/CONTRACTS.md`'s evidence bundle, rather than inventing a second audit
format. The audit store itself, and how long records are retained, is
Phase 5 scope.

## What Phase 5 decides, not this document

- The concrete queue or scheduling mechanism between controller and
  workers.
- The RBAC store and role model.
- Where audit records persist and for how long.
- Whether workers run as container replicas, a job runner, or something
  else; this document only fixes that they are stateless, single-job,
  short-lived-credentialed, and call the same deterministic workflow
  functions the API already calls.
