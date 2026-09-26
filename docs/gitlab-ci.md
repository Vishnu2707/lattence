# GitLab CI integration

Lattence ships a GitLab CI job template alongside the existing GitHub
Action. It reuses the same commands the GitHub Action already runs:
`lattence scan` (or `lattence attack`) followed by `lattence sarif` to
convert the report into a standard SARIF file.

## Usage

Copy `templates/gitlab-ci.yml` into your project, or include it remotely:

```yaml
include:
  - remote: https://raw.githubusercontent.com/Vishnu2707/lattence/dev/templates/gitlab-ci.yml
```

This adds a `lattence-scan` job to the `test` stage. Configure it with
CI/CD variables:

| Variable | Default | Meaning |
| --- | --- | --- |
| `LATTENCE_PATH` | `.` | Project path to scan, relative to the job workspace. |
| `LATTENCE_FAIL_ON` | `high` | Severity gate: `critical`, `high`, `medium`, `low`, `info`, or `none`. |
| `LATTENCE_RUN_ATTACK` | `false` | Set to `true` to also run the native attack catalog (requires a `lattence.targets.yaml` in the target path). |
| `LATTENCE_SOURCE` | `pypi` | `pypi` installs the published package; `local` installs from the current checkout. |

## What it produces

The job publishes three artifacts, kept for 30 days:

- `lattence-scan/lattence-report.json`, the full report.
- `lattence-scan/lattence-report.html`, the self-contained dashboard.
- `lattence-scan/lattence.sarif.json`, a standard SARIF 2.1.0 file.

The job fails the pipeline when findings meet the configured severity gate,
the same behavior as the GitHub Action's `fail-on` input.

## What this does not do

GitLab's Security Dashboard reads its own `gl-sast-report.json` schema, not
SARIF. This template does not produce that schema and does not appear in
the Security Dashboard. It publishes a standard SARIF artifact you can
download, or feed into another SARIF-aware tool, and it fails the build on
the severity gate like any other CI check. Native Security Dashboard
support is unimplemented; if you need it, open an issue.
