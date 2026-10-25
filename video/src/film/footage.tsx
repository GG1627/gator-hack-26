import { Video } from "@remotion/media";
import { AbsoluteFill, Sequence, staticFile } from "remotion";
import { color } from "./theme";
import { SceneMotion } from "./SceneMotion";

// Video and any future source-relative transcript share this trim boundary.
export const Footage = ({
  src,
  trim = 0,
  duration,
  label = "Recorded app · accelerated experiment replay",
}: {
  src: string;
  trim?: number;
  duration: number;
  label?: string;
}) => (
  <SceneMotion duration={duration} recorded>
    <Sequence name={label} trimBefore={trim} durationInFrames={duration}>
      <AbsoluteFill style={{ background: color.ink }}>
        <Video
          src={staticFile(src)}
          muted
          objectFit="contain"
          style={{ width: "100%", height: "100%" }}
        />
        <div
          style={{
            position: "absolute",
            left: 30,
            top: 22,
            padding: "7px 13px",
            background: "#242629e8",
            color: color.paper,
            fontSize: 19,
            borderRadius: 20,
          }}
        >
          {label}
        </div>
      </AbsoluteFill>
    </Sequence>
  </SceneMotion>
);
