import numpy as np
import pytest

from photon.gaussian import (Gaussian, GaussianFitConfig, IntensityCalibration,
                             detect_and_fit, fit_component, render_gaussians)


@pytest.mark.parametrize("shape,center,covariance",[
    ((65,65),[31.3,32.6],[[9,2],[2,16]]),
    ((33,65,65),[16.1,31.8,32.2],[[2.25,0.5,0],[0.5,9,1],[0,1,16]]),
])
def test_moments_recover_analytic_center_covariance(shape,center,covariance):
    expected = Gaussian(np.array(center),np.array(covariance),0.7)
    signal = render_gaussians(shape,[expected],truncate=8,clip_max=None)
    recovered = fit_component(signal,np.ones(shape,dtype=bool),covariance_floor=0.01)
    np.testing.assert_allclose(recovered.center,center,atol=2e-4)
    np.testing.assert_allclose(recovered.covariance,covariance,rtol=2e-4,atol=2e-4)
    assert recovered.amplitude == pytest.approx(0.7,rel=2e-4)
    config = GaussianFitConfig(min_signal=1e-5,noise_multiplier=0,smoothing_um=0,min_voxels=4,covariance_floor_voxels=0.01)
    components,_ = detect_and_fit(signal,np.ones(len(shape)),0,config)
    assert len(components)==1
    np.testing.assert_allclose(components[0].center,center,atol=0.01)
    # Explicitly tolerate tail truncation by the segmentation threshold.
    np.testing.assert_allclose(components[0].covariance,covariance,rtol=0.015,atol=0.015)


def test_renderer_matches_independent_rotated_gaussian_formula():
    center = np.array([4.,5.])
    covariance = np.array([[2.,0.6],[0.6,3.]])
    g = Gaussian(center,covariance,0.8)
    result = render_gaussians((9,11),[g],truncate=10,clip_max=None)
    expected = np.empty((9,11))
    for y in range(9):
        for x in range(11):
            offset = np.array([y,x])-center
            expected[y,x] = 0.8*np.exp(-0.5*offset@np.linalg.solve(covariance,offset))
    np.testing.assert_allclose(result,expected,rtol=2e-6,atol=1e-7)
    assert result.dtype == np.float32
    assert result[4,5] == pytest.approx(0.8)
    clipped = render_gaussians((9,11),[g,g])
    assert clipped.max()==1 and clipped.min()>=0 and np.isfinite(clipped).all()
    assert not render_gaussians((9,11),[]).any()


def test_thin_and_boundary_components_are_stable():
    signal = np.zeros((3,5,5),dtype=np.float32)
    signal[0,0,0] = 1
    component = fit_component(signal,signal>0)
    assert np.linalg.eigvalsh(component.covariance).min()>0
    rendered = render_gaussians(signal.shape,[component])
    assert np.isfinite(rendered).all() and rendered[0,0,0]>0
    outside = Gaussian(np.array([1e100,1e100]),np.eye(2),1)
    assert not render_gaussians((3,3),[outside]).any()


def test_calibration_is_finite_on_dark_constant_and_invalid_images():
    dark = np.zeros((4,8,8),dtype=np.uint16)
    calibration = IntensityCalibration.from_image(dark)
    assert np.isfinite(calibration.normalize(dark)).all()
    assert not calibration.normalize(dark).any()
    for image in (np.full((3,3),np.nan),np.full((3,3),np.inf),np.zeros((3,3),dtype=complex)):
        with pytest.raises(ValueError):
            IntensityCalibration.from_image(image)
    with pytest.raises(ValueError):
        Gaussian(np.zeros(2),np.array([[1,2],[2,1]]),1)
    with pytest.raises(ValueError):
        Gaussian(np.zeros(2),np.eye(2),np.nan)
    with pytest.raises(ValueError):
        fit_component(np.zeros((3,3)),np.zeros((3,3),dtype=bool))
    with pytest.raises(ValueError):
        render_gaussians((3,3),[],truncate=-1)
