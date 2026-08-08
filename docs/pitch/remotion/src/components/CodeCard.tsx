import React from "react";
import { CODE_SNIPPET } from "../data/copy";
import { colors, fonts } from "../theme";

export const CodeCard: React.FC<{ code?: string }> = ({
  code = CODE_SNIPPET,
}) => (
  <div
    style={{
      background: colors.card,
      border: `1px solid ${colors.line}`,
      borderRadius: 14,
      padding: "40px 44px",
      fontFamily: fonts.mono,
      fontSize: 28,
      lineHeight: 1.55,
      color: colors.paper,
      whiteSpace: "pre",
      boxShadow: "0 20px 60px rgba(0,0,0,0.35)",
      maxWidth: 1100,
    }}
  >
    {code.split("\n").map((line, i) => (
      <div key={i}>
        {line.startsWith("#") ? (
          <span style={{ color: colors.muted }}>{line}</span>
        ) : (
          <>
            {line.includes("run") ? (
              <span>
                {line.split("run")[0]}
                <span style={{ color: colors.accent }}>run</span>
                {line.split("run").slice(1).join("run")}
              </span>
            ) : (
              line
            )}
          </>
        )}
      </div>
    ))}
  </div>
);
