import { Audio } from "@remotion/media";
import { createTikTokStyleCaptions, type Caption } from "@remotion/captions";
import {
  Sequence,
  interpolate,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import {
  effects,
  music,
  voiceover,
  type VoiceClip,
  type SoundCue,
} from "./media";
import { clipFade, musicDuck } from "./audio-envelope.mjs";

export const Subtitles = ({ captions }: { captions: Caption[] }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const { pages } = createTikTokStyleCaptions({
    captions,
    combineTokensWithinMilliseconds: 1600,
  });
  const page = pages.find(
    (p) =>
      (frame / fps) * 1000 >= p.startMs &&
      (frame / fps) * 1000 < p.startMs + p.durationMs,
  );
  if (!page) return null;
  return (
    <div
      style={{
        position: "absolute",
        left: 250,
        right: 250,
        bottom: 24,
        textAlign: "center",
        pointerEvents: "none",
        opacity: interpolate(
          (frame / fps) * 1000 - page.startMs,
          [0, 100],
          [0, 1],
          { extrapolateLeft: "clamp", extrapolateRight: "clamp" },
        ),
      }}
    >
      <span
        style={{
          display: "inline-block",
          background: "#17191df0",
          color: "#fff9eb",
          borderRadius: 12,
          padding: "18px 30px",
          fontSize: 42,
          lineHeight: 1.4,
        }}
      >
        {page.text}
      </span>
    </div>
  );
};

const MusicBed = ({
  track,
  clips,
}: {
  track: { src: string; gain: number } | null;
  clips: VoiceClip[];
}) => {
  const { durationInFrames, fps } = useVideoConfig();
  if (!track) return null;
  return (
    <Audio
      src={staticFile(track.src)}
      volume={(frame) =>
        track.gain *
        clipFade(frame, durationInFrames, Math.round(fps * 2)) *
        interpolate(
          frame,
          [0, Math.round(durationInFrames * 0.7), durationInFrames - 1],
          [0.65, 1, 1.15],
          { extrapolateLeft: "clamp", extrapolateRight: "clamp" },
        ) *
        musicDuck(frame, clips, fps)
      }
    />
  );
};

export const Soundtrack = ({
  voiceClips = voiceover,
  cues = effects,
  musicTrack = music,
  captionsEnabled = true,
}: {
  voiceClips?: VoiceClip[];
  cues?: SoundCue[];
  musicTrack?: { src: string; gain: number } | null;
  captionsEnabled?: boolean;
}) => {
  const { fps } = useVideoConfig();
  return (
    <>
      <MusicBed track={musicTrack} clips={voiceClips} />
      {voiceClips.map((clip) => (
        <Sequence
          key={`${clip.src}-${clip.from}`}
          name={`Narration: ${clip.src}`}
          from={clip.from}
          durationInFrames={clip.duration}
          premountFor={Math.round(fps * 3)}
        >
          <Audio
            src={staticFile(clip.src)}
            premountFor={Math.round(fps * 3)}
            volume={(frame) =>
              0.84 *
              clipFade(
                frame,
                clip.duration,
                Math.max(2, Math.round(fps * 0.05)),
              )
            }
          />
          {captionsEnabled ? <Subtitles captions={clip.captions} /> : null}
        </Sequence>
      ))}
      {cues.map((cue) => (
        <Sequence
          key={`${cue.src}-${cue.from}`}
          name={`SFX: ${cue.src}`}
          from={cue.from}
          durationInFrames={cue.duration}
          premountFor={fps}
        >
          <Audio
            src={staticFile(cue.src)}
            volume={(frame) =>
              cue.gain *
              clipFade(frame, cue.duration, Math.max(2, Math.round(fps * 0.08)))
            }
          />
        </Sequence>
      ))}
    </>
  );
};
