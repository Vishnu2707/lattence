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
