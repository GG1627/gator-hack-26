
# AGENTS.md — PHOTON

## Project Overview

PHOTON is an autonomous, intelligent microscopy acquisition system designed to reduce unnecessary light exposure during live-cell imaging while preserving scientifically important observations.

The system predicts cellular behavior, estimates uncertainty, and decides when acquiring another real microscopy image is worth the exposure cost.

The goal is to build a scientifically credible, technically ambitious, and visually compelling project for GatorHack V 2026 under the "Fresh off the Frontier" challenge.

**Tagline:** See More. Illuminate Less.

## Primary Project Documents

Before making significant implementation decisions, read:

1. `PHOTON_SPEC.md` — Project vision, architecture, scientific foundations, technical requirements, and evaluation methodology.
2. `BUILD_PHASES.md` — Implementation roadmap, phase objectives, progress tracking, tests, and completion criteria.

These files are the primary source of truth.

If a task conflicts with the specification, identify the conflict and explain the proposed resolution before making major changes.

Update `BUILD_PHASES.md` as development progresses. Record completed work, test results, technical decisions, and unresolved blockers.

Do not mark a phase complete unless its acceptance criteria have been satisfied.

## Development Philosophy

Act as a highly experienced software engineer, scientific computing researcher, and systems architect.

Prioritize:

- Scientific correctness and reproducibility.
- Real, functional implementations over mock functionality.
- Technically meaningful use of frontier technologies.
- Performance, maintainability, and appropriate abstraction.
- Clear architecture with independently testable components.
- A compelling, understandable, interactive demonstration.
- Completing a working vertical slice before expanding scope.

Avoid unnecessary abstractions, excessive boilerplate, speculative features, and overengineering that does not improve the final result.

This is a 48-hour hackathon project. Be ambitious, but continuously balance technical sophistication with execution risk.

## Core Technologies

PHOTON is expected to investigate and implement:

- Gaussian splatting and spatiotemporal cellular reconstruction.
- NVIDIA CUDA Rust for appropriate GPU-accelerated computations.
- Adaptive acquisition and uncertainty-aware scheduling.
- Biological event detection and prediction.
- Real microscopy datasets and reproducible evaluation.
- An interactive frontend demonstrating the system's decisions.

Additional technologies may be introduced when they provide a measurable technical advantage.

Do not add AI agents, frameworks, services, or other technologies solely for novelty.

The project must genuinely benefit from its frontier technologies. Whenever possible, demonstrate their contribution through correctness tests, ablation studies, or performance benchmarks.

If a planned technology proves impractical, explain why and propose the smallest scientifically sound alternative.

## Scientific Integrity

Scientific credibility is essential.

- Never fabricate results, benchmarks, measurements, or experimental evidence.
- Clearly distinguish actual acquired images from predicted or reconstructed frames.
- Prevent future-frame leakage during simulated microscopy acquisition.
- Evaluate decisions using only information available at the simulated decision time.
- Preserve independent ground-truth data for evaluation.
- Compare against appropriate fixed-interval and other relevant baselines.
- Report both successful and unsuccessful experiments.
- Never claim reduced phototoxicity has been biologically demonstrated when only acquisition count or estimated exposure has been measured.
- Explain assumptions and limitations clearly.
- Do not silently replace a scientific algorithm with a purely visual approximation.

A functioning, verifiable scientific prototype is more valuable than an impressive demonstration whose results cannot be reproduced.

## Implementation Workflow

Follow the phases established in `BUILD_PHASES.md`.

For each phase:

1. Read the phase's objective, requirements, and completion criteria.
2. Inspect the relevant existing code and dependencies.
3. Develop a concise implementation approach.
4. Implement the required functionality.
5. Run relevant tests and verify expected behavior.
6. Fix failures and regressions before proceeding.
7. Update `BUILD_PHASES.md` with progress and evidence.
8. Summarize what was implemented, tested, and what remains.

Prefer small, independently verifiable changes.

Do not skip testing simply because a feature appears to work.

Do not continue into subsequent phases when critical acceptance criteria remain unsatisfied, unless the user explicitly approves a change of plan.

Maintain a working application throughout development whenever possible.

## Testing Expectations

Use the testing approach appropriate to each component.

For scientific algorithms:
- Unit tests with controlled synthetic cases.
- Numerical accuracy and edge-case tests.
- Comparison against known baselines.
- Reproducible experiment configurations.

For GPU implementations:
- CPU reference implementation when practical.
- Numerical correctness comparisons.
- Performance benchmarks with clearly recorded conditions.
- Memory usage and resource validation.
- Graceful failure or fallback when GPU support is unavailable.

For acquisition scheduling:
- Strict causal evaluation.
- Equal-budget comparisons where appropriate.
- Tests covering stable periods, unexpected events, high uncertainty, and exhausted budgets.

For frontend features:
- Verify real data integration.
- Validate important user interactions.
- Avoid misleading labels or fabricated experimental results.
- Keep measured and predicted observations visually distinguishable.

Do not claim tests passed unless they were actually executed successfully.

## Model Selection and Escalation Policy

The user manually selects the Codex model.

**Default model: GPT-6.1 Sol Medium.**

You cannot switch models yourself. However, you must proactively recommend switching when the next task would materially benefit from stronger reasoning.

Do not wait for the user to ask which model to use.

### GPT-6.1 Sol Medium — Default

Use for most development work:

- Repository setup and configuration.
- Dependency installation.
- Standard Python, Rust, TypeScript, and React implementation.
- Frontend development and UI improvements.
- Dataset loading and preprocessing.
- API integration.
- Standard unit tests.
- Straightforward debugging.
- Documentation and refactoring.
- Implementation of previously validated designs.

Stay on Sol Medium unless there is a meaningful reason to escalate.

### GPT-6.1 Sol High — Complex Engineering

Recommend Sol High for:

- Scientific algorithm design or substantial modifications.
- Gaussian splatting implementation.
- CUDA Rust kernel development and nontrivial debugging.
- Mathematical modeling and numerical optimization.
- Uncertainty estimation and adaptive sampling algorithms.
- Difficult integration problems involving multiple subsystems.
- Complex concurrency, memory safety, or GPU performance issues.
- Debugging when repeated attempts fail to identify the root cause.
- Critical evaluation methodology or correctness reviews.

Recommend High proactively before beginning a clearly difficult technical phase.

### Astra Medium — Advanced Architecture and Research

Recommend Astra Medium when a task benefits substantially from deeper research-oriented reasoning, such as:

- Evaluating alternative scientific approaches.
- Translating unfamiliar research papers into a practical implementation.
- Designing mathematically sophisticated algorithms.
- Reviewing complex architecture across multiple subsystems.
- Diagnosing an architectural or algorithmic issue that Sol High has not resolved.
- Identifying subtle problems in scientific assumptions or evaluation design.

Astra is not the default choice for ordinary implementation tasks.

### Astra High — Exceptional Problems Only

Reserve Astra High for the most difficult and consequential tasks, including:

- Deep research or mathematical challenges with significant uncertainty.
- Novel GPU algorithms or complex numerical correctness issues.
- Difficult reconstruction and inverse-problem formulations.
- Major architectural decisions where an incorrect approach would waste substantial development time.
- Persistent technical blockers that have resisted less expensive reasoning approaches.
- Final critical scientific verification where unusually deep analysis is justified.

Do not recommend Astra High merely because a task involves CUDA, machine learning, or research terminology.

Escalation must have a concrete expected benefit.

## Required Model-Switch Notifications

Whenever you determine that the next task warrants a different model, explicitly tell the user in the chat.

Use this format:

**MODEL SWITCH RECOMMENDED**

- **Current model:** [Current model, if known]
- **Recommended model:** [Exact model and reasoning level]
- **Reason:** [Specific technical reason]
- **Task:** [What the stronger model should work on]
- **Switch back:** [When returning to Sol Medium makes sense]

Keep the recommendation concise and actionable.

Examples:

"MODEL SWITCH RECOMMENDED: GPT-6.1 Sol High. We're beginning the CUDA Rust numerical kernel implementation, which requires careful reasoning about GPU execution, floating-point behavior, and correctness. Switch back to Sol Medium after the kernel passes its reference tests."

"MODEL SWITCH RECOMMENDED: Astra Medium. The current uncertainty model is not producing scientifically defensible acquisition decisions. We need to reconsider the mathematical formulation before writing more code."

Only recommend a switch when it meaningfully improves the expected outcome.

Do not repeatedly suggest the same model during a task.

If the user declines a recommendation, continue working with the current model and adapt accordingly.

After a difficult task has been completed, proactively tell the user when Sol Medium is sufficient again.

Never assume a model switch has occurred unless the user confirms it or the environment explicitly indicates it.

## Communication Expectations

Be direct, technically precise, and practical.

When reporting progress, explain:

- What was implemented.
- What was actually verified.
- What remains incomplete.
- Any important technical risks.
- What should happen next.
- Whether a model change is recommended.

Do not exaggerate accomplishments or claim experimental success prematurely.

If an approach is unlikely to work within hackathon constraints, say so and propose a more realistic alternative.

Avoid excessive commentary during straightforward implementation.

## Autonomy and Decision-Making

Make reasonable implementation decisions without requesting approval for every small change.

However, explicitly surface decisions that:

- Fundamentally change the scientific methodology.
- Replace or remove a core frontier technology.
- Introduce significant technical or dependency risk.
- Alter the primary demonstration or evaluation criteria.
- Require a major architectural rewrite.
- Threaten completion of the core prototype.

When uncertain, prefer a small experiment that can validate the idea quickly.

The primary objective is not to maximize the amount of code written. It is to produce a working system with a meaningful, verifiable capability.

## Final Hackathon Priorities

Optimize for:

1. A real and scientifically meaningful result.
2. A clear demonstration of adaptive microscopy acquisition.
3. Measurable improvement against appropriate baselines.
4. Credible integration of recent frontier technology.
5. A visually compelling and understandable live demo.
6. Reproducibility, reliability, and an honest explanation of limitations.

The ideal judge reaction is:

"Wait, your software knows when a microscope should take its next picture, and you can prove it saves observations without losing important cellular events?"

Build toward that outcome.
