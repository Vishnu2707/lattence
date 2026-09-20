# API module notes

`lattence-api` is a uv workspace member under `lattence-api/src/lattence_api`.
It is an optional install (`lattence[api]` extra and a `lattence-api` dev
dependency for tests) so the core CLI package stays free of a web framework
dependency.

`create_app()` in `lattence_api/app.py` returns a FastAPI application. It
exposes `/health` today. Routes for `/v1/scan`, `/v1/attack`, and `/v1/chain`
will call directly into the existing `lattence.cli.workflow` and
`lattence.cli.presentation_workflow` functions and return the same frozen
Pydantic models the CLI already serializes; the API layer must not redefine
`Report`, `Finding`, `EvidenceBundle`, or `SecurityPresentation`.

Authentication is a single static bearer token for v1.0. RBAC and SSO are out
of scope until Phase 5.

`GET /v1/scan` (`routes/scan.py`) calls `lattence.cli.workflow.create_report`
directly and returns the frozen `Report` model. A missing project path
returns 404. `lattence-api` depends on the root `lattence` package (declared
as a workspace source) for every workflow function it calls.

Local verification must use `uv sync --all-packages --dev`, the same command
CI runs. A plain `uv sync` only installs the direct dependency closure and
leaves sibling workspace packages (`lattence-core`, `lattence-evidence`, and
so on) unavailable as editable installs, which makes `mypy --strict` report
spurious `import-untyped` errors for packages that do carry a `py.typed`
marker.
