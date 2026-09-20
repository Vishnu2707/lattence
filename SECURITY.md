# Security policy

## Supported versions

Security fixes are released for the latest minor version line only.

| Version | Supported |
| --- | --- |
| 1.0.x | yes |
| < 1.0 | no |

## Reporting a vulnerability

Email vish27uk@gmail.com with a description of the issue, the affected
version or commit, and reproduction steps. Do not open a public issue for a
security report.

This repository does not yet use GitHub's private vulnerability reporting.
It requires GitHub Advanced Security on a private repository under a
personal account, which is not available here. Email is the reporting
channel until that changes.

Expect an acknowledgement within 5 business days. We aim to confirm or
resolve reported issues within 90 days of the initial report, and will tell
you if a fix needs more time. We ask that you hold public disclosure until a
fix is released or the 90 days pass, whichever comes first.

## Responsible use of this tool

Lattence is offensive security tooling. It discovers agent, tool, and model
attack surface, and its `attack` and `crypto chaos` commands run active
checks against a project. Point it only at systems you own or are
explicitly authorized to test. This applies equally when running through
the REST API (`POST /v1/attack`) or the job queue (`POST /v1/jobs?
operation=attack`), not only the CLI.

`attack` and `crypto chaos` enforce this technically: both refuse to run
without a `lattence.targets.yaml` declaration in the project root that
names the target and acknowledges `owned-or-authorized`. Project targets
cannot resolve outside the declared root, and URL targets cannot embed
credentials. This is a consent gate, not a guarantee. It stops accidental
misuse, not a user who deliberately declares a target they are not
authorized to test.

The REST API's bearer token (`LATTENCE_API_TOKEN`) and RBAC API keys grant
whoever holds them the roles they were issued. Treat both like any other
credential: rotate a token by restarting the server with a new value,
revoke an RBAC key with `lattence rbac revoke CALLER_ID`, and do not commit
either to source control.

If you find that Lattence itself can be made to scan or attack a target
outside its declared scope, or that the API's authentication or RBAC
enforcement can be bypassed, report it as a security issue under this
policy.
