# Full film planning brief — 2026-10-25

> Planning pass completed after the user confirmed switching models. See
> IMPLEMENTATION_PLAN.md, CAPTURE_PLAN.md and film-plan.json for the current
> deliverables. Historical pending instructions below are retained as context.
> The user asked to omit synthetic from spoken narration; the script says
> controlled experiment while preserving existing app labels and evidence scope.

The user approved the silent 10-second style study and wants an unusually strong
Devpost shortlisting video. Next deliverable: a detailed, executable production
plan, before building the remaining film. Target remains 120–150 seconds at
1920×1080/30fps. Existing PRODUCTION_PLAN.md is a draft storyboard, not a complete
shot/script/asset implementation contract. Preserve the isolated video workspace.

## Voice and account check

Read-only ElevenLabs subscription and voices endpoints succeeded. The user placed
the API key in the ignored **repository-root `.env`**, not `video/.env`. Do not
print or commit it. Existing generation scripts load video/.env; configure the
credential locally there before an explicitly approved generation request. No
generation, subscription change, or credit-consuming request was made. Account
reported free tier, character_count 0, character_limit 10000 at inspection.

Recommended first audition: **Eric — Smooth, Trustworthy**,
`cjVigY5qzO86Huf0OWal`, returned as `premade`, American English, conversational,
middle-aged, smooth tenor. Desired delivery: warm, curious, confident, restrained;
no booming trailer cadence. This recommendation is based on provider metadata,
not an audition of our script. Alternate: **Matilda — Knowledgable, Professional**,
`XrExE9yKIg1WjnnlVkGX`, premade American English educational voice. Both list
eleven_multilingual_v2 support. Do not assume professional/community voices in the
account listing are free-tier API-eligible: official docs prohibit Voice Library
API use on free tier. Audition existing previews first; then a tightly bounded
script sample only when credit use and publication rights are settled.

The official free-plan terms say noncommercial use only and publication requires
attribution in the title. Do not declare a prize submission eligible without
clarification. User-recorded narration is the no-subscription fallback; alternatively
resolve usage rights before generating the final assets. Upgrading later should
not be assumed to retroactively license prior free-tier generations.

- https://elevenlabs.io/docs/overview/capabilities/voices
- https://elevenlabs.io/docs/overview/administration/billing
- https://elevenlabs.io/docs/help-center/legal/can-i-publish-the-content-i-generate-on-the-platform

## Required contents of the next implementation plan

1. Define the shortlist pitch: problem, useful behavior, proof and frontier
   contribution. Show understandable product behavior early; avoid a long branded
   intro. Reassess the draft's 42-second delay before the main demo.
2. Write the full narration first, with a word/time budget, natural pauses and
   pronunciations. Give every claim its source, scope and on-screen qualifier.
3. Specify each shot: exact time/frame range, focal point, narration, picture,
   movement, transition, sound cue and exit state. Account for transition overlaps.
4. Specify an actual app capture session: routes, viewport, seed/mode, interactions,
   frames to seek, takes, source footage durations and source timecodes. No fake
   cursor activity or reconstructed UI presented as a recording.
5. Inventory new visuals with a reason for each: causal acquisition timing,
   changing Gaussian shape and native Rust parallel rendering. Reuse actual app
   footage/assets where they communicate better. Label conceptual visualization;
   do not make generated microscopy into evidence. Defer unnecessary 3D/dependencies.
6. Map each shot to Remotion components, editable scene boundaries, assets,
   caption tracks, configuration and file paths. Implement a working rough cut
   before adding detail. Keep scientific computation and production app untouched.
7. Budget voice generation, alternate takes and effects inside verified quota.
   Include rights/credits, music selection, ducking, fades, precise cue alignment,
   Whisper proofreading and final encoded loudness analysis. Do not spend quota
   regenerating an unapproved script or invent missing audio.
8. Set review gates: script/storyboard → recorded rough cut → graphics → sound →
   final export. Include silent comprehension and unfamiliar-viewer checks, phone
   playback/readability, fact review, A/V sync, offline backup, and actual submission
   requirements. Verify organizer duration/hosting requirements from the specific
   event rules before locking the final cut; don't invent a Devpost-wide limit.

## Scientific evidence to preserve

Use docs/DEMO_PREP.md, docs/cuda-latency-audit.md and source ledgers. Featured
synthetic seed 304: 32/40 images, 4/4 versus 1/4 divisions covered within ±1 frame,
selected after evaluation. Twenty percent less estimated imaging light assumes
equal illumination per capture; no biological health improvement measured.
GPU dense rendering call: 12.7×, 10,000 synthetic Gaussians, 64×64, warmed persistent
worker, startup excluded. CPU fits/decides; native cuTile Rust renders; browser
replays saved data. Preserve known abrupt-division failures, the distinction from
real microscopy evaluation and the scope of CellSplat4D inspiration.

## Model recommendation

Recommend **Astra Medium for the next planning pass**: synthesize narrative,
scientific constraints, shot design, implementation and audio budget into one
coherent plan. This is a quality-focused creative/technical planning recommendation,
not a claim that ordinary Remotion coding needs Astra. Return to GPT-6.1 Sol Medium
for implementation once the production plan is accepted. No model switch has been
confirmed, and no sub-agents should be spawned without explicit authorization.
