# UX module note

T-040 added the geometric lattice mark, dark and light logo lockups, favicon,
monochrome mark, ASCII banner, four PNG mark sizes, and a 1280 by 640 social
card. SVG files contain no editor metadata and use only straight, square-ended
geometry. Raster dimensions and SVG hygiene have automated tests.

T-042 added a deterministic scan tape and a 1000 by 600 GIF under
`assets/demo/`. The tape uses a 100-column by 30-row presentation, the frozen
dark palette, 40 millisecond typing, a fixed fixture, and no cursor blink. Run
`make demos` from a synced source checkout to reproduce it. The GIF is checked
for its signature and the 2 MB release limit.

A later design-system pass added an `attack.tape` and `attack.gif` alongside
`scan`, both re-rendered from the real `examples/vulnerable-agent` output
(the `LT-AGENT`, `LT-AI`, and `LT-MCP` findings, and the indirect prompt
injection chain). `tests/ux/test_demo.py` parametrizes over both pairs. The
same pass wired the existing `assets/brand/banner.txt` into the CLI: it now
renders on `lattence --version` and at the top of `lattence tui`'s pending
scaffold output, force-included into the wheel at `lattence/assets/banner.txt`
the same way the report schema is bundled. It also fixed a gap where `attack`
accepted `--no-color` but never used it: `attack` output now colors
`VULNERABLE` lines with the `fail` token, the same way `scan` colors severity
words, matching "color is never the only signal, but a signal all the same"
in `BUILD/DESIGN.md`. The HTML report and terminal severity colors were
checked against the frozen tokens directly and already matched; no change
was needed there.

Note for a future session, corrected after hitting this directly during
T-047: the wheel's force-included packages (`lattence_ai`, `lattence_crypto`,
and the `lattence.discovery` / `lattence.graph` / `lattence.evidence` /
`lattence.mcp` subpackages, added in T-045) install as physical directories
in the shared `.venv`, alongside the same packages' own editable workspace
installs, both under the same import names. This is not merely cosmetic:
`uv run` only rebuilds the root `lattence` wheel when files inside its own
declared package tree (`lattence-cli/src/lattence`) change. Editing
`lattence-ai`, `lattence-core`, `lattence-crypto`, `lattence-evidence`, or
`lattence-mcp` source and then running `uv run pytest` or `uv run python`
can silently import the stale physical copy bundled at the last root-wheel
build, not the edit. Force a rebuild after such edits with
`uv sync --all-packages --dev --reinstall-package lattence` before trusting
a test run. This does not affect CI: every CI job starts from a fresh
checkout, so its one `uv sync` builds everything from the same current
source with nothing stale to shadow it. Revisit the packaging split if this
keeps costing local iteration time.

T-077 added a dense flagship crypto view with explicit graph, ML-KEM and
ML-DSA migration, hybrid TLS, five-component agility, downgrade, and finding
sections. Plain mode contains no terminal escapes; color mode uses the frozen
status and heading tokens without making color the only signal.

T-078 added two accessible 1200 by 680 SVG diagrams under
`docs/architecture/`: the offline crypto assurance pipeline and the bounded
crypto chaos safety boundary. Both use the frozen palette, plain geometric
shapes, embedded titles and descriptions, and no generator metadata.

T-084 replaces the ambiguous crypto terminal metric with separate isolated
vulnerable asset and traversable path counts. The HTML report exposes the same
two metrics.

T-086 makes the shared crypto renderer require its invoking command name.
`pqc assess` and `crypto chaos` now retain their distinct identities in the
terminal heading instead of both being labeled `crypto`.

T-094 establishes the version 1 visual grammar consumed by both v0.5 surfaces.
It contains the frozen palette, twelve navigation labels, spacing and type
scales, 32-pixel row geometry, valid state words, dense table capabilities,
and right-side detail behavior. The dashboard CSS maps every token without
gradients or shadows. Python and dependency-free JavaScript tests enforce the
same canonical JSON manifest.

T-095 implements the TUI presentation shell with Rich layouts driven by the
shared grammar manifest. The fixed twelve-section rail, dense tables, selected
row state, right-side detail panel, and help footer render without escape
sequences in plain mode. Tab or arrow navigation, j/k row movement, Enter,
Escape, help, and quit actions reduce through a deterministic state model.

T-096 implements the browser dashboard shell over the same grammar. It has the
fixed twelve-section rail, 32-pixel table rows, a sticky sortable header,
filtering, saved view state, keyboard row movement, virtual row selection, JSON
copy and export actions, and a right-side detail panel. The shell loads a
`presentation.json` document and renders an explicit empty state when none is
available.

T-097 makes cross-layer chains interactive in both surfaces. The TUI detail
panel shows every edge type, stored direction, traversal direction, node pair,
and evidence reference, with bracket keys selecting a hop. The dashboard path
panel exposes the same hop sequence, supports pointer selection and horizontal
arrow selection, and places the selected hop beside the full chain evidence.

T-099 adds the cross-layer chain source and rendered SVG. The diagram labels
the AI finding, affected dataset, tool, concrete X25519 asset, stored edge
directions, traversal directions, and evidence files. It uses only frozen
colors and plain geometry. The new `tui.tape` and sub-2 MB GIF record the real
offline example, and `make demos` renders all three committed demonstrations.
TUI rendering now writes once to standard output and fits its default shell in
the fixed recording viewport.
