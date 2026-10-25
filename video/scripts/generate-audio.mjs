import { writeFileSync } from "node:fs";
import { readJson, prepareOutput } from "./lib.mjs";
const [kind, id, ...flags] = process.argv.slice(2);
const config = readJson("audio-production.json");
if (!["narration", "effect"].includes(kind) || !/^[a-z0-9-]+$/.test(id ?? ""))
  throw new Error(
    "Usage: npm run audio:generate -- narration hook [--allow-paid] OR effect capture [--allow-paid]",
  );
const text =
  kind === "narration" ? config.narration[id] : config.effects[id]?.text;
if (!text)
  throw new Error("Unknown audio ID. Edit audio-production.json first.");
const paid = flags.includes("--allow-paid");
console.log(
  JSON.stringify(
    {
      mode: paid
        ? "PAID REQUEST EXPLICITLY ENABLED"
        : "DRY RUN: no network request",
      kind,
      id,
      characters: text.length,
      voiceConfigured: Boolean(process.env.ELEVENLABS_VOICE_ID),
      keyConfigured: Boolean(process.env.ELEVENLABS_API_KEY),
      text,
    },
    null,
    2,
  ),
);
if (!paid) process.exit(0);
if (!process.env.ELEVENLABS_API_KEY)
  throw new Error("Missing ELEVENLABS_API_KEY in ignored video/.env.");
if (kind === "narration" && !process.env.ELEVENLABS_VOICE_ID)
  throw new Error("Missing ELEVENLABS_VOICE_ID.");
const output = prepareOutput(`public/audio/generated/${kind}-${id}.mp3`);
const settings = config.voice;
const endpoint =
  kind === "narration"
    ? `text-to-speech/${encodeURIComponent(process.env.ELEVENLABS_VOICE_ID)}`
    : "sound-generation";
const payload =
  kind === "narration"
    ? {
        text,
        model_id: settings.modelId,
        voice_settings: {
          stability: settings.stability,
          similarity_boost: settings.similarityBoost,
          style: settings.style,
          speed: settings.speed,
        },
      }
    : {
        text,
        duration_seconds: config.effects[id].durationSeconds,
        prompt_influence: 0.3,
      };
const response = await fetch(
  `https://api.elevenlabs.io/v1/${endpoint}?output_format=mp3_44100_128`,
  {
    method: "POST",
    headers: {
      "xi-api-key": process.env.ELEVENLABS_API_KEY,
      "Content-Type": "application/json",
      Accept: "audio/mpeg",
    },
    body: JSON.stringify(payload),
    signal: AbortSignal.timeout(120000),
  },
);
if (!response.ok)
  throw new Error(
    `ElevenLabs HTTP ${response.status}; not retried to avoid duplicate charges.`,
  );
writeFileSync(output, Buffer.from(await response.arrayBuffer()));
writeFileSync(
  output + ".json",
  JSON.stringify(
    {
      kind,
      id,
      createdAt: new Date().toISOString(),
      payload,
      voiceId: kind === "narration" ? process.env.ELEVENLABS_VOICE_ID : null,
      source: "ElevenLabs",
    },
    null,
    2,
  ),
);
console.log(
  `Saved ${kind}-${id}.mp3; listen and normalize before adding it to src/media.ts.`,
);
