# API authentication

`lattence-api` supports two authentication modes on `GET /v1/scan`,
`POST /v1/attack`, and `GET /v1/chain`. `GET /health` requires no
authentication. The modes can run together: a request is checked against
RBAC first when RBAC is configured, then against the legacy static token.

## Team mode: a single static token

Set `LATTENCE_API_TOKEN` to a random secret before starting the server.
There is no default and no fallback: a request to a `/v1/*` route on a
server with neither `LATTENCE_API_TOKEN` nor RBAC configured returns `503`
rather than serving unauthenticated. A caller presenting this token gets
full access to every route, audited under the fixed actor id `team-token`.
This is what `docker compose` team mode (Phase 3) uses.

```bash
curl -H "Authorization: Bearer $LATTENCE_API_TOKEN" \
  "http://127.0.0.1:8000/v1/scan?path=."
```

## RBAC mode: per-caller API keys

Set `LATTENCE_RBAC_DB` to a file path. Lattence creates a SQLite database
there on first use. Issue a key with the CLI, not the API; there is no
self-service key creation route:

```bash
LATTENCE_RBAC_DB=./rbac.db lattence rbac create-key alice --role run_scans --role read_findings
```

The command prints the plaintext key once. Only its SHA-256 hash is stored.
`lattence rbac list` shows every caller id and its roles; `lattence rbac
revoke CALLER_ID` deletes all of a caller's keys.

Roles: `read_findings` (gates `GET /v1/chain`), `run_scans` (gates
`GET /v1/scan`), `run_attacks` (gates `POST /v1/attack`), and
`manage_policy` (not yet gating an API route; `policy check` is still
CLI-only, and this role is recorded in the audit log there instead).

A request with a valid key missing the route's required role returns `403`
naming the caller and the missing role. A request with a key that does not
resolve to anything, and that also does not match the legacy token, returns
`401`.

## Error responses

- `503`: neither `LATTENCE_API_TOKEN` nor `LATTENCE_RBAC_DB` is configured.
- `401 missing bearer token`: no `Authorization` header, or not a `Bearer`
  scheme.
- `401 invalid bearer token`: the presented token matches neither a known
  RBAC key nor the legacy token.
- `403`: a known RBAC key without the role the route requires.

Token comparison for the legacy path uses a constant-time check so a wrong
guess cannot be distinguished from a near-miss by timing.

## SSO extension point

`lattence_api.sso.SSOProvider` is a protocol for resolving an external
identity token (an OIDC access or ID token, for example) to a Lattence
caller id and role set. Call `lattence_api.sso.set_sso_provider(provider)`
before serving requests to activate one; `require_access` checks it before
RBAC and before the legacy token. `lattence_api.sso.MockSSOProvider` is the
shipped reference implementation: it resolves tokens of the form
`mock-sso:<caller_id>:<role,role,...>` without contacting any external
service, proving the seam works end to end. Wiring a real identity
provider means implementing `SSOProvider.resolve` to validate the token
against that provider (JWKS fetch, signature check, issuer and audience
validation) instead of parsing a role list out of the token string; no
real OIDC client ships in v1.0.

## What is still deferred

- A real OIDC client: the extension point is real, a production identity
  provider integration is not shipped.
- There is no session concept; every request re-authenticates.
- The distributed controller/worker mode's own authorization uses this
  same RBAC store; see
  [deployment modes](additional-info.md#deployment-modes).
