"""Checked CPU/CUDA Rust batch renderer. No frame source, oracle or labels.

The original CPU renderer remains the reference. GPU geometry is FP64; values
are FP32. Voxels near the discontinuous truncation boundary are recomputed on
CPU. `auto` records why it fell back; explicit CUDA never claims CPU work as GPU.
"""
from dataclasses import dataclass
import hashlib
import json
import math
import os
from pathlib import Path, PureWindowsPath
import shutil
import struct
import subprocess
import tempfile
import queue
import threading
from time import perf_counter

import numpy as np

from photon.gaussian import Gaussian, render_gaussians


class GPUUnavailable(RuntimeError):
    pass


@dataclass(frozen=True)
class RenderBatch:
    pixels: np.ndarray
    metadata: dict


def validate_batch(shape, scenes):
    shape = tuple(shape)
    if len(shape) not in (2, 3) or any(isinstance(d, bool) or not isinstance(d, (int, np.integer)) or d < 1 for d in shape):
        raise ValueError("Expected a positive 2D/3D render shape")
    shape = tuple(int(d) for d in shape)
    scenes = tuple(tuple(scene) for scene in scenes)
    if math.prod(shape)*len(scenes) > 128*1024*1024:
        raise ValueError("Render batch exceeds 128M-voxel safety limit")
    for scene in scenes:
        if any(not isinstance(g, Gaussian) or g.center.size != len(shape) for g in scene):
            raise ValueError("Scene contains invalid Gaussian dimensions/types")
    return shape, scenes


def pack_batch(shape, scenes):
    shape, scenes = validate_batch(shape, scenes)
    if len(scenes) > 64 or max(shape) > 4096 or np.prod(shape, dtype=np.int64)*len(scenes) > 128*1024*1024:
        raise GPUUnavailable("Batch exceeds validated CUDA dimensions/memory limit")
    counts = [len(scene) for scene in scenes]
    if max(counts, default=0) > 10_000:
        raise GPUUnavailable("CUDA supports at most 10000 Gaussians per scene")
    packed = np.zeros((len(scenes), max(1, max(counts, default=0)), 16), dtype="<f8")
    for b, scene in enumerate(scenes):
        if not scene:
            continue
        centers = np.stack([g.center for g in scene])
        covariances = np.stack([g.covariance for g in scene])
        amplitudes = np.array([g.amplitude for g in scene])
        eigenvalues = np.linalg.eigvalsh(covariances)
        if (np.max(np.abs(centers)) > 1e6 or eigenvalues.min() < 1e-8 or eigenvalues.max() > 1e8
                or np.any(eigenvalues[:, -1]/eigenvalues[:, 0] > 1e6) or amplitudes.max() > 1e6):
            raise GPUUnavailable("Gaussian outside validated CUDA numerical domain; CPU reference available")
        if len(shape) == 2:
            centers = np.pad(centers, ((0, 0), (1, 0)))
            covariances = np.pad(covariances, ((0, 0), (1, 0), (1, 0)))
            covariances[:, 0, 0] = 1.
        precision = np.linalg.inv(covariances)
        if not np.allclose(precision, precision.swapaxes(-1, -2), rtol=1e-12, atol=1e-12):
            raise GPUUnavailable("CUDA requires symmetric precision; CPU reference available")
        n = len(scene)
        packed[b, :n, :3] = centers
        packed[b, :n, 3:12] = precision.reshape(n, 9)
        packed[b, :n, 12] = amplitudes
        packed[b, :n, 13] = np.abs(precision).sum(axis=(1, 2))
    return (shape if len(shape) == 3 else (1, *shape)), counts, packed


def boundary_reference(shape, scene, indices):
    """Use the exact original array layout/reduction at the discontinuity.

    A point-only einsum can change FP64 reduction order relative to the original
    volume einsum. Even tiny differences matter at q=16, so an affected scene is
    conservatively rendered in full; only flagged values are substituted.
    """
    return render_gaussians(shape, scene).ravel()[indices]


def _linux_path(path):
    path = str(Path(path).resolve())
    if os.name != "nt":
        return path
    windows = PureWindowsPath(path)
    if len(windows.drive) != 2 or windows.drive[1] != ":":
        raise GPUUnavailable("CUDA bridge requires a local Windows drive")
    return "/mnt/"+windows.drive[0].lower()+"/"+"/".join(windows.parts[1:])


class CudaRustRunner:
    def __init__(self, binary=None, *, timeout=180, cache_namespace=None, persistent=False):
        self.root = Path(__file__).resolve().parents[3]
        self.binary = Path(binary or os.environ.get("PHOTON_GPU_BINARY", self.root/".tools/photon-gpu/photon-gpu")).resolve()
        self.timeout = timeout
        self.cache_namespace = cache_namespace
        self.persistent = persistent
        self._process = None
        self._lock = threading.RLock()
        self._responses = None
        self._stderr = None
        self.worker_startup_ms = None
        self.worker_context_ms = None

    def command(self, *arguments):
        command = [str(self.binary), *map(str, arguments)]
        environment = os.environ.copy()
        if self.cache_namespace is not None:
            environment["PHOTON_GPU_CACHE_NAMESPACE"] = self.cache_namespace
        if os.name == "nt":
            command = [_linux_path(self.binary), *map(str, arguments)]
            if self.cache_namespace is not None:
                command = ["env", "PHOTON_GPU_CACHE_NAMESPACE="+self.cache_namespace, *command]
            command = ["wsl", "-d", os.environ.get("PHOTON_WSL_DISTRO", "Ubuntu-22.04"), "--exec", *command]
        return command, environment

    def _response(self):
        try:
            line = self._responses.get(timeout=self.timeout)
        except queue.Empty as error:
            raise GPUUnavailable("CUDA worker response timed out") from error
        if not line:
            self._stderr.seek(0)
            raise GPUUnavailable("CUDA worker exited: "+self._stderr.read().decode(errors="replace")[-3000:])
        try:
            return json.loads(line)
        except (ValueError, UnicodeError) as error:
            raise GPUUnavailable("Invalid CUDA worker response") from error

    def start(self):
        """Initialize once; each job still owns and validates its own buffers."""
        with self._lock:
            if self._process is not None:
                return self
            if not self.binary.is_file():
                raise GPUUnavailable(f"CUDA Rust binary missing: {self.binary}")
            start = perf_counter()
            command, environment = self.command("--worker")
            self._stderr = tempfile.TemporaryFile()
            self._responses = queue.Queue()
            try:
                self._process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                                 stderr=self._stderr, env=environment)
                process, responses = self._process, self._responses
                def read_responses():
                    try:
                        for line in iter(process.stdout.readline, b""):
                            responses.put(line)
                    finally:
                        responses.put(None)
                self._reader = threading.Thread(target=read_responses, daemon=True)
                self._reader.start()
                ready = self._response()
                if ready.get("ready") is not True:
                    raise GPUUnavailable("CUDA worker failed to initialize")
                self.worker_context_ms = ready["context_ms"]
                self.worker_startup_ms = (perf_counter()-start)*1000
            except (OSError, GPUUnavailable) as error:
                self.close()
                raise GPUUnavailable(f"CUDA worker startup failed: {error}") from error
        return self

    def close(self):
        with self._lock:
            if self._process is not None:
                process = self._process
                try:
                    process.stdin.close()
                    process.wait(timeout=5)
                except (OSError, subprocess.TimeoutExpired):
                    process.kill()
                    process.wait(timeout=5)
                process.stdout.close()
                self._reader.join(timeout=1)
                self._process = None
            if self._stderr is not None:
                self._stderr.close()
                self._stderr = None

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()

    def _invoke(self, input_path, output_path):
        if not self.persistent:
            command, environment = self.command(_linux_path(input_path), _linux_path(output_path))
            try:
                process = subprocess.run(command, capture_output=True, timeout=self.timeout, env=environment)
            except (OSError, subprocess.TimeoutExpired) as error:
                raise GPUUnavailable(f"CUDA Rust invocation failed: {error}") from error
            if process.returncode or not output_path.exists():
                raise GPUUnavailable("CUDA Rust failed: "+process.stderr.decode(errors="replace")[-3000:])
            return json.loads(process.stdout.splitlines()[-1])
        with self._lock:
            try:
                self.start()
                job = json.dumps({"input":_linux_path(input_path), "output":_linux_path(output_path)}).encode()+b"\n"
                self._process.stdin.write(job)
                self._process.stdin.flush()
                response = self._response()
                if response.get("ok") is not True:
                    raise GPUUnavailable("CUDA worker failed: "+str(response.get("error")))
                return response["metadata"]
            except (OSError, GPUUnavailable) as error:
                self.close()
                raise GPUUnavailable(str(error)) from error

    def render(self, shape, scenes, *, repeats=0):
        started = perf_counter()
        shape, scenes = validate_batch(shape, scenes)
        shape3, counts, packed = pack_batch(shape, scenes)
        pack_ms = (perf_counter()-started)*1000
        if isinstance(repeats, bool) or not isinstance(repeats, int) or not 0 <= repeats <= 1000:
            raise ValueError("repeats must be an integer in [0,1000]")
        if not scenes:
            return RenderBatch(np.empty((0, *shape), dtype=np.float32), {"backend":"cuda-rust", "kernel_executed":False, "reason":"empty batch"})
        if not self.binary.is_file():
            raise GPUUnavailable(f"CUDA Rust binary missing: {self.binary}; run scripts/build_gpu.py")
        parent = (self.root/".tools/photon-gpu/requests").resolve()
        if not parent.is_relative_to(self.root):
            raise GPUUnavailable("CUDA request directory escapes workspace")
        parent.mkdir(parents=True, exist_ok=True)
        directory = Path(tempfile.mkdtemp(prefix="render-", dir=parent)).resolve()
        batch_metadata = None
        try:
            write_start = perf_counter()
            input_path, output_path = directory/"input.bin", directory/"output.bin"
            header = json.dumps({"version":1, "shape":shape3, "counts":counts, "repeats":repeats}).encode()
            with input_path.open("wb") as file:
                file.write(b"PHOTON01"+struct.pack("<I", len(header))+header)
                file.write(packed.tobytes())
            input_write_ms = (perf_counter()-write_start)*1000
            call_started = perf_counter()
            native_metadata = self._invoke(input_path, output_path)
            process_wall_ms = (perf_counter()-call_started)*1000
            read_start = perf_counter()
            with output_path.open("rb") as file:
                prefix = file.read(12)
                if len(prefix) != 12 or prefix[:8] != b"PHOTOUT1":
                    raise RuntimeError("Invalid CUDA Rust response magic")
                size = struct.unpack("<I", prefix[8:])[0]
                if not 0 < size <= 65536:
                    raise RuntimeError("Invalid CUDA response metadata size")
                metadata = json.loads(file.read(size))
                # Timings finalized after file flush travel on the control channel.
                metadata.update(native_metadata)
                batch_metadata = metadata
                payload = file.read()
            n = len(scenes)*int(np.prod(shape))
            if len(payload) != n*5 or metadata["shape"] != list(shape3) or metadata["batch"] != len(scenes):
                raise RuntimeError("CUDA response geometry/length mismatch")
            pixels = np.frombuffer(payload, dtype="<f4", count=n).copy().reshape(len(scenes), *shape)
            flags = np.frombuffer(payload, dtype=np.uint8, offset=n*4).reshape(len(scenes), -1)
            if not np.isfinite(pixels).all() or np.any(pixels < 0) or np.any(pixels > 1) or np.any(flags > 1):
                raise RuntimeError("CUDA produced invalid image/flag values")
            repair_started = perf_counter()
            output_read_validate_ms = (repair_started-read_start)*1000
            repaired = []
            for b, scene in enumerate(scenes):
                indices = np.flatnonzero(flags[b])
                repaired.append(len(indices))
                if len(indices):
                    pixels[b].ravel()[indices] = boundary_reference(shape, scene, indices)
            metadata.update({"kernel_executed":True, "cpu_boundary_repair_voxels":repaired,
                             "cpu_boundary_repair_ms":(perf_counter()-repair_started)*1000,
                             "cpu_boundary_repair_strategy":"full CPU reference per affected scene; replace flagged voxels only",
                             "python_subprocess_wall_ms":process_wall_ms,
                             "python_pack_ms":pack_ms,"python_input_write_ms":input_write_ms,
                             "python_output_read_validate_ms":output_read_validate_ms,
                             "transport":"persistent-worker" if self.persistent else "one-shot",
                             "worker_startup_ms":self.worker_startup_ms,
                             "context_timing_note":"context_ms is worker lifetime setup, not charged again to warm requests",
                             "python_batch_end_to_end_ms":(perf_counter()-started)*1000,
                             "binary_sha256":hashlib.sha256(self.binary.read_bytes()).hexdigest(),
                             "arithmetic":"FP64 geometry; FP32 exponent/value/accumulation; FP64 CPU repair at truncation boundary"})
            return RenderBatch(pixels, metadata)
        finally:
            cleanup_start = perf_counter()
            # Only this freshly-created request directory may be removed.
            if directory.parent == parent and directory.is_relative_to(self.root):
                shutil.rmtree(directory)
            if batch_metadata is not None:
                batch_metadata["python_cleanup_ms"] = (perf_counter()-cleanup_start)*1000
                batch_metadata["python_batch_end_to_end_ms"] = (perf_counter()-started)*1000


def render_gaussian_batch(shape, scenes, *, backend="cpu", runner=None, repeats=0):
    shape, scenes = validate_batch(shape, scenes)
    if backend not in ("cpu", "cuda-rust", "auto"):
        raise ValueError("Unknown render backend")
    fallback = None
    if backend != "cpu":
        try:
            return (runner or CudaRustRunner()).render(shape, scenes, repeats=repeats)
        except GPUUnavailable as error:
            if backend == "cuda-rust":
                raise
            fallback = str(error)
    start = perf_counter()
    pixels = np.stack([render_gaussians(shape, scene) for scene in scenes]) if scenes else np.empty((0, *shape), dtype=np.float32)
    return RenderBatch(pixels, {"backend":"cpu", "requested_backend":backend, "fallback_reason":fallback,
                               "cpu_batch_ms":(perf_counter()-start)*1000, "kernel_executed":False})
