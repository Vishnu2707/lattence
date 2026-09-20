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

Authentication (`auth.py`, `require_bearer_token`) is a static bearer token
read from the `LATTENCE_API_TOKEN` environment variable on every request, so
rotation only requires restarting the process with a new value, no stored
credential table. It is wired as a router-level `Depends` on the scan,
attack, and chain routers in `app.py`, not on `/health`. Missing server
configuration returns 503 (service unavailable, not a client error), a
missing or malformed header returns 401, and a
mismatched token returns 401. Comparison uses `secrets.compare_digest` to
avoid a timing side channel. This is the whole v1.0 auth model: one shared
secret, no per-caller identity, no scopes. RBAC and SSO are Phase 5 work; see
[[phase2-auth-deferred]].

`/v1/scan` and `/v1/attack` call `lattence.cli.workflow.machine_report`
before returning, which runs the same `jsonschema.Draft202012Validator`
against `docs/schemas/report.v1.json` that the CLI's `--json` output already
uses. A validation failure is a server-side contract defect, not a client
error, so it maps to 500 with the jsonschema message. `/v1/chain` needs no
separate schema check: `build_security_presentation` runs
`SecurityPresentation.references_are_valid` at construction time, so an
invalid presentation can never reach the route handler in the first place.

`tests/api/test_live_instance.py` runs `uvicorn.Server` in a background
thread bound to an ephemeral `127.0.0.1` port and issues real `httpx`
requests over that socket, not FastAPI's in-process `TestClient` ASGI
transport. This is the literal live-instance check the phase gate needs
before the manual `curl` walkthrough.

`lattence serve` (`lattence-cli/src/lattence/cli/serve_command.py`) starts
the API with uvicorn. It imports `fastapi`, `uvicorn`, and `lattence_api`
lazily inside the function body, not at module import time, so a plain
`pip install lattence` (no `api` extra) still gets every other command
working; `serve` alone fails with a clear message pointing at
`pip install lattence[api]`. `lattence-api` is deliberately not
force-included in the main wheel (`[tool.hatch.build.targets.wheel]` in the
root `pyproject.toml`): it stays an optional workspace member installed
through the `lattence[api]` extra, matching the decision recorded as D-026
in `BUILD/DECISIONS.md`. `serve` is documented in `BUILD/CONTRACTS.md`'s CLI
contract section as an addition outside the universal `--json`/`--out`/...
option set, since a long-running server process has no single output mode.

Local verification must use `uv sync --all-packages --dev`, the same command
CI runs. A plain `uv sync` only installs the direct dependency closure and
leaves sibling workspace packages (`lattence-core`, `lattence-evidence`, and
so on) unavailable as editable installs, which makes `mypy --strict` report
spurious `import-untyped` errors for packages that do carry a `py.typed`
marker.
