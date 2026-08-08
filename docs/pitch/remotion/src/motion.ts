import { Easing, interpolate } from "remotion";

/** Crisp UI entrance — Remotion timing skill default. */
export const easeOut = Easing.bezier(0.16, 1, 0.3, 1);

export const clampEnter = (
  frame: number,
  from: number,
  to: number,
  range: [number, number] = [0, 1],
) =>
  interpolate(frame, [from, to], range, {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: easeOut,
  });

/** Soft exit near end of a beat (opacity → 0). */
export const beatExit = (
  frame: number,
  durationInFrames: number,
  fadeFrames = 10,
) =>
  interpolate(
    frame,
    [durationInFrames - fadeFrames, durationInFrames],
    [1, 0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" },
  );
