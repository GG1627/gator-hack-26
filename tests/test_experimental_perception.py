import numpy as np
import pytest
from photon.gaussian import GaussianFitConfig, detect_and_fit
from experiments.perception.watershed import WatershedConfig, watershed_and_fit


def touching_pair():
    spacing = np.array([0.6,0.2,0.2])
    z,y,x = np.indices((17,45,65))*spacing[:,None,None,None]
    image = sum(np.exp(-0.5*(((z-4.8)/0.9)**2+((y-4.4)/0.9)**2+((x-c)/0.9)**2)) for c in [4.5,7.5])
    return image,spacing


def test_splits_touching_anisotropic_nuclei_and_preserves_foreground():
    image,spacing = touching_pair()
    config = GaussianFitConfig(min_voxels=8)
    baseline,_ = detect_and_fit(image,spacing,0,config)
    components,diagnostics,labels = watershed_and_fit(image,spacing,0,config)
    assert len(baseline)==1
    assert len(components)==2
    centers = sorted([component.center*spacing for component in components],key=lambda c:c[2])
    np.testing.assert_allclose(centers,[[4.8,4.4,4.5],[4.8,4.4,7.5]],atol=0.25)
    assert diagnostics["retained_foreground_fraction"]==1.0
    assert np.count_nonzero(labels)==sum(component.voxel_count for component in components)


def test_splits_before_upper_size_rejection():
    image,spacing = touching_pair()
    config = GaussianFitConfig(min_voxels=8,max_voxels=2000)
    baseline,_ = detect_and_fit(image,spacing,0,config)
    components,_,_ = watershed_and_fit(image,spacing,0,config)
    assert len(baseline)==0
    assert len(components)==2


def test_empty_signal_and_invalid_physical_spacing():
    image = np.zeros((5,7,9))
    components,diagnostics,labels = watershed_and_fit(image,[1,1,1],0)
    assert not components and diagnostics["markers"]==0 and not labels.any()
    with pytest.raises(ValueError,match="Spacing"):
        watershed_and_fit(image,[1,0,1],0)
    with pytest.raises(ValueError):
        WatershedConfig(peak_radius_um=float('nan'))


def test_plateau_has_one_seed_and_inputs_are_unchanged():
    image = np.zeros((20,20));image[5:15,5:15]=1
    before = image.copy()
    config = GaussianFitConfig(smoothing_um=0,min_voxels=4)
    components,diagnostics,_ = watershed_and_fit(image,[1,1],0,config)
    assert len(components)==diagnostics["markers"]==1
    np.testing.assert_array_equal(image,before)


def test_neighbor_suppression_does_not_drop_disconnected_dim_component():
    image = np.zeros((30,30))
    image[10:13,10:13]=1.0
    image[10:13,14:17]=0.3
    config = GaussianFitConfig(smoothing_um=0,min_voxels=4)
    components,diagnostics,labels = watershed_and_fit(image,[1,1],0,config,
        WatershedConfig(seed_smoothing_um=0.1,peak_radius_um=5))
    assert len(components)==diagnostics["markers"]==2
    assert np.count_nonzero(labels)==18


def test_marker_resource_limit_fails_explicitly():
    image,spacing = touching_pair()
    with pytest.raises(ValueError,match="Marker limit"):
        watershed_and_fit(image,spacing,0,GaussianFitConfig(max_components=1))
