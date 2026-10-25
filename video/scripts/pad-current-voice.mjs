import { readFileSync, writeFileSync, existsSync } from "node:fs";
import { inside, readJson } from "./lib.mjs";
import { paddedWav } from "./audio-padding.mjs";
const plan = readJson("film-plan.json"),
  voice = readJson("src/film/voice-preview.json");
for (const clip of voice.clips) {
  if (clip.paddingApplied) continue;
  const original = inside("public/" + clip.src);
  const target = original.replace(".wav", ".padded.wav");
  const padded = paddedWav(readFileSync(original));
  if (!existsSync(target)) writeFileSync(target, padded.buffer);
  clip.src = clip.src.replace(".wav", ".padded.wav");
  clip.duration = Math.ceil(padded.seconds * 30);
  clip.seconds = padded.seconds;
  clip.speechEnd += padded.leadSeconds;
  clip.captions = clip.captions.map((c) => ({
    ...c,
    startMs: c.startMs + padded.leadSeconds * 1000,
    endMs: c.endMs + padded.leadSeconds * 1000,
    timestampMs:
      c.timestampMs === null ? null : c.timestampMs + padded.leadSeconds * 1000,
  }));
  clip.paddingApplied = { leadSeconds: padded.leadSeconds, tailSeconds: 0.15 };
  const s = plan.scenes.find((s) => s.id === clip.id);
  s.voiceAsset = clip.src;
  // Start the source at the scene boundary; its actual speech begins after the lead-in.
  clip.from = s.from;
}
writeFileSync(
  inside("src/film/voice-preview.json"),
  JSON.stringify(voice, null, 2) + "\n",
);
writeFileSync(inside("film-plan.json"), JSON.stringify(plan, null, 2) + "\n");
console.log(
  "Narration WAVs padded at sample boundaries; captions shifted with speech. Three-second premount is enabled in the player.",
);
