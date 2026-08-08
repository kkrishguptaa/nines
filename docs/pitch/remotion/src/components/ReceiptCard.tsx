import React from "react";
import { interpolate, useCurrentFrame } from "remotion";
import { easeOut } from "../motion";
import { colors, fonts } from "../theme";

export type ModelChip = { model: string; pass: number; trials: number };

type ReceiptCardProps = {
  variant: "green" | "red";
  task: string;
  targetMet: boolean;
  passes?: number;
  trials?: number;
  costUsd?: number;
  models?: readonly ModelChip[];
  /** 0..1 flip / enter */
  progress?: number;
};

export const ReceiptCard: React.FC<ReceiptCardProps> = ({
  variant,
  task,
  targetMet,
  passes,
  trials,
  costUsd,
  models,
  progress = 1,
}) => {
  const border = variant === "green" ? colors.green : colors.red;
  const y = interpolate(progress, [0, 1], [36, 0], { easing: easeOut });
  const opacity = interpolate(progress, [0, 1], [0, 1], { easing: easeOut });
  const scale = interpolate(progress, [0, 1], [0.96, 1], { easing: easeOut });

  return (
    <div
      style={{
        background: colors.card,
        border: `2px solid ${border}`,
        borderRadius: 16,
        padding: "36px 40px",
        fontFamily: fonts.mono,
        transform: `translateY(${y}px) scale(${scale})`,
        opacity,
        boxShadow: `0 28px 90px rgba(0,0,0,0.5)`,
        minWidth: 420,
      }}
    >
      <div style={{ fontSize: 18, color: colors.muted, marginBottom: 12 }}>
        receipt · {task}
      </div>
      <div
        style={{
          fontSize: 42,
          fontWeight: 600,
          color: border,
          marginBottom: 24,
          fontFamily: fonts.display,
        }}
      >
        target_met: {targetMet ? "true" : "false"}
      </div>
      {passes != null && trials != null ? (
        <div style={{ fontSize: 24, color: colors.paper, marginBottom: 10 }}>
          passes {passes}/{trials}
        </div>
      ) : null}
      {costUsd != null ? (
        <div style={{ fontSize: 22, color: colors.muted, marginBottom: 18 }}>
          cost ≈ ${costUsd.toFixed(2)}
        </div>
      ) : null}
      {models && models.length > 0 ? (
        <div style={{ display: "flex", gap: 10, flexWrap: "wrap", marginTop: 8 }}>
          {models.map((m) => (
            <div
              key={m.model}
              style={{
                border: `1px solid ${colors.line}`,
                borderRadius: 8,
                padding: "8px 12px",
                fontSize: 18,
                color: colors.paper,
                background: colors.bg,
              }}
            >
              <span style={{ color: colors.accent }}>{m.model}</span>{" "}
              {m.pass}/{m.trials}
              <div
                style={{
                  marginTop: 8,
                  height: 4,
                  background: colors.line,
                  borderRadius: 2,
                  overflow: "hidden",
                }}
              >
                <div
                  style={{
                    width: `${(m.pass / m.trials) * 100}%`,
                    height: "100%",
                    background: border,
                  }}
                />
              </div>
            </div>
          ))}
        </div>
      ) : null}
    </div>
  );
};

export const AnimatedReceiptCard: React.FC<
  Omit<ReceiptCardProps, "progress"> & { durationInFrames?: number }
> = ({ durationInFrames = 24, ...rest }) => {
  const frame = useCurrentFrame();
  const progress = interpolate(frame, [0, durationInFrames], [0, 1], {
    extrapolateRight: "clamp",
  });
  return <ReceiptCard {...rest} progress={progress} />;
};
