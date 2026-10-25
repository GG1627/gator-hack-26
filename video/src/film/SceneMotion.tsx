import type { ReactNode } from "react";
import { AbsoluteFill, Easing, interpolate, useCurrentFrame } from "remotion";
import { ease } from "./theme";
// A short fade through charcoal keeps every recording and narration on its own clock.
export const SceneMotion = ({
  children,
  duration,
  recorded = false,
}: {
  children: ReactNode;
  duration: number;
  recorded?: boolean;
}) => {
  const f = useCurrentFrame();
  return (
    <AbsoluteFill
      style={{
        opacity: interpolate(
          f,
          [0, 14, Math.max(15, duration - 12), duration - 1],
          [0, 1, 1, 0],
          { ...ease, easing: Easing.inOut(Easing.cubic) },
        ),
        ...(recorded
          ? {}
          : { translate: `0 ${interpolate(f, [0, 28], [12, 0], ease)}px` }),
      }}
    >
      {children}
    </AbsoluteFill>
  );
};
