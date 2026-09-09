# Roadmap

This lists what is scaffolded but not yet working, and what is planned. It
does not list work already shipped. See [CHANGELOG.md](CHANGELOG.md) for
that.

## Scaffolded commands

These commands exist in the CLI tree and accept their documented options,
but exit with an internal error and no behavior:

- `harden`
- `verify`
- `tui`
- `crypto chaos`
- `provider enable`
- `provider list`
- `policy check`

## Planned

- An `llm` planner mode alongside the default deterministic rules planner.
  `--planner llm` is accepted today but not implemented.
- A published PyPI package. Install is source-only today.
- A Docker image. None exists yet.
- Private vulnerability reporting through GitHub, once the repository is
  public or otherwise eligible. See [SECURITY.md](SECURITY.md).

Nothing here is scheduled to a date. Open an issue if one of these matters
to your use case.
