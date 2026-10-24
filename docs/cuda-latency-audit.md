# CUDA Rust latency audit

This follow-up preserves the Phase4 kernel and frozen acquisition methodology.
Generated measurements are under `runs/cuda-latency-audit/`; historical results
and their exact source snapshot remain under `runs/phase4-*`.

## Execution path

1. `AdaptivePolicy.decide()` checks history, computes scalar uncertainty/motion/
   morphology/gap priorities and exact-budget feasibility on CPU. It does not
   call `predict()` or the GPU. `observe()` fits and associates acquired nuclei
   on CPU. Only acquired images enter these functions.
2. Optional `GaussianSceneModel.predict()` constructs mean geometry and, when
   requested, six physical-axis perturbations. `render_gaussian_batch()` sends
   those descriptors and public output dimensions to `CudaRustRunner.render()`.
3. The bridge validates and packs FP64 descriptors, creates an owned request
   directory and writes a checked binary request. One-shot mode invokes
   `wsl --exec photon-gpu INPUT OUTPUT` for every call. Persistent mode starts
   `photon-gpu --worker` once and sends JSON file paths over stdin; a response
   reader with a timeout receives completion and timing metadata on stdout.
4. Rust validates the request, copies descriptors/counts to GPU, allocates/fills
   outputs, prepares the unchanged cuTile render kernel, synchronously renders,
   synchronously copies values/boundary flags to host and flushes the response.
   The worker retains only CUDA context/stream and cuTile's process cache;
   request buffers are freed between jobs. No raw images, frame source, oracle,
   event labels or controller scores enter native code.
5. Python reads and validates the full response, repairs flagged truncation
   boundary pixels with the original CPU reference, records binary SHA256,
   removes the request directory and returns. These costs are in caller timing.
   For uncertainty maps, `predict()` then performs the original CPU Welford
   disagreement reduction. Predictions never feed back into acquisition scores.

## Minimal changes

- Optional `CudaRustRunner(persistent=True)` retains CUDA initialization and
  cuTile's in-process compiled-kernel cache. The existing one-shot path stays
  available. Explicit CUDA failures remain errors; `backend="auto"` records CPU
  fallback. Timeout/process death closes the worker; a subsequent call can start
  a new one. Context managers bound worker lifetime; requests are serialized.
- NumPy stacks covariance matrices and batches eigendecomposition/inversion
  instead of making thousands of tiny Python calls. Domain checks are retained.
  Tests and the 10,000-component ablation compare packed values bit for bit.
- Native output buffering increases from8KiB to1MiB. The controlled ablation
  retains the old size via `PHOTON_GPU_SMALL_WRITES=1`. There is no kernel rewrite,
  buffer pool, new framework, GPU scoring algorithm or replacement CPU baseline.
- Timings now cover packing, request write, response read/validation, native
  response write and cleanup. Final post-flush native timings travel over the
  control channel. `python_subprocess_wall_ms` is retained for compatibility;
  for a worker it measures the synchronous request/response interval.

## Reproduction

Use the pinned release build, installed Python environment and Phase3 saved
development states. Each output must be new. Run measurement scripts sequentially,
without overlapping CUDA tests or other benchmark jobs:

```powershell
.venv/Scripts/python.exe scripts/build_gpu.py --offline
.venv/Scripts/python.exe scripts/diagnose_gpu_io.py --output runs/cuda-latency-audit/io-ablation.json
.venv/Scripts/python.exe scripts/benchmark_gpu_latency.py --output runs/cuda-latency-audit/matrix
.venv/Scripts/python.exe scripts/benchmark_gpu_crossover.py --output runs/cuda-latency-audit/crossover.json
.venv/Scripts/python.exe scripts/benchmark_adaptive_latency.py --output runs/cuda-latency-audit/adaptive
.venv/Scripts/python.exe -m pytest -q
.venv/Scripts/python.exe scripts/verify_gpu_latency.py
```

The I/O ablation reads the original implementation from the preserved
`runs/phase4-source-snapshot.zip`. Both real benchmarks use development s1 only;
the adaptive benchmark requires the full s1 TIFF window. Its three probe times
are the preexisting Phase4 times1/134/268. It replays the actual controller and
checks exact54 acquisitions, every decision field and final state against the
original CPU run. Prediction probes use the same frozen causal state repeatedly;
they are checked not to mutate it. No withheld truth or annotations are read.

## Timing definitions and limits

- **Cold:** fresh native process, context and unique empty cuTile disk cache for
  each of5 samples per size. WSL VM, OS filesystem cache and NVIDIA driver caches
  remain warm. No WSL shutdown, GPU reset or driver cache purge is performed.
- **One-shot disk cache:**15 full Python calls, each with a new native process
  and context but a populated cuTile disk cache. Cargo is never invoked at render
  time; its separately recorded release build is an incremental host build.
- **Warm CPU:**15 calls to the unchanged bounding-box CPU renderer after warmup.
- **Warm kernel:**15 CUDA-event intervals around resident CUDA-graph replay;
  synchronize the end event before recording elapsed time. Excludes allocation,
  transfer, JIT, IPC and CPU repair. Host enqueue gaps can appear in this interval.
- **GPU plus transfers:** synchronized H2D, output allocation/fill, one render
  dispatch/synchronization and D2H. Includes host allocation/dispatch overhead,
  excludes JIT preparation, file transport, Python and CPU boundary repair.
- **Worker full:**15 calls after startup and one same-shape warmup, including
  all per-request packing/files/transfers/render/read/repair/hash/cleanup.
  Startup/first-request latency is reported separately and must be amortized.
  `context_ms` describes lifetime context/stream/cache-store initialization;
  its repeated presence in metadata does not mean it is charged on each job.
- Median and p95 use NumPy's linear sample percentile. Five cold samples give
  only a rough tail estimate. Raw samples and component metadata are retained.

CPU and GPU produce equivalent arrays with different work: CPU culls local
Gaussian bounding boxes; GPU scans the full volume for each component. Gaussian
count alone cannot predict crossover for arbitrary shapes/covariances. Every
reported GPU call is checked against CPU at rtol2e-4/atol2e-5. Map disagreement uses
rtol3e-4/atol3e-5. Boundary repair can add a complete CPU render of an affected
scene. Free-memory snapshots are not peak-VRAM measurements. The active laptop
has no locked clocks, CPU affinity or exclusive GPU reservation.

The adaptive decision timing repeats each causal input state while restoring
only `decide()`'s clock/pending/decision fields, then commits the identical final
action. Acquisition I/O and observation timings span the54 actual captures.
Prediction latency includes full `predict()` work, including disagreement maps.
Benchmark repetition time is not presented as normal whole-experiment latency.

## Measured rendering results

Intel Core Ultra9 185H,16GB host RAM; RTX4070 Laptop/sm89/8188MiB,
driver581.57, WSL2 Ubuntu22.04,
CUDA13.3/cuTile0.5.0/Rust1.98.0, NumPy2.5.4/CPython3.13.5. Each cell below is
**median / p95 in milliseconds**. Warm modes have15 samples; cold has5.

| Geometry/workload | Warm CPU | Warm kernel graph | GPU + transfers | Warm worker full | One-shot cached full | Fresh-process/JIT cold full |
|---|---:|---:|---:|---:|---:|---:|
|64x64, G1/B1 |0.664 /1.072 |0.017 /0.040 |2.190 /2.631 |92.568 /98.438 |1898.820 /2017.337 |3010.506 /4801.360 |
|64x64, G10/B1 |3.095 /7.657 |0.035 /0.078 |1.673 /2.130 |90.429 /101.065 |1928.068 /2012.498 |2860.866 /2913.011 |
|64x64, G100/B1 |31.236 /35.402 |0.217 /0.253 |1.786 /2.148 |110.230 /120.153 |1922.042 /2016.238 |2841.435 /2897.111 |
|64x64, G1000/B1 |294.675 /334.492 |1.998 /2.025 |3.436 /5.039 |129.097 /170.928 |2012.089 /2225.416 |2857.071 /2951.118 |
|64x64, G10000/B1 |2913.980 /3080.486 |19.820 /19.962 |21.801 /22.249 |230.120 /290.729 |2062.454 /2141.119 |3027.844 /4793.808 |
|64x64, G100/B7 |223.177 /283.633 |1.404 /1.444 |2.899 /3.861 |130.827 /243.374 |1917.755 /2089.119 |2971.589 /3164.345 |
|Real s1 t260, 41x512x512, G17/B1 |99.823 /115.877 |49.403 /58.279 |317.697 /374.887 |1501.052 /1924.154 |3178.821 /3958.306 |4085.807 /4124.527 |
|Same real geometry, seven-state ensemble |627.122 /770.205 |346.033 /346.695 |1366.442 /1405.555 |9147.040 /10085.138 |10091.474 /10527.325 |11198.666 /11608.145 |

All measured arrays matched CPU; maximum absolute difference over the matrix
was1.7881393432617188e-7. All warm worker calls reported0 backend compiles and0
disk-cache hits: they used the in-process cache. All cold samples compiled
kernels. Normal caller samples render once; profiling loops are separate.

The sparse real-volume warm worker remains about15 times slower than CPU. Even
the GPU-plus-transfers path exceeds CPU time. The seven-state batch is slightly
slower than seven separate warm worker calls (8360.837 /11046.035ms), whereas
synthetic B7 improves over seven calls (823.008 /870.469ms). Batching is useful
for small outputs; it is not a universal improvement.

The alternating-order crossover sweep (also15 repetitions) found these medians:

|64x64 workload |CPU ms |Warm full GPU ms |
|---|---:|---:|
|G200/B1 |64.296 |120.035 |
|G300/B1 |91.388 |124.005 |
|G400/B1 |124.912 |131.932 |
|G600/B1 |184.988 |137.696 |
|G100/B2 |63.841 |119.080 |
|G100/B4 |126.004 |123.140 |

Thus the observed single-scene warmed crossover is bracketed by400–600
Gaussians for this synthetic geometry. B4 is a near tie, not a robust gain; B7
has a clearer median improvement. G1000/B1 is2.28x and G10000/B1 is12.66x faster
through the full warm caller. These are rendering results, not acquisition
controller or whole-experiment speedups. Current one-shot G10000 also beats CPU
after the packing fix, but fresh-JIT median does not. Startup/first request costs
remain material: e.g. synthetic B7 first request1839.665ms versus130.827ms warm,
so a simple amortization estimate is roughly19 comparable requests to recover that extra setup cost
against its223.177ms CPU median (excluding teardown and timing variation).

## Where the time goes

The original bridge's repeated context setup cost about340–410ms, output-fill
preparation240–290ms and main-kernel preparation850–910ms, despite disk-cache
hits. Fresh native launches pay these repeatedly. The controlled WSL `/bin/true`
median is284.497ms; the native `--ping` median is290.374ms without CUDA setup.
These launch probes are baselines, not additive estimates for every request.

In the new matrix's real B1 one-shot calls, median context/stream/cache-store
initialization is443.13ms, output allocation/fill270.50ms, render preparation
915.45ms and native output write779.19ms. Persistent mode reduces JIT preparation
to0.02ms, but its real B1 response write is846.52ms and Python response
read/validation211.24ms. For real B7 those become4913.56ms and1368.99ms. Its D2H
copy alone costs750.16ms. Responses contain5 bytes per logical voxel:53.74MB for
B1 and376.18MB for B7. Native device output uses8 bytes per padded voxel before
packing flags down to bytes. Sparse CPU bounding-box rendering avoids this
bridge. No Cargo compilation happens in the application call path.

Native single-render dispatch/synchronization costs are also larger than warmed
graph intervals (e.g. real B1 median220.86ms versus49.40ms graph event time).
The graph benchmark is not the normal production launch path. The full caller
retains that direct-launch overhead and all other costs, including per-call
binary hashing and directory management; residual overhead is not attributed
to PCIe or WSL startup without measurement. Medians of components do not sum
exactly to the median total. No instruction profiler or isolated PCIe bandwidth
measurement is claimed.

The controlled packing ablation measures2855.405 /3113.220ms before versus
64.747 /68.507ms after for10000 descriptors, with bit-identical packed values.
The buffer-size ablation observes1198.887ms full median at8KiB versus1083.902ms
at1MiB; native output-write medians are703.43/632.15ms. This is a modest,
fixed-order comparison under variable laptop conditions, not the main benefit.
The persistent context/cache and packing fix are the major changes. No GPU
buffer pool or transport rewrite is justified by the current sparse experiment.

## Actual acquisition and prediction path

The full270-step development replay retained exactly54 acquisitions, every
recorded decision field and final state from the original CPU run. There were
no annotation reads, withheld-image reads or prediction-driven controller state
updates. The saved trace/state and all statistics are independently checked by
`verify_gpu_latency.py`.

The actual decision function stays CPU in both rendering modes. Its4050
measurements (15 repetitions of each270 causal states) have median/p950.023400 /
0.061485ms. The54 actual acquired-image fitting/tracking updates cost1282.634 /
4050.994ms, and acquisition I/O61.340 /306.811ms. These last two distributions
span different acquired images, not repeated identical work. Image fitting,
rather than the scalar scheduler, dominates current controller computation.

Full `model.predict()` results below include geometry construction, optional
uncertainty reduction, renderer transport/repair and result construction.
Each cell is median/p95 milliseconds from15 same-state repetitions:

|Causal probe |Active tracks |CPU mean |GPU worker mean |CPU mean + uncertainty map |GPU worker mean + map |
|---|---:|---:|---:|---:|---:|
|t1, based on acquired t0 |7 |62.318 /87.051 |1142.038 /1595.312 |1522.725 /1674.058 |9621.192 /10578.915 |
|t134,29 acquisitions available |87 |534.257 /560.375 |1639.342 /2002.198 |5993.239 /9639.668 |15167.662 /30469.055 |
|t268,54 acquisitions available |17 |137.980 /608.525 |1986.145 /5356.882 |2095.996 /3686.086 |14779.392 /23577.527 |

Maximum prediction difference1.7881393432617188e-7; maximum uncertainty-map
difference8.940696716308594e-8. Every probe has only earlier acquired indices,
and `state_dict()` is identical before/after all predictions. No actual real
prediction workload in this audit benefited from GPU execution. There is no
GPU acquisition-score implementation or observed scheduler crossover to report.
Adding one solely to accelerate its tiny scalar function is unjustified.

These repeated probes retain reference/warmup/previous prediction arrays for
validation. Large host arrays and the16GB laptop's variable memory conditions
can affect the long tails. Host/GPU peak allocation and isolated production
memory pressure were not profiled. The GPU prediction currently returns a mean
view backed by the batch array, which can also retain substantial memory. These
limits reinforce the scope of the reported harness timings; they do not justify
a universal latency guarantee. No whole270-step experiment speedup is inferred
from component medians, and fitting/I/O remain CPU work in either render mode.

**Decision:** keep CPU default for current real microscopy/controller/prediction
workloads. Use the explicit persistent runner for repeated dense small-output
render batches when measured full-call savings amortize startup. Preserve
one-shot mode, logged CPU fallback and all causal/numerical guards. Leave kernel,
controller methodology and Phase5 independent scientific evaluation unchanged.

The full-caller chart is `runs/cuda-latency-audit/full-caller.png`; raw samples,
source/binary hashes, startup/component times, memory snapshots, crossover and
controlled ablations are in the neighboring JSON artifacts. The rendering
matrix uses5 cold and15 warm samples per size, not the historical Phase4
five/three-sample protocol.
