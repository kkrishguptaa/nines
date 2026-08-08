/** Editable constants — match README / SCRIPTS measured numbers. */

export const METRICS = {
  wilsonAt15: 0.8,
  wilsonAt25: 0.87,
  wilsonAt40: 0.91,
  costs: {
    t07: 0.02,
    t08: 0.06,
    t09: 0.13,
  },
  calls: {
    t07: 17,
    t08: 27,
    t09: 42,
  },
  attempts: {
    t07: 15,
    t08: 25,
    t09: 40,
  },
  refuseModels: [
    { model: "opus", pass: 5, trials: 8 },
    { model: "sonnet", pass: 7, trials: 8 },
    { model: "haiku", pass: 1, trials: 9 },
  ],
} as const;

export type SlideId =
  | "title"
  | "gap"
  | "oneCall"
  | "pipeline"
  | "wilson"
  | "cost"
  | "moment"
  | "claims";

export const SLIDES: {
  id: SlideId;
  title: string;
  say: string;
}[] = [
    {
      id: "title",
      title: "NINES",
      say: "Agents are right most of the time. Shipping needs a number — and a system that refuses when it can't prove it.",
    },
    {
      id: "gap",
      title: "The gap",
      say: "Today you pick a model and hope. Nothing lets you declare a reliability target and spend compute until the math clears it — or stop honestly.",
    },
    {
      id: "oneCall",
      title: "One call",
      say: "One public seam. You name the bar and the budget. You get a receipt — green ship or red escalate. Never a silent best-guess when nothing passed.",
    },
    {
      id: "pipeline",
      title: "Pipeline",
      say: "Verifier first — from the task alone. Canary kills checkers that accept garbage. Then diverse solvers. Every candidate gated. target_met only if the Wilson lower bound clears your target.",
    },
    {
      id: "wilson",
      title: "Why Wilson, not Wald",
      say: "Textbook Wald intervals collapse at perfect or zero passes. Wilson stays honest at the edges. Fifteen perfect trials → lower bound about 0.80. That's why our attempt counts are 15 / 25 / 40 for 0.7 / 0.8 / 0.9 — not arbitrary.",
    },
    {
      id: "cost",
      title: "Cost of evidence",
      say: "Setup is almost free — two calls, three if canary regenerates. The rest is sampling. You're paying for evidence, and you choose how much.",
    },
    {
      id: "moment",
      title: "The product moment",
      say: "Easy task: you didn't gain a better answer — you gained knowing. Hard task: the pool fails, and we refuse. Everyone else will show something working. We can show a product declining to lie.",
    },
    {
      id: "claims",
      title: "Claims / non-claims",
      say: "We're infrastructure around Claude — Apache 2.0, embeddable. Judges: ask us anything about the receipt. Demo next.",
    },
  ];

/** Demo reel beats in seconds [start, end). Total ~85s. */
export const REEL_BEATS = [
  { id: "title", start: 0, end: 5 },
  { id: "problem", start: 5, end: 16 },
  { id: "hope", start: 16, end: 23 },
  { id: "how", start: 23, end: 42 },
  { id: "wilson", start: 42, end: 52 },
  { id: "green", start: 52, end: 62 },
  { id: "red", start: 62, end: 74 },
  { id: "end", start: 74, end: 85 },
] as const;

/** PRD problem statement — compounding reliability (not a third-party study). */
export const PROBLEM = {
  steps: 20,
  perStep: 0.95,
  endToEnd: 0.358,
  caption: "20 steps × 95% each → ≈36% end-to-end",
  source: "Nines PRD problem statement (compounding reliability)",
} as const;

export const CODE_SNIPPET = `receipt = run(task, target=0.8, budget=Budget(...))
# target_met  → ship
# else        → human`;

export const PIPELINE_NODES = [
  { label: "task", note: "" },
  { label: "synthesize", note: "independent" },
  { label: "canary", note: "known-bad" },
  { label: "fan-out", note: "model×effort×framing" },
  { label: "gate", note: "" },
  { label: "Wilson", note: "lower bound ≥ target" },
  { label: "receipt", note: "" },
] as const;
