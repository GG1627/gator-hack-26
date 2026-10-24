"""Trusted replay boundary; policies receive metadata/history, never an oracle.

This is API isolation for cooperative research code, not a Python security sandbox.
The runner alone advances the clock. Failed/incomplete runs cannot be evaluated.
"""
from photon.schemas import ObservedFrame


class ReplayOracle:
    def __init__(self, sequence, budget):
        if isinstance(budget, bool) or not isinstance(budget, int) or not 1 <= budget <= sequence.metadata.frame_count:
            raise ValueError("budget must be between 1 and frame count")
        self.__sequence = sequence
        self.__budget = budget
        self.__clock = -1
        self.__acquired = []
        self.__closed = False

    def public_metadata(self):
        return self.__sequence.metadata

    def advance(self, t):
        if self.__closed or t != self.__clock + 1 or not 0 <= t < self.public_metadata().frame_count:
            raise ValueError("Replay must advance one source frame at a time")
        self.__clock = t

    def acquire(self, t):
        if self.__closed or t != self.__clock:
            raise ValueError("Only the current replay time can be acquired")
        if t in self.__acquired or len(self.__acquired) >= self.__budget:
            raise ValueError("Duplicate acquisition or exhausted budget")
        pixels = self.__sequence.read(t).copy()
        pixels.flags.writeable = False
        self.__acquired.append(t)
        return ObservedFrame(t, pixels, source=self.public_metadata().source)

    def finish(self):
        if self.__clock != self.public_metadata().frame_count - 1 or len(self.__acquired) != self.__budget:
            raise ValueError("Cannot finish incomplete replay or unequal acquisition count")
        self.__closed = True
        return tuple(self.__acquired)

    def evaluate_after_run(self, record):
        if not self.__closed or tuple(record.acquired_indices) != tuple(self.__acquired):
            raise ValueError("Evaluation requires a completed matching run")
        count = len(self.__acquired)
        return {"acquisitions": count, "relative_exposure_proxy": count / self.public_metadata().frame_count,
                "reconstruction_mse": None, "event_coverage": None,
                "metric_reasons": {"reconstruction_mse": "No prediction model in Phase 1",
                                   "event_coverage": "Event scoring deferred to Phase 5; annotation audit is separate"}}

    def read_evaluation_after_run(self, record, t):
        """Raw source pixels for trusted offline evaluation only after closure."""
        self.evaluate_after_run(record)
        from photon.schemas import EvaluationFrame
        if isinstance(t, bool) or not isinstance(t, int) or not 0 <= t < self.public_metadata().frame_count:
            raise ValueError("Evaluation index outside source window")
        pixels = self.__sequence.read(t).copy()
        pixels.flags.writeable = False
        return EvaluationFrame(t, pixels, self.public_metadata().source)

    def evaluate_prediction_after_run(self,record,prediction,*,foreground_threshold=0.1):
        """Reveal one withheld target only after closure; no evaluator feedback to policy.

        Errors are normalized 3D/2D signal errors, clipped using the frozen first
        acquired observation's calibration. ROI is a common evaluation-only union
        of forecast, last-observation baseline and truth above a declared threshold.
        This single-target development preview is not a policy benchmark.
        """
        self.evaluate_after_run(record)  # closed/matching acquisition record is mandatory
        import numpy as np
        from photon.gaussian import IntensityCalibration
        from photon.schemas import EvaluationFrame, PredictedFrame
        if not isinstance(prediction,PredictedFrame):
            raise ValueError("Expected a PredictedFrame")
        target = prediction.index
        if not isinstance(target,int) or not 0<=target<self.public_metadata().frame_count or target in self.__acquired:
            raise ValueError("Evaluation target must be a withheld source index")
        expected_history = tuple(t for t in self.__acquired if t<=target)
        if not expected_history or prediction.based_on_indices!=expected_history:
            raise ValueError("Prediction history is incomplete or includes observations after its target")
        if prediction.pixels.shape!=self.public_metadata().shape or not np.isfinite(prediction.pixels).all():
            raise ValueError("Invalid prediction geometry/values")
        if not np.isfinite(foreground_threshold) or not 0<foreground_threshold<1:
            raise ValueError("Foreground threshold must be in (0,1)")
        calibration = IntensityCalibration.from_image(self.__sequence.read(self.__acquired[0]))
        if prediction.normalization!=calibration.to_dict():
            raise ValueError("Prediction calibration must match the first acquired observation")
        truth = calibration.normalize(self.__sequence.read(target))
        baseline = calibration.normalize(self.__sequence.read(expected_history[-1]))
        predicted = prediction.pixels
        if np.any(predicted<0) or np.any(predicted>1):
            raise ValueError("Expected normalized predicted signal in [0,1]")
        error = predicted.astype(np.float64)-truth
        baseline_error = baseline.astype(np.float64)-truth
        roi = np.maximum(np.maximum(predicted,truth),baseline)>foreground_threshold
        metrics = {"target_index":target,"based_on_indices":list(expected_history),
                   "normalization":calibration.to_dict(),"value_space":"first-observation normalized signal clipped to [0,1]",
                   "reconstruction_mse":float(np.mean(error**2)),"reconstruction_mae":float(np.mean(np.abs(error))),
                   "hold_last_mse":float(np.mean(baseline_error**2)),"foreground_threshold":foreground_threshold,
                   "foreground_roi_voxels":int(roi.sum()),
                   "foreground_roi_mse":float(np.mean(error[roi]**2)) if roi.any() else None,
                   "hold_last_foreground_roi_mse":float(np.mean(baseline_error[roi]**2)) if roi.any() else None,
                   "roi_definition":"evaluation-only union of truth, prediction and last observation > threshold",
                   "uncertainty_um":prediction.uncertainty,"uncertainty_calibrated":False,
                   "event_coverage":None,"event_coverage_reason":"No event predictor/policy evaluation in Phase 2",
                   "scope":"single withheld development frame; not adaptive acquisition performance"}
        truth.flags.writeable = False
        return EvaluationFrame(target,truth,self.public_metadata().source),metrics
