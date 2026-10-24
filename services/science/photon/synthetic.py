"""Deterministic 2D+t TEST DATA, not real microscopy or model predictions.

One Gaussian nucleus drifts right; at frame 4 it becomes two separating blobs.
Additive Gaussian noise is clipped into [0, 1]. All times are source-frame
indices, with no claim about biological cadence. Full clips belong only in
fixtures/oracles, never in controller state.
"""

import numpy as np
from numpy.typing import NDArray


def make_synthetic_clip(seed: int = 42) -> NDArray[np.float32]:
    """Return eight 32x32 float32 frames using a local seeded generator."""
    rng = np.random.default_rng(seed)
    y, x = np.mgrid[:32, :32]
    frames = []
    for t in range(8):
        center_x = 12 + 0.5 * t
        centers = [(16.0, center_x)] if t < 4 else [
            (16 - (t - 3), center_x), (16 + (t - 3), center_x)
        ]
        image = np.zeros((32, 32), dtype=np.float64)
        for cy, cx in centers:
            image += 0.65 * np.exp(-0.5 * (((x - cx) / 2) ** 2 + ((y - cy) / 2) ** 2))
        image += rng.normal(0, 0.005, image.shape)
        frames.append(np.clip(image, 0, 1).astype(np.float32))
    return np.stack(frames)
