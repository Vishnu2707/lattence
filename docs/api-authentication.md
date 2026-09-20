# API authentication

`lattence-api` exposes `GET /v1/scan`, `POST /v1/attack`, and `GET /v1/chain`
behind a single static bearer token. `GET /health` requires no
authentication.

## Configuring the token

Set the `LATTENCE_API_TOKEN` environment variable to a random secret before
starting the server. There is no default value and no fallback: a request
to a `/v1/*` route on a server without `LATTENCE_API_TOKEN` set returns
`503` rather than serving unauthenticated. Rotating the token means changing
the environment variable and restarting the process; there is no revocation
list or expiry, since there is only one token.

## Making an authenticated request

Send the token as a standard bearer credential:

```
curl -H "Authorization: Bearer $LATTENCE_API_TOKEN" \
  "http://127.0.0.1:8000/v1/scan?path=."
```

A missing or malformed `Authorization` header returns `401` with detail
`missing bearer token`. A header present but not matching the configured
token returns `401` with detail `invalid bearer token`. The comparison uses
a constant-time check so a wrong guess cannot be distinguished from a
near-miss by timing.

## What this model is, and is not

This is the entire v1.0 authentication model: one shared secret, checked on
every request, with no notion of caller identity, roles, or scope. Anyone
holding the token can call every route with full access. There is no user
store, no session, no audit trail of which caller made which request beyond
whatever the deployment's own HTTP logs capture.

## Deferred to Phase 5

Phase 5 is scoped for enterprise controls, including per-caller identity,
role-based access control, and SSO integration. Until that phase ships:

- Do not deploy `lattence-api` where multiple parties with different trust
  levels need different access; the token is all-or-nothing.
- Treat the token like any other high-value secret: it grants read access to
  a project's full security graph, findings, and evidence, and grants the
  ability to run `attack` against a declared target.
- A production deployment that needs multi-tenant isolation or fine-grained
  permissions should wait for Phase 5, or terminate the API behind its own
  reverse proxy that adds per-caller authentication in front of this token.
