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

`POST /v1/attack` (`routes/attack.py`) requires `lattence.targets.yaml` in the
target path, same as the CLI `attack` command, using
`lattence.cli.load_target_declaration`. A missing or invalid declaration
returns 400, mirroring the CLI's `BadParameter` behavior instead of silently
running an unauthorized attack. It then calls
`lattence.cli.workflow.create_attack_report` and returns the same `Report`
model that already embeds `Finding` and `EvidenceBundle`.

`GET /v1/chain` (`routes/chain.py`) calls
`lattence.cli.presentation_workflow.create_security_presentation` and returns
`SecurityPresentation`. `SecurityPresentation.cross_layer_summary` is a
`@computed_field`, not a settable field: it serializes into the response JSON
but `model_validate` rejects it back as an unknown field on a model with
`extra="forbid"`. Tests that round-trip the response must strip that key
before revalidating, or assert on it separately.

Local verification must use `uv sync --all-packages --dev`, the same command
CI runs. A plain `uv sync` only installs the direct dependency closure and
leaves sibling workspace packages (`lattence-core`, `lattence-evidence`, and
so on) unavailable as editable installs, which makes `mypy --strict` report
spurious `import-untyped` errors for packages that do carry a `py.typed`
marker.
