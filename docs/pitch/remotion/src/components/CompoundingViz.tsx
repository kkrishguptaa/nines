import React from "react";
import { interpolate, useCurrentFrame } from "remotion";
import { easeOut } from "../motion";
import { colors, fonts } from "../theme";

/** PRD problem math: 0.95^n end-to-end survival. */
export const COMPOUND_POINTS = [
  { step: 1, rate: 0.95 },
  { step: 5, rate: 0.774 },
  { step: 10, rate: 0.599 },
  { step: 20, rate: 0.358 },
] as const;

type CompoundingVizProps = {
  progress: number;
};

export const CompoundingViz: React.FC<CompoundingVizProps> = ({ progress }) => {
  const maxH = 320;

  return (
    <div style={{ width: "100%" }}>
      <div
        style={{
          display: "flex",
          alignItems: "flex-end",
          gap: 48,
          height: maxH + 80,
          paddingLeft: 8,
        }}
      >
        {COMPOUND_POINTS.map((p, i) => {
          const local = interpolate(
            progress,
            [i * 0.18, i * 0.18 + 0.22],
            [0, 1],
            { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: easeOut },
          );
          const h = p.rate * maxH * local;
          const isEnd = i === COMPOUND_POINTS.length - 1;
          return (
            <div key={p.step} style={{ flex: 1, textAlign: "center" }}>
              <div
                style={{
                  fontFamily: fonts.mono,
                  fontSize: isEnd ? 36 : 28,
                  fontWeight: 600,
                  color: isEnd ? colors.red : colors.paper,
                  marginBottom: 12,
                  opacity: local,
                }}
              >
                {Math.round(p.rate * 100)}%
              </div>
              <div
                style={{
                  height: maxH,
                  display: "flex",
                  alignItems: "flex-end",
                  justifyContent: "center",
                }}
              >
                <div
                  style={{
                    width: "70%",
                    maxWidth: 120,
                    height: Math.max(h, 2),
                    background: isEnd ? colors.red : colors.accent,
                    borderRadius: "8px 8px 2px 2px",
                    opacity: 0.35 + 0.65 * local,
                    boxShadow: isEnd
                      ? `0 0 40px rgba(255,107,107,0.25)`
                      : undefined,
                  }}
                />
              </div>
              <div
                style={{
                  marginTop: 16,
                  fontFamily: fonts.mono,
                  fontSize: 20,
                  color: colors.muted,
                }}
              >
                {p.step} step{p.step === 1 ? "" : "s"}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export const AnimatedCompoundingViz: React.FC<{
  durationInFrames?: number;
}> = ({ durationInFrames = 90 }) => {
  const frame = useCurrentFrame();
  const progress = interpolate(frame, [0, durationInFrames], [0, 1], {
    extrapolateRight: "clamp",
    easing: easeOut,
  });
  return <CompoundingViz progress={progress} />;
};
