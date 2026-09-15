# Roadmap

This lists what is scaffolded but not yet working, and what is planned. It
does not list work already shipped. See [CHANGELOG.md](CHANGELOG.md) for
that.

## Scaffolded commands

These commands exist in the CLI tree and accept their documented options,
but exit with an internal error and no behavior:

- `tui`
- `crypto chaos`

## Planned

- `crypto chaos` remains scheduled for v0.4.
- An `llm` planner mode may land in v0.4 or later. `--planner llm` is
  recognized today and exits with a not-implemented error.
- The terminal UI moves to v0.5 alongside the dashboard so both use one visual
  grammar.
- A published PyPI package. Install is source-only today.
- A Docker image. None exists yet.
- Private vulnerability reporting through GitHub, once the repository is
  public or otherwise eligible. See [SECURITY.md](SECURITY.md).

No roadmap item has a calendar date. Open an issue if one matters to your use
case.
