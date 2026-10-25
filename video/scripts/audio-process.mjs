import { existsSync, writeFileSync } from "node:fs";
import path from "node:path";
import { inside, prepareOutput, ffmpeg } from "./lib.mjs";
const [mode, inputName, outputName] = process.argv.slice(2);
if (!["analyze", "normalize", "wav"].includes(mode) || !inputName)
  throw new Error(
    "Usage: audio:process -- analyze|normalize|wav input [new-output] (paths relative to video/)",
  );
const input = inside(inputName);
if (!existsSync(input)) throw new Error("Input audio/video does not exist.");
const target = "loudnorm=I=-16:TP=-1.5:LRA=11";
if (mode === "wav") {
  const output = prepareOutput(outputName);
  if (path.extname(output) !== ".wav")
    throw new Error("Whisper output must end in .wav.");
  ffmpeg([
    "-nostdin",
    "-n",
    "-i",
    input,
    "-vn",
    "-ac",
    "1",
    "-ar",
    "16000",
    "-c:a",
    "pcm_s16le",
    output,
  ]);
  console.log("Created 16 kHz mono PCM WAV for local Whisper.");
} else {
  const stderr = ffmpeg([
    "-nostdin",
    "-i",
    input,
    "-vn",
    "-af",
    target + ":print_format=json",
    "-f",
    "null",
    "-",
  ]);
  const match = stderr.match(/\{\s*"input_i"[\s\S]*?\}/);
  if (!match)
    throw new Error("No loudness report; input must have a real audio stream.");
  const measured = JSON.parse(match[0]);
  console.log(JSON.stringify(measured, null, 2));
  if (mode === "normalize") {
    if (
      [
        "input_i",
        "input_tp",
        "input_lra",
        "input_thresh",
        "target_offset",
      ].some((k) => !Number.isFinite(Number(measured[k])))
    )
      throw new Error("Cannot normalize silence or invalid audio.");
    const output = prepareOutput(outputName);
    const filter = `${target}:measured_I=${measured.input_i}:measured_TP=${measured.input_tp}:measured_LRA=${measured.input_lra}:measured_thresh=${measured.input_thresh}:offset=${measured.target_offset}:linear=true:print_format=json`;
    const videoArgs =
      path.extname(output).toLowerCase() === ".mp4"
        ? [
            "-c:v",
            "copy",
            "-c:a",
            "aac",
            "-b:a",
            "320k",
            "-movflags",
            "+faststart",
          ]
        : ["-vn", "-c:a", "pcm_s24le"];
    if (
      path.extname(output).toLowerCase() !== ".mp4" &&
      path.extname(output).toLowerCase() !== ".wav"
    )
      throw new Error("Normalize to .wav, or .mp4 with copied video.");
    const final = ffmpeg([
      "-nostdin",
      "-n",
      "-i",
      input,
      "-af",
      filter,
      "-ar",
      "48000",
      ...videoArgs,
      output,
    ]);
    writeFileSync(
      output + ".loudness.json",
      JSON.stringify(
        {
          firstPass: measured,
          secondPass: final.match(/\{\s*"input_i"[\s\S]*?\}/)?.[0] ?? null,
        },
        null,
        2,
      ),
    );
    console.log(
      "Two-pass normalization complete; analyze the result and listen before approval.",
    );
  }
}
