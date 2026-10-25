import { existsSync, readFileSync, writeFileSync, mkdirSync } from "node:fs";
import { parseEnv } from "node:util";
import { spawnSync } from "node:child_process";
import path from "node:path";
import { inside, root, readJson, ffmpeg } from "./lib.mjs";
import { paddedWav, pcmWav } from "./audio-padding.mjs";
const copy = readJson("narration-v3.json");
const plan = readJson("film-plan.json");
const allIds = plan.scenes.map((s) => s.id);
const previousVoice = readJson("src/film/voice-preview.json");
const ids = copy.generateOnly ?? allIds;
if (new Set(ids).size !== ids.length || ids.some((id) => !allIds.includes(id)))
  throw Error("Invalid scene selection.");
if (copy.generateOnly && previousVoice.voiceId !== copy.voiceId)
  throw Error("Partial revision requires the same narrator voice.");
if (
  copy.generateOnly &&
  plan.scenes.some(
    (scene) =>
      !ids.includes(scene.id) && scene.narration !== copy.scenes[scene.id],
  )
)
  throw Error(
    "Text changed outside the selected scenes; update generateOnly before generating audio.",
  );
const paragraphs = ids.map((id) => copy.scenes[id]);
const text = paragraphs.join("\n\n");
if (text.length > 4000) throw Error("Natural-take credit cap exceeded.");
const generate = process.argv.includes("--allow-credits");
const reuseOnly = process.argv.includes("--reuse");
console.log(
  JSON.stringify({
    voice: copy.voiceName,
    voiceId: copy.voiceId,
    characters: text.length,
    mode: reuseOnly
      ? "REUSE SAVED TAKE"
      : generate
        ? "USER-REQUESTED NATURAL VOICE PASS"
        : "DRY RUN",
    requests: generate && !reuseOnly ? 1 : 0,
  }),
);
if (!generate && !reuseOnly && !process.argv.includes("--check"))
  process.exit(0);
const local = Object.assign(
  {},
  ...[path.join(root, "..", ".env"), inside(".env")]
    .filter(existsSync)
    .map((f) => parseEnv(readFileSync(f, "utf8"))),
);
const key = process.env.ELEVENLABS_API_KEY || local.ELEVENLABS_API_KEY;
if (!key && !reuseOnly) throw Error("Missing local ElevenLabs key.");
const headers = { "xi-api-key": key, "Content-Type": "application/json" };
async function api(endpoint, body) {
  const r = await fetch("https://api.elevenlabs.io/v1/" + endpoint, {
    method: body ? "POST" : "GET",
    headers,
    ...(body ? { body: JSON.stringify(body) } : {}),
    signal: AbortSignal.timeout(120000),
  });
  if (!r.ok) {
    const j = await r.json().catch(() => ({}));
    throw Error(
      `ElevenLabs HTTP ${r.status}: ${j.detail?.status || "request_failed"}. No retry or plan change attempted.`,
    );
  }
  return r.json();
}
const subscription = reuseOnly
  ? { tier: "saved-take", character_limit: 0, character_count: 0 }
  : await api("user/subscription");
if (!reuseOnly)
  console.log(
    JSON.stringify({
      tier: subscription.tier,
      remaining: subscription.character_limit - subscription.character_count,
    }),
  );
if (subscription.tier === "free") {
  console.log(
    `${copy.voiceName} generation pending: account still reports free tier. No generation request made.`,
  );
  process.exit(2);
}
if (!generate && !reuseOnly) process.exit(0);
if (
  !reuseOnly &&
  subscription.character_limit - subscription.character_count <
    text.length + 500
)
  throw Error(
    "Not enough included credits with safety margin; overage will not be used.",
  );
const revision = copy.revision;
if (!/^[a-z0-9-]+$/.test(revision)) throw Error("Invalid audio revision.");
const dir = `public/audio/generated/${revision}`;
mkdirSync(inside(dir), { recursive: true });
const mp3 = inside(dir + "/master.mp3"),
  responsePath = inside(dir + "/master.response.json");
let response;
if (existsSync(mp3) && existsSync(responsePath)) {
  response = readJson(dir + "/master.response.json");
  if (response.script !== text)
    throw Error(
      "Existing take uses different text; preserve it and choose a new revision.",
    );
  if (
    response.voiceId !== copy.voiceId ||
    JSON.stringify(response.voiceSettings) !==
      JSON.stringify(copy.voiceSettings)
  )
    throw Error(
      "Saved take uses different voice settings; choose a new revision.",
    );
} else {
  if (reuseOnly)
    throw Error("No complete saved take exists. No API request made.");
  if (existsSync(mp3) || existsSync(responsePath))
    throw Error("Partial take exists; inspect before a second request.");
  response = await api(
    `text-to-speech/${copy.voiceId}/with-timestamps?output_format=mp3_44100_128`,
    {
      text,
      model_id: "eleven_multilingual_v2",
      voice_settings: copy.voiceSettings,
    },
  );
  writeFileSync(mp3, Buffer.from(response.audio_base64, "base64"));
  const { audio_base64, ...metadata } = response;
  void audio_base64;
  writeFileSync(
    responsePath,
    JSON.stringify(
      {
        ...metadata,
        script: text,
        voiceId: copy.voiceId,
        voice: copy.voiceName,
        voiceSettings: copy.voiceSettings,
        subscriptionTier: subscription.tier,
        createdAt: new Date().toISOString(),
      },
      null,
      2,
    ),
  );
}
const a = response.alignment;
if (!a || a.characters.join("") !== text)
  throw Error(
    "Exact character alignment is unavailable; preserve audio for manual alignment. No automated cuts made.",
  );
const wav = inside(dir + "/master.normalized.wav");
if (!existsSync(wav)) {
  const result = spawnSync(
    process.execPath,
    [inside("scripts/audio-process.mjs"), "normalize", mp3, wav],
    { encoding: "utf8", windowsHide: true },
  );
  if (result.status !== 0)
    throw Error("Master normalization failed: " + result.stderr.slice(-500));
}
const bytes = readFileSync(wav);
const wave = pcmWav(bytes),
  masterSeconds = wave.data.length / wave.blockAlign / wave.sampleRate;
let char = 0;
const ranges = paragraphs.map((p, i) => {
  const start = char;
  char += p.length + (i < paragraphs.length - 1 ? 2 : 0);
  return { first: start, last: start + p.length - 1 };
});
const cuts = [
  0,
  ...ranges
    .slice(1)
    .map(
      (r, i) =>
        (a.character_end_times_seconds[ranges[i].last] +
          a.character_start_times_seconds[r.first]) /
        2,
    ),
  masterSeconds,
];
// Keep real recordings complete; allow narration to determine the remaining pacing.
const preferred = [0, 0, 22, 3.5, 0, 8, 15, 0, 0, 6, 0];
const clips = [];
let from = 0;
for (let i = 0; i < ids.length; i++) {
  const range = ranges[i],
    id = ids[i];
  const padded = paddedWav(bytes, {
    startSeconds: cuts[i],
    endSeconds: cuts[i + 1],
    leadSeconds: 0.18,
    tailSeconds: 0.18,
  });
  const output = inside(`${dir}/${id}.padded.wav`);
  writeFileSync(output, padded.buffer);
  const captions = [];
  let word = "",
    start = 0,
    end = 0;
  const relative = (t) =>
    Math.round((t - padded.sourceFirstSeconds + padded.leadSeconds) * 1000);
  const flush = () => {
    if (word.trim())
      captions.push({
        text: (captions.length ? " " : "") + word.trim(),
        startMs: relative(start),
        endMs: relative(end),
        timestampMs: relative((start + end) / 2),
        confidence: null,
      });
    word = "";
  };
  for (let k = range.first; k <= range.last; k++) {
    const c = a.characters[k];
    if (/\s/.test(c)) {
      flush();
      continue;
    }
    if (!word) start = a.character_start_times_seconds[k];
    word += c;
    end = a.character_end_times_seconds[k];
  }
  flush();
  const speechEnd = captions[captions.length - 1].endMs / 1000;
  const duration = Math.max(
    Math.round(preferred[allIds.indexOf(id)] * 30),
    Math.ceil((padded.seconds + 0.02) * 30),
    Math.ceil((speechEnd + 0.28) * 30),
  );
  const s = plan.scenes.find((scene) => scene.id === id);
  s.from = from;
  s.durationInFrames = duration;
  s.narration = paragraphs[i];
  s.voiceAsset = `audio/generated/${revision}/${id}.padded.wav`;
  s.captionsAsset = `audio/generated/${revision}/${id}.captions.json`;
  writeFileSync(
    inside("public/" + s.captionsAsset),
    JSON.stringify(captions, null, 2),
  );
  clips.push({
    id,
    src: s.voiceAsset,
    from,
    duration: Math.ceil(padded.seconds * 30),
    captions,
    seconds: padded.seconds,
    speechEnd,
    sourceStartSeconds: cuts[i],
    sourceEndSeconds: cuts[i + 1],
    paddingApplied: { leadSeconds: 0.18, tailSeconds: 0.18 },
  });
  from += duration;
}
// Preserve every untouched audio file and its exact samples, then move its scene.
const replacements = new Map(clips.map((clip) => [clip.id, clip]));
clips.length = 0;
from = 0;
for (const scene of plan.scenes) {
  const replacement = replacements.get(scene.id);
  const clip =
    replacement ?? previousVoice.clips.find((c) => c.id === scene.id);
  if (!clip || (!replacement && scene.narration !== copy.scenes[scene.id]))
    throw Error(`Untouched scene text/audio mismatch: ${scene.id}`);
  scene.from = from;
  clips.push({ ...clip, from });
  from += scene.durationInFrames;
}
if (from > 5400)
  throw Error(
    `Natural speech needs ${from / 30}s, exceeding the three-minute limit. Audio saved; current preview preserved.`,
  );
plan.durationInFrames = from;
// Aligned caption words place editorial reveals for both revised and preserved scenes.
const phraseFrame = (id, phrase) => {
  const captions = clips.find((clip) => clip.id === id).captions;
  for (let i = 0; i < captions.length; i++) {
    if (
      captions
        .slice(i)
        .map((c) => c.text.trim())
        .join(" ")
        .startsWith(phrase)
    )
      return Math.round(captions[i].startMs * 0.03);
  }
  throw Error(`Missing visual cue: ${phrase}`);
};
plan.visualTimings = {
  premiseResearch: phraseFrame("premise", "In one study"),
  premiseQuestion: phraseFrame("premise", "And that got us thinking"),
  premiseBrand: phraseFrame("premise", "That's why") - 30,
  demoPlayback: Math.max(0, plan.scenes[2].durationInFrames - 660),
  limitsEvidence: phraseFrame("limits", "And in our separate benchmark"),
  limitsFootage: Math.min(
    225,
    Math.max(180, phraseFrame("limits", "And in our separate benchmark")),
  ),
  closeBrand: phraseFrame("close", "That's Peekaboo"),
};
const takeDescription = copy.generateOnly
  ? "Opening revised as a connected take; remaining scene audio preserved"
  : "One continuous take, split only at paragraph pauses";
plan.status = `${copy.voiceName}: ${takeDescription}; padded/preloaded speech, final mix pending`;
writeFileSync(inside("film-plan.json"), JSON.stringify(plan, null, 2) + "\n");
writeFileSync(
  inside("NARRATION.md"),
  [
    "# Peekaboo narration",
    "",
    `Review copy of \`narration-v3.json\`, the editable source. ${takeDescription}.`,
    "",
    `Voice: ${copy.voiceName} (${copy.voiceId}). Runtime: ${(from / 30).toFixed(2)} seconds.`,
    "",
    "## Voice direction",
    "",
    copy.direction,
    "",
    ...allIds.flatMap((id, i) => [
      `## ${i + 1}. ${id[0].toUpperCase() + id.slice(1)}`,
      "",
      copy.scenes[id],
      "",
    ]),
  ].join("\n"),
);
writeFileSync(
  inside("src/film/voice-preview.json"),
  JSON.stringify(
    {
      voice: copy.voiceName,
      voiceId: copy.voiceId,
      status: `${takeDescription}; paragraph-pause cuts; 180ms leading/trailing silence; provider alignment`,
      clips,
    },
    null,
    2,
  ) + "\n",
);
const config = readJson("src/film/audio-config.json");
const positions = [
  plan.scenes[1].from + plan.visualTimings.premiseBrand,
  plan.scenes[2].from - 8,
  plan.scenes[2].from + plan.visualTimings.demoPlayback + 393,
  plan.scenes[6].from - 8,
  plan.scenes[10].from + plan.visualTimings.closeBrand,
];
config.effects.forEach((cue, i) => (cue.from = positions[i]));
writeFileSync(
  inside("src/film/audio-config.json"),
  JSON.stringify(config, null, 2) + "\n",
);
console.log(
  JSON.stringify({
    complete: true,
    voice: copy.voiceName,
    seconds: from / 30,
    clips: clips.length,
    source: `${takeDescription}; no mid-word trims or post-production speed changes`,
  }),
);
