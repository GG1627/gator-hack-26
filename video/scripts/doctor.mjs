import { existsSync } from "node:fs";
import { inside, readJson, ffmpeg } from "./lib.mjs";
const pkg = readJson("package.json");
const versions = Object.fromEntries(
  Object.entries(pkg.dependencies).filter(
    ([key]) => key === "remotion" || key.startsWith("@remotion/"),
  ),
);
if (new Set(Object.values(versions)).size !== 1)
  throw new Error("Remotion package versions must match exactly.");
ffmpeg(["-version"]);
console.log(
  JSON.stringify(
    {
      node: process.version,
      versions,
      officialSkills: existsSync(
        inside(".agents/skills/remotion-best-practices/SKILL.md"),
      ),
      elevenLabsKeyPresent: Boolean(process.env.ELEVENLABS_API_KEY),
      voiceIdPresent: Boolean(process.env.ELEVENLABS_VOICE_ID),
      ffmpeg: "Remotion bundled binary (or configured override)",
      whisperInstalled: existsSync(inside("whisper.cpp/main.exe")),
      whisperModel: existsSync(inside("whisper.cpp/ggml-base.en.bin")),
      paidRequestsMade: 0,
    },
    null,
    2,
  ),
);
