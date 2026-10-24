import importlib.util
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
spec=importlib.util.spec_from_file_location('glimpse_spatial',ROOT/'scripts/build_glimpse_spatial.py')
spatial=importlib.util.module_from_spec(spec)
spec.loader.exec_module(spatial)


def test_physical_covariance_and_ellipsoid_basis_reconstruct_original():
    from photon.gaussian import Gaussian
    covariance=np.array([[4,.3,.4],[.3,9,.5],[.4,.5,16.]])
    g=Gaussian(np.array([2,3,4]),covariance,.8)
    value=spatial.physical_gaussian(g,[.15,.15,.75])
    np.testing.assert_allclose(value['center'],[.6,.45,1.5])
    expected=covariance[::-1,::-1]*np.outer([.15,.15,.75],[.15,.15,.75])
    np.testing.assert_allclose(np.asarray(value['covariance']).reshape(3,3),expected)
    basis=np.asarray(value['basis']).reshape(3,3)
    np.testing.assert_allclose(basis@np.diag(np.square(value['radii']))@basis.T,expected,atol=1e-12)
    assert np.linalg.det(basis)>0


def test_voxel_samples_preserve_coordinates_threshold_and_determinism():
    raw=np.arange(4*9*9,dtype=np.uint16).reshape(4,9,9)
    normalization={'background':0,'scale':400}
    a,eligible=spatial.sample_voxels(raw,normalization,cap=7)
    b,_=spatial.sample_voxels(raw,normalization,cap=7)
    np.testing.assert_array_equal(a,b)
    assert len(a)==7 and eligible>7
    assert np.all(a[:,0]%3==0) and np.all(a[:,1]%3==0)
    values=raw[a[:,2],a[:,1],a[:,0]].astype(np.float32)/400
    assert np.all(values>=.2)
    np.testing.assert_array_equal(a[:,3],np.rint(values*65535).astype(np.uint16))


@pytest.mark.skipif(not (ROOT/'apps/web/public/demo/spatial/manifest.json').exists(),reason='Local spatial export absent')
def test_saved_geometry_points_and_frozen_source_are_exact():
    from photon.development import load_scenes
    import tifffile
    output=ROOT/'apps/web/public/demo/spatial'
    manifest=spatial.read(output/'manifest.json')
    assert len(manifest['conditions'])==6
    assert len(manifest['files'])==546
    for name,digest in manifest['files'].items():
        assert spatial.sha(output/name)==digest
    for key,name in manifest['conditions'].items():
        value=spatial.read(output/name)
        folder=ROOT/'runs/phase5'/key/'photon'
        cfg=spatial.read(folder/'config.json')
        fits=load_scenes(folder/'held_scenes.npz')
        forecasts=load_scenes(folder/'forecasts.npz')
        for filename,digest in value['source_sha256'].items():
            assert spatial.sha(folder/filename)==digest
        for frame in value['frames']:
            t=frame['t'];acquired=cfg['acquired_indices']
            assert frame['source_t']==max(i for i in acquired if i<=t)
            assert frame['kind']==('fit' if t in acquired else 'forecast')
            original=fits[t] if t in acquired else forecasts[t]
            assert frame['gaussians']==[spatial.physical_gaussian(g,cfg['voxel_size_xyz_um']) for g in original]
    for sid in manifest['sequences']:
        cfg=spatial.read(ROOT/f'runs/phase5/{sid}/b54/photon/config.json')
        for t in (0,134,269):
            raw=tifffile.imread(ROOT/f'data/mskcc-audit/mskcc-confocal/{sid}/images/{sid}_t{t:03d}.tif')
            expected,_=spatial.sample_voxels(raw,cfg['normalization'])
            assert (output/f'{sid}/points/{t}.bin').read_bytes()==expected.tobytes()
    protocol=spatial.read(ROOT/'runs/phase5/protocol.json')
    for name,digest in protocol['implementation_hashes'].items():
        assert spatial.sha(ROOT/name)==digest
