# Frozen design system

Version: 1.0. This system is frozen before terminal or dashboard work begins.
A token or structural change requires a decision record and a dedicated task.

## Direction

Lattence uses the visual language of infrastructure command line tools and
operational data tables. It favors dense information, explicit state, and
repeatable geometry.

- Prefer density to empty space. A security engineer should see many rows.
- Use monospace for data. Use proportional type only for prose.
- Use one accent color. Severity uses only the fixed severity scale.
- Do not use gradients, glow, decorative shadows, pervasive pills, emoji,
  illustrations, mascots, or celebratory effects.
- A one-pixel border is the strongest panel elevation.
- Express every state with a glyph or word. Color is never the only signal.

## Color tokens

| Token | Dark value | Purpose |
| --- | --- | --- |
| `surface.0` | `#0B0D10` | Base background |
| `surface.1` | `#12151A` | Panel |
| `surface.2` | `#1A1F26` | Raised surface and table header |
| `border` | `#262C35` | Rules and panel boundaries |
| `text.primary` | `#E6E9EE` | Primary text |
| `text.muted` | `#8A94A6` | Secondary text |
| `accent` | `#4C8DFF` | Focus and selected state |
| `sev.critical` | `#E5484D` | Critical severity |
| `sev.high` | `#F76808` | High severity |
| `sev.medium` | `#E2A336` | Medium severity |
| `sev.low` | `#3E9B4F` | Low severity |
| `sev.info` | `#6E7A8A` | Informational severity |
| `pass` | `#3E9B4F` | Passing state |
| `fail` | `#E5484D` | Failing state |

The light theme mechanically inverts the three surfaces and two text tokens.
It keeps the accent and severity ramp unchanged. The light palette must meet
WCAG AA contrast for text and state labels before release.

## Typography

The terminal inherits the user's font. Dashboard tokens:

- `mono`: JetBrains Mono, then `ui-monospace`, SFMono-Regular, and Menlo.
- `sans`: Inter, then `system-ui`.
- `size`: 11, 12, 13, 14, 16, 20, and 28 pixels. No other size is valid.
- Numeric table cells use tabular numerals.
- Data labels, identifiers, commands, paths, timestamps, and measurements use
  `mono`. Paragraphs and long explanations use `sans`.

## Spacing and geometry

- Base spacing unit: 4 pixels.
- Valid spacing: 4, 8, 12, 16, 20, 24, and 32 pixels.
- Table row height: 32 pixels.
- Control height: 28 or 32 pixels.
- Border width: 1 pixel.
- Corner radius: 2 pixels for panels, controls, and side panels.
- Focus ring: 2 pixels in `accent`, offset by 1 pixel.
- Icons use a 16 pixel square and a 1.5 pixel stroke.

## Terminal interface

Use Rich for layout, not decoration. Use single-line box drawing, fixed column
widths, aligned labels, and right-aligned numbers.

Valid state words are `PASS`, `FAIL`, `WARN`, `SKIP`, `BLOCKED`, and
`VULNERABLE`. Do not substitute symbols or colored dots.

Scanning shows one overwritable progress line containing phase, item count, and
elapsed time. A non-interactive stream receives periodic plain phase lines, not
cursor control sequences.

Honor `NO_COLOR`, `--no-color`, and non-TTY output. Plain mode uses aligned
ASCII and contains no escape sequences. With `--json`, stdout contains one
machine-readable document and stderr contains logs. `--quiet` suppresses all
non-error logs.

Exit codes:

| Code | Meaning |
| ---: | --- |
| 0 | Clean or below the configured finding gate |
| 1 | At least one finding meets the gate |
| 2 | Invalid usage or input |
| 3 | Internal failure |

Reference `scan` output:

```text
LATTENCE  scan  examples/vulnerable-agent

DISCOVERY
  Agents               2
  MCP servers          2
  Tools                8
  External APIs        3
  Vector stores        1

AI ATTACK SURFACE
  Prompt injection     HIGH
  Excessive agency     HIGH
  Unsafe tool use      MEDIUM

CRYPTOGRAPHY
  RSA-2048             2
  ECDSA P-256          3
  X25519               2
  ML-KEM-768           0
  Quantum vulnerable   7 paths
  PQC readiness        18%

Attack paths           12
Findings               9   critical 1  high 3  medium 4  low 1

Report  ./lattence-report.html      Elapsed  4.2s
```

`lattence tui` opens a full-screen, keyboard-driven view with the dashboard
information architecture. `?` opens help. The version command and TUI start may
show a plain block-character banner of no more than six lines.

## Dashboard structure

The fixed left rail contains exactly these entries, in this order:

1. Overview
2. Applications
3. Attack Surface
4. AI Security
5. Agent Security
6. MCP
7. Cryptography
8. PQC Readiness
9. Attack Graph
10. Findings
11. Verification
12. Reports

Every list uses a dense virtualized table with a sticky header, column sorting,
a filter bar, saved views, and keyboard navigation. Rows are 32 pixels tall.
A selected row opens its detail in a right side panel. Do not use a modal.

Finding detail contains the description, target node, evidence bundle, exact
reproduction command, OWASP mappings, and a Verify action that runs replay.

The attack graph uses a dark canvas. Node type is encoded by shape and label.
An edge label states its trust or cryptographic attribute. Selecting a path
highlights the full chain and opens its cross-layer explanation.

Chrome must carry data or navigation. Do not add hero banners, onboarding
cards, or illustrated empty states. An empty state is one sentence and one
command. Loading states use skeleton rows. Every view provides copy as JSON and
export actions.

## Logo system

Brand assets live in `assets/brand/` and use hand-authored SVG.

The mark is a 4 by 4 lattice on a 24-unit grid. Points sit on coordinates 3, 9,
15, and 21 on both axes. A subset of straight edges forms an `L` in negative
space. Lines use a 2-unit stroke, square caps, no curves, and integer or half
integer coordinates. The mark must remain legible at 16 pixels.

Required assets:

- `logo.svg`: mark and lowercase `lattence` wordmark.
- `mark.svg`: color mark.
- `mark-mono.svg`: one-color mark.
- `logo-light.svg` and `logo-dark.svg`: surface-specific lockups.
- `favicon.svg`.
- PNG marks at 32, 64, 256, and 512 pixels.
- `social-card.png` at 1280 by 640 pixels.

The wordmark uses the mono face with visible letter spacing. SVG and raster
files contain no editor or generator metadata.

## Architecture diagrams

Mermaid sources live in `docs/architecture/`. Rendered SVG files live in
`assets/diagrams/`. Rendering uses the design tokens and runs in CI. Commit both
source and output.

Required diagrams: system architecture, engine pipeline, security graph model,
dynamic attack loop, cross-layer attack chain, deployment modes, and CI flow.

## Demonstrations

VHS source tapes and rendered GIFs live in `assets/demo/`. Required pairs are
`scan`, `attack`, `pqc`, `verify`, and `tui`.

- Terminal size is 100 columns by 30 rows.
- Theme colors match this file.
- Typing interval is 40 milliseconds.
- Cursor blink is disabled.
- Fixture output is deterministic.
- Each GIF is below 2 MB.
- `make demos` renders every tape.

If VHS is unavailable, commit the tapes and target, record a manual render step
in `BUILD/STATE.md`, and continue.
