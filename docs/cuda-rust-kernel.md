# Phase 4: native CUDA Rust Gaussian rendering

The Rust `photon-gpu` executable performs actual anisotropic Gaussian signal
accumulation on the NVIDIA GPU through cuTile Rust. It receives only Gaussian
parameters and public image dimensions. It does not receive image sequences,
future frames, annotations, an oracle, or acquisition-controller access.
Rendering is a scientific prediction/evaluation operation. It does not change
the controller's CPU fitting, tracking, score or budget decisions.

## Numerical contract

The reference is `photon.gaussian.render_gaussians`: additive intensity,
Mahalanobis radius4 truncation, sequential float32 accumulation and final[0,1]
clipping. Arrays use YX or ZYX voxel axes. The GPU supports the same2D/3D image
operation;2D parameters are embedded in a3D plane. It is not alpha compositing,
PSF deconvolution, a learned reconstruction, or a new biological model.

Python calculates the same float64 precision matrix as the reference and packs
each Gaussian into16 float64 fields: center3, full precision9, amplitude1,
precision L1 norm1, padding2. FP64 geometry on the GPU protects thin/rotated
objects. Exponent/value evaluation and sequential accumulation use FP32.
Every voxel sums Gaussians in source order. Pixels outside the logical image in
the final tile are discarded; padding-only blocks skip the Gaussian loop.

The radius4 cutoff is discontinuous. A tiny geometry rounding difference can
include/exclude a contribution even when the smooth exponential is accurate.
The kernel flags voxels satisfying

`abs(q-16) <= 1e-12 * (1 + ||delta||_1^2 * ||precision||_entrywise_1)`

for any component. Python renders an affected scene with the exact original CPU
volume routine and substitutes only flagged voxels. This preserves the original
array-layout-dependent FP64 reduction order at the discontinuity; a point-only
einsum can differ by a few FP64 bits. The conservative
band exceeds basic FP64 arithmetic rounding scales in the validated domain; it
is an engineering safeguard, not a proof for arbitrary floating-point inputs.
Repair counts/time are reported. Even one flagged voxel incurs a full affected
scene CPU render. Adversarial boundary-heavy workloads can spend substantial time
on CPU; that time belongs in caller latency. CPU remains the default.

The declared output tolerance is **rtol2e-4, atol2e-5** against the existing CPU
renderer, including real cases and covariance/cutoff fixtures. This is numerical
backend parity, not proof of reconstruction quality. Unit tests exercise empty
scenes, rotated/thin Gaussians, non-tile-aligned shapes, clipping, hard boundaries,
10,000 components, uncertainty scenarios and invalid/resource-heavy inputs.

## Layout, limits and failure behavior

Input is a versioned binary file with JSON metadata followed by packed f64
parameters. Output is versioned metadata, normalized f32 pixels, then u8 boundary
flags. Sizes/versions/types/nonfinite parameters are checked. Native code also
checks precision symmetry/positive definiteness, amplitude and payload bounds
before allocating GPU buffers. Python additionally restricts covariance
eigenvalues/conditioning and rejects unsupported geometry explicitly.

Limits:1..64 scenes per native request,0..10,000 Gaussians per scene,2D/3D axes
1..4096, at most128M logical output voxels in the batch, input file<=128MiB,
centers within1e6 voxels, amplitude<=1e6. Python's validated covariance eigenvalues
are1e-8..1e8 with condition number<=1e6. Empty batches return an explicit no-kernel
result; an empty scene goes through the real kernel and yields zeros.

The output tensor is `[batch, ceil(P/8192), 8192]`, partitioned into
`[1,1,128]` tiles. Grid coordinates give pixel block
`(grid_y*64 + grid_z)*128`. This preserves contiguous per-scene output while
keeping CUDA grid-Y/grid-Z below their65,535 limits. An initial2D grid failed on
the full41x512x512 volume because it required83,968 grid-Y blocks. The3D mapping
and an above-limit volume regression test address that failure; small-case
success alone did not establish full-volume support.

`render_gaussian_batch(..., backend="cuda-rust")` fails clearly if the native
engine is unavailable. `backend="auto"` can use the original CPU reference and
records requested/actual backend plus fallback reason. Numerical response failures
are errors, not silently hidden as successful CPU fallback. `backend="cpu"`
remains the default. Files are local temporary request files; cleanup verifies
the newly created directory remains within the workspace.

`GaussianSceneModel.predict(..., backend="cuda-rust")` batches the predicted mean
and, if requested, the2D/3D positive/negative-axis ensemble states in one native
request. CPU Welford aggregation produces the same heuristic disagreement map.
The `PredictedFrame` records actual backend and native metadata. Uncertainty is
still uncalibrated; rendering faster does not improve the model's biological
validity or repair its known loss to hold-last.

## Timing and reproducibility

The native binary records context setup, H2D allocation/copy wall time, output
allocation/fill, JIT preparation/cache loading, first launch, CUDA graph capture,
warm graph CUDA-event intervals, host dispatch/synchronization, D2H wall time,
buffer bytes and observed device-free memory. Memory snapshots are not claimed
to be exact peak usage. Transfer wall times include host API/allocation overhead;
they are not isolated PCIe bandwidth measurements.

Normal production requests render once. Profiling requests explicitly ask for
warmups and repeated graph launches. CUDA event intervals exclude compilation,
transfers and context creation, but include any host enqueue gaps. They are not
profiler-instruction execution times. All captured buffers/graph remain alive
until the completion event; async launch safety conditions are documented in code.

`scripts/benchmark_gpu.py` compares the existing optimized/local-bounds CPU
reference, warm device interval, and a separate **single-render full Python call**
including validation/packing/files/WSL/context/GPU/readback/repair/cleanup. Raw
samples and medians are exported; a fresh cache namespace measures actual cold
JIT and later disk hits. The CUDA kernel evaluates the full grid while the CPU
reference culls local boxes, so algorithmic work counts differ despite equivalent
outputs. Kernel-only ratios must not be presented as application speedups.

Host Cargo build time is recorded separately, without assuming an empty compile
cache. Benchmark conditions use an active laptop without clock locking/exclusive
GPU control. The release profile, binary/source/lock hashes, GPU/driver and
dependency versions are saved. A speedup is an experimental outcome, not a gate
assumption. Earlier partial/failed measurements are retained separately.

The upstream source is pinned at
`fc747196f2d46dce41bd844e3f5b1c5882751f2b`, cuTile0.5.0, Rust1.98.0;
the tested machine has CUDA13.3/tileiras13.3.36 and RTX4070 Laptop sm89.
Build and benchmark commands/results are tracked in BUILD_PHASES.md and README.
Official interfaces consulted:
[cuTile introduction](https://nvlabs.github.io/cutile-rs/main/guide/introduction.html),
[NVIDIA source at the pinned revision](https://github.com/NVIDIA/cuda-rust/tree/fc747196f2d46dce41bd844e3f5b1c5882751f2b),
including SAXPY, graph capture, event timing and JIT-cache examples.

## Verified measurements

The final checked run is `runs/phase4-benchmark-verified/benchmark.json`.
Each case has5 CPU-reference samples,5 warmed CUDA graph intervals and3 separate
single-render Python calls. Warm GPU inputs are resident. The initial unique
cache namespace compiled3 backends (two fill kernels and render); the first
render JIT preparation took1613.011631ms. Later same-case single-render processes
reported0 backend compiles/3 disk hits, but still paid AST/cache/context costs.
Host release build wall time76091.5513ms is separate and not claimed cold.

| Case | CPU median ms | Device interval ms | Full caller ms | Max absolute error |
|---|---:|---:|---:|---:|
|G1/B1,64x64 |0.2602 |0.045056 |1857.9186 |2.98e-8 |
|G100/B1,64x64 |33.2419 |0.214016 |1984.2963 |1.49e-8 |
|G10000/B1,64x64 |3087.0184 |19.818497 |5291.0072 |4.47e-8 |
|G100/B6,64x64 |194.3397 |1.199104 |2127.4398 |1.49e-8 |
|Observed s1 t260,G17/B1,41x512x512 |85.6794 |49.300480 |5335.4638 |1.19e-7 |

No original one-shot caller beat CPU. Keep CPU as the deployment default. The
subsequent [latency audit](cuda-latency-audit.md) adds opt-in persistent context/
process reuse, a packing fix and full-call comparisons; these original values
are preserved as historical evidence. All benchmark cases needed0 boundary repairs; adverse
boundary costs are tested separately and must not be inferred from this table.

`runs/phase4-real-gpu-verified/` and `phase4-real-cpu-fallback-verified/`
contain real270-step s1 replays with identical54 acquisitions, decisions and
final state as the earlier CPU run. Causally saved geometry at1/134/268 is rendered
in one batch. Maximum differences are1.7881393432617188e-7,
1.1920928955078125e-7,1.1920928955078125e-7. Fallback records CPU, missing-binary
reason and zero GPU work; it does not pretend to execute CUDA. Labels are not read.
The renderer receives no truth; source errors are evaluated only after closure.

Final Python suite80 passed in50.45s; native formatting and one checked-input
Rust unit test pass. `runs/phase4-verification.json` independently verifies
benchmark accounting and re-renders saved real geometry against source errors.
The measurement chart was inspected and its margins corrected from JSON without
changing any timing values. Phase5 quality/event comparisons remain outstanding.
