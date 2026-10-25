# Peekaboo video workspace

Isolated Remotion 4.0.538 project. All commands below run **inside `video/`**.
No app/backend imports or root workspace dependencies. Node 24 was used for setup;
the scripts use Node's native env-file support.

```powershell
cd video
npm ci
npm run doctor
npm run dev -- --port=3001
```

Open [the narrated preview](http://localhost:3001/Peekaboo-Submission): **2:58.3,
1920×1080, 30fps**, eleven scenes, recorded app footage and explanatory graphics.
It includes **Ashley**, voice ID `bxiObU1YDrf7lrFAyV99`, generated on Starter.
The opening was revised as a connected take; the nine remaining scene recordings
are preserved from the original continuous narration. Scene excerpts are cut at paragraph
pauses, with 180ms silence on both ends and three-second preloading. Captions use
actual provider character timing. Soft scene fades, title/mascot motion, generated
effects and Mixkit's “Your Breath” by Eugenio Mininni are included. The separate
[10-second study](http://localhost:3001/Peekaboo-StyleStudy) remains available.
The current script, including the approved opening revisions, is in [NARRATION.md](NARRATION.md),
with editable text, voice settings and revision in [narration-v3.json](narration-v3.json).
Research, question, brand and closing reveals follow actual speech timing.
Read [IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md) and
[CAPTURE_PLAN.md](CAPTURE_PLAN.md) for the current production contract.

```powershell
npm run film:evidence   # re-extract checked source values; fails if evidence differs
npm run capture:app     # requires the app server; records actual browser interactions
npm run film:check      # footage format/trims, timeline and evidence hashes
npm run preview:film    # full-resolution stills only; no MP4 export
```

Capture tooling uses an existing local Playwright installation and Chromium.
Override `PLAYWRIGHT_MODULE`, `CHROME_PATH` and `APP_URL` for a different machine;
these tools are isolated from application dependencies. Source recordings are
ignored; `src/film/media-manifest.json` records hashes/trims and source revision.
Recreate or restore them before previewing from a fresh checkout. The main
composition lives in `src/film/Film.tsx`; draft-script and draft-overlay props are
editable in Studio. `film:check -- --final` intentionally rejects the current
preview until human voice/caption review and encoded final-mix analysis are complete.

The opening research card cites PhotoFiTT (Nature Communications, 2025): 80% fewer
mitotic events in the tested CHO population at 60 J/cm² near-UV exposure. This is
published motivation, separate from Peekaboo's capture-count results.

Current voice workflow:

```powershell
node scripts/generate-natural-take.mjs             # dry run
node scripts/generate-natural-take.mjs --check     # subscription/credits only
node scripts/generate-natural-take.mjs --allow-credits # explicit generation; reuses saved take
node scripts/generate-natural-take.mjs --reuse     # retime saved audio; zero API requests
node scripts/check-studio-audio.cjs               # browser playback/signal check
```

The current script is editable in `narration-v3.json`; `narration-v2.json` preserves
the previous version. Existing master audio is
preserved; changed text requires a new generation revision. This script never
upgrades subscriptions, enables overage or retries failed generation. Older Eric
scripts are retained for reproducibility; `generate-natural-take.mjs` is the current
Ashley workflow. Raw audio and music are ignored; keep local media when moving machines.

## Editing

- `src/Composition.tsx`: two named, individually editable scenes and a short fade.
- `src/Root.tsx`: composition metadata and editable tagline default prop.
- `src/media.ts`: approved voice, music and effect paths, start/duration in frames,
  gains, and source-relative `Caption[]`. Empty entries omit missing media.
- `src/Soundtrack.tsx`: smooth music ducking, clip fades and animated caption pages.
- `src/RecordedClip.tsx`: genuine video wrapper labeled Recorded app; shared parent
  trim keeps its transcript aligned. Do not add simulated UI as recorded footage.
- `public/ASSETS.md`: asset origin, licenses and missing material.

## ElevenLabs setup and individual asset tools

Copy `.env.example` to `.env` and fill it locally. Set `ELEVENLABS_API_KEY` and an
approved `ELEVENLABS_VOICE_ID`. Secrets are read only by Node scripts, never by
the composition/browser. Scripts, pacing and voice parameters live in
`audio-production.json`. Choose one request at a time; scripts never auto-retry.

```powershell
# Safe previews: no API call, even when credentials exist
npm run audio:generate -- narration hook
npm run audio:generate -- effect capture

# ONLY after approving the script, voice, account costs and usage rights:
npm run audio:generate -- narration hook --allow-paid
npm run audio:generate -- effect capture --allow-paid
```

Generated originals and provenance go to ignored `public/audio/generated/`.
Existing output files are never overwritten. No music is bundled; bring a licensed
instrumental/stems and record credits before adding it to `src/media.ts`.

## Audio preparation and captions

FFmpeg is the copy already bundled with Remotion; no global installation needed.
`FFMPEG_PATH` can override it. Paths are relative to `video/`, outputs must be new.

```powershell
# Convert/normalize actual approved narration, then run local Whisper
npm run audio:process -- normalize public/audio/generated/narration-hook.mp3 public/audio/generated/hook-mix.wav
npm run audio:process -- wav public/audio/generated/hook-mix.wav public/audio/generated/hook-whisper.wav
npm run whisper:setup
npm run captions -- public/audio/generated/hook-whisper.wav public/audio/generated/hook.captions.json
```

Whisper.cpp **1.6.0 + base.en** is installed locally on this machine. Fresh checkouts
need `whisper:setup` (free downloads, ~148 MB model plus binary). Output is Remotion
`Caption[]` with source-relative timestamps. Proofread against actual speech;
no guessed timing or fabricated transcript is included. For edits, put the caption
array on the same scene/trim boundary as its audio/video.

Music ducking is keyed to actual narration intervals. Use short clip fades, leave
room for effect tails, and adjust levels by listening; volume controls alone do
not guarantee a finished mix. Target final mix: −16 LUFS / true peak ≤−1.5 dBTP.

```powershell
# Explicit export only, when wanted; native Remotion renderer remains primary
npm run render:proof

# For an eventual film with real audio, finish audio without re-encoding video
npm run audio:process -- normalize out/film.mp4 out/film-master.mp4
npm run audio:process -- analyze out/film-master.mp4
```

Analyze the final encoded file and listen on headphones/laptop speakers. No final
professional mix is claimed until approved narration, music and effects exist.

## Checks and previews

```powershell
npm run lint
npm test
npm run doctor
npm run build
npm run preview:stills
```

`preview:stills` validates the composition metadata and saves five full-resolution
frames in ignored `.cache/stills/`. It uses Remotion's browser (may need a first-time
download), or an existing Chromium via `CHROME_PATH`. It does not export a video.
Generated renders, recordings, model files, audio and secrets remain ignored.
Official Remotion skills were already installed in `.agents/skills/` with their
lockfile; compatible agents discover them on their next turn.

Security setup: a local **Zod 4.6.6 override** patches the oversized-validation
advisory in Remotion's pinned 4.5.4 dependency. npm install's audit reported zero
vulnerabilities after the override. Remotion's strict version checker consequently
prints a Zod-version warning; lint/typecheck, Studio, bundle and still previews are
checked with the override. Do not apply a forced downgrade or silence the warning.
Revisit the override when upgrading the pinned Remotion family together.

Remotion licensing: [official terms](https://www.remotion.dev/license).
