import type { Caption } from "@remotion/captions";

export type VoiceClip = {
  src: string;
  from: number;
  duration: number;
  captions: Caption[];
};
export type SoundCue = {
  src: string;
  from: number;
  duration: number;
  gain: number;
};
// Paths are relative to public/. Empty arrays are intentional: no audio exists yet.
// Add only approved, normalized files. Captions retain source-relative timing.
export const voiceover: VoiceClip[] = [];
export const effects: SoundCue[] = [];
export const music: { src: string; gain: number } | null = null;
