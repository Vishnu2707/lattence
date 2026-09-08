# Decision log

Append decisions as three lines: date and identifier, decision, and rationale.
Do not rewrite earlier entries.

2026-09-08 D-001
Decision: Core models use a shared namespace package with graph-owned schemas.
Rationale: Separate workspace packages can extend one public Python namespace.

2026-09-08 D-002
Decision: The documented rule schema is bundled with the discovery package.
Rationale: Installed wheels validate offline, while a test prevents schema drift.
