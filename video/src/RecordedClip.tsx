import { Video } from "@remotion/media";
import type { Caption } from "@remotion/captions";
import { AbsoluteFill, Sequence, staticFile } from "remotion";
import { Subtitles } from "./Soundtrack";

// Keep source trims on the parent so footage and transcript remain synchronized.
export const RecordedClip = ({
  src,
  captions,
  trimBefore = 0,
  duration,
}: {
  src: string;
  captions: Caption[];
  trimBefore?: number;
  duration: number;
}) => (
  <Sequence
    name="Recorded application"
    trimBefore={trimBefore}
    durationInFrames={duration}
  >
    <AbsoluteFill style={{ backgroundColor: "#242629" }}>
      <Video
        src={staticFile(src)}
        muted
        objectFit="contain"
        style={{ width: "100%", height: "100%" }}
      />
      <div
        style={{
          position: "absolute",
          top: 44,
          right: 60,
          padding: "10px 16px",
          background: "#242629e8",
          borderRadius: 8,
          fontSize: 22,
          color: "#f6d48b",
        }}
      >
        Recorded app
      </div>
      <Subtitles captions={captions} />
    </AbsoluteFill>
  </Sequence>
);
