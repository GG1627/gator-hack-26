import { Easing } from "remotion";
export const color = {
  ink: "#242629",
  paper: "#f5f1e7",
  butter: "#f6d48b",
  amber: "#e9b669",
  blue: "#7da5c3",
  muted: "#b7bbb8",
  line: "#ffffff25",
};
export const ease = {
  extrapolateLeft: "clamp",
  extrapolateRight: "clamp",
  easing: Easing.bezier(0.16, 1, 0.3, 1),
} as const;
