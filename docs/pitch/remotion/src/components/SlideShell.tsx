import React from "react";
import { AbsoluteFill } from "remotion";
import { colors, fonts } from "../theme";

type SlideShellProps = {
  children: React.ReactNode;
  /** Real heading — not a kicker/eyebrow. */
  heading?: string;
  note?: string;
  showNote?: boolean;
};

export const SlideShell: React.FC<SlideShellProps> = ({
  children,
  heading,
  note,
  showNote = false,
}) => (
  <AbsoluteFill
    style={{
      backgroundColor: colors.bg,
      color: colors.paper,
      fontFamily: fonts.display,
      padding: "72px 96px",
      boxSizing: "border-box",
      display: "flex",
      flexDirection: "column",
    }}
  >
    <AbsoluteFill
      style={{
        opacity: 0.07,
        backgroundImage:
          "linear-gradient(#fff 1px, transparent 1px), linear-gradient(90deg, #fff 1px, transparent 1px)",
        backgroundSize: "64px 64px",
        pointerEvents: "none",
      }}
    />
    {heading ? (
      <h1
        style={{
          position: "relative",
          margin: "0 0 36px",
          fontSize: 56,
          fontWeight: 700,
          letterSpacing: "-0.03em",
          lineHeight: 1.1,
          color: colors.paper,
          flexShrink: 0,
        }}
      >
        {heading}
      </h1>
    ) : null}
    <div
      style={{
        position: "relative",
        flex: 1,
        minHeight: 0,
        display: "flex",
        flexDirection: "column",
        justifyContent: "center",
      }}
    >
      {children}
    </div>
    {showNote && note ? (
      <div
        style={{
          position: "relative",
          flexShrink: 0,
          marginTop: 28,
          fontSize: 18,
          color: colors.muted,
          fontFamily: fonts.mono,
          borderTop: `1px solid ${colors.line}`,
          paddingTop: 16,
          lineHeight: 1.45,
        }}
      >
        SAY · {note}
      </div>
    ) : null}
  </AbsoluteFill>
);
