import { existsSync, readFileSync, writeFileSync, mkdirSync } from "node:fs";
import { parseEnv } from "node:util";
import path from "node:path";
import { inside, root, readJson, ffmpeg } from "./lib.mjs";
const plan = readJson("film-plan.json");
const settings = {
  stability: 0.4,
  similarity_boost: 0.75,
  style: 0.3,
  speed: 1.04,
  use_speaker_boost: true,
};
const voiceId = "cjVigY5qzO86Huf0OWal";
const modelId = "eleven_multilingual_v2";
const revision =
  process.argv.find((x) => x.startsWith("--revision="))?.slice(11) || "v1";
if (!/^v\d+$/.test(revision)) throw Error("Invalid revision.");
const only = process.argv.find((x) => x.startsWith("--only="))?.slice(7);
const dir = `public/audio/generated/eric-preview-${revision}`;
const characters = plan.scenes
  .filter((s) => !only || s.id === only)
  .reduce((n, s) => n + s.narration.length, 0);
if (characters > 2500) throw Error("Preview character cap exceeded.");
const generate = process.argv.includes("--allow-credits");
console.log(
  JSON.stringify({
    mode: generate ? "USER-REQUESTED VOICE PREVIEW" : "DRY RUN",
    voice: "Eric",
    modelId,
    characters,
    maxCharacters: 2500,
    sceneCount: plan.scenes.length,
  }),
);
if (!generate) process.exit(0);
const envFiles = [path.join(root, "..", ".env"), inside(".env")];
const local = Object.assign(
  {},
  ...envFiles.filter(existsSync).map((f) => parseEnv(readFileSync(f, "utf8"))),
);
const key = process.env.ELEVENLABS_API_KEY || local.ELEVENLABS_API_KEY;
if (!key) throw Error("No local ElevenLabs credential found.");
async function api(endpoint, body) {
  const r = await fetch(`https://api.elevenlabs.io/v1/${endpoint}`, {
    method: body ? "POST" : "GET",
    headers: {
      "xi-api-key": key,
      ...(body ? { "Content-Type": "application/json" } : {}),
    },
    ...(body ? { body: JSON.stringify(body) } : {}),
    signal: AbortSignal.timeout(120000),
  });
  if (!r.ok)
    throw Error(`ElevenLabs HTTP ${r.status}; no retry or upgrade attempted.`);
  return r.json();
}
const sub = await api("user/subscription");
if (sub.tier !== "free")
  throw Error(
    "This preview is restricted to the verified free plan; review changed billing before generation.",
  );
const remaining = sub.character_limit - sub.character_count;
if (remaining < characters + 500)
  throw Error("Insufficient included credits plus safety margin.");
console.log(
  JSON.stringify({
    tier: sub.tier,
    remainingBefore: remaining,
    requestedCharacters: characters,
  }),
);
mkdirSync(inside(dir), { recursive: true });
const clips = [];
const report = {
  voice: "Eric",
  voiceId,
  modelId,
  settings,
  characters,
  quotaBefore: sub.character_count,
  quotaLimit: sub.character_limit,
  purpose:
    "Private local voice preview; publication rights remain a separate final-delivery consideration.",
  clips,
};
function captionsFromAlignment(a) {
  if (
    !a ||
    a.characters.length !== a.character_start_times_seconds.length ||
    a.characters.length !== a.character_end_times_seconds.length
  )
    throw Error("Missing or malformed speech alignment.");
  const captions = [];
  let word = "",
    start = 0,
    end = 0;
  const flush = () => {
    if (word.trim())
      captions.push({
        text: (captions.length ? " " : "") + word.trim(),
        startMs: Math.round(start * 1000),
        endMs: Math.round(end * 1000),
        timestampMs: Math.round((start + end) * 500),
        confidence: null,
      });
    word = "";
  };
  a.characters.forEach((c, i) => {
    if (/\s/.test(c)) {
      flush();
      return;
    }
    if (!word) start = a.character_start_times_seconds[i];
    word += c;
    end = a.character_end_times_seconds[i];
  });
  flush();
  return captions;
}
for (let i = 0; i < plan.scenes.length; i++) {
  const s = plan.scenes[i];
  const prefix = `${dir}/${s.id}`;
  if (only && s.id !== only) continue;
  const mp3 = inside(prefix + ".mp3");
  const json = inside(prefix + ".response.json");
  let response;
  if (existsSync(mp3) && existsSync(json)) {
    response = JSON.parse(readFileSync(json, "utf8"));
    console.log(`Reusing ${s.id}; no request.`);
  } else {
    if (existsSync(mp3) || existsSync(json))
      throw Error(
        `Partial output for ${s.id}; inspect before making another request.`,
      );
    const payload = {
      text: s.narration,
      model_id: modelId,
      voice_settings: settings,
      previous_text: plan.scenes[i - 1]?.narration,
      next_text: plan.scenes[i + 1]?.narration,
    };
    response = await api(
      `text-to-speech/${voiceId}/with-timestamps?output_format=mp3_44100_128`,
      payload,
    );
    if (!response.audio_base64) throw Error("Provider returned no audio.");
    writeFileSync(mp3, Buffer.from(response.audio_base64, "base64"));
    const { audio_base64, ...metadata } = response;
    void audio_base64;
    writeFileSync(
      json,
      JSON.stringify(
        {
          ...metadata,
          script: s.narration,
          createdAt: new Date().toISOString(),
        },
        null,
        2,
      ),
    );
  }
  const captions = captionsFromAlignment(
    response.alignment || response.normalized_alignment,
  );
  writeFileSync(
    inside(prefix + ".captions.json"),
    JSON.stringify(captions, null, 2),
  );
  const info = ffmpeg(["-i", mp3, "-t", "0", "-c", "copy", "-f", "null", "-"]);
  const m = info.match(/Duration: (\d+):(\d+):([\d.]+)/);
  if (!m) throw Error("Cannot measure voice clip.");
  const seconds = Number(m[1]) * 3600 + Number(m[2]) * 60 + Number(m[3]);
  const speechEnd = captions.length
    ? captions[captions.length - 1].endMs / 1000
    : seconds;
  const offsetFrames = s.id === "hook" ? 6 : 12;
  clips.push({
    id: s.id,
    src: prefix.replace(/^public\//, "") + ".mp3",
    from: s.from + offsetFrames,
    duration: Math.ceil(seconds * 30),
    captions,
    seconds,
    speechEnd,
    sceneAvailableSeconds: (s.durationInFrames - offsetFrames) / 30,
  });
  writeFileSync(
    inside(dir + "/generation-report.json"),
    JSON.stringify(report, null, 2),
  );
  console.log(
    JSON.stringify({
      scene: s.id,
      seconds,
      speechEnd,
      available: (s.durationInFrames - offsetFrames) / 30,
    }),
  );
}
const after = await api("user/subscription");
report.quotaAfter = after.character_count;
report.creditsConsumed = after.character_count - sub.character_count;
writeFileSync(
  inside(dir + "/generation-report.json"),
  JSON.stringify(report, null, 2),
);
const previous = existsSync(inside("src/film/voice-preview.json"))
  ? readJson("src/film/voice-preview.json").clips
  : [];
const merged = plan.scenes
  .map(
    (s) =>
      clips.find((c) => c.id === s.id) || previous.find((c) => c.id === s.id),
  )
  .filter(Boolean);
writeFileSync(
  inside("src/film/voice-preview.json"),
  JSON.stringify(
    {
      voice: "Eric",
      status:
        "Private generated preview; source loudness normalization pending",
      clips: merged,
    },
    null,
    2,
  ),
);
console.log(
  JSON.stringify({
    complete: true,
    creditsConsumed: report.creditsConsumed,
    remaining: after.character_limit - after.character_count,
  }),
);
