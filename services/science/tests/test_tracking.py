import numpy as np
import pytest

from photon.gaussian import Gaussian, GaussianFitConfig, render_gaussians
from photon.schemas import ObservedFrame
from photon.tracking import GaussianSceneModel, TrackingConfig


def image(center,*,amplitude=0.8,covariance=None):
    covariance = np.eye(2)*4 if covariance is None else covariance
    return render_gaussians((65,65),[Gaussian(np.array(center),covariance,amplitude)],truncate=8,clip_max=None)


def make_model(**tracking):
    return GaussianSceneModel((1.,1.),fit_config=GaussianFitConfig(min_signal=1e-4,noise_multiplier=0,smoothing_um=0,min_voxels=3),
                              tracking_config=TrackingConfig(**tracking))


def test_constant_velocity_forecast_uses_actual_source_time_gaps():
    model = make_model(damping_per_frame=0,velocity_smoothing=1)
    model.observe(ObservedFrame(0,image([30,25]),"synthetic"))
    identifier = next(iter(model.tracks))
    original = model.tracks[identifier]
    model.observe(ObservedFrame(2,image([30,29]),"synthetic"))
    assert list(model.tracks)==[identifier]
    np.testing.assert_allclose(model.tracks[identifier].velocity,[0,2],atol=0.01)
    prediction = model.predict(4,include_uncertainty_map=True)
    assert prediction.kind=="PREDICTED" and prediction.based_on_indices==(0,2)
    np.testing.assert_allclose(model.scene_at(4)[0].center,[30,33],atol=0.02)
    assert np.unravel_index(np.argmax(prediction.pixels),prediction.pixels.shape)==(30,33)
    np.testing.assert_array_equal(prediction.pixels,model.predict(4).pixels)
    np.testing.assert_array_equal(prediction.uncertainty_map,model.predict(4,include_uncertainty_map=True).uncertainty_map)
    # Earlier immutable track snapshots must not be rewritten by observations.
    np.testing.assert_allclose(original.gaussian.center,[30,25],atol=0.01)


def test_uncertainty_grows_without_acquisition_even_for_empty_state():
    for pixels in (image([30,30]),np.zeros((65,65),dtype=np.float32)):
        model = make_model()
        model.observe(ObservedFrame(0,pixels,"synthetic"))
        values = [model.predict(t).uncertainty for t in (0,1,5,20)]
        assert np.all(np.diff(values)>0)
        assert np.isfinite(values).all()


def test_split_candidates_get_new_ids_and_preserve_mother_snapshot():
    fit = GaussianFitConfig(min_signal=0.4,noise_multiplier=0,smoothing_um=0,min_voxels=3)
    model = GaussianSceneModel((1.,1.),fit_config=fit,tracking_config=TrackingConfig(split_gate_um=5))
    model.observe(ObservedFrame(0,image([32,32],covariance=np.eye(2)*9),"synthetic"))
    mother = next(iter(model.tracks.values()))
    children = image([32,28],amplitude=1,covariance=np.eye(2)*2.25)+image([32,36],amplitude=1,covariance=np.eye(2)*2.25)
    model.observe(ObservedFrame(1,children,"synthetic"))
    assert len(model.tracks)==2 and mother.identifier not in model.tracks
    assert all(t.parent_hint==mother.identifier for t in model.tracks.values())
    assert any(e["kind"]=="candidate_split" for e in model.observation_log[-1]["events"])
    np.testing.assert_allclose(mother.gaussian.center,[32,32],atol=0.01)


def test_unexpected_birth_and_disappearance_are_explicit():
    model = make_model()
    model.observe(ObservedFrame(0,image([20,20]),"synthetic"))
    old = next(iter(model.tracks))
    model.observe(ObservedFrame(1,image([20,20])+image([45,45]),"synthetic"))
    assert len(model.tracks)==2 and old in model.tracks
    assert any(e["kind"]=="birth_or_unmatched_detection" for e in model.observation_log[-1]["events"])
    model.observe(ObservedFrame(2,np.zeros((65,65)),"synthetic"))
    assert not model.tracks
    assert len([e for e in model.observation_log[-1]["events"] if e["kind"]=="retired_unmatched_track"])==2


def test_no_prediction_before_observation_or_retroactive_update():
    model = make_model()
    with pytest.raises(ValueError):
        model.predict(0)
    model.observe(ObservedFrame(2,image([20,20]),"synthetic"))
    for t in (0,1,2):
        with pytest.raises(ValueError):
            model.observe(ObservedFrame(t,image([20,20]),"synthetic"))
    with pytest.raises(ValueError):
        model.predict(1)
    with pytest.raises(ValueError):
        model.predict(True)


def test_assignment_gate_uses_physical_zyx_spacing():
    def volume(center):
        return render_gaussians((17,33,33),[Gaussian(np.array(center),np.diag([1.,4.,4.]),0.8)],truncate=8,clip_max=None)
    for center,should_match in (([5,16,20],True),([9,16,16],False)):
        model = GaussianSceneModel((0.75,0.15,0.15),
            fit_config=GaussianFitConfig(min_signal=1e-4,noise_multiplier=0,smoothing_um=0,min_voxels=3),
            tracking_config=TrackingConfig(assignment_gate_um=1,detect_candidate_splits=False))
        model.observe(ObservedFrame(0,volume([5,16,16]),"synthetic"))
        initial = next(iter(model.tracks))
        model.observe(ObservedFrame(1,volume(center),"synthetic"))
        assert (initial in model.tracks) == should_match


def test_predicted_or_evaluation_frames_cannot_be_observations():
    from photon.schemas import EvaluationFrame
    model = make_model()
    model.observe(ObservedFrame(0,image([20,20]),"synthetic"))
    for not_observed in (model.predict(1),EvaluationFrame(1,image([20,20]),"synthetic")):
        with pytest.raises(ValueError,match="acquired ObservedFrame"):
            model.observe(not_observed)
