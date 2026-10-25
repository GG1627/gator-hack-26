# Peekaboo — submission film implementation plan

Planning revision: October 25, 2026. Target: **under 3:00, 1920 × 1080, 30 fps**.
Status: narrated preview implemented; human listening review and final export remain pending.
Update: the full narrated preview and actual app recordings are now implemented in
`src/film/Film.tsx` / `Peekaboo-Submission`. Current runtime is 178.27 seconds with
user-selected Ashley, a conversational continuous take, padded/preloaded audio,
provider-timed subtitles, generated effects and licensed Mixkit music. A sourced
PhotoFiTT statistic now anchors the cost-of-looking scene. The current script and
actual timing in film-plan.json supersede the original allocations below. Human
listening/caption review and final export/mix analysis remain pending.
The user's complete replacement script is in `NARRATION.md` / `narration-v3.json`.
The user-approved opening is now one direct hook and a connected explanation of
imaging light and cellular damage. The remaining nine scene recordings preserve
the full replacement script and original audio exactly (SHA-256 checked).
Ashley delivery uses speed 1.06, split at provider-aligned scene pauses with PCM padding.
The edit uses 5348 frames, with no post-production speech time stretching. The
opening now follows problem, published result, question and product reveal; a
mission card leads into the final brand. The full 22-second recorded comparison
and the actual CUDA tile interaction remain visible. Original scene allocations
below are planning history; `film-plan.json` governs the current edit.
The approved ten-second style study remains a separate composition. This document
supersedes the initial storyboard in PRODUCTION_PLAN.md; retain that file as setup history.
Narration and frame boundaries live in [film-plan.json](film-plan.json).

## 1. The film's job

Make a judge understand and remember this: **Peekaboo chooses when to take the next
microscopy image. Our controlled experiment demonstrates useful timing with fewer
captures, and recent cuTile Rust tooling performs actual Gaussian model rendering.**

The experience should feel like a carefully demonstrated research instrument:
confident, curious, precise, visually spacious. The product is the protagonist.
Beautiful motion earns its time by explaining something. No prolonged logo sequence,
generic AI imagery, decorative code rain, fictional microscope feed or rapid feature tour.

The user confirmed the model switch for this planning pass and supplied the challenge:
use a technology/resource first publicly available within the preceding twelve months,
make it central, show what it does, explain difficulties and substantiate recency.
The user subsequently asked to omit the word synthetic from narration. The script
uses **controlled experiment**; retain the app's existing data labels and accessible
evidence disclosures. Do not relabel these results as real microscopy or hide their
provenance through cropping. No extra spoken real/synthetic classification is needed
for the featured comparison. Its selected-example scope remains spoken.

### Challenge coverage

| Judge's question | Answer in the film | Evidence |
|---|---|---|
| Why does this matter? | 0–13s: observing living cells costs light; timing matters | Existing problem/research sources in docs/DEMO_PREP.md |
| Does it work? | 13–48s: continuous actual app replay and measured result | Saved seed 304 acquisition/evaluation ledgers |
| What is new? | 76–94s: cuTile Rust, initial tagged release April 7, 2026 | Upstream changelog; dated NVIDIA announcement |
| Is the new technology central? | Gaussian parameters → our native Rust kernel → actual saved model image | crates/photon-gpu/src/main.rs; native export verification |
| What did you build with it? | Kernel and CPU reference; scientific model imagery, not just browser effects | GPU source, bridge, model assets, latency audit |
| What was difficult? | 108–120s: numerical agreement and repeated initialization costs | Existing parity tests, persistent worker audit, CPU fallback |
| What have you learned? | 120–134s: missing warning cues and real-data limitations | Controlled adverse cohort; completed Phase 5 evaluation |

Central does not mean irreplaceable. A CPU reference exists deliberately. Do not say
CUDA chooses captures, that the controller needs GPU outputs to decide, or that the
browser runs CUDA live. Explain a concrete contribution in the actual pipeline.
CellSplat4D is supporting research inspiration; do not rest eligibility solely on
the paper, generic Gaussian splatting, or an older dataset.

### Dated evidence and event requirements

- [cuTile Rust changelog](https://github.com/NVlabs/cutile-rs/blob/main/CHANGELOG.md)
  records an initial tagged release on April 7, 2026. This is release evidence,
  not by itself proof there was no earlier public code. Before final submission,
  preserve a pinned upstream revision and check earliest public history/release
  evidence against the challenge window. Never convert the September announcement
  into a claim of first public availability. If older public availability is found,
  reassess eligibility wording rather than conceal it.
- [NVIDIA announcement](https://developer.nvidia.com/blog/introducing-cuda-rust-two-tracks-for-writing-gpu-kernels/)
  is dated September 8, 2026. Show it as announcement context, distinct from release.
- [CellSplat4D v1](https://arxiv.org/abs/2610.04199v1) was submitted October 3, 2026.
  Our simplified model is inspired by it, not a reproduction of its full pipeline.
- [Event requirements](https://gatorhack2026.devpost.com/) checked October 25:
  maximum video duration three minutes. Our 142-second target leaves ample margin.
  [Rules](https://gatorhack2026.devpost.com/rules) describe offline shortlisting.
  Treat the user's challenge text as an additional requirement; the public overview
  does not replace it. Recheck submission UI/hosting requirements before upload.

## 2. Editorial structure and exact shot plan

All frame intervals below are **start-inclusive/end-exclusive**, totaling 4,260 frames.
These are editorial allocations, not measured speech timestamps. Cut around actual
approved speech within 120–150 seconds; never accelerate narration to force a fit.
Use named scenes with explicit Sequence positions. Base edit has no overlapping
durations. For a dissolve, provide clip handles and overlay within these allocations;
do not subtract transition duration a second time from the master timeline.

| Scene / frames / time | Picture, focus and movement | Sound and exit |
|---|---|---|
| Hook / 0–150 / 0–5s | Adapt the approved charcoal optical study. One soft amber signal, one large question. Text readable by 0.6s. No metrics. Conceptual label. A single signal becoming visible is the focal point. | Narrator enters by 0.3s. Quiet air, no dramatic boom. Leave a short pause after “look.” Signal contracts into the next scene's optical mark. |
| Premise / 150–390 / 5–13s | 5–9s: one illumination pulse and plain sentence about observation cost. 9–13s: butter Peekaboo reveal with small mascot; product definition replaces the question. Reveal lasts four seconds, not ten. | Music gains warmth on the name. Soft reveal cue only if licensed. Cut cleanly to actual app at 13s. |
| Demo / 390–1050 / 13–35s | Full comparison, matching panel scales, same timeline, actual Play interaction. Slot includes setup hold, full continuous replay and result arrival; measure actual recording duration. Fixed stays left; Peekaboo stays right. Keep labels/counters visible. Editorial captions appear only in unused space. No moving camera while judging capture behavior. | Narration introduces fixed, then adaptive, then leaves space to watch. Align the final invitation before source frame 140, not after divisions have passed. At most one quiet capture accent near a genuine acquisition; no audio on every tick. Exit on actual results opening. |
| Result / 1050–1440 / 35–48s | 35–39s recorded results; 39–44s isolate **32 vs 40 images**, with **4/4 vs 1/4 covered** beside it; 44–48s emphasize **20% fewer exposures**. An editorial statistic card may enlarge the exact recorded values. Retain selected-example and equal-light scope. | Music lifts slightly after the numbers, not over them. Hold the completed card at least three seconds. No rolling counters that show invented intermediate outcomes. |
| Causality / 1440–1860 / 48–62s | New two-lane acquired/hidden diagram. 48–52s an acquired frame enters; 52–57s CPU shape estimate and next-capture decision; 57–62s hidden frames remain behind a labeled boundary. Arrow returns only when capture happens. “Only acquired images guide decisions.” Conceptual label. | Three restrained steps, primarily visual. No scary lock/error sounds. Exit with one acquired nucleus as the next focal point. |
| Gaussians / 1860–2280 / 62–76s | 62–67s recorded model controls and acquired/fit pair. 67–72s clean Gaussian explanation: position, brightness, shape revealed one at a time. 72–76s shape elongation beside shorter target gaps. Small CellSplat4D inspiration/date citation. Explicitly conceptual explanatory surface; actual saved fit is separately labeled. | Gentle spatial movement, no continuous spinning. Native/source imagery remains still enough to inspect. Transition using the same Gaussian parameters into compute. |
| Frontier / 2280–2820 / 76–94s | 76–81s **cuTile Rust · initial tagged release 7 Apr 2026**, with source. 81–89s parameters → native Rust tile calculation → actual model image; show a short authentic kernel excerpt as supporting texture. 89–94s recorded compute slide tile selection. CPU and GPU responsibilities remain visible. | Clear pronunciation and a small pause around the tool's name. Introduce a subtle rhythmic layer. End on the actual image, not a logo wall. |
| Benchmark / 2820–3240 / 94–108s | 94–98s workload establishes scope: 10,000 Gaussians, 64×64. 98–104s bars from zero show CPU 2,914ms / GPU 230ms, then 12.7×. 104–108s hold. Warm full rendering call / startup excluded visible throughout result. No animation implying real-time benchmark execution. | Narrator states component scope. A quiet landing on the ratio; no rising casino count sound. All numbers are read from the evidence snapshot. |
| Difficulty / 3240–3600 / 108–120s | 108–114s actual CPU/GPU parity evidence and the real acquired/fit output, with concise label “Checked against CPU reference.” 114–120s conceptual one-start / repeated-render worker diagram. Small “CPU fallback retained” line. No wall of terminal text. | Simplify rhythm so the explanation lands. Describe engineering work without pretending it created a universal speedup. Cut directly to boundaries of the method. |
| Limits / 3600–4020 / 120–134s | 120–126s recorded sudden-division case or cohort disclosure, with clear missed-event outcome. 126–134s restrained evidence card: “Separate real-microscopy evaluation: no division-coverage improvement over fixed.” If authentic real image is used, label it and cite its dataset; never use it under the earlier winning numbers. | Music thins, not a failure alarm. Measured, confident delivery. No tiny rapidly flashed disclaimer. Exit toward the next research step. |
| Close / 4020–4260 / 134–142s | Butter brand return, mascot, **See more. Illuminate less.** Small “Next: microscope validation.” Repository address / source access secondary and verified before export. Final two seconds are a calm hold. | Narration ends before final visual fade. Music resolves with tail; finish without a hard audio cut. |

### Readable hierarchy

Use the local Manrope and existing charcoal/butter/amber/blue palette from the
approved study. At 1080p: headline 80–112px, main explanations 44–56px, essential
qualifiers 30–36px, source identifiers at least 24px. One main claim, at most two
supporting groups per screen. Keep 80px side margins and a subtitle-safe bottom
region of approximately 150px. Do not place critical source labels under subtitles.

Keep amber/blue method assignment consistent with the app. Never encode coverage
only by color: include labels or shapes. Avoid full-screen flashes and continuous
background motion behind data. Decorative movement generally 12–24 frames; deliberate
content holds 60–120 frames or longer. Optical diagrams may move slowly. No bouncy
overshoot on evidence. Cuts carry most transitions; reserve fades/matches for meaning.

At phone preview size, essential comparison must remain legible. Use editorial
insets of the original recording when necessary, preserving an overview and labels.
Do not redraw a simplified fake UI and call it a screen recording.

## 3. Narration and delivery contract

The complete editable script is [film-plan.json](film-plan.json), one passage per
scene. About 300 written words; spoken numbers and technical names expand timing.
Most scenes allocate 120–150 written words/minute, with breathing room in hook,
demo and ending. The premise is tight: if the actual take sounds rushed, shorten
it to “Observing living cells costs light. Peekaboo chooses when to take the next image.”

Delivery: thoughtful researcher showing something interesting to a colleague.
Warm curiosity in the opening; observational clarity during the demo; confidence
without triumphalism on results. No sales voice, trailer rumble or rushed caveats.
Pronunciations to approve by listening: Peekaboo “peek-a-boo”; CUDA “coo-duh”;
cuTile “cue-tile”; Gaussian “GOW-see-un”; CellSplat4D “cell splat four dee.”
Use phonetic aliases only in TTS input, retaining correct spelling in captions.

Recommended voice remains Eric, premade ID `cjVigY5qzO86Huf0OWal`; alternate Matilda,
`XrExE9yKIg1WjnnlVkGX`. This is a metadata-based selection, not a completed audition.
Listen to existing provider previews first. User-recorded narration is a valid final
choice and a strong fallback if generation rights remain unresolved.

Read the whole script aloud against the timeline before generation. First timed
scratch take may be local human audio or silent timed text. Make scene edits before
polishing audio. Avoid separate generated clauses: produce scene-length passages
with consistent settings and enough leading/trailing handles for clean cuts.

## 4. Claim and evidence contract

| Claim | Exact source / scope | Must stay with it |
|---|---|---|
| 32 vs 40; 4/4 vs 1/4 | apps/web/public/demo/controlled/budget32/{manifest,evidence}.json; key 304-precursor | Selected controlled example; 240 source frames; coverage within ±1 source frame |
| 20% fewer exposures | 1 − 32/40 | Equal illumination per image required for the light interpretation; no measured health benefit |
| Controller responds to shape | experiments/controlled/event_focus.py; saved decisions | Heuristic acquired-image shape cues; declared budget; not calibrated biological prediction |
| Model view | Saved observed/model assets and export metadata | Latest acquired-image fit held between captures; never call it a predicted unseen division |
| Native GPU contribution | crates/photon-gpu/src/main.rs; services/science/photon/gpu.py; export verification | CPU fits/decides; GPU renders; browser replays saved output |
| 12.7× | runs/cuda-latency-audit/matrix/latency.json; docs/cuda-latency-audit.md | 10,000 synthetic Gaussians, 64×64, warmed persistent full rendering call, 15-sample medians, startup excluded; not kernel-only or app speedup |
| CPU/GPU agreement | Export verification and docs/DEMO_PREP.md | Sampled export maximum absolute error 1.1920928955078125e-7 below 2e-6; do not transfer this error to a different benchmark |
| Limits | docs/DEMO_PREP.md; controlled cohort evidence; Phase 5 artifacts | Abrupt events can be missed; older frozen real-data controller differs from newer controlled controller |

Do not overload the main film with every cohort table. The script states the featured
selection and the limitation; the result card may add “All six seeds available in
evidence.” Full 23/24 vs 11/24 precursor and 4/24 vs 11/24 abrupt results remain
accessible through the app/repository. Do not blend equal-budget and lower-budget
cohorts, or claim that 32 was automatically discovered as the minimum budget.

Create a video-local evidence snapshot with source paths, source hashes, run key,
method keys, exact values and displayed rounding. This is read-only extraction,
not a new benchmark. Keep generated snapshots reproducible; do not hand-edit results.
The verification script must reject missing inputs rather than silently invent a value.

## 5. Recording and asset production

See [CAPTURE_PLAN.md](CAPTURE_PLAN.md) for exact app states and takes. Record actual
interactions at 1920×1080, 30fps, browser viewport fixed, 100% zoom, no developer
panels or personal tabs. App entry is / with hash navigation; verify whichever local
port is actually running. Keep complete master takes and trim copies only in Remotion.

Each take gets an ID, source filename, duration, source in/out frames, frame-rate
metadata, app revision and content notes in a media manifest. Source timecodes
remain null until captured; source experiment frames are a different clock. No
invented media filenames may pass a final render preflight.

### Purposeful new components

| Component | What it explains | Inputs / fallback |
|---|---|---|
| AcquisitionBoundary | Past observations vs hidden future, and capture decision order | Conceptual states; no numerical outcome; replace with three static stages if necessary |
| GaussianExplainer | Position/brightness/shape and observed elongation cue | Analytic SVG surface plus separately labeled actual fit; reuse app recording if time is tight |
| NativeRenderFlow | Where cuTile Rust is actually used | Read-only parameter/sample/output assets and real kernel excerpt; CPU and GPU lanes |
| BenchmarkCard | Workload-scoped renderer benefit | Evidence snapshot; exact labeled bars; no fake stopwatch |
| ResultFocus | Readable selected comparison on small screens | Exact recorded result values, scope, no invented UI interactions |
| EvidenceBoundary | Honest limit and next validation step | Actual adverse case and real-data conclusion; static card is sufficient |

Use SVG/React/frame-driven motion for these. No new Three.js/GSAP dependency is
justified by this plan. No generated biological imagery is necessary. Existing
mascot and font are available; no new image generation is on the critical path.

## 6. Isolated Remotion implementation map

All implementation remains under video/. Root app/backend packages and scientific
architecture are unchanged. BUILD_PHASES.md receives progress records only.

Planned files (not yet implemented):

```text
src/film/Film.tsx                explicit authored scenes, master audio and edit positions
src/film/timing.ts               validated frame boundaries derived from film-plan.json
src/film/theme.ts                approved visual tokens and safe areas
src/film/scenes/                 Hook, Premise, Demo, Result, Causality, Gaussians,
                                Frontier, Benchmark, Difficulty, Limits, Close
src/film/components/             explanatory components listed above; SourceNote
src/film/evidence.json           reproducible local snapshot, no raw microscopy data
src/film/media-manifest.json     real source files, trims, hashes, licenses, cue positions
scripts/collect-film-evidence.mjs read-only extraction and verification
scripts/check-film.mjs           metadata, missing-media, timings, provenance checks
public/recordings/               ignored masters and selected recordings
public/audio/generated/         ignored narration/effects
public/audio/licensed/          local licensed music, ignored if large
public/captions/                 corrected source-relative captions
```

Register `Peekaboo-Submission` separately in Root.tsx; keep `Peekaboo-StyleStudy`
available unchanged. Reuse RecordedClip, Soundtrack, local font loading, audio
envelopes and caption tooling after checking their actual contracts. Give each
independently edited scene/clip an explicit JSX node. Share visual primitives,
not a generic scene template that forces every shot into the same layout.

Composition props: caption visibility, draft overlays, music enabled, preview scene.
Do not expose arbitrary overrides for scientific metric values. Draft missing-media
slates are allowed in Studio, visibly marked; final preflight rejects them.

## 7. Audio workflow and budget

No generation calls are authorized by this plan. The earlier read-only account
check reported free tier with 10,000 credits/characters allowance and none used;
recheck before a request because availability and billing conversion can change.
Existing generation scripts default to dry-run. The key was found in root .env;
video scripts load video/.env. Configure the ignored local file without printing,
committing or copying secrets into any public asset or report.

1. Listen to existing voice previews. Resolve publication rights for the intended
   submission before generating final assets. Follow the provider's current terms;
   do not assume upgrading retroactively licenses free-tier generations. Prior
   sources and constraints are recorded in PLANNING_HANDOFF.md.
2. Lock script after a timed read. Compute actual request character counts and
   provider credit estimate before each request. Reserve approximately 60% of the
   available allowance for the final pass, 20% for corrections, 20% unspent. These
   are spending caps, not an assertion that all models/effects cost one credit per
   character. If final text exceeds its cap, reduce retries or use human narration.
3. If explicitly authorized, audition one 15–20s excerpt containing brand, cuTile
   and a number; not the full script in two voices. Select one voice, settings and
   output format. Generate scene takes once; regenerate only a faulty scene.
4. Prefer one properly licensed instrumental track, approximately 145–155s with a
   clear ending: restrained ambient pulse, warm harmonic development, no vocals.
   Music is a missing asset. No paid search/purchase/generation without authorization.
   Store source, author, exact license/receipt and permitted use in ASSETS.md.
5. Use at most three families of sounds: optical reveal, quiet acquisition tick,
   soft transition. They are optional. License existing assets or make bounded
   ElevenLabs requests after authorization and cost check. Missing SFX should be
   silence, never a fake generated asset claim. Avoid spending narration credits
   on decorative effects before the voice is secure.
6. Normalize source narration with bundled FFmpeg, align scene boundaries, then
   transcribe actual audio with local Whisper. Proofread scientific terms/numbers.
   Keep timestamps relative to the source; trim speech/captions together. Export
   plain SRT as well as styled subtitles if useful for hosting.
7. Narration owns the mix. Start music roughly 18–24dB below voice perceptually,
   then listen and adjust; existing duck envelope is a starting point, not a
   guarantee. Subtle SFX below speech. Use clip fades and musical cut points;
   preserve room/tail continuity between takes. No time-stretching to hide bad pacing.
8. Measure the encoded final mix: target −16 LUFS integrated, at most −1.5dBTP,
   48kHz. Re-analyze after final normalization/encoding. Test laptop, headphones,
   mono and quiet playback. Document actual measurements; Remotion gain is no limiter.

Captions: one or two lines, sentence/phrase groups, approximately 42–48px with
high-contrast backing; gentle 4–6-frame entrance, no word-by-word bouncing. Do not
duplicate giant titles unnecessarily. Preview with captions on and off. Ambient
music and SFX must not mask division explanation or the scope of benchmark numbers.

## 8. Build order and review gates

| Milestone | Concrete deliverable | Pass condition |
|---|---|---|
| A: Evidence and script | Extract verified values, retain dated technology sources, timed script read | Every spoken/on-screen claim has scope/source; earliest-public-history check recorded; no voice rushing |
| B: Record | Complete app masters and media manifest | Correct states, no loading/errors, exact source clocks, real interactions, enough handles |
| C: Full rough cut | All eleven scenes in Studio, actual footage, draft graphics and scratch audio/text | Complete 120–150s story; product by 13s; full demo legible; no missing segment hidden by polish |
| D: Visual finish | Purposeful diagrams, optical continuity, result/benchmark cards | Phone-sized readability, single focal point, no mislabeled data or fake behavior |
| E: Voice and sound | Approved narrator, music rights, sparse effects, corrected captions | Rights/cost resolved, speech fits naturally, subtitles synchronized, balanced mix |
| F: Submission finish | Export when requested, metadata/report, playback and hosting check | Correct duration/resolution/fps, audio verified, all assets resolved, no debug slates, link accessible |

Use short scene previews and contact sheets during construction. Check the first
five seconds, demo, result and compute segment before detailing minor transitions.
After each material edit run video lint/typecheck and relevant existing tests.
Add meaningful checks for contiguous timeline, source trims, evidence consistency,
missing final assets and caption boundaries; do not create tests that merely mirror CSS.
Production bundle after integration. No application test rerun is needed when its
code/assets/dependencies have not changed.

### Human review

- Show the first 20 seconds silently to an unfamiliar viewer: can they identify
  what the software changes and distinguish the two methods?
- After the full cut: can they name the recent tool, describe what it computes,
  explain the result, and recall one limit? If not, simplify before adding visuals.
- Review at 1920×1080 and approximately 640×360. Essential scope cannot require pause.
- Audit frame-level transitions for text collisions, missing imagery and caption cuts.
- Inspect recordings for accidental future labels, changed settings, hidden jumps
  or misleading crop. Our editorial observations do not become controller inputs.
- Watch the final encoded file start-to-finish and test an offline copy. Verify the
  hosted link in a signed-out context; inspect thumbnail and title. Publishing remains
  a separate action from local preparation.

### Scope control

If time is tight, retain the uninterrupted demo, result, recent-tool contribution,
benchmark scope, one honest limitation and a clean ending. Replace custom motion
with beautifully typeset static diagrams before cutting evidence. Drop extra SFX,
secondary code shots and decorative 3D first. Preserve the established 2–2.5-minute
target rather than expanding to the event's three-minute maximum.

## 9. Current handoff

Plan and script complete for implementation review; actual recorded media, voice,
music and full film remain pending. No credit-consuming call was made during planning.
No new scientific experiment or application behavior was introduced. The next concrete
step is evidence extraction and actual app capture, followed immediately by a full
rough cut. GPT-6.1 Sol Medium is sufficient for implementing this reviewed plan;
the user controls whether and when to switch back.
