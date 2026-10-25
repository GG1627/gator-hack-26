import { existsSync, mkdirSync, readFileSync } from "node:fs";
import { createRequire } from "node:module";
import path from "node:path";
import { spawnSync } from "node:child_process";
export const root = path.resolve(import.meta.dirname, "..");
export const readJson = (file) =>
  JSON.parse(readFileSync(path.join(root, file), "utf8"));
export function inside(file) {
  const target = path.resolve(root, file);
  if (!target.startsWith(root + path.sep))
    throw new Error("Path must be inside video/.");
  return target;
}
export function prepareOutput(file) {
  const output = inside(file);
  if (existsSync(output))
    throw new Error("Output already exists; choose a new filename.");
  mkdirSync(path.dirname(output), { recursive: true });
  return output;
}
export function ffmpeg(args) {
  const require = createRequire(import.meta.url);
  const suffix =
    process.platform === "win32"
      ? "-msvc"
      : process.platform === "linux"
        ? "-gnu"
        : "";
  const binary =
    process.env.FFMPEG_PATH ||
    path.join(
      path.dirname(
        require.resolve(
          `@remotion/compositor-${process.platform}-${process.arch}${suffix}`,
        ),
      ),
      process.platform === "win32" ? "ffmpeg.exe" : "ffmpeg",
    );
  const result = spawnSync(binary, args, {
    encoding: "utf8",
    maxBuffer: 20 * 1024 * 1024,
    windowsHide: true,
  });
  if (result.error) throw result.error;
  if (result.status !== 0)
    throw new Error(
      `FFmpeg failed (${result.status}): ${result.stderr.slice(-2000)}`,
    );
  return result.stderr;
}
