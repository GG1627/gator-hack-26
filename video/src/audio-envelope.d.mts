export function clipFade(
  frame: number,
  duration: number,
  fadeFrames: number,
): number;
export function musicDuck(
  frame: number,
  clips: { from: number; duration: number }[],
  fps: number,
): number;
