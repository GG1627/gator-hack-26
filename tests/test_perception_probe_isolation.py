import importlib.util
from pathlib import Path
import numpy as np
import pytest
import photon.tracking as canonical
from photon.schemas import ObservedFrame, PredictedFrame

spec = importlib.util.spec_from_file_location("probe",Path(__file__).parents[1]/"scripts/probe_perception_forecasts.py")
probe = importlib.util.module_from_spec(spec)
spec.loader.exec_module(probe)


def test_private_detector_does_not_mutate_canonical_tracker():
    original = canonical.detect_and_fit
    candidate = probe.candidate_tracking_module()
    assert canonical.detect_and_fit is original
    assert candidate.GaussianSceneModel is not canonical.GaussianSceneModel
    assert candidate.detect_and_fit is not original
    image = np.zeros((24,24),dtype=np.float32);image[8:16,8:16]=1
    model = candidate.GaussianSceneModel([1,1])
    model.observe(ObservedFrame(0,image,"synthetic"))
    result = model.predict(2)
    assert result.based_on_indices==(0,)
    assert np.isfinite(result.pixels).all()
    with pytest.raises(ValueError,match="acquired ObservedFrame"):
        model.observe(PredictedFrame(2,image,(0,),0.1))
    assert canonical.detect_and_fit is original
