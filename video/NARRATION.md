# Peekaboo narration

Review copy of `narration-v3.json`, the editable source. Opening revised as a connected take; remaining scene audio preserved.

Voice: Ashley (bxiObU1YDrf7lrFAyV99). Runtime: 178.27 seconds.

## Voice direction

Warm, conversational, and curious. Speak like a knowledgeable friend showing someone something genuinely interesting. Keep the narration connected, with natural breaths and subtle changes in emphasis. Give important results a moment to land. No dramatic trailer voice, forced excitement, or overly polished corporate delivery.

## 1. Hook

What if a microscope knew exactly when to take its next picture?

## 2. Premise

Taking pictures of living cells requires light, but too much of that light can damage them and disrupt cell division.

In one study using high-dose near-ultraviolet light, researchers observed eighty percent fewer cell divisions.

And that got us thinking. What if, instead of taking pictures constantly, a microscope could be smarter about when it captures them?

That's why we built Peekaboo.

## 3. Demo

Here's how it works.

We're replaying the same controlled experiment in two different ways.

One approach takes pictures at fixed intervals, whether anything is happening or not.

Peekaboo works differently. When the cells appear stable, it waits a little longer. But when it starts noticing changes in their shape, it captures more frequently.

And look at the difference.

## 4. Result

In this particular example, Peekaboo captured all four cell divisions using just thirty-two images.

The fixed approach? Forty images, but it only captured one of those divisions.

That's twenty percent fewer exposures, assuming the same amount of light per image, while capturing more of the important events.

## 5. Causality

Now, there's something important about how this works.

Peekaboo can only make decisions based on images it's already captured.

It doesn't get to see what happens between those images. We keep that information separate, so we can evaluate its decisions afterward.

## 6. Gaussians

So how does it figure out when to look again?

We represent each cell nucleus as a Gaussian, describing its position, brightness, and shape.

Drawing inspiration from recent research on four-dimensional cell reconstruction, we built a simplified model that tracks how those shapes change over time.

When the acquired images show a nucleus starting to elongate, Peekaboo knows to shorten the time until its next capture.

## 7. Frontier

And we wanted the visualization to be fast, too.

For that, we used NVIDIA's cue-tile library, written in Rust, to render our Gaussian models on the GPU.

The CPU handles fitting the shapes and deciding when to capture. The GPU handles rendering them.

## 8. Benchmark

And here's where things got interesting.

With ten thousand Gaussians, our warmed GPU rendering call was twelve point seven times faster than the CPU reference.

Now, that's specifically the rendering operation, not a twelve-times speedup of the entire application.

## 9. Difficulty

We also checked that the GPU output matched our CPU reference, and measured rendering separately from startup overhead.

For smaller workloads, the CPU can actually be the better choice.

## 10. Limits

Of course, this is still an early prototype.

If a division happens suddenly between captures, Peekaboo might miss it.

And in our separate benchmark using real microscopy data, it didn't improve division coverage compared with fixed timing.

So while our controlled example demonstrates what's possible, there's still work to do before we can claim the same benefits on real microscopes.

## 11. Close

And that's what we want to explore next.

Because the goal isn't just to take fewer pictures.

It's to capture the moments that matter, while exposing cells to less light.

That's Peekaboo.

See more. Illuminate less.
