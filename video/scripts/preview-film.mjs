import { bundle } from "@remotion/bundler";
import { getCompositions, renderStill } from "@remotion/renderer";
import { mkdirSync, writeFileSync } from "node:fs";
import { inside, readJson } from "./lib.mjs";
const plan = readJson("film-plan.json");
const serveUrl = await bundle({
  entryPoint: inside("src/index.ts"),
  outDir: inside(".cache/film-bundle"),
});
const browserExecutable =
  process.env.CHROME_PATH ||
  "C:/Users/gael8/AppData/Local/ms-playwright/chromium-1247/chrome-win64/chrome.exe";
const compositions = await getCompositions(serveUrl, { browserExecutable });
const composition = compositions.find((x) => x.id === "Peekaboo-Submission");
if (
  !composition ||
  composition.durationInFrames !== plan.durationInFrames ||
  composition.fps !== 30
)
  throw Error("Film metadata mismatch.");
mkdirSync(inside(".cache/film-stills"), { recursive: true });
const v = plan.visualTimings;
const frames = [
  Math.round(plan.scenes[0].durationInFrames / 2),
  ...[
    v.premiseResearch / 2,
    (v.premiseResearch + v.premiseQuestion) / 2,
    (v.premiseQuestion + v.premiseBrand) / 2,
    (v.premiseBrand + plan.scenes[1].durationInFrames) / 2,
  ].map((x) => plan.scenes[1].from + Math.round(x)),
  ...plan.scenes
    .slice(2)
    .map((s) => s.from + Math.round(s.durationInFrames * 0.55)),
  plan.scenes[6].from + plan.scenes[6].durationInFrames - 25,
  plan.scenes[10].from + v.closeBrand + 35,
  plan.scenes[1].from - 4,
  plan.scenes[1].from + 4,
  plan.scenes[2].from - 4,
  plan.scenes[2].from + 4,
];
for (const frame of frames) {
  await renderStill({
    serveUrl,
    composition,
    frame,
    output: inside(`.cache/film-stills/${frame}.png`),
    browserExecutable,
  });
  console.log(`Reviewed frame prepared: ${frame}`);
}
writeFileSync(
  inside(".cache/film-preview.json"),
  JSON.stringify(
    {
      id: composition.id,
      frames,
      width: composition.width,
      height: composition.height,
      durationInFrames: composition.durationInFrames,
      fps: composition.fps,
    },
    null,
    2,
  ),
);
