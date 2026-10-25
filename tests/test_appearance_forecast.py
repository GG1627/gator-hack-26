import numpy as np
import pytest
from photon.gaussian import IntensityCalibration
from photon.schemas import ObservedFrame, PredictedFrame
from experiments.forecasting.appearance import appearance_forecast


def prediction(t,pixels,history=(0,),calibration=None):
    calibration=calibration or IntensityCalibration(0,1,0)
    return PredictedFrame(t,np.asarray(pixels,dtype=np.float32),history,.2,normalization=calibration.to_dict())


def test_zero_predicted_change_preserves_the_acquired_pixels_exactly():
    pixels=np.random.default_rng(42).random((17,19),dtype=np.float32)
    imperfect_fit=pixels*.45
    before=pixels.copy()
    result=appearance_forecast(ObservedFrame(0,pixels,"synthetic"),prediction(0,imperfect_fit),
        prediction(3,imperfect_fit),IntensityCalibration(0,1,0))
    np.testing.assert_array_equal(result.pixels,pixels)
    np.testing.assert_array_equal(pixels,before)
    assert result.based_on_indices==(0,) and not result.pixels.flags.writeable


def test_known_model_change_retains_unmodeled_static_texture():
    y,x=np.indices((25,25))
    before=(.45*np.exp(-((x-10)**2+(y-12)**2)/10)).astype(np.float32)
    after=(.45*np.exp(-((x-12)**2+(y-12)**2)/10)).astype(np.float32)
    texture=(.05*(1+np.sin(x*1.7))).astype(np.float32)
    measured=before+texture;truth=after+texture
    result=appearance_forecast(ObservedFrame(0,measured,"synthetic"),prediction(0,before),
        prediction(2,after),IntensityCalibration(0,1,0))
    np.testing.assert_allclose(result.pixels,truth,atol=1e-7)
    assert np.mean((result.pixels-truth)**2)<np.mean((measured-truth)**2)
    assert np.mean((result.pixels-truth)**2)<np.mean((after-truth)**2)


def test_clipping_and_invalid_provenance_are_explicit():
    observed=ObservedFrame(0,np.array([[.1,.9]],dtype=np.float32),"synthetic")
    fitted=prediction(0,[[1,0]]);future=prediction(1,[[0,1]])
    result=appearance_forecast(observed,fitted,future,IntensityCalibration(0,1,0))
    np.testing.assert_array_equal(result.pixels,[[0,1]])
    with pytest.raises(ValueError,match="acquired ObservedFrame"):
        appearance_forecast(fitted,fitted,future,IntensityCalibration(0,1,0))
    with pytest.raises(ValueError,match="history"):
        appearance_forecast(observed,fitted,prediction(2,[[0,1]],history=(0,1)),IntensityCalibration(0,1,0))
    with pytest.raises(ValueError,match="calibration"):
        appearance_forecast(observed,fitted,future,IntensityCalibration(0,2,0))
