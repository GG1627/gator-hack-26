import { readFileSync, writeFileSync, existsSync } from "node:fs";
import { spawnSync } from "node:child_process";
import { readJson, inside } from "./lib.mjs";
const plan = readJson("film-plan.json");
const voice = readJson("src/film/voice-preview.json");
if(voice.voice!=='Eric')throw Error('Historical Eric preparation only. The current Anya workflow is generate-natural-take.mjs.');
// Recut around actual speech. Keep the uninterrupted comparison at 22 seconds.
const slots = [4.7, 9.3, 22, 12.7, 14.9, 16.5, 19.1, 13, 13.7, 16.9, 7];
let start = 0;
for (let i = 0; i < plan.scenes.length; i++) {
  const s = plan.scenes[i];
  s.from = start;
  s.durationInFrames = Math.round(slots[i] * 30);
  start += s.durationInFrames;
  const clip = voice.clips.find((c) => c.id === s.id);
  clip.from = s.from + 6;
  if (clip.speechEnd + 0.2 > s.durationInFrames / 30 - 0.3)
    throw Error(`Speech does not fit ${s.id}. Recut instead of truncating it.`);
  const original = "public/" + clip.src;
  const normalized = original.replace(/\.mp3$/, ".normalized.wav");
  if (!existsSync(inside(normalized))) {
    const r = spawnSync(
      process.execPath,
      [inside("scripts/audio-process.mjs"), "normalize", original, normalized],
      { encoding: "utf8", windowsHide: true },
    );
    if (r.status !== 0)
      throw Error(`Normalization failed for ${s.id}: ${r.stderr.slice(-700)}`);
  }
  clip.src = normalized.replace(/^public\//, "");
  s.voiceAsset=clip.src;
  s.captionsAsset=clip.src.replace('.normalized.wav','.captions.json');
}
plan.durationInFrames = start;
plan.status =
  "Voice preview; actual ElevenLabs Eric speech and provider character alignment; music and final mix pending";
voice.status =
  "Private voice preview; source tracks two-pass normalized to -16 LUFS; actual provider alignment";
if (start / 30 > 150) throw Error("Recut exceeds 2.5 minute target.");
writeFileSync(inside("film-plan.json"), JSON.stringify(plan, null, 2) + "\n");
writeFileSync(
  inside("src/film/voice-preview.json"),
  JSON.stringify(voice, null, 2) + "\n",
);
console.log(
  JSON.stringify({
    seconds: start / 30,
    frames: start,
    voice: "Eric",
    normalizedClips: voice.clips.length,
  }),
);
