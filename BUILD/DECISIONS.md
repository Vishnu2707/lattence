# Decision log

Append decisions as three lines: date and identifier, decision, and rationale.
Do not rewrite earlier entries.

2026-09-08 D-001
Decision: Core models use a shared namespace package with graph-owned schemas.
Rationale: Separate workspace packages can extend one public Python namespace.

2026-09-08 D-002
Decision: The documented rule schema is bundled with the discovery package.
Rationale: Installed wheels validate offline, while a test prevents schema drift.

2026-09-08 D-003
Decision: The root project builds the public package from `lattence-cli/src`.
Rationale: One distribution owns the binary while workspace libraries stay separate.
## 2026-09-08, T-038, installed presentation namespace
Decision: Place terminal presentation code under `lattence.cli.presentation`.
Consequence: The frozen `lattence` namespace remains importable from the wheel.

2026-09-08 D-004
Decision: Duplicate bare test module names broke full-suite collection, so every test directory is now a package.
Rationale: Scoped runs never loaded both names; package markers preserve predictable dotted imports as the tree grows.
