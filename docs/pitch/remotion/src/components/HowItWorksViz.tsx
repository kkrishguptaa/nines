import React from "react";
import { interpolate, useCurrentFrame } from "remotion";
import { easeOut } from "../motion";
import { colors, fonts } from "../theme";

type Stage = {
  id: string;
  label: string;
  detail: string;
  phase: 1 | 2;
};

const STAGES: Stage[] = [
  { id: "task", label: "Task", detail: "prompt + target + budget", phase: 1 },
  { id: "synth", label: "Synthesize", detail: "checker from task alone", phase: 1 },
  { id: "canary", label: "Canary", detail: "reject known-bad", phase: 1 },
  { id: "fanout", label: "Fan-out", detail: "model × effort × framing", phase: 2 },
  { id: "gate", label: "Gate", detail: "checker on output only", phase: 2 },
  { id: "wilson", label: "Wilson", detail: "lower bound ≥ target?", phase: 2 },
  { id: "receipt", label: "Receipt", detail: "target_met or refuse", phase: 2 },
];

type HowItWorksVizProps = {
  progress: number;
};

export const HowItWorksViz: React.FC<HowItWorksVizProps> = ({ progress }) => {
  const n = STAGES.length;
  const active = Math.min(n - 1, Math.floor(progress * n));

  return (
    <div style={{ width: "100%" }}>
      <div
        style={{
          display: "flex",
          gap: 24,
          marginBottom: 28,
          fontFamily: fonts.mono,
          fontSize: 18,
        }}
      >
        <PhasePill
          label="Phase 1 · Setup"
          detail="~2 LLM calls"
          on={progress > 0.05}
        />
        <PhasePill
          label="Phase 2 · Sample"
          detail="N attempts until bar or budget"
          on={progress > 0.4}
        />
      </div>

      <div
        style={{
          display: "flex",
          alignItems: "stretch",
          gap: 10,
          width: "100%",
        }}
      >
        {STAGES.map((stage, i) => {
          const on = i <= active;
          const local = interpolate(
            progress,
            [i / n, (i + 0.85) / n],
            [0, 1],
            { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: easeOut },
          );
          const isReceipt = stage.id === "receipt";
          return (
            <React.Fragment key={stage.id}>
              <div
                style={{
                  flex: 1,
                  opacity: 0.25 + 0.75 * (on ? local : 0),
                  transform: `translateY(${on ? (1 - local) * 14 : 14}px)`,
                }}
              >
                <div
                  style={{
                    background: colors.card,
                    border: `1.5px solid ${on
                        ? isReceipt
                          ? colors.green
                          : stage.phase === 1
                            ? colors.accent
                            : colors.paper
                        : colors.line
                      }`,
                    borderRadius: 12,
                    padding: "20px 14px",
                    minHeight: 140,
                    display: "flex",
                    flexDirection: "column",
                    justifyContent: "center",
                  }}
                >
                  <div
                    style={{
                      fontFamily: fonts.mono,
                      fontSize: 14,
                      color: colors.muted,
                      marginBottom: 8,
                    }}
                  >
                    {stage.phase === 1 ? "setup" : "loop"}
                  </div>
                  <div
                    style={{
                      fontFamily: fonts.display,
                      fontSize: 24,
                      fontWeight: 600,
                      marginBottom: 8,
                    }}
                  >
                    {stage.label}
                  </div>
                  <div
                    style={{
                      fontFamily: fonts.mono,
                      fontSize: 15,
                      color: colors.muted,
                      lineHeight: 1.35,
                    }}
                  >
                    {stage.detail}
                  </div>
                </div>
              </div>
              {i < n - 1 ? (
                <div
                  style={{
                    width: 18,
                    alignSelf: "center",
                    height: 2,
                    background:
                      i < active ? colors.accent : colors.line,
                    flexShrink: 0,
                    opacity: i < active ? 1 : 0.4,
                  }}
                />
              ) : null}
            </React.Fragment>
          );
        })}
      </div>

      {/* Escalate loop hint under Wilson */}
      <div
        style={{
          marginTop: 28,
          fontFamily: fonts.mono,
          fontSize: 20,
          color: colors.muted,
          opacity: interpolate(progress, [0.7, 0.9], [0, 1], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
          }),
        }}
      >
        If Wilson lower bound is below target → escalate another batch. Else stop.
        Zero passes → no silent best-guess.
      </div>
    </div>
  );
};

const PhasePill: React.FC<{ label: string; detail: string; on: boolean }> = ({
  label,
  detail,
  on,
}) => (
  <div
    style={{
      border: `1px solid ${on ? colors.accent : colors.line}`,
      borderRadius: 999,
      padding: "10px 18px",
      opacity: on ? 1 : 0.45,
      background: colors.card,
    }}
  >
    <span style={{ color: on ? colors.accent : colors.muted }}>{label}</span>
    <span style={{ color: colors.muted }}> · {detail}</span>
  </div>
);

export const AnimatedHowItWorksViz: React.FC<{
  durationInFrames?: number;
}> = ({ durationInFrames = 120 }) => {
  const frame = useCurrentFrame();
  const progress = interpolate(frame, [0, durationInFrames], [0, 1], {
    extrapolateRight: "clamp",
    easing: easeOut,
  });
  return <HowItWorksViz progress={progress} />;
};
