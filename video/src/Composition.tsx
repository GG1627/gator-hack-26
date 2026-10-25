import { loadFont } from "@remotion/fonts";
import { TransitionSeries, linearTiming } from "@remotion/transitions";
import { fade } from "@remotion/transitions/fade";
import {
  AbsoluteFill,
  Easing,
  Img,
  interpolate,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { Soundtrack } from "./Soundtrack";

loadFont({
  family: "Manrope",
  url: staticFile("fonts/manrope.woff2"),
  weight: "200 800",
});
const ease = {
  extrapolateLeft: "clamp",
  extrapolateRight: "clamp",
  easing: Easing.bezier(0.16, 1, 0.3, 1),
} as const;
const ink = "#242629",
  butter = "#f6d48b";

const SignalStudy = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  return (
    <AbsoluteFill
      style={{ backgroundColor: ink, color: butter, overflow: "hidden" }}
    >
      <svg
        viewBox="0 0 1920 1080"
        style={{
          position: "absolute",
          inset: 0,
          width: "100%",
          height: "100%",
        }}
      >
        <defs>
          <radialGradient id="signal">
            <stop stopColor="#edbb6b" stopOpacity=".8" />
            <stop offset=".45" stopColor="#d99b50" stopOpacity=".25" />
            <stop offset="1" stopColor="#d99b50" stopOpacity="0" />
          </radialGradient>
        </defs>
        <g
          style={{
            opacity: interpolate(frame, [0, fps], [0, 1], ease),
            translate: `${interpolate(frame, [0, 5 * fps], [40, 0], ease)}px 0`,
          }}
        >
          <ellipse cx="1460" cy="530" rx="340" ry="260" fill="url(#signal)" />
          {[1, 0.7, 0.4].map((scale) => (
            <ellipse
              key={scale}
              cx="1460"
              cy="530"
              rx={250 * scale}
              ry={175 * scale}
              transform="rotate(-28 1460 530)"
              fill="none"
              stroke="#e6b66a"
              strokeOpacity={0.3 + scale * 0.15}
              strokeWidth="1.3"
            />
          ))}
          <path
            d="M1120 530H1800M1460 240V820"
            stroke="#f6d48b"
            strokeOpacity=".16"
            strokeDasharray="4 12"
          />
          <circle cx="1460" cy="530" r="5" fill={butter} />
        </g>
      </svg>
      <div
        style={{
          position: "absolute",
          left: 140,
          top: 110,
          fontSize: 28,
          fontWeight: 700,
          letterSpacing: -1,
          opacity: interpolate(frame, [4.6 * fps, 5 * fps], [1, 0], ease),
        }}
      >
        Peekaboo<span style={{ color: "#d99b50" }}> .</span>
      </div>
      <div
        style={{
          position: "absolute",
          left: 140,
          top: 310,
          width: 1200,
          opacity:
            interpolate(frame, [0, 0.6 * fps], [0, 1], ease) *
            interpolate(frame, [4.6 * fps, 5 * fps], [1, 0], ease),
          translate: `0 ${interpolate(frame, [0, 1.2 * fps], [34, 0], ease)}px`,
        }}
      >
        <h1
          style={{
            fontSize: 108,
            lineHeight: 1.1,
            letterSpacing: -5,
            margin: 0,
            fontWeight: 750,
          }}
        >
          What if a microscope
          <br />
          knew when to look?
        </h1>
        <div
          style={{
            width: interpolate(frame, [1.5 * fps, 3 * fps], [0, 160], ease),
            height: 3,
            backgroundColor: "#d99b50",
            marginTop: 52,
          }}
        />
      </div>
      <div
        style={{
          position: "absolute",
          left: 140,
          bottom: 100,
          fontSize: 22,
          color: "#bfc0bb",
          opacity: interpolate(frame, [4.6 * fps, 5 * fps], [1, 0], ease),
        }}
      >
      </div>
    </AbsoluteFill>
  );
};

const ProductReveal = ({ tagline }: { tagline: string }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  return (
    <AbsoluteFill
      style={{ backgroundColor: butter, color: ink, overflow: "hidden" }}
    >
      <div
        style={{
          position: "absolute",
          left: 140,
          top: 110,
          fontSize: 28,
          fontWeight: 700,
          opacity: interpolate(frame, [0.35 * fps, 0.9 * fps], [0, 1], ease),
        }}
      >
        Meet Peekaboo.
      </div>
      <div
        style={{
          position: "absolute",
          left: 140,
          top: 360,
          opacity: interpolate(frame, [0.35 * fps, 0.9 * fps], [0, 1], ease),
          translate: `0 ${interpolate(frame, [0, 1.2 * fps], [40, 0], ease)}px`,
        }}
      >
        <h1
          style={{
            fontSize: 174,
            fontWeight: 800,
            letterSpacing: -10,
            lineHeight: 1,
            margin: 0,
          }}
        >
          Peekaboo.
        </h1>
        <p
          style={{
            fontSize: 44,
            fontWeight: 600,
            letterSpacing: -1.2,
            margin: "44px 0 0",
          }}
        >
          {tagline}
        </p>
        <p
          style={{
            fontSize: 29,
            lineHeight: 1.6,
            maxWidth: 740,
            margin: "28px 0 0",
          }}
        >
          Software that chooses when a microscope
          <br />
          takes its next image.
        </p>
      </div>
      <Img
        src={staticFile("brand/capybara.png")}
        style={{
          position: "absolute",
          right: 60,
          top: 205,
          width: 720,
          height: 700,
          objectFit: "contain",
          opacity: interpolate(frame, [0.1 * fps, 0.9 * fps], [0, 1], ease),
          translate: `${interpolate(frame, [0, 1.5 * fps], [45, 0], ease)}px 0`,
        }}
      />
    </AbsoluteFill>
  );
};

export type ProofProps = { tagline: string };
export const ProofOfStyle = ({ tagline }: ProofProps) => {
  const { fps } = useVideoConfig();
  return (
    <AbsoluteFill style={{ fontFamily: "Manrope, sans-serif" }}>
      <TransitionSeries>
        <TransitionSeries.Sequence
          name="Question / conceptual signal"
          durationInFrames={5.5 * fps}
        >
          <SignalStudy />
        </TransitionSeries.Sequence>
        <TransitionSeries.Transition
          presentation={fade()}
          timing={linearTiming({ durationInFrames: 0.5 * fps })}
        />
        <TransitionSeries.Sequence
          name="Product reveal"
          durationInFrames={5 * fps}
        >
          <ProductReveal tagline={tagline} />
        </TransitionSeries.Sequence>
      </TransitionSeries>
      <Soundtrack />
    </AbsoluteFill>
  );
};
