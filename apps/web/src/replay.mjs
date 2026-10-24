/** @type {Record<string, string>} */
export const names = { fixed: 'Fixed timing', photon: 'Glimpse adaptive', image_change: 'Image change', random_7: 'Random · seed 7', random_42: 'Random · seed 42', random_2026: 'Random · seed 2026' };

// The replay is a viewer of a closed experiment. No policy runs in this process.
// Even though the whole schedule is available, image selection uses only <= t.
export function frameState(run, method, t, gaussian = false) {
  const indices = run.methods[method].config.acquired_indices;
  const past = indices.filter(index => index <= t);
  if (!past.length) throw new Error('No acquired measurement at this replay time');
  const last = past[past.length - 1];
  const measured = last === t;
  const predicted = !measured && gaussian && method === 'photon';
  return {
    last, count: past.length, measured, predicted,
    label: measured ? 'MEASURED' : predicted ? 'PREDICTED' : 'MEASURED · HELD',
    image: predicted ? `/demo/${run.key}/predictions/${t}.png` : `/demo/images/${run.sequence_id}/${last}.png`,
  };
}

export function evaluationUrl(condition, revealed) {
  return revealed ? `/demo/${condition.evaluation}` : null;
}

export function metricValue(value, digits = 6) {
  return value == null ? 'Pending' : Number(value).toFixed(digits);
}

/** @type {Record<string, string>} */
export const reasonText = {
  mandatory_initial: 'Acquire the first observation to initialize the model.',
  minimum_gap: 'Skip: the minimum interval since the last observation has not elapsed.',
  priority_threshold: 'Acquire: the causal priority reached its threshold.',
  below_priority_threshold: 'Skip: priority remains below the acquisition threshold.',
  reserve_for_future_coverage: 'Skip: preserve budget for coverage later in the experiment.',
  max_gap_due: 'Acquire: the maximum permitted observation gap is due.',
  budget_exhausted: 'Skip: the image budget has been used.',
  pacing_limit: 'Skip: pace acquisitions across the remaining experiment.',
  pacing_reservation: 'Skip: pace acquisitions across the remaining experiment.',
};
