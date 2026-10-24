import {test} from 'node:test';
import assert from 'node:assert/strict';
import { frameState, evaluationUrl, metricValue } from '../src/replay.mjs';

const run = {key: 'embryo/b3', sequence_id: 'embryo', methods: {fixed: {config: {acquired_indices: [0, 4, 8]}}, photon: {config: {acquired_indices: [0, 3, 9]}}}};
test('held image never uses a later acquisition, even with full closed schedule available', () => {
  for (let t = 0; t < 10; t++) {
    for (const name of ['fixed', 'photon']) {
      const state = frameState(run, name, t);
      assert.ok(state.last <= t);
      assert.equal(state.image, `/demo/images/embryo/${state.last}.png`);
    }
  }
  assert.equal(frameState(run, 'fixed', 3).last, 0);
  assert.equal(frameState(run, 'photon', 3).last, 3);
});
test('only a skipped PHOTON step can show a saved forecast; labels stay distinct', () => {
  assert.equal(frameState(run, 'photon', 4, true).label, 'PREDICTED');
  assert.equal(frameState(run, 'photon', 4, true).image, '/demo/embryo/b3/predictions/4.png');
  assert.equal(frameState(run, 'photon', 3, true).label, 'MEASURED');
  assert.equal(frameState(run, 'fixed', 3, true).label, 'MEASURED · HELD');
});
test('evaluation URL is unavailable until the explicit reveal action; null is not zero', () => {
  assert.equal(evaluationUrl({evaluation: 'condition/evaluation.json'}, false), null);
  assert.equal(evaluationUrl({evaluation: 'condition/evaluation.json'}, true), '/demo/condition/evaluation.json');
  assert.equal(metricValue(null), 'Pending');
  assert.equal(metricValue(0), '0.000000');
});
