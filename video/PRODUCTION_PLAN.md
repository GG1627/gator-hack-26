# Peekaboo film — production setup

> Updated planning: [IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md) supersedes the
> draft storyboard below. The current 142-second edit and full narration are in
> [film-plan.json](film-plan.json); actual recording instructions are in
> [CAPTURE_PLAN.md](CAPTURE_PLAN.md). This file preserves the setup checkpoint.

Target: **2–2.5 minutes**, 1920×1080, 30 fps. Working storyboard: 135 seconds.
This checkpoint builds only a 10-second style study, not the final film.

## Product and evidence

Peekaboo is the presentation identity of PHOTON: an offline, causal microscopy
acquisition controller, not a connected microscope. The controlled demo fits
acquired Gaussian shapes on CPU and selects target gaps of 12/4/2 frames subject
to budget/gap guards. A real native cuTile Rust kernel renders Gaussian intensity;
the browser replays saved outputs. Research inspiration is not paper reproduction.

Primary evidence: `../docs/DEMO_PREP.md`, `../docs/LOWER_CAPTURE_DEMO.md`,
`../docs/cuda-latency-audit.md`, `../PHOTON_SPEC.md`, and saved demo ledgers.
Featured synthetic seed 304: 32 versus 40 images; 4/4 versus 1/4 divisions covered
within ±1 frame. The example was selected after evaluation; retain that disclosure.
20% fewer images implies 20% less estimated imaging light only under equal light
per capture. Cell health and reduced phototoxicity have not been demonstrated.
Show a short abrupt-division failure: adaptive does not always win.
12.7× is dense warmed full rendering-call speed, 10,000 synthetic Gaussians,
64×64, 2,914 versus 230 ms, startup excluded; not a scheduler/application speedup.

## Creative direction

Premium product launch with research clarity. Match existing charcoal, butter,
amber and blue identity; use the locally bundled Manrope font. One idea per shot.
Large type, slow purposeful reveals, restrained optical motifs, brief fades rather
than constant transitions. Existing capybara is a signature reveal, not an overlay
competing with the demo. Real screen recordings get a small “Recorded app” label.
Scientific explanatory motion gets “Conceptual visualization”. Preserve native
specimen geometry; never generate microscopy evidence. No fake cursors or clicks.

The 10-second study tests optical Gaussian motion → typographic reveal. It is
explicitly conceptual, silent, and contains no experimental result or app recording.
Review the Studio preview before developing the remaining scenes.

## Storyboard (draft timing, not a locked narration edit)

| Time | Viewer takeaway / picture | Narration direction | Audio cue / source needed |
|---|---|---|---|
| 0–5 | A fleeting moment worth seeing; abstract signal emerges in darkness | “What if a microscope knew when to look?” | Quiet atmosphere; one gentle optical tick |
| 5–15 | Peekaboo. See more. Illuminate less. Signature mascot reveal | Introduce software choosing when to acquire | Warm musical arrival; existing transparent mascot |
| 15–29 | Too frequent / too sparse; actual problem slide recording | Light exposure and missed divisions trade off | Narrator leads; music recedes |
| 29–42 | Observe → estimate → decide, clearly conceptual | Only acquired images guide the next observation | Three soft cues, no continuous UI bleeps |
| 42–76 | Main recorded demo: shared clock, stable wait, shape change, capture burst | Explain held images versus new exposures | Keep real interactions uninterrupted; one subtle capture accent |
| 76–91 | Recorded result reveal, selected seed 304 | 32/40 captures; 4/4 vs 1/4, qualified selected synthetic run | Brief musical lift then space for the numbers |
| 91–105 | Recorded Gaussian controls + model fit | Compact position, shape, brightness; measured shape change | Light texture, no trailer impact |
| 105–120 | Recorded CUDA tile interaction + separate benchmark typography | Rust kernel, CPU scheduler; dense warm 12.7× rendering-call result | Precise, restrained technical rhythm |
| 120–129 | Abrupt division failure + evidence access | No precursor means missed moments; synthetic proof is bounded | Music simplifies; leave narration intelligible |
| 129–135 | Peekaboo / See more. Illuminate less. | End on the product and research direction | Resolve and fade naturally |

## Assets still needed

- Real 1080p application recordings: problem, full default demo, result reveal,
  Gaussian controls, CUDA tile selection, abrupt failure. Record at a shared source
  clock; keep holds/predictions labeled. Filename/location: `public/recordings/`.
- Approved narrator voice ID and delivery. No ElevenLabs key or voice ID was found
  in the current environment or video .env at setup; no provider plugin was found.
  Supply secrets locally in ignored `.env`, not in chat or public assets.
- Approved script, then per-scene generated/recorded narration. No fabricated audio
  files or estimated word timings will be described as transcription.
- Licensed instrumental music with a gentle build, ideally stems. Record author,
  source URL, license/receipt and attribution in `public/ASSETS.md` before use.
- Approved generated SFX: airy reveal, gentle capture tick, soft transition. Scripts
  are dry-run by default and require explicit per-request paid-call opt-in.
- Whisper captions derived from actual recorded narration and manually corrected
  for Peekaboo, cuTile, CUDA and scientific terms.

## Integration choices

- Official Remotion skills already installed locally in `.agents/skills/` and
  pinned in `skills-lock.json`; preserve them. They become available automatically
  to compatible agents on the next turn. No global install necessary.
- Pin all added Remotion packages to the existing **4.0.538**. Transitions, media,
  captions and local fonts are useful immediately. Remotion remains the renderer.
- Use frame-driven `interpolate`/spring animation. GSAP is supported officially,
  but adds no benefit to this proof; defer it until a shot needs an editable GSAP
  timeline. Defer `@remotion/three` until a meaningful scientific 3D shot is approved;
  do not install it for background decoration. No HyperFrames.
- Use local Whisper.cpp for offline transcription. Windows uses supported 1.6.0
  binary + base.en, configured separately from the app; no CMake changes. The
  official skills also offer WebGPU Whisper for later GPU transcription, but the
  smaller CPU workflow avoids an additional inference stack at setup.
- FFmpeg is already bundled with Remotion. Use it only for audio conversion,
  two-pass loudness normalization and final mix analysis; do not install a second
  renderer or global FFmpeg. No paid service is needed for local transcription.

## Audio finish and quality gates

Use `audio-production.json` for scripts, voice settings and SFX prompts. Put
prepared tracks into `src/media.ts` with source-relative captions and frame cues.
Narration should sound conversational, with pauses around technical claims.
Music gets a smooth attack/release duck under every narration interval. Apply
short fades to every asset; leave final tails intact. Do not time-stretch narration
to match an arbitrary storyboard duration; recut around approved speech.

Normalize narration and final mix with the supplied two-pass script; working final
target **−16 LUFS integrated / −1.5 dBTP**, 48 kHz. These are production targets,
not measured output. Inspect loudness report and listen on headphones and laptop
speakers before claiming the mix is finished. Remotion volume is not a limiter.
Render through Remotion; if needed, normalize only the audio of the rendered MP4
with video stream copy. Final audio needs a fresh analysis, no clipping, clear
speech, no abrupt starts/ends and license/provenance review.

## Setup verification — 2026-10-25

Lint/TypeScript, five audio safety/envelope tests, doctor and the production bundle
passed. Five full-resolution frames (30/90/157/210/299) were generated and visually
reviewed; the transition was refined to avoid overlapping headlines. Studio loads
the 300-frame composition without page errors. The study remains silent.
Local Whisper.cpp/base.en installation, PCM conversion and caption JSON output
were exercised on a labeled, ignored test-tone fixture; this does not validate
speech accuracy. Two-pass normalization of that fixture measured −16.05 LUFS
integrated and −12.31 dBTP on re-analysis. Actual narration/music are still missing.
The video's Zod 4.6.6 override removed npm's advisories; Remotion still prints its
strict expected-version warning, documented in README. No app code was changed.

## Research links

- https://www.remotion.dev/docs/ai/skills
- https://www.remotion.dev/docs/transitions
- https://www.remotion.dev/docs/gsap/use-gsap-timeline
- https://www.remotion.dev/docs/install-whisper-cpp/install-whisper-cpp
- https://www.remotion.dev/docs/install-whisper-cpp/transcribe
- https://elevenlabs.io/docs/api-reference/text-to-speech/convert
- https://elevenlabs.io/docs/api-reference/text-to-sound-effects/convert
