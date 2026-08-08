import React from "react";
import {
  AbsoluteFill,
  Sequence,
  interpolate,
  useCurrentFrame,
} from "remotion";
import { AnimatedCompoundingViz } from "../components/CompoundingViz";
import { AnimatedHowItWorksViz } from "../components/HowItWorksViz";
import { AnimatedReceiptCard } from "../components/ReceiptCard";
import { AnimatedWaldWilson } from "../components/WaldWilson";
import { METRICS, PROBLEM } from "../data/copy";
import { beatExit, clampEnter, easeOut } from "../motion";
import { REPO_URL, colors, fonts, fps } from "../theme";

const sec = (s: number) => Math.round(s * fps);

/**
 * DemoReel — silent B-roll for VO (~85s).
 * THESIS: compounding failure → hope is not a bar → Nines measures or refuses.
 * Numbers from PRD problem statement only (no invented studies).
 */

export const DemoReel: React.FC = () => {
  return (
    <AbsoluteFill style={{ backgroundColor: colors.bg }}>
      <Sequence from={sec(0)} durationInFrames={sec(5)} name="title">
        <TitleBeat />
      </Sequence>
      <Sequence from={sec(5)} durationInFrames={sec(11)} name="problem">
        <ProblemBeat />
      </Sequence>
      <Sequence from={sec(16)} durationInFrames={sec(7)} name="hope">
        <HopeBeat />
      </Sequence>
      <Sequence from={sec(23)} durationInFrames={sec(19)} name="how">
        <HowBeat />
      </Sequence>
      <Sequence from={sec(42)} durationInFrames={sec(10)} name="wilson">
        <WilsonBeat />
      </Sequence>
      <Sequence from={sec(52)} durationInFrames={sec(10)} name="green">
        <GreenBeat />
      </Sequence>
      <Sequence from={sec(62)} durationInFrames={sec(12)} name="red">
        <RedBeat />
      </Sequence>
      <Sequence from={sec(74)} durationInFrames={sec(11)} name="end">
        <EndBeat />
      </Sequence>
    </AbsoluteFill>
  );
};

const TitleBeat: React.FC = () => {
  const frame = useCurrentFrame();
  const dur = sec(5);
  const exit = beatExit(frame, dur, 10);
  const titleY = clampEnter(frame, 0, 18, [28, 0]);
  const titleOp = clampEnter(frame, 0, 16);
  const titleBlur = interpolate(frame, [0, 16], [8, 0], {
    extrapolateRight: "clamp",
    easing: easeOut,
  });
  const subOp = clampEnter(frame, 16, 32);
  const rule = clampEnter(frame, 22, 38);

  return (
    <Scene exitOpacity={exit}>
      <div style={{ opacity: titleOp * exit, transform: `translateY(${titleY}px)` }}>
        <div
          style={{
            fontSize: 168,
            fontWeight: 700,
            letterSpacing: "-0.045em",
            lineHeight: 0.92,
            fontFamily: fonts.display,
            filter: `blur(${titleBlur}px)`,
          }}
        >
          NINES
        </div>
        <div
          style={{
            marginTop: 28,
            fontSize: 42,
            color: colors.muted,
            fontFamily: fonts.display,
            fontWeight: 500,
            opacity: subOp,
          }}
        >
          Reliability compiler for Claude
        </div>
        <div
          style={{
            marginTop: 36,
            height: 3,
            width: interpolate(rule, [0, 1], [0, 220]),
            background: colors.accent,
            borderRadius: 2,
          }}
        />
      </div>
    </Scene>
  );
};

const ProblemBeat: React.FC = () => {
  const frame = useCurrentFrame();
  const dur = sec(11);
  const exit = beatExit(frame, dur, 12);
  const headOp = clampEnter(frame, 0, 14);
  const callout = clampEnter(frame, 70, 95);

  return (
    <Scene exitOpacity={exit}>
      <div style={{ width: "100%", opacity: exit }}>
        <div
          style={{
            fontFamily: fonts.display,
            fontSize: 44,
            fontWeight: 700,
            letterSpacing: "-0.03em",
            marginBottom: 12,
            opacity: headOp,
          }}
        >
          Per-step errors compound
        </div>
        <div
          style={{
            fontFamily: fonts.mono,
            fontSize: 22,
            color: colors.muted,
            marginBottom: 36,
            opacity: headOp,
          }}
        >
          {PROBLEM.steps} agent steps · {Math.round(PROBLEM.perStep * 100)}%
          reliable each
        </div>
        <AnimatedCompoundingViz durationInFrames={sec(7)} />
        <div
          style={{
            marginTop: 28,
            display: "flex",
            justifyContent: "space-between",
            alignItems: "baseline",
            opacity: callout,
          }}
        >
          <div
            style={{
              fontFamily: fonts.display,
              fontSize: 36,
              fontWeight: 600,
              color: colors.red,
            }}
          >
            {PROBLEM.caption}
          </div>
          <div
            style={{
              fontFamily: fonts.mono,
              fontSize: 16,
              color: colors.muted,
              maxWidth: 420,
              textAlign: "right",
            }}
          >
            {PROBLEM.source}
          </div>
        </div>
      </div>
    </Scene>
  );
};

const HopeBeat: React.FC = () => {
  const frame = useCurrentFrame();
  const dur = sec(7);
  const exit = beatExit(frame, dur, 10);
  const cardOp = clampEnter(frame, 0, 14);
  const cardY = clampEnter(frame, 0, 14, [20, 0]);
  const lineH = clampEnter(frame, 12, 30, [0, 56]);
  const textOp = clampEnter(frame, 24, 42);

  return (
    <Scene exitOpacity={exit}>
      <div style={{ textAlign: "center", opacity: exit }}>
        <div
          style={{
            display: "inline-block",
            border: `1px solid ${colors.line}`,
            background: colors.card,
            borderRadius: 14,
            padding: "28px 44px",
            fontFamily: fonts.mono,
            fontSize: 32,
            opacity: cardOp,
            transform: `translateY(${cardY}px)`,
            boxShadow: "0 28px 80px rgba(0,0,0,0.4)",
          }}
        >
          single-shot Claude
        </div>
        <div
          style={{
            width: 2,
            height: lineH,
            background: colors.accent,
            margin: "0 auto",
            marginTop: 8,
          }}
        />
        <div
          style={{
            fontFamily: fonts.display,
            fontSize: 40,
            color: colors.muted,
            marginTop: 20,
            opacity: textOp,
            fontWeight: 500,
          }}
        >
          An answer. No measured reliability.
        </div>
      </div>
    </Scene>
  );
};

const HowBeat: React.FC = () => {
  const frame = useCurrentFrame();
  const dur = sec(19);
  const exit = beatExit(frame, dur, 14);
  const headOp = clampEnter(frame, 0, 16);

  return (
    <Scene exitOpacity={exit}>
      <div style={{ width: "100%", opacity: exit }}>
        <div
          style={{
            fontFamily: fonts.display,
            fontSize: 48,
            fontWeight: 700,
            letterSpacing: "-0.03em",
            marginBottom: 32,
            opacity: headOp,
          }}
        >
          How Nines works
        </div>
        <AnimatedHowItWorksViz durationInFrames={sec(15)} />
      </div>
    </Scene>
  );
};

const WilsonBeat: React.FC = () => {
  const frame = useCurrentFrame();
  const dur = sec(10);
  const exit = beatExit(frame, dur, 10);
  const headOp = clampEnter(frame, 0, 12);

  return (
    <Scene exitOpacity={exit}>
      <div style={{ width: "100%", opacity: exit }}>
        <div
          style={{
            fontFamily: fonts.display,
            fontSize: 48,
            fontWeight: 700,
            marginBottom: 36,
            letterSpacing: "-0.03em",
            opacity: headOp,
          }}
        >
          Wilson, not Wald
        </div>
        <AnimatedWaldWilson durationInFrames={sec(7)} caption />
      </div>
    </Scene>
  );
};

const GreenBeat: React.FC = () => {
  const frame = useCurrentFrame();
  const dur = sec(10);
  const exit = beatExit(frame, dur, 10);
  const labelOp = clampEnter(frame, 0, 12);

  return (
    <Scene exitOpacity={exit}>
      <div
        style={{
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          gap: 28,
          opacity: exit,
        }}
      >
        <div
          style={{
            fontFamily: fonts.display,
            fontSize: 36,
            fontWeight: 600,
            color: colors.green,
            opacity: labelOp,
          }}
        >
          Easy task clears the bar
        </div>
        <AnimatedReceiptCard
          variant="green"
          task="is_palindrome"
          targetMet
          passes={15}
          trials={15}
          costUsd={METRICS.costs.t07}
          durationInFrames={26}
        />
      </div>
    </Scene>
  );
};

const RedBeat: React.FC = () => {
  const frame = useCurrentFrame();
  const dur = sec(12);
  const exit = beatExit(frame, dur, 10);
  const labelOp = clampEnter(frame, 0, 12);

  return (
    <Scene exitOpacity={exit}>
      <div
        style={{
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          gap: 28,
          opacity: exit,
        }}
      >
        <div
          style={{
            fontFamily: fonts.display,
            fontSize: 36,
            fontWeight: 600,
            color: colors.red,
            opacity: labelOp,
          }}
        >
          Hard task — refuse to lie
        </div>
        <AnimatedReceiptCard
          variant="red"
          task="parse_money"
          targetMet={false}
          models={METRICS.refuseModels}
          durationInFrames={26}
        />
      </div>
    </Scene>
  );
};

const EndBeat: React.FC = () => {
  const frame = useCurrentFrame();
  const line1 = clampEnter(frame, 0, 16);
  const line2 = clampEnter(frame, 10, 28);
  const line3 = clampEnter(frame, 20, 36);
  const meta = clampEnter(frame, 28, 48);

  return (
    <Scene exitOpacity={1}>
      <div style={{ textAlign: "center", maxWidth: 1400 }}>
        <div
          style={{
            fontFamily: fonts.display,
            fontSize: 54,
            fontWeight: 700,
            letterSpacing: "-0.03em",
            lineHeight: 1.25,
          }}
        >
          <span style={{ display: "block", opacity: line1 }}>Declare the bar.</span>
          <span style={{ display: "block", opacity: line2 }}>Buy the evidence.</span>
          <span
            style={{
              display: "block",
              opacity: line3,
              color: colors.accent,
            }}
          >
            Or get an honest no.
          </span>
        </div>
        <div
          style={{
            marginTop: 40,
            fontFamily: fonts.mono,
            fontSize: 24,
            color: colors.muted,
            opacity: meta,
          }}
        >
          Apache 2.0 · {REPO_URL}
        </div>
      </div>
    </Scene>
  );
};

const Scene: React.FC<{
  children: React.ReactNode;
  exitOpacity?: number;
}> = ({ children, exitOpacity = 1 }) => (
  <AbsoluteFill
    style={{
      backgroundColor: colors.bg,
      color: colors.paper,
      fontFamily: fonts.display,
      padding: "64px 96px",
      boxSizing: "border-box",
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
      opacity: exitOpacity,
    }}
  >
    <AbsoluteFill
      style={{
        background:
          "radial-gradient(ellipse 70% 55% at 50% 40%, rgba(245,165,36,0.07), transparent 70%)",
        pointerEvents: "none",
      }}
    />
    <AbsoluteFill
      style={{
        opacity: 0.06,
        backgroundImage:
          "linear-gradient(#fff 1px, transparent 1px), linear-gradient(90deg, #fff 1px, transparent 1px)",
        backgroundSize: "72px 72px",
        pointerEvents: "none",
      }}
    />
    <div style={{ position: "relative", width: "100%" }}>{children}</div>
  </AbsoluteFill>
);
