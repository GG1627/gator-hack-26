import { bundle } from "@remotion/bundler";
import { getCompositions, renderStill } from "@remotion/renderer";
import { mkdirSync, writeFileSync } from "node:fs";
import { inside } from "./lib.mjs";
// Preview stills only; never exports the full film or calls an audio service.
const serveUrl = await bundle({
  entryPoint: inside("src/index.ts"),
  outDir: inside(".cache/preview-bundle"),
});
const browserExecutable = process.env.CHROME_PATH || undefined;
const compositions = await getCompositions(serveUrl, { browserExecutable });
const composition = compositions.find((c) => c.id === "Peekaboo-StyleStudy");
if (
  !composition ||
  composition.durationInFrames !== 300 ||
  composition.width !== 1920 ||
  composition.height !== 1080 ||
  composition.fps !== 30
)
  throw new Error("Unexpected proof composition metadata.");
mkdirSync(inside(".cache/stills"), { recursive: true });
for (const frame of [30, 90, 157, 210, 299]) {
  await renderStill({
    serveUrl,
    composition,
    frame,
    output: inside(`.cache/stills/frame-${frame}.png`),
    browserExecutable,
  });
}
writeFileSync(
  inside(".cache/preview-metadata.json"),
  JSON.stringify(
    {
      id: composition.id,
      fps: composition.fps,
      width: composition.width,
      height: composition.height,
      frames: composition.durationInFrames,
      previewFrames: [30, 90, 157, 210, 299],
    },
    null,
    2,
  ),
);
console.log(
  "Five full-resolution preview stills written to .cache/stills/. No MP4 exported.",
);
