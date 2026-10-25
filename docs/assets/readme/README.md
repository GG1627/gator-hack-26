# README media

These assets support the repository's main README. They are committed, relative
files, so the product overview does not depend on an external image host.

| Asset | Purpose and source |
|---|---|
| `hero.png` | Peekaboo branding using the existing capybara scientist from `apps/web/public/peekaboo/solution-capybara.png`, the product's amber/charcoal palette, and Manrope. The mascot is generated brand artwork, not microscopy evidence. |
| `demo.gif` | An actual browser recording of the default lower-capture replay: seed 304, visible precursors, adaptive 32 / fixed 40. Extracted from `video/public/recordings/demo-304.mp4`, source seconds 3–25. Original playback speed, 22 seconds, 8 FPS, 1000 × 562, 128-color GIF. No UI states or scores were generated for this animation. |
| `comparison.png` | Fresh application capture at source frame 195, acquired-pixel view, with past-only division markers enabled. The panels show each method's own latest acquisition; these are not simultaneous ground-truth frames. |
| `results.png` | The same featured comparison after replay completion, showing the saved run metrics and their assumptions. |
| `cuda-rust.png` | Fresh capture of the actual compute slide with tile 6 selected. The Gaussian input diagram is explanatory; the intensity panel is saved native renderer output. The 12.7× statistic has its own dense-workload scope. |
| `architecture.svg` | Repository-authored explanatory diagram. It describes data access and execution responsibilities; it is not an experimental result or a screenshot. |

The still captures use a 1600 × 1000 Chromium viewport and the actual application
at source revision `9043f13a1fefb49db3595c7ba363c5610bb0c5d5`. They preserve existing
scientific labels. `capture.json` records the capture time, states, and browser
errors; `manifest.json` records file hashes and the source recording hash.

The capybara illustration and local Manrope font already form the application
identity. Font and library notices are in `apps/web/public/third-party/`.
No publication figures or third-party microscopy images were copied into these
README screenshots. Real-data attribution remains in the root README and dataset audit.
