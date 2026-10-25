const clamp = (value) => Math.max(0, Math.min(1, value));
export const clipFade = (frame, duration, fadeFrames) =>
  Math.min(
    clamp(frame / fadeFrames),
    clamp((duration - 1 - frame) / fadeFrames),
  );
export const musicDuck = (frame, clips, fps) =>
  clips.reduce((gain, clip) => {
    const attack = Math.max(1, Math.round(0.18 * fps));
    const release = Math.max(1, Math.round(0.5 * fps));
    const envelope =
      frame < clip.from
        ? clamp((frame - clip.from + attack) / attack)
        : frame <= clip.from + clip.duration
          ? 1
          : clamp(1 - (frame - clip.from - clip.duration) / release);
    return Math.min(gain, 1 - 0.75 * envelope);
  }, 1);
