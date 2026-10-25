import { mkdirSync, existsSync, readFileSync, writeFileSync } from "node:fs";
import { parseEnv } from "node:util";
import { createHash } from "node:crypto";
import path from "node:path";
import { inside, root, readJson, ffmpeg } from "./lib.mjs";
const plan = readJson("film-plan.json");
const generate = process.argv.includes("--allow-credits");
const definitions = [
  {
    id: "reveal",
    text: "A single gentle warm glass shimmer with a soft airy rise and delicate rounded landing, premium science product reveal, subtle and optimistic, no voice, no music, no loud bass impact.",
    duration_seconds: 1.8,
  },
  {
    id: "transition",
    text: "One soft short airy whoosh, smooth brushed air and a subtle rounded tail, refined motion graphics transition, quiet and precise, no voice, no music, no harsh high frequencies.",
    duration_seconds: 0.7,
  },
  {
    id: "capture",
    text: "One delicate optical capture tick, a very soft tiny rounded mechanical click with a clean short tail, subtle laboratory interface feedback, no voice, no music, not a camera shutter burst.",
    duration_seconds: 0.5,
  },
];
console.log(
  JSON.stringify({
    mode: generate ? "USER-REQUESTED SOUND PREVIEW" : "DRY RUN",
    effects: definitions.length,
    creditCap: 900,
    music: "Cylinder One — Chris Zabriskie, CC BY 4.0; no paid music API",
  }),
);
if (!generate) process.exit(0);
const local = Object.assign(
  {},
  ...[path.join(root, "..", ".env"), inside(".env")]
    .filter(existsSync)
    .map((f) => parseEnv(readFileSync(f, "utf8"))),
);
const key = process.env.ELEVENLABS_API_KEY || local.ELEVENLABS_API_KEY;
if (!key) throw Error("No ElevenLabs key.");
const headers = { "xi-api-key": key, "Content-Type": "application/json" };
const subscription = async () => {
  const r = await fetch("https://api.elevenlabs.io/v1/user/subscription", {
    headers,
  });
  if (!r.ok) throw Error(`Subscription check failed ${r.status}`);
  return r.json();
};
const before = await subscription();
if (
  !['free','starter'].includes(before.tier) ||
  before.character_limit - before.character_count < 1200
)
  throw Error("Free preview quota check failed; no paid call attempted.");
const revision=process.argv.find(x=>x.startsWith('--revision='))?.slice(11)||'v1';
if(!/^v\d+$/.test(revision))throw Error('Invalid sound revision.');
const dir = `public/audio/generated/sfx-preview-${revision}`;
mkdirSync(inside(dir), { recursive: true });
const report = {
  source: "ElevenLabs",
  subscriptionTier:before.tier,
  purpose: "Private local sound preview",
  effects: [],
  quotaBefore: before.character_count,
};
let spent = 0;
for (const d of definitions) {
  const file = inside(`${dir}/${d.id}.mp3`);
  let cost = 0;
  if (!existsSync(file)) {
    if (spent + 300 > 900) throw Error("Effect budget exhausted.");
    const r = await fetch(
      "https://api.elevenlabs.io/v1/sound-generation?output_format=mp3_44100_128",
      {
        method: "POST",
        headers,
        body: JSON.stringify({
          text: d.text,
          duration_seconds: d.duration_seconds,
          prompt_influence: 0.45,
          model_id: "eleven_text_to_sound_v2",
        }),
        signal: AbortSignal.timeout(120000),
      },
    );
    if (!r.ok) throw Error(`Sound generation HTTP ${r.status}; not retried.`);
    cost = Number(r.headers.get("character-cost") || 200);
    spent += cost;
    writeFileSync(file, Buffer.from(await r.arrayBuffer()));
    writeFileSync(
      file + ".json",
      JSON.stringify(
        {
          ...d,
          source: "ElevenLabs",
          createdAt: new Date().toISOString(),
          reportedCost: cost,
        },
        null,
        2,
      ),
    );
  }
  report.effects.push({ ...d, reportedCost: cost });
  console.log(`Prepared ${d.id}.`);
}
const musicDir = "public/audio/licensed";
mkdirSync(inside(musicDir), { recursive: true });
const musicPath = inside(musicDir + "/cylinder-one.m4a");
const source = "https://audio.chriszabriskie.com/cylinders/cylinders-01.m4a";
if (!existsSync(musicPath)) {
  const r = await fetch(source, { signal: AbortSignal.timeout(60000) });
  if (!r.ok) throw Error(`Licensed track download failed ${r.status}`);
  writeFileSync(musicPath, Buffer.from(await r.arrayBuffer()));
}
const provenance = {
  title: "Cylinder One",
  artist: "Chris Zabriskie",
  album: "Cylinders",
  sourcePage: "https://chriszabriskie.com/cylinders/",
  source,
  license: "CC BY 4.0",
  licenseUrl: "https://creativecommons.org/licenses/by/4.0/",
  permission: "https://chriszabriskie.com/use/",
  sha256: createHash("sha256").update(readFileSync(musicPath)).digest("hex"),
  modifications:
    "Excerpt used under narration with fades, ducking and volume automation.",
};
writeFileSync(
  inside(musicDir + "/cylinder-one.provenance.json"),
  JSON.stringify(provenance, null, 2),
);
const cue = (id, from, gain) => ({
  src: `${dir.replace(/^public\//,'')}/${id}.mp3`,
  from,
  duration: Math.ceil(
    definitions.find((d) => d.id === id).duration_seconds * 30,
  ),
  gain,
});
const audio = {
  music: readJson('src/film/audio-config.json').music || { src: "audio/licensed/cylinder-one.m4a", gain: 0.15 },
  effects: [
    cue("reveal", plan.scenes[1].from + 210, 0.17),
    cue("transition", plan.scenes[2].from - 8, 0.1),
    cue("capture", plan.scenes[2].from + Math.round(13.1 * 30), 0.1),
    cue("transition", plan.scenes[6].from - 8, 0.1),
    cue("reveal", plan.scenes[10].from, 0.15),
  ],
};
// Listen/preview cues as editorial accents; the capture tick is not an instrument recording.
writeFileSync(
  inside("src/film/audio-config.json"),
  JSON.stringify(audio, null, 2),
);
const after = await subscription();
report.quotaAfter = after.character_count;
report.creditDifference = after.character_count - before.character_count;
writeFileSync(
  inside(dir + "/generation-report.json"),
  JSON.stringify(report, null, 2),
);
console.log(
  JSON.stringify({
    effects: definitions.length,
    reportedEffectCredits: spent,
    musicLicense: provenance.license,
    quotaDifference: report.creditDifference,
  }),
);
