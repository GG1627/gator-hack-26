import type { CSSProperties, ReactNode } from "react";
import { AbsoluteFill, interpolate, useCurrentFrame } from "remotion";
import { color, ease } from "./theme";

export const Canvas = ({
  children,
  light = false,
}: {
  children: ReactNode;
  light?: boolean;
}) => (
  <AbsoluteFill
    style={{
      background: light ? color.butter : color.ink,
      color: light ? color.ink : color.paper,
      padding: "86px 110px 155px",
      overflow: "hidden",
    }}
  >
    {children}
  </AbsoluteFill>
);
export const Eyebrow = ({ children }: { children: ReactNode }) => (
  <div
    style={{
      fontSize: 25,
      fontWeight: 650,
      letterSpacing: 2,
      textTransform: "uppercase",
      marginBottom: 32,
      opacity: 0.65,
    }}
  >
    {children}
  </div>
);
export const Title = ({
  children,
  style,
}: {
  children: ReactNode;
  style?: CSSProperties;
}) => {
  const f = useCurrentFrame();
  return (
    <h1
      style={{
        fontSize: 88,
        lineHeight: 1.08,
        letterSpacing: -4,
        fontWeight: 700,
        margin: 0,
        maxWidth: 1500,
        opacity: interpolate(f, [3, 24], [0, 1], ease),
        translate: `0 ${interpolate(f, [3, 32], [22, 0], ease)}px`,
        ...style,
      }}
    >
      {children}
    </h1>
  );
};
export const Note = ({ children }: { children: ReactNode }) => (
  <div
    style={{
      position: "absolute",
      left: 110,
      right: 110,
      bottom: 150,
      fontSize: 25,
      lineHeight: 1.5,
      opacity: 0.65,
    }}
  >
    {children}
  </div>
);
export const Enter = ({
  children,
  at = 0,
  style,
}: {
  children: ReactNode;
  at?: number;
  style?: CSSProperties;
}) => {
  const f = useCurrentFrame();
  return (
    <div
      style={{
        ...style,
        opacity: interpolate(f, [at, at + 24], [0, 1], ease),
        translate: `0 ${interpolate(f, [at, at + 30], [20, 0], ease)}px`,
      }}
    >
      {children}
    </div>
  );
};
export const Rule = () => (
  <div style={{ height: 1, background: color.line, margin: "36px 0" }} />
);
export const DraftTag = () => (
  <div
    style={{
      position: "absolute",
      right: 28,
      top: 24,
      padding: "8px 15px",
      borderRadius: 30,
      fontSize: 19,
      color: "#fff",
      background: "#242629dc",
    }}
  >
    PREVIEW · narrated
  </div>
);
