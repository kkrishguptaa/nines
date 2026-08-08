import React from "react";
import { interpolate, useCurrentFrame } from "remotion";
import { METRICS } from "../data/copy";
import { colors, fonts } from "../theme";

type WaldWilsonProps = {
  /** 0..1 animation progress */
  progress: number;
  caption?: boolean;
};

export const WaldWilson: React.FC<WaldWilsonProps> = ({
  progress,
  caption = true,
}) => {
  const wilsonLow = METRICS.wilsonAt15;
  // Wald at 15/15: width collapses to 0 at p=1
  const waldWidth = interpolate(progress, [0, 0.55, 1], [0.35, 0.08, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const wilsonReveal = interpolate(progress, [0.25, 0.85], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <div style={{ width: "100%" }}>
      <div
        style={{
          fontFamily: fonts.mono,
          fontSize: 20,
          color: colors.muted,
          marginBottom: 36,
        }}
      >
        15 passes / 15 trials
      </div>

      <Row
        label="Wald"
        sub="width → 0 at n/n"
        track={
          <div style={{ position: "relative", height: 28 }}>
            <Track />
            <div
              style={{
                position: "absolute",
                left: `${(1 - waldWidth) * 100}%`,
                right: 0,
                top: 8,
                height: 12,
                background: colors.red,
                borderRadius: 4,
                opacity: interpolate(progress, [0, 0.4], [0.9, 0.35]),
              }}
            />
            <Tick at={1} label="1.0" />
          </div>
        }
      />

      <div style={{ height: 40 }} />

      <Row
        label="Wilson"
        sub={`lower bound ≈ ${wilsonLow.toFixed(2)}`}
        track={
          <div style={{ position: "relative", height: 36, opacity: wilsonReveal }}>
            <Track />
            <div
              style={{
                position: "absolute",
                left: `${wilsonLow * 100}%`,
                right: 0,
                top: 8,
                height: 12,
                background: colors.accent,
                borderRadius: 4,
                boxShadow: `0 0 0 1px ${colors.accent}`,
              }}
            />
            <Tick at={wilsonLow} label={`${wilsonLow.toFixed(2)}`} accent />
            <Tick at={1} label="1.0" />
          </div>
        }
      />

      {caption ? (
        <div
          style={{
            marginTop: 48,
            fontSize: 22,
            color: colors.muted,
            maxWidth: 900,
            lineHeight: 1.4,
          }}
        >
          Wald lies at 0/n and n/n — exactly where agent demos live. Wilson keeps
          an honest lower gate. That is why 15 / 25 / 40 clear 0.7 / 0.8 / 0.9.
        </div>
      ) : null}
    </div>
  );
};

export const AnimatedWaldWilson: React.FC<{
  durationInFrames?: number;
  caption?: boolean;
}> = ({ durationInFrames = 50, caption }) => {
  const frame = useCurrentFrame();
  const progress = interpolate(frame, [0, durationInFrames], [0, 1], {
    extrapolateRight: "clamp",
  });
  return <WaldWilson progress={progress} caption={caption} />;
};

const Track: React.FC = () => (
  <div
    style={{
      position: "absolute",
      left: 0,
      right: 0,
      top: 13,
      height: 2,
      background: colors.line,
    }}
  />
);

const Tick: React.FC<{ at: number; label: string; accent?: boolean }> = ({
  at,
  label,
  accent,
}) => (
  <>
    <div
      style={{
        position: "absolute",
        left: `${at * 100}%`,
        top: 4,
        width: 2,
        height: 22,
        background: accent ? colors.accent : colors.paper,
        transform: "translateX(-1px)",
      }}
    />
    <div
      style={{
        position: "absolute",
        left: `${at * 100}%`,
        top: 28,
        transform: "translateX(-50%)",
        fontFamily: fonts.mono,
        fontSize: 16,
        color: accent ? colors.accent : colors.muted,
      }}
    >
      {label}
    </div>
  </>
);

const Row: React.FC<{
  label: string;
  sub: string;
  track: React.ReactNode;
}> = ({ label, sub, track }) => (
  <div style={{ display: "flex", gap: 32, alignItems: "flex-start" }}>
    <div style={{ width: 160, flexShrink: 0 }}>
      <div style={{ fontSize: 28, fontWeight: 600 }}>{label}</div>
      <div style={{ fontSize: 16, color: colors.muted, marginTop: 6 }}>{sub}</div>
    </div>
    <div style={{ flex: 1 }}>{track}</div>
  </div>
);
