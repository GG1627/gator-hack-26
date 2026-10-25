import { existsSync, writeFileSync } from "node:fs";
import {
  installWhisperCpp,
  downloadWhisperModel,
  transcribe,
  toCaptions,
} from "@remotion/install-whisper-cpp";
import { inside, prepareOutput } from "./lib.mjs";
const version = "1.6.0"; // Official installer supports this prebuilt Windows release.
const whisperPath = inside("whisper.cpp");
const [mode, input, output] = process.argv.slice(2);
if (mode === "setup") {
  await installWhisperCpp({ to: whisperPath, version });
  await downloadWhisperModel({ model: "base.en", folder: whisperPath });
  console.log(
    "Local Whisper.cpp + base.en ready. No audio was sent to a service.",
  );
} else if (mode === "transcribe") {
  const source = inside(input);
  if (!existsSync(source))
    throw new Error(
      "Missing input: convert approved audio to a 16 kHz PCM WAV first.",
    );
  const target = prepareOutput(output);
  const result = await transcribe({
    inputPath: source,
    whisperPath,
    whisperCppVersion: version,
    model: "base.en",
    tokenLevelTimestamps: true,
    language: "en",
  });
  const { captions } = toCaptions({ whisperCppOutput: result });
  writeFileSync(target, JSON.stringify(captions, null, 2));
  console.log(
    "Caption JSON written with source-relative timestamps; proofread scientific terms.",
  );
} else
  throw new Error(
    "Usage: whisper.mjs setup OR transcribe public/audio/...wav public/audio/...captions.json",
  );
