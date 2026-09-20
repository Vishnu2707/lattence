# Roadmap

This lists what is scaffolded but not yet working, and what is planned. It
does not list work already shipped. See [CHANGELOG.md](CHANGELOG.md) for
that.

## Planned

- An `llm` planner mode may land in a future release. `--planner llm` is
  recognized today and exits with a not-implemented error.
- A real OIDC client. `lattence_api.sso.SSOProvider` is a working extension
  point with a mock reference provider; no built-in provider validates a
  real identity token yet.
- Multi-host distributed workers. The job queue today is a single
  controller process with an in-process worker pool; see
  [docs/enterprise-deployment-design.md](docs/enterprise-deployment-design.md)
  for what a real distributed version still needs.
- Private vulnerability reporting through GitHub, once the repository is
  public or otherwise eligible. See [SECURITY.md](SECURITY.md).

No roadmap item has a calendar date. Open an issue if one matters to your use
case.
