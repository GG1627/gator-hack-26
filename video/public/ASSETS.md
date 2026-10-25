# Asset manifest

The full rough cut uses five actual application recordings captured October 25,
2026. Current preview audio uses Anya, three generated effect sources and licensed
Mixkit music. Earlier Eric/free-tier takes are unused alternatives.

| Asset | Origin | Permission / meaning |
|---|---|---|
| fonts/manrope.woff2 | Existing app @fontsource-variable/manrope | SIL Open Font License; bundled OFL.txt |
| brand/capybara.png | Existing app solution-capybara.png | Previously generated project illustration; decorative mascot, not specimen data |
| SVG signal study | Authored in src/Composition.tsx | Conceptual Gaussian drawing, not experimental data |
| recordings/demo-304.mp4 | Actual local app, saved seed 304 precursor run; recorded with Playwright | App/data labels retained; shared-clock accelerated replay, division annotations are evaluation-only |
| recordings/featured-result.mp4 | Actual app result reveal for the same saved run | Selected example; all-source provenance remains available |
| recordings/gaussian-controls.mp4 | Actual model slide and shape-control interaction | Conceptual control surface and separately labeled saved acquired-image fit |
| recordings/cuda-tiles.mp4 | Actual compute slide and tile selection | Illustrative tiling and saved native model output |
| recordings/abrupt-304.mp4 | Actual saved sudden-division result | Selected adverse example; adaptive 0/4 vs fixed 1/4 |
| Authored film diagrams | src/film/diagrams.tsx and scenes.tsx | Conceptual acquisition/model/compute explanations; benchmark and result values extracted from source artifacts |
| audio/generated/anya-natural-v1/ | ElevenLabs Anya, d3MFdIuCfbAIwiu7jC4a, multilingual v2, one continuous take | Generated after the user upgraded to Starter; exact script/settings/source alignment retained in master.response.json; normalized once, split at paragraph pauses, padded 180ms on both ends |
| audio/generated/sfx-preview-v2/ | ElevenLabs reveal, transition and capture prompts | Regenerated on Starter; sparse editorial accents, not recorded microscope sounds; generation report records tier and reported cost |
| audio/licensed/mixkit-your-breath.mp3, normalized WAV and preview M4A | “Your Breath” by Eugenio Mininni, Mixkit | Mixkit Stock Music Free License; https://mixkit.co/license/#musicFree ; source https://mixkit.co/free-stock-music/tag/technology/ ; download/hash/metadata in mixkit-your-breath.provenance.json; excerpt, fades, ducking and volume automation; 192kbps AAC preview reduces loading size |
| audio/licensed/cylinder-one.m4a | “Cylinder One” by Chris Zabriskie | Unused alternate; CC BY 4.0, requires attribution if used; https://chriszabriskie.com/cylinders/ and https://chriszabriskie.com/use/ |

Published research statistic: PhotoFiTT, Nature Communications (2025),
https://doi.org/10.1038/s41467-025-66209-6, supplementary Fig. S1a. The 80% decrease
refers to mitotic events in an unsynchronised CHO population at high-dose near-UV
exposure (60 J/cm²); it is not a Peekaboo measurement or a universal imaging effect.
No paper figure or third-party microscopy footage was copied for the new card.

Suggested music credit: “Your Breath” — Eugenio Mininni, via Mixkit.

Recorded MP4 sources are CFR 30fps, 1920×1080, prepared using the bundled FFmpeg.
Source file hashes, actual media durations, trims and capture timestamps are in
`src/film/media-manifest.json`. Recordings remain ignored to avoid large media in Git.

Generated audio goes under ignored `audio/generated/`; recordings go under ignored
`recordings/`. Record filenames, source, generation settings/date or license URL,
author, attribution, and receipts here when assets are approved. Keys never belong
in this directory. Missing files are omitted, never replaced with fake sound.
