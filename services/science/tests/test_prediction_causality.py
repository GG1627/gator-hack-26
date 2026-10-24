from types import SimpleNamespace

import numpy as np
import pytest

from photon.data import SequenceMetadata
from photon.gaussian import Gaussian, GaussianFitConfig, render_gaussians
from photon.oracle import ReplayOracle
from photon.replay import RunRecord
from photon.tracking import GaussianSceneModel, TrackingConfig


def frames():
    return [render_gaussians((41,41),[Gaussian(np.array([20.,14+t]),np.eye(2)*4,0.8)],truncate=8,clip_max=None) for t in range(6)]


def execute(clip):
    reads=[]
    def read(t):
        reads.append(t)
        return clip[t]
    sequence = SimpleNamespace(metadata=SequenceMetadata("synthetic-test","01",6,(41,41),"float32",source="synthetic"),read=read)
    oracle = ReplayOracle(sequence,2)
    model = GaussianSceneModel((1.,1.),fit_config=GaussianFitConfig(min_signal=1e-4,smoothing_um=0,min_voxels=3),
                               tracking_config=TrackingConfig(damping_per_frame=0,velocity_smoothing=1))
    prediction=None
    for t in range(6):
        oracle.advance(t)
        if t in (0,2):
            model.observe(oracle.acquire(t))
        if t==3:
            prediction = model.predict(t,include_uncertainty_map=True)
            with pytest.raises(ValueError,match="completed"):
                oracle.evaluate_prediction_after_run(RunRecord("test",0,2,(0,2),()),prediction)
            assert reads==[0,2]
    record = RunRecord("test",0,2,oracle.finish(),())
    assert reads==[0,2]
    truth,metrics = oracle.evaluate_prediction_after_run(record,prediction)
    assert reads==[0,2,0,3,2]
    assert truth.kind=="GROUND TRUTH (EVAL ONLY)"
    return prediction,truth,metrics


def test_unseen_frames_cannot_change_predictions_but_change_posthoc_error():
    first = frames()
    changed = [frame.copy() for frame in first]
    for t in (1,3,4,5):
        changed[t] = np.random.default_rng(t).uniform(0,1,first[t].shape).astype(np.float32)
    a,_,metrics_a = execute(first)
    b,_,metrics_b = execute(changed)
    np.testing.assert_array_equal(a.pixels,b.pixels)
    np.testing.assert_array_equal(a.uncertainty_map,b.uncertainty_map)
    assert a.uncertainty==b.uncertainty and a.based_on_indices==b.based_on_indices==(0,2)
    assert metrics_a["reconstruction_mse"]<metrics_b["reconstruction_mse"]
    assert metrics_a["reconstruction_mse"]<metrics_a["hold_last_mse"]


def test_posthoc_scores_match_independent_array_computation():
    prediction,truth,metrics = execute(frames())
    expected=np.mean((prediction.pixels.astype(float)-truth.pixels)**2)
    assert metrics["reconstruction_mse"]==pytest.approx(expected,abs=1e-12)
    assert metrics["uncertainty_calibrated"] is False
