import { test } from "node:test";
import assert from "node:assert/strict";
import { clipFade, musicDuck } from "../src/audio-envelope.mjs";
test("music ducks smoothly before speech and recovers after it; overlapping narration does not pump louder", () => {
  const clips = [
    { from: 60, duration: 60 },
    { from: 100, duration: 50 },
  ];
  assert.equal(musicDuck(0, clips, 30), 1);
  assert.equal(musicDuck(60, clips, 30), 0.25);
  assert.equal(musicDuck(110, clips, 30), 0.25);
  assert.equal(musicDuck(170, clips, 30), 1);
  for (let i = 0; i < 200; i++)
    assert.ok(musicDuck(i, clips, 30) >= 0.25 && musicDuck(i, clips, 30) <= 1);
  assert.ok(musicDuck(57, clips, 30) < musicDuck(55, clips, 30));
  assert.ok(musicDuck(155, clips, 30) < musicDuck(160, clips, 30));
});
test("clips start and finish at silence and retain unity gain through the middle", () => {
  assert.equal(clipFade(0, 300, 15), 0);
  assert.equal(clipFade(299, 300, 15), 0);
  assert.equal(clipFade(150, 300, 15), 1);
});
