## Inspiration

I partly blame *Project Hail Mary*.

The [Astrophage](https://msutoday.msu.edu/news/2026/03/what-project-hail-mary-gets-right-about-alien-microbes) storyline got me interested in building something around microscopic life. I'm also part of UF's Engineering in Medicine and Biology Society (EMBS), so I was already looking for a project that connected software with biomedical research.

That curiosity led me to phototoxicity. Microscopes need light to image living cells, but too much illumination can damage them and disrupt cell division. Research such as [PhotoFiTT](https://www.nature.com/articles/s41467-025-66209-6) shows how strongly those effects can depend on dose and wavelength.

Researchers still need enough images to catch important events. Take too few, and a division can happen between observations. Take more, and every acquisition adds light exposure.

**What if a microscope knew exactly when to take its next picture?**

That became Peekaboo.

## What it does

Peekaboo is a software prototype for adaptive microscopy acquisition. It uses the shape of nuclei in images it has already acquired to choose when to look again.

When shapes are stable, it waits longer. When an acquired image shows elongation, it shortens the gap. An image budget and spacing constraints keep the schedule feasible.

The interactive demo lets you watch fixed timing and Peekaboo observe the same experiment. Each view holds its own last acquired image between captures, and a shared timeline shows exactly when each method spends an exposure.

![Actual Peekaboo application replay: fixed timing in blue and adaptive timing in amber.](https://raw.githubusercontent.com/GG1627/gator-hack-26/aeb3ae7caf4b82924de0f8c86ca1b713594364d8/docs/assets/readme/demo.gif)

In the featured controlled example:

| | Peekaboo | Fixed timing |
|---|---:|---:|
| Images acquired | **32** | 40 |
| Divisions covered | **4 of 4** | 1 of 4 |

That's **20% fewer exposures**, assuming equal illumination per image. Coverage means an acquisition within ±1 source frame of a division. This example, seed 304, was selected after evaluation; the other seeds and unsuccessful cases remain available in the demo.

## How we built it

The scientific pipeline uses **Python, NumPy, SciPy, and TIFF microscopy data**. A replay engine controls access to images: the controller receives a frame only when it chooses to acquire it. CPU fitting extracts Gaussian geometry from those pixels, and the controller chooses the next capture time.

Each Gaussian describes a nucleus through position, brightness, and covariance. The representation was inspired by [CellSplat4D](https://arxiv.org/abs/2610.04199), first submitted on October 3, 2026. Peekaboo uses a simplified model rather than reproducing that paper's complete reconstruction pipeline.

The model renderer sums the intensity contributed by the Gaussians:

$$
I(x)=\sum_{i=1}^{N} a_i\exp\left[-\frac{1}{2}(x-\mu_i)^T\Sigma_i^{-1}(x-\mu_i)\right].
$$

Here, **aᵢ** controls brightness, **μᵢ** controls position, and **Σᵢ** controls shape. The GPU evaluates this sum across output pixels.

For that computation, I wrote a **native GPU kernel using NVIDIA cuTile Rust**. Its [initial tagged release was April 7, 2026](https://github.com/NVlabs/cutile-rs/blob/main/CHANGELOG.md), followed by NVIDIA's [CUDA Rust announcement on September 8](https://developer.nvidia.com/blog/introducing-cuda-rust-two-tracks-for-writing-gpu-kernels/). This is the recent technology at the center of our **Fresh off the Frontier** submission: it executes the Gaussian rendering computation and produces model images used in the demo.

**The CPU fits shapes and chooses captures; the GPU renders models.** A **React, TypeScript, Vite, and Three.js** frontend replays saved outputs and exposes their evidence, so judges can explore the project without installing CUDA.

![Actual CUDA Rust view showing Gaussian parameters, native tile selection, and saved renderer output.](https://raw.githubusercontent.com/GG1627/gator-hack-26/aeb3ae7caf4b82924de0f8c86ca1b713594364d8/docs/assets/readme/cuda-rust.png)

## Challenges we ran into

- **Preventing future-frame leakage.** The controller cannot inspect an image before deciding to acquire it. Hidden frames and division labels stay with a separate evaluator, which scores the schedule after the run closes. The frontend also has to preserve that distinction.
- **Making GPU performance useful and measurable.** Packing data, transfers, startup, and numerical checks all affect a rendering call. I profiled those costs, added a persistent worker, and kept a CPU path for workloads where GPU overhead dominates. Floating-point behavior near truncation boundaries also required conservative handling and CPU-reference checks.
- **Making the experiment understandable.** A frozen image can mean "waiting without another exposure." The interface needed to communicate that clearly. Capture feedback, held-image labels, and the shared timeline became essential parts of the demo.

## Accomplishments that we're proud of

My favorite part to show is the timeline: you can watch the captures spread out during quiet stretches and bunch up around visible changes. Then you can open the results and check whether that timing helped.

- Across **six evaluation seeds with visible precursors**, Peekaboo covered **23 of 24 divisions using 32 images per run**, compared with **11 of 24 using 40 fixed captures**. The [complete cohort](https://github.com/GG1627/gator-hack-26/blob/main/docs/CONTROLLED_BUDGET_RESULTS.md) also includes the equal-budget fixed comparator and adverse cases.
- The **warm full GPU rendering call was 12.7× faster** than the CPU reference: **230 ms versus 2,914 ms**, for 10,000 Gaussians and a 64 × 64 output on an RTX 4070 Laptop GPU. These are 15-sample medians, including per-call bridge costs and excluding startup. The [latency audit](https://github.com/GG1627/gator-hack-26/blob/main/docs/cuda-latency-audit.md) records the full conditions; this is a rendering result, not a whole-application speedup.
- The demo's numbers come from saved schedules and checked evidence. The interface lets a viewer inspect the comparison instead of relying on a presentation slide.

## What we learned

Better timing depends on having a useful signal. Visible elongation helped in the precursor experiments. Without that warning, the same lower-budget controller covered only **4 of 24 sudden divisions**, compared with **11 of 24 for fixed timing**.

The [separate real-microscopy benchmark](https://github.com/GG1627/gator-hack-26/blob/main/docs/PHASE5_RESULTS.md), using an earlier frozen controller, also failed to improve division coverage over fixed timing. It included 36 runs on two held-out *C. elegans* embryo sequences. The newer controlled result gives us a direction to investigate; it does not establish the same benefit on real specimens.

That shaped how I think about biomedical software: a useful prototype needs an explanation of where it works, where it fails, and what the next experiment should test.

We measured acquisition counts and event coverage. Reduced phototoxicity and improved cell health still need biological validation.

## What's next for Peekaboo

Next, I want to test the newer shape-driven controller on real microscopy sequences and find out which cues remain useful outside the controlled experiments.

Then comes calibrated uncertainty: when the model becomes unreliable, the system should know it needs another observation. Connecting the controller to microscope hardware would make it possible to measure actual illumination dose and test effects on cell health.

The goal is to give researchers a better way to decide when another image is worth the light it costs.

**See more. Illuminate less.**
