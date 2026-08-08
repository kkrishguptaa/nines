import React from "react";
import { AbsoluteFill, Sequence, interpolate, useCurrentFrame } from "remotion";
import { CodeCard } from "../components/CodeCard";
import { Pipeline } from "../components/Pipeline";
import { ReceiptCard } from "../components/ReceiptCard";
import { SlideShell } from "../components/SlideShell";
import { WaldWilson } from "../components/WaldWilson";
import { METRICS, SLIDES } from "../data/copy";
import { REPO_URL, colors, fonts, slideDurationInFrames } from "../theme";

const SHOW_NOTES = true;

export const PitchDeck: React.FC = () => {
  return (
    <AbsoluteFill style={{ backgroundColor: colors.bg }}>
      {SLIDES.map((slide, i) => (
        <Sequence
          key={slide.id}
          from={i * slideDurationInFrames}
          durationInFrames={slideDurationInFrames}
          name={slide.title}
        >
          <SlideFrame id={slide.id} note={slide.say} />
        </Sequence>
      ))}
    </AbsoluteFill>
  );
};

const SlideFrame: React.FC<{
  id: (typeof SLIDES)[number]["id"];
  note: string;
}> = ({ id, note }) => {
  const frame = useCurrentFrame();
  const enter = interpolate(frame, [0, 10], [0.92, 1], {
    extrapolateRight: "clamp",
  });

  switch (id) {
    case "title":
      return (
        <SlideShell note={note} showNote={SHOW_NOTES}>
          <div style={{ opacity: enter }}>
            <div
              style={{
                fontSize: 168,
                fontWeight: 700,
                letterSpacing: "-0.04em",
                lineHeight: 0.9,
              }}
            >
              NINES
            </div>
            <div
              style={{
                marginTop: 28,
                fontSize: 40,
                color: colors.muted,
                fontWeight: 500,
                maxWidth: 900,
              }}
            >
              Reliability compiler for Claude
            </div>
            <div
              style={{
                marginTop: 44,
                fontFamily: fonts.mono,
                fontSize: 22,
                color: colors.accent,
              }}
            >
              Apache 2.0 · {REPO_URL}
            </div>
          </div>
        </SlideShell>
      );

    case "gap":
      return (
        <SlideShell heading="Hope is not a reliability bar" note={note} showNote={SHOW_NOTES}>
          <div style={{ display: "flex", gap: 48, opacity: enter }}>
            <Panel title="Ask Claude once">
              <div style={{ fontSize: 34, color: colors.muted }}>then hope</div>
            </Panel>
            <Panel title="Declared reliability" empty>
              <div
                style={{
                  height: 3,
                  width: 120,
                  background: colors.line,
                  marginBottom: 16,
                }}
              />
              <div style={{ color: colors.muted, fontSize: 22 }}>missing today</div>
            </Panel>
          </div>
        </SlideShell>
      );

    case "oneCall":
      return (
        <SlideShell heading="One public seam" note={note} showNote={SHOW_NOTES}>
          <div style={{ opacity: enter }}>
            <CodeCard />
          </div>
        </SlideShell>
      );

    case "pipeline":
      return (
        <SlideShell heading="Verifier first, then evidence" note={note} showNote={SHOW_NOTES}>
          <div style={{ opacity: enter }}>
            <Pipeline
              progress={interpolate(frame, [0, 50], [0, 1], {
                extrapolateRight: "clamp",
              })}
            />
          </div>
        </SlideShell>
      );

    case "wilson":
      return (
        <SlideShell heading="Wilson, not Wald" note={note} showNote={SHOW_NOTES}>
          <div style={{ opacity: enter }}>
            <WaldWilson
              progress={interpolate(frame, [0, 55], [0, 1], {
                extrapolateRight: "clamp",
              })}
            />
          </div>
        </SlideShell>
      );

    case "cost":
      return (
        <SlideShell heading="You pay for evidence" note={note} showNote={SHOW_NOTES}>
          <div style={{ opacity: enter }}>
            <table
              style={{
                width: "100%",
                borderCollapse: "collapse",
                fontFamily: fonts.mono,
                fontSize: 28,
              }}
            >
              <thead>
                <tr style={{ color: colors.muted, textAlign: "left" }}>
                  <th style={th}>Target</th>
                  <th style={th}>Attempts</th>
                  <th style={th}>LLM calls</th>
                  <th style={th}>Cost USD</th>
                </tr>
              </thead>
              <tbody>
                <CostRow
                  bar="0.7"
                  attempts={METRICS.attempts.t07}
                  calls={METRICS.calls.t07}
                  cost={METRICS.costs.t07}
                />
                <CostRow
                  bar="0.8"
                  attempts={METRICS.attempts.t08}
                  calls={METRICS.calls.t08}
                  cost={METRICS.costs.t08}
                />
                <CostRow
                  bar="0.9"
                  attempts={METRICS.attempts.t09}
                  calls={METRICS.calls.t09}
                  cost={METRICS.costs.t09}
                />
              </tbody>
            </table>
            <div style={{ marginTop: 40, fontSize: 24, color: colors.muted }}>
              Setup is about two calls. The rest is sampling.
            </div>
          </div>
        </SlideShell>
      );

    case "moment":
      return (
        <SlideShell heading="Clear the bar — or refuse" note={note} showNote={SHOW_NOTES}>
          <div
            style={{
              display: "flex",
              gap: 40,
              opacity: enter,
              alignItems: "stretch",
              justifyContent: "center",
              width: "100%",
            }}
          >
            <ReceiptCard
              variant="green"
              task="is_palindrome"
              targetMet
              passes={15}
              trials={15}
              costUsd={METRICS.costs.t07}
              progress={1}
            />
            <ReceiptCard
              variant="red"
              task="parse_money"
              targetMet={false}
              models={METRICS.refuseModels}
              progress={1}
            />
          </div>
        </SlideShell>
      );

    case "claims":
      return (
        <SlideShell heading="What we claim" note={note} showNote={SHOW_NOTES}>
          <div style={{ display: "flex", gap: 48, opacity: enter }}>
            <ClaimCol
              title="Claimed"
              items={[
                "orchestration to a Receipt",
                "independent verifier and canary",
                "budgeted diverse fan-out",
                "Wilson-gated target_met",
              ]}
              good
            />
            <ClaimCol
              title="Not claimed"
              items={[
                "novel model or weights",
                "production SLA",
                "multi-tenant isolation",
              ]}
            />
          </div>
          <div
            style={{
              marginTop: 48,
              fontSize: 22,
              color: colors.muted,
              maxWidth: 1100,
              lineHeight: 1.45,
            }}
          >
            Limit: we measure checker-pass rate, not ground-truth correctness.
            The canary reduces that risk. It does not remove it.
          </div>
        </SlideShell>
      );

    default:
      return null;
  }
};

const Panel: React.FC<{
  title: string;
  children: React.ReactNode;
  empty?: boolean;
}> = ({ title, children, empty }) => (
  <div
    style={{
      flex: 1,
      background: colors.card,
      border: `1px solid ${empty ? colors.line : colors.accent}`,
      borderRadius: 16,
      padding: "48px 40px",
      minHeight: 280,
    }}
  >
    <div style={{ fontSize: 32, fontWeight: 600, marginBottom: 28 }}>{title}</div>
    {children}
  </div>
);

const th: React.CSSProperties = {
  padding: "16px 12px",
  borderBottom: `1px solid ${colors.line}`,
  fontWeight: 500,
};

const CostRow: React.FC<{
  bar: string;
  attempts: number;
  calls: number;
  cost: number;
}> = ({ bar, attempts, calls, cost }) => (
  <tr>
    <td style={td}>{bar}</td>
    <td style={td}>{attempts}</td>
    <td style={td}>{calls}</td>
    <td style={{ ...td, color: colors.accent }}>{cost.toFixed(2)}</td>
  </tr>
);

const td: React.CSSProperties = {
  padding: "22px 12px",
  borderBottom: `1px solid ${colors.line}`,
  color: colors.paper,
};

const ClaimCol: React.FC<{
  title: string;
  items: string[];
  good?: boolean;
}> = ({ title, items, good }) => (
  <div
    style={{
      flex: 1,
      background: colors.card,
      borderRadius: 16,
      padding: "40px 36px",
      border: `1px solid ${good ? colors.green : colors.line}`,
    }}
  >
    <div
      style={{
        fontSize: 28,
        fontWeight: 600,
        marginBottom: 24,
        color: good ? colors.green : colors.muted,
      }}
    >
      {title}
    </div>
    <ul style={{ margin: 0, paddingLeft: 22, fontSize: 26, lineHeight: 1.7 }}>
      {items.map((item) => (
        <li key={item}>{item}</li>
      ))}
    </ul>
  </div>
);
