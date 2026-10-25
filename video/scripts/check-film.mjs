import { readFileSync, existsSync, writeFileSync, mkdirSync } from "node:fs";
import { createHash } from "node:crypto";
import path from "node:path";
import { execFileSync } from "node:child_process";
import { ffmpeg, inside, readJson, root } from "./lib.mjs";
const plan = readJson("film-plan.json");
const evidence = readJson("src/film/evidence.json");
const voice = readJson("src/film/voice-preview.json");
const audio = readJson("src/film/audio-config.json");
let end = 0;
for (const scene of plan.scenes) {
  if (scene.from !== end || scene.durationInFrames <= 0 || !scene.narration)
    throw Error(`Invalid scene ${scene.id}`);
  end += scene.durationInFrames;
}
if (
  end !== plan.durationInFrames ||
  end / plan.fps > 180 ||
  end / plan.fps < 120
)
  throw Error("Duration outside approved range.");
const visual = plan.visualTimings;
if (
  !(
    visual.premiseResearch > 0 &&
    visual.premiseQuestion > visual.premiseResearch &&
    visual.premiseBrand > visual.premiseQuestion &&
    visual.premiseBrand < plan.scenes[1].durationInFrames - 30 &&
    visual.demoPlayback + 660 <= plan.scenes[2].durationInFrames &&
    visual.closeBrand > 0 &&
    visual.closeBrand < plan.scenes[10].durationInFrames - 30
  )
)
  throw Error("Invalid speech-aligned visual boundaries.");
for (const source of evidence.sources) {
  const actual = createHash("sha256")
    .update(readFileSync(path.resolve(root, "..", source.path)))
    .digest("hex");
  if (actual !== source.sha256) throw Error(`Evidence changed: ${source.path}`);
}
for (const scene of plan.scenes) {
  const clip = voice.clips.find((x) => x.id === scene.id);
  if (!clip || !existsSync(inside("public/" + clip.src)))
    throw Error(`Missing narration for ${scene.id}`);
  if (
    clip.from < scene.from ||
    clip.from + clip.speechEnd * plan.fps >
      scene.from + scene.durationInFrames - 8
  )
    throw Error(`Narration exceeds scene ${scene.id}`);
  if (
    clip.captions.some(
      (c) =>
        c.endMs < c.startMs ||
        c.startMs < 0 ||
        c.endMs > clip.seconds * 1000 + 50,
    )
  )
    throw Error(`Invalid captions for ${scene.id}`);
}
if (audio.music && !existsSync(inside("public/" + audio.music.src)))
  throw Error("Missing music source.");
for (const cue of audio.effects) {
  if (
    !existsSync(inside("public/" + cue.src)) ||
    cue.from < 0 ||
    cue.from + cue.duration > plan.durationInFrames
  )
    throw Error("Invalid sound cue.");
}
const recordings = [
  { id: "demo", src: "recordings/demo-304.mp4", trim: 90, duration: 660 },
  {
    id: "result",
    src: "recordings/featured-result.mp4",
    trim: 90,
    duration: 105,
  },
  {
    id: "gaussians",
    src: "recordings/gaussian-controls.mp4",
    trim: 90,
    duration: 150,
  },
  {
    id: "cuda",
    src: "recordings/cuda-tiles.mp4",
    trim: 90,
    duration: plan.scenes[6].durationInFrames - 300,
  },
  {
    id: "abrupt",
    src: "recordings/abrupt-304.mp4",
    trim: 150,
    duration: plan.visualTimings.limitsFootage,
  },
];
const metadata = new Map();
for (const shot of recordings) {
  const file = inside("public/" + shot.src);
  if (!existsSync(file)) throw Error(`Missing footage ${shot.src}`);
  if (!metadata.has(file)) {
    const info = ffmpeg([
      "-i",
      file,
      "-t",
      "0",
      "-c",
      "copy",
      "-f",
      "null",
      "-",
    ]);
    const match = info.match(/Duration: (\d+):(\d+):([\d.]+)/);
    if (!match || !info.includes("1920x1080") || !info.includes("30 fps"))
      throw Error(`Unexpected recording format ${shot.src}`);
    metadata.set(file, {
      durationSeconds:
        Number(match[1]) * 3600 + Number(match[2]) * 60 + Number(match[3]),
      sha256: createHash("sha256").update(readFileSync(file)).digest("hex"),
    });
  }
  Object.assign(shot, metadata.get(file));
  if ((shot.trim + shot.duration) / plan.fps > shot.durationSeconds)
    throw Error(`Trim exceeds source: ${shot.id}`);
}
const finalRequested = process.argv.includes("--final");
const captureReport = readJson(".cache/capture/report.json");
writeFileSync(
  inside("src/film/media-manifest.json"),
  JSON.stringify(
    {
      status: "Recorded application sources; narration and music pending",
      appRevision: execFileSync("git", ["rev-parse", "HEAD"], {
        cwd: root,
        encoding: "utf8",
        windowsHide: true,
      }).trim(),
      recordings: recordings.map((shot) => ({
        ...shot,
        sourceInFrame: shot.trim,
        sourceOutFrame: shot.trim + shot.duration,
        fps: 30,
        width: 1920,
        height: 1080,
        playbackRate: 1,
        capture: captureReport
          .filter((x) => x.src === shot.src)
          .slice(-1)
          .map((x) => ({
            recordedAt: x.recordedAt,
            cues: x.cues,
            errors: x.errors,
          }))[0],
      })),
    },
    null,
    2,
  ) + "\n",
);
if (finalRequested) {
  throw Error(
    "Final release is pending: human narration/caption review and encoded mix loudness analysis. Local narrated preview is available.",
  );
}
mkdirSync(inside(".cache"), { recursive: true });
writeFileSync(
  inside(".cache/film-preflight.json"),
  JSON.stringify(
    {
      status: "voiced-preview-ready",
      finalReady: false,
      frames: end,
      seconds: end / plan.fps,
      recordings,
      missingFinal: [
        "human voice/caption review",
        "encoded mix loudness analysis",
      ],
    },
    null,
    2,
  ),
);
console.log(
  `Voiced preview verified: ${plan.scenes.length} scenes, ${end / plan.fps}s, ${voice.clips.length} timed narration clips, ${audio.effects.length} effects; source trims and evidence hashes verified.`,
);
