# Security policy

## Supported versions

Lattence is pre-1.0. Security fixes are released for the latest minor
version line only. That is currently 0.1.x.

| Version | Supported |
| --- | --- |
| 0.1.x | yes |
| < 0.1 | no |

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
attack surface, and its `attack` command runs a native catalog of attack
checks against a project. Point it only at systems you own or are
explicitly authorized to test.

The `attack` command enforces this technically: it refuses to run without a
`lattence.targets.yaml` declaration in the project root that names the
target and acknowledges `owned-or-authorized`. Project targets cannot
resolve outside the declared root, and URL targets cannot embed credentials.
This is a consent gate, not a guarantee. It stops accidental misuse, not a
user who deliberately declares a target they are not authorized to test.

If you find that Lattence itself can be made to scan or attack a target
outside its declared scope, report it as a security issue under this
policy.
