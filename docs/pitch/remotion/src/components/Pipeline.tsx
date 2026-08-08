import React from "react";
import { interpolate, useCurrentFrame } from "remotion";
import { PIPELINE_NODES } from "../data/copy";
import { easeOut } from "../motion";
import { colors, fonts } from "../theme";

type PipelineProps = {
  /** 0..1 draw progress */
  progress: number;
  compact?: boolean;
};

export const Pipeline: React.FC<PipelineProps> = ({
  progress,
  compact = false,
}) => {
  const n = PIPELINE_NODES.length;
  const visible = Math.min(n, Math.floor(progress * n) + (progress > 0 ? 1 : 0));

  return (
    <div
      style={{
        display: "flex",
        alignItems: "flex-start",
        gap: compact ? 12 : 18,
        width: "100%",
        justifyContent: "space-between",
      }}
    >
      {PIPELINE_NODES.map((node, i) => {
        const on = i < visible;
        const local = interpolate(
          progress,
          [i / n, (i + 1) / n],
          [0, 1],
          {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
            easing: easeOut,
          },
        );
        return (
          <React.Fragment key={node.label}>
            <div
              style={{
                flex: 1,
                opacity: on ? interpolate(local, [0, 1], [0.35, 1]) : 0.15,
                transform: `translateY(${on ? interpolate(local, [0, 1], [12, 0]) : 12}px)`,
                textAlign: "center",
              }}
            >
              <div
                style={{
                  border: `1px solid ${on ? colors.accent : colors.line}`,
                  background: colors.card,
                  borderRadius: 10,
                  padding: compact ? "14px 8px" : "18px 10px",
                  fontFamily: fonts.mono,
                  fontSize: compact ? 16 : 20,
                  fontWeight: 500,
                  color: colors.paper,
                }}
              >
                {node.label}
              </div>
              {node.note ? (
                <div
                  style={{
                    marginTop: 10,
                    fontSize: compact ? 13 : 15,
                    color: colors.muted,
                    fontFamily: fonts.display,
                  }}
                >
                  {node.note}
                </div>
              ) : (
                <div style={{ height: 28 }} />
              )}
            </div>
            {i < n - 1 ? (
              <div
                style={{
                  width: compact ? 18 : 28,
                  height: 2,
                  marginTop: compact ? 28 : 32,
                  background:
                    i < visible - 1
                      ? colors.accent
                      : colors.line,
                  flexShrink: 0,
                  opacity: i < visible - 1 ? 1 : 0.35,
                }}
              />
            ) : null}
          </React.Fragment>
        );
      })}
    </div>
  );
};

/** Convenience: drive progress from frame over `duration` frames. */
export const AnimatedPipeline: React.FC<{
  durationInFrames?: number;
  compact?: boolean;
}> = ({ durationInFrames = 60, compact }) => {
  const frame = useCurrentFrame();
  const progress = interpolate(frame, [0, durationInFrames], [0, 1], {
    extrapolateRight: "clamp",
    easing: easeOut,
  });
  return <Pipeline progress={progress} compact={compact} />;
};
