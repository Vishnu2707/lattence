# Roadmap

This lists what is scaffolded but not yet working, and what is planned. It
does not list work already shipped. See [CHANGELOG.md](CHANGELOG.md) for
that.

## Scaffolded commands

The `tui` command exists in the CLI tree and accepts its documented options,
but exits with an internal error until its visual system ships with the
dashboard.

## Planned

- An `llm` planner mode may land in a future release. `--planner llm` is
  recognized today and exits with a not-implemented error.
- The terminal UI is planned for v0.5 alongside the dashboard so both use one visual
  grammar.
- A published PyPI package. Install is source-only today.
- A Docker image. None exists yet.
- Private vulnerability reporting through GitHub, once the repository is
  public or otherwise eligible. See [SECURITY.md](SECURITY.md).

No roadmap item has a calendar date. Open an issue if one matters to your use
case.
