import { test } from "node:test";
import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import { inside } from "../scripts/lib.mjs";
test("audio generation remains a dry run even when credentials exist, without exposing a key", () => {
  const key = "TEST_SECRET_MUST_NOT_APPEAR";
  const result = spawnSync(
    process.execPath,
    [inside("scripts/generate-audio.mjs"), "narration", "hook"],
    {
      encoding: "utf8",
      env: {
        ...process.env,
        ELEVENLABS_API_KEY: key,
        ELEVENLABS_VOICE_ID: "test-voice",
      },
    },
  );
  assert.equal(result.status, 0);
  assert.match(result.stdout, /DRY RUN: no network request/);
  assert.ok(!result.stdout.includes(key));
});
test("explicit paid mode refuses missing credentials before attempting generation", () => {
  const result = spawnSync(
    process.execPath,
    [inside("scripts/generate-audio.mjs"), "effect", "capture", "--allow-paid"],
    { encoding: "utf8", env: { ...process.env, ELEVENLABS_API_KEY: "" } },
  );
  assert.equal(result.status, 1);
  assert.match(result.stderr, /Missing ELEVENLABS_API_KEY/);
});
test("external output paths are rejected", () => {
  assert.throws(() => inside("../outside.wav"), /inside video/);
});
