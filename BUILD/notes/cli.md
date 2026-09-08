# CLI module

The root project builds the `lattence` distribution from `lattence-cli/src` and
installs the `lattence` binary. The command tree exposes all frozen v1 commands
and their seven common options. Commands are scaffolds that return internal
error code 3 until their owning implementation tasks wire behavior.

Public entry points are `lattence.cli:app`, `lattence.cli:main`, and
`python -m lattence.cli`. The current package version is `0.0.0`.

T-023 added strict loading for `lattence.targets.yaml`. Attack execution must
find a version 1 declaration, an `owned-or-authorized` acknowledgement, and an
explicit project-root target. Invalid declarations fail without echoing file
content. Project paths cannot escape the root and URL targets cannot embed
credentials.

T-038 added plain and color terminal scan summaries under the installed
`lattence.cli.presentation` namespace. Plain output contains no terminal escape
sequences and reports discovery counts, attack findings, crypto inventory, PQC
readiness, graph relationships, output path, and elapsed time.
