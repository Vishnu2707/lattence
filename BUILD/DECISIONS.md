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

2026-09-08 D-005
Decision: CI coverage gate is set to 85 percent through `pytest-cov`, against a current total near 91 percent.
Rationale: The threshold catches real regressions without pinning to the exact current number and breaking on small, legitimate drops.

2026-09-08 D-006
Decision: The wheel force-includes the source of every workspace package it needs, and root dependencies list real third-party libraries instead of the workspace package names.
Rationale: A wheel built with the workspace names as dependencies cannot be installed outside the uv workspace, and was missing most of the runtime import surface.

2026-09-09 D-007
Decision: `--version` now prints the frozen ASCII banner before the version line, changing its previously exact-match output contract.
Rationale: BUILD/DESIGN.md allows a banner on the version command and at TUI start; the existing test pinned a narrower contract than the design system called for, so the test was widened to check the version line specifically rather than the whole output.
