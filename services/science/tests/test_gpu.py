import json
from pathlib import Path
import struct
import subprocess

import numpy as np
import pytest

from photon.gaussian import Gaussian, render_gaussians
from photon.gpu import (CudaRustRunner, GPUUnavailable, boundary_reference, pack_batch,
                        render_gaussian_batch)
from photon.schemas import ObservedFrame
from photon.tracking import GaussianSceneModel


def scene(ndim=3):
    if ndim == 2:
        return [Gaussian(np.array([5.1,7.3]),np.array([[3.,.7],[.7,6.]]),.8)]
    return [Gaussian(np.array([3.1,5.1,7.3]),np.array([[1.,.2,0],[.2,3.,.7],[0,.7,6.]]),.8)]


@pytest.mark.parametrize("shape", [(17,19),(9,17,19)])
def test_packed_precision_and_analytic_boundary_values(shape):
    objects = scene(len(shape))
    objects += [Gaussian(np.zeros(len(shape)),np.eye(len(shape)),.6)]
    origin = Gaussian(np.zeros(len(shape)),np.eye(len(shape)),.6)
    coordinates = [tuple([0]*len(shape)),tuple([0]*(len(shape)-1)+[4]),tuple([0]*(len(shape)-1)+[5])]
    indices = np.array([np.ravel_multi_index(point,shape) for point in coordinates])
    np.testing.assert_allclose(boundary_reference(shape,[origin],indices),[.6,.6*np.exp(-8),0],rtol=2e-6,atol=1e-8)
    packed_shape,counts,packed = pack_batch(shape,[objects,[]])
    assert len(packed_shape)==3 and counts==[2,0] and packed.dtype==np.float64
    np.testing.assert_allclose(packed[0,0,13],abs(packed[0,0,3:12]).sum())


def test_fallback_is_explicit_and_numerical_failures_are_not_hidden(tmp_path):
    missing = CudaRustRunner(tmp_path/"missing")
    result = render_gaussian_batch((17,19),[scene(2)],backend="auto",runner=missing)
    assert result.metadata["backend"]=="cpu" and "missing" in result.metadata["fallback_reason"]
    np.testing.assert_array_equal(result.pixels[0],render_gaussians((17,19),scene(2)))
    with pytest.raises(GPUUnavailable):
        render_gaussian_batch((17,19),[scene(2)],backend="cuda-rust",runner=missing)
    class Broken:
        def render(self,*args,**kwargs):
            raise RuntimeError("invalid GPU numerical output")
    with pytest.raises(RuntimeError,match="numerical"):
        render_gaussian_batch((17,19),[scene(2)],backend="auto",runner=Broken())


def test_resource_and_numerical_domain_validation():
    for shape in ((0,2),(True,2),(3.,4),(4096,4096,4096)):
        with pytest.raises(ValueError):
            render_gaussian_batch(shape,[[]])
    with pytest.raises(ValueError):
        pack_batch((4,4),[scene(3)])
    with pytest.raises(GPUUnavailable):
        pack_batch((4,4),[[Gaussian(np.array([1e100,1e100]),np.eye(2),1)]])
    with pytest.raises(GPUUnavailable):
        pack_batch((4,4),[[scene(2)[0]]*10001])
    assert render_gaussian_batch((4,4),[]).pixels.shape==(0,4,4)


def test_vectorized_pack_matches_individual_inverse_and_domain_checks():
    for ndim in (2,3):
        rng = np.random.default_rng(15)
        objects = []
        for _ in range(113):
            a = rng.normal(size=(ndim,ndim))
            objects.append(Gaussian(rng.uniform(0,20,ndim),a@a.T+np.eye(ndim),.7))
        _,_,packed = pack_batch((32,)*ndim,[objects,[]])
        for i,g in enumerate(objects):
            cov = g.covariance if ndim==3 else np.block([[np.ones((1,1)),np.zeros((1,2))],[np.zeros((2,1)),g.covariance]])
            np.testing.assert_array_equal(packed[0,i,3:12],np.linalg.inv(cov).ravel())
        with pytest.raises(GPUUnavailable):
            pack_batch((32,)*ndim,[[Gaussian(np.ones(ndim),np.diag([1e-9]+[1.]*(ndim-1)),.7)]])


def test_worker_timeout_closes_process_and_auto_falls_back(monkeypatch):
    import os
    import sys
    runner = CudaRustRunner(sys.executable,persistent=True,timeout=1)
    script = 'import time; print(\'{"ready":true,"context_ms":0}\',flush=True); time.sleep(30)'
    monkeypatch.setattr(runner,"command",lambda *args:([sys.executable,"-u","-c",script],os.environ.copy()))
    actual = render_gaussian_batch((17,19),[scene(2)],backend="auto",runner=runner)
    assert actual.metadata["backend"]=="cpu" and "timed out" in actual.metadata["fallback_reason"]
    assert runner._process is None and runner._stderr is None


GPU = pytest.mark.skipif(not CudaRustRunner().binary.is_file(),reason="native CUDA Rust binary not built")


@GPU
def test_worker_reuses_context_handles_changed_data_and_closes():
    with CudaRustRunner(persistent=True) as worker:
        for shape,objects in [((17,19),[scene(2)]),((17,19),[[]]),
                              ((17,19),[scene(2),[]]),((9,17,19),[scene()])]:
            actual = worker.render(shape,objects)
            np.testing.assert_allclose(actual.pixels,render_gaussian_batch(shape,objects).pixels,rtol=2e-4,atol=2e-5)
        process = worker._process
        warm = worker.render((9,17,19),[scene()])
        assert worker._process is process
        assert warm.metadata["jit_backend_compiles"]==0 and warm.metadata["jit_disk_hits"]==0
        assert warm.metadata["transport"]=="persistent-worker"
        boundary = [[Gaussian(np.array([8.,8.]),np.eye(2),.8)]]
        repaired = worker.render((17,19),boundary)
        assert repaired.metadata["cpu_boundary_repair_voxels"][0]>0
        np.testing.assert_allclose(repaired.pixels,render_gaussian_batch((17,19),boundary).pixels,rtol=2e-4,atol=2e-5)
    assert process.poll()==0 and worker._process is None


@GPU
def test_worker_death_falls_back_then_can_restart():
    with CudaRustRunner(persistent=True) as worker:
        worker.render((17,19),[scene(2)])
        worker._process.kill()
        worker._process.wait(timeout=10)
        actual = render_gaussian_batch((17,19),[scene(2)],backend="auto",runner=worker)
        assert actual.metadata["backend"]=="cpu" and worker._process is None
        assert worker.render((17,19),[scene(2)]).metadata["kernel_executed"]


@GPU
def test_native_parity_batch_empty_rotated_boundary_and_large_gaussian_counts(tmp_path):
    runner = CudaRustRunner()
    cases = [((9,17,19),[scene(),[]]),
             ((17,19),[[Gaussian(np.array([8.,8.]),np.eye(2),.8)],scene(2)]),
             ((3,5,7),[[Gaussian(np.array([1.2,2.1,3.3]),np.diag([.1,2.,3.]),.003)]*10000])]
    evidence = []
    for shape,objects in cases:
        reference = render_gaussian_batch(shape,objects)
        actual = runner.render(shape,objects)
        np.testing.assert_allclose(actual.pixels,reference.pixels,rtol=2e-4,atol=2e-5)
        assert actual.metadata["kernel_executed"]
        evidence.append({"shape":shape,"max_absolute_error":float(np.max(abs(actual.pixels-reference.pixels))),
                         "repaired_voxels":actual.metadata["cpu_boundary_repair_voxels"]})
    assert evidence[1]["repaired_voxels"][0]>0  # four-sigma integer-grid boundary is exercised


@GPU
def test_prediction_and_uncertainty_map_use_batched_native_kernel():
    model = GaussianSceneModel((.75,.15,.15))
    pixels = render_gaussians((9,17,19),scene())
    model.observe(ObservedFrame(0,pixels,"synthetic"))
    cpu = model.predict(2,include_uncertainty_map=True)
    gpu = model.predict(2,include_uncertainty_map=True,backend="cuda-rust")
    assert gpu.backend=="cuda-rust" and gpu.backend_metadata["batch"]==7
    assert gpu.based_on_indices==cpu.based_on_indices==(0,)
    np.testing.assert_allclose(gpu.pixels,cpu.pixels,rtol=2e-4,atol=2e-5)
    np.testing.assert_allclose(gpu.uncertainty_map,cpu.uncertainty_map,rtol=3e-4,atol=3e-5)
    assert not gpu.pixels.flags.writeable and not gpu.uncertainty_map.flags.writeable


@GPU
def test_large_volume_exceeds_original_cuda_y_grid_limit():
    shape = (33,512,512)  # 67584 tiles: exceeds the original grid-Y limit of65535
    objects = [[Gaussian(np.array([16.,256.,256.]),np.diag([2.,9.,9.]),.8)]]
    cpu = render_gaussian_batch(shape,objects)
    gpu = render_gaussian_batch(shape,objects,backend="cuda-rust")
    np.testing.assert_allclose(gpu.pixels,cpu.pixels,rtol=2e-4,atol=2e-5)
    assert gpu.metadata["kernel_executed"]


@GPU
def test_rotated_near_cutoff_repairs_preserve_reference_inclusion_exactly():
    rng = np.random.default_rng(17)
    scenes = []
    for _ in range(12):
        a = rng.normal(size=(2,2))*.3
        covariance = a@a.T+np.eye(2)*.5
        delta = 4*np.linalg.cholesky(covariance)[:,0]
        scenes.append([Gaussian(np.array([8.,8.])-delta,covariance,1e5)])
    cpu = render_gaussian_batch((17,19),scenes)
    gpu = render_gaussian_batch((17,19),scenes,backend="cuda-rust")
    assert all(n>0 for n in gpu.metadata["cpu_boundary_repair_voxels"])
    np.testing.assert_array_equal(gpu.pixels[:,8,8],cpu.pixels[:,8,8])
    np.testing.assert_allclose(gpu.pixels,cpu.pixels,rtol=2e-4,atol=2e-5)


@GPU
def test_native_rejects_malformed_payload_without_allocating_gpu(tmp_path):
    runner = CudaRustRunner()
    header = json.dumps({"version":1,"shape":[4096,4096,4096],"counts":[0],"repeats":0}).encode()
    request = tmp_path/"bad.bin"
    request.write_bytes(b"PHOTON01"+struct.pack("<I",len(header))+header+bytes(128))
    from photon.gpu import _linux_path
    import os
    command = [str(runner.binary),str(request),str(tmp_path/"out.bin")]
    if os.name=="nt":
        command = ["wsl","-d","Ubuntu-22.04","--exec",_linux_path(runner.binary),_linux_path(request),_linux_path(tmp_path/"out.bin")]
    completed = subprocess.run(command,capture_output=True,timeout=30)
    assert completed.returncode!=0 and b"safety limit" in completed.stderr
    assert not (tmp_path/"out.bin").exists()
