// XYZ physical coordinates -> Three world (X, Z, -Y), a proper rigid rotation.
// The same transformation applies to centers, covariance and eigenvectors.
export function worldPoint(xyz, origin) {
  return [xyz[0] - origin[0], xyz[2] - origin[2], -(xyz[1] - origin[1])];
}

export function worldCovariance(c) {
  return [c[0], c[2], -c[1], c[6], c[8], -c[7], -c[3], -c[5], c[4]];
}

export function projectCovariance(c, right, up) {
  const product = (a, b) => a.reduce((sum, ai, i) => sum + ai * b.reduce((s, bj, j) => s + c[i * 3 + j] * bj, 0), 0);
  return [product(right, right), product(right, up), product(up, up)];
}

export function pointCloudUrl(run, t) {
  const acquired = run.methods.photon.config.acquired_indices.filter(i => i <= t);
  if (!acquired.length) throw new Error('No acquired point cloud at this replay time');
  return `/demo/spatial/${run.sequence_id}/points/${acquired.at(-1)}.bin`;
}

export function contactSlots(run, method, t, count = 18, windowSize = 72) {
  const indices = run.methods[method].config.acquired_indices;
  const total = Math.min(run.frame_count, windowSize);
  const rangeStart = Math.max(0, Math.min(Math.floor(t - total / 2), run.frame_count - total));
  return Array.from({length: count}, (_, slot) => {
    const start = rangeStart + Math.floor(slot * total / count);
    const end = rangeStart + Math.floor((slot + 1) * total / count) - 1;
    const past = indices.filter(i => i >= start && i <= Math.min(t, end));
    return {start, end, indices: past, imageIndex: past.length ? past.at(-1) : null,
      kind: start > t ? 'future' : past.length ? 'acquired' : 'skipped'};
  });
}
