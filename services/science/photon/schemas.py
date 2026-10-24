"""Separate measured observations from model outputs at API boundaries.

Synthetic measurements must carry synthetic provenance. These containers do not
grant access to a sequence; Phase 1 will enforce acquisition via the replay oracle.
"""

from dataclasses import dataclass, field
from typing import Literal

import numpy as np
from numpy.typing import NDArray


@dataclass(frozen=True)
class ObservedFrame:
    index: int
    pixels: NDArray[np.uint8 | np.uint16 | np.float32]
    source: Literal["synthetic", "microscopy"]
    kind: Literal["MEASURED"] = field(default="MEASURED", init=False)


@dataclass(frozen=True)
class PredictedFrame:
    index: int
    pixels: NDArray[np.float32]
    based_on_indices: tuple[int, ...]
    uncertainty: float
    kind: Literal["PREDICTED"] = field(default="PREDICTED", init=False)
    uncertainty_map: NDArray[np.float32] | None = None
    normalization: dict | None = None
    uncertainty_kind: str = "heuristic position RMS in micrometers"
    backend: str = "cpu"
    backend_metadata: dict | None = None


@dataclass(frozen=True)
class EvaluationFrame:
    index: int
    pixels: NDArray[np.float32]
    source: Literal["synthetic", "microscopy"]
    kind: Literal["GROUND TRUTH (EVAL ONLY)"] = field(default="GROUND TRUTH (EVAL ONLY)", init=False)
