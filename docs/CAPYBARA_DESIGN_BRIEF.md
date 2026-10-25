# Peekaboo — capybara design exploration

## Current brief

The user rejected the rose-gold rendered design and requested solid-color surfaces,
an animated/illustrated look, and a capybara scientist wearing a lab coat and
looking into a microscope. Keep the presentation easy to follow, with bespoke
components, clear science, and a dedicated head-to-head demo. The user selected **M ? After Hours**. Its refined design and asset package are
in [AFTER_HOURS_DESIGN.md](AFTER_HOURS_DESIGN.md). Implementation is next; N and O
remain historical alternatives.

The capybara should feel curious, focused, and slightly humorous. Use its distinct
long broad muzzle, small ears and calm eyes. Avoid generic rodent anatomy, giant
eyes, chibi proportions, or a mascot that overwhelms the experiment. User now
explicitly wants a mascot; this supersedes the earlier mascot-free preference.

## Three candidates

| Concept | Palette | Illustration | Intended character |
| --- | --- | --- | --- |
| M — After Hours | Charcoal, butter yellow, cornflower blue, amber | Hand-inked 2D animation cel | A focused evening lab; warm and quietly cinematic |
| N — Apricot Lab | Solid apricot, aubergine, copper | Plum contours and flat editorial character illustration | Warm, playful, approachable; retains warmth without photographic glass |
| O — Field Station | Moss green, pale yellow-green, terracotta, mint | Organic cut shapes and selective contours | Natural-history laboratory; calm and distinctive |

Each board compares a complete opening slide with an uncluttered demo screen.
Black image windows, timelines and controls must remain legible independently of
the character artwork. Generated microscopy on boards is placeholder imagery.
Implementation will retain actual saved observations, models and metrics.

## Mascot and motion roles

- Opening: a capybara leans into a microscope, paw at its focus wheel. One short,
  gentle action can invite attention: a blink, small head lean or focus adjustment.
  Prefer a brief entrance or long quiet pauses to constant bouncing.
- Story: reuse the same character sparingly to direct attention, if it helps the
  explanation. A small pointing pose is optional; do not decorate every slide.
- Demo: prioritize actual images and timing. Capture animation remains the main
  motion. Keep the mascot out of image panes and acquisition feedback.
- Results: let measured outcomes lead. A small restrained pose is optional and
  must not visually celebrate runs whose outcomes are unfavorable.
- Reduced motion: static illustration, immediate slide changes, clear textual
  acquisition states. Animation must never be required for understanding.

## SideRays proposal

User supplied React Bits SideRays TS/CSS source and its registry install command.
This is permission to consider/adapt the component, not a requirement to install
shadcn or add a framework before the direction is chosen. SideRays has since been integrated and tested, with upstream notice retained. See the current design specification and implementation record.

Use rays on the opening only, behind the capybara/microscope, with a mostly solid
background. Choose colors from the selected palette. Start slower and lower in
intensity than the supplied default, with dust off and weak or disabled mouse
tracking. Keep rays away from title and controls. Provide a motion toggle if the
effect runs continuously; pause/unmount when inactive and respect reduced motion.

Implementation review should cover WebGL2 fallback, context loss/recovery,
StrictMode cleanup, viewport resizing, changing reduced-motion preferences, pixel
budget and the absence of render loops while offscreen/hidden. The supplied code
is a decorative browser effect, not the native CUDA Rust scientific kernel.

## What remains stable

Peekaboo name; See more. Illuminate less.; guided story → final demo → results;
authentic dataset image for context; truthful Gaussian and CUDA Rust explanation;
saved synthetic comparisons and real-data evidence kept distinct; exposure
reduction calculated from capture counts; no invented health measurements.

The presentation navigation and replay state work was reused and browser QA has now passed. Do not roll back unrelated files,
change scientific algorithms, or rerun long experiments for visual exploration.

## Current handoff

M is selected; the corrected transparent mascot, coordinated opening/demo/results
board and component specification are saved. Follow AFTER_HOURS_DESIGN.md and
PEEKABOO_IMPLEMENTATION_PLAN.md. A pose set is deferred: the static asset plus
entrance/rays is sufficient. Implementation and browser QA are complete; Sol Medium is sufficient for isolated refinements.
