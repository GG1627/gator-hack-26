"""Preserve acquired appearance while applying a causal Gaussian intensity delta.

Hypothesis: holding the model's unrepresented residual can avoid the reconstruction
error floor of direct Gaussian rendering. Residual texture is held, not transported;
ghosting, inaccurate motion and unmodeled divisions can still make this worse than
raw hold. No biological or uncertainty-calibration guarantee is implied.
"""
import numpy as np
from photon.gaussian import IntensityCalibration, valid_image
from photon.schemas import ObservedFrame, PredictedFrame


def appearance_forecast(observed, fitted, forecast, calibration):
    """I_hat(t) = clip(I_acquired + G_forecast(t) - G_fit(last_acquisition), 0, 1)."""
    if not isinstance(observed,ObservedFrame) or observed.kind!="MEASURED":
        raise ValueError("A real acquired ObservedFrame is required")
    if not isinstance(fitted,PredictedFrame) or not isinstance(forecast,PredictedFrame):
        raise ValueError("Fit and forecast must carry prediction provenance")
    if not isinstance(calibration,IntensityCalibration):
        raise ValueError("Explicit first-acquisition calibration is required")
    history=forecast.based_on_indices
    if not history or tuple(sorted(set(history)))!=history or history[-1]!=observed.index:
        raise ValueError("Forecast history must end at the supplied acquired image")
    if fitted.index!=observed.index or fitted.based_on_indices!=history or forecast.index<observed.index:
        raise ValueError("Fit and forecast must use the same causal acquisition history")
    if any(frame.normalization!=calibration.to_dict() for frame in [fitted,forecast]):
        raise ValueError("Fit and forecast calibration must agree")
    pixels=valid_image(observed.pixels)
    if any(valid_image(frame.pixels).shape!=pixels.shape for frame in [fitted,forecast]):
        raise ValueError("Measured, fitted and forecast volume shapes must agree")
    delta=np.subtract(forecast.pixels,fitted.pixels,dtype=np.float32)
    prediction=np.clip(calibration.normalize(pixels)+delta,0,1).astype(np.float32)
    prediction.flags.writeable=False
    return PredictedFrame(forecast.index,prediction,history,forecast.uncertainty,
        normalization=calibration.to_dict(),backend="cpu",
        backend_metadata={"method":"experimental_acquired_appearance_plus_gaussian_delta",
                          "upstream_renderer":forecast.backend,
                          "uncertainty_note":"Inherited heuristic position sigma; not calibrated image uncertainty"})
