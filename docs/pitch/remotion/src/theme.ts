import { loadFont as loadDisplay } from "@remotion/google-fonts/BricolageGrotesque";
import { loadFont as loadMono } from "@remotion/google-fonts/IBMPlexMono";

const display = loadDisplay("normal", {
  weights: ["400", "500", "600", "700"],
  subsets: ["latin"],
});
const mono = loadMono("normal", {
  weights: ["400", "500", "600"],
  subsets: ["latin"],
});

export const colors = {
  bg: "#0E1116",
  paper: "#F4F1EA",
  muted: "#9AA3AF",
  accent: "#F5A524",
  green: "#3DDC97",
  red: "#FF6B6B",
  line: "#2A303A",
  card: "#161B22",
} as const;

export const fonts = {
  display: display.fontFamily,
  mono: mono.fontFamily,
} as const;

export const fps = 30;
export const width = 1920;
export const height = 1080;

/** Frames for DemoReel (~85s): problem numbers + how-it-works + receipts. */
export const reelDurationInFrames = 85 * fps;

/** Frames per pitch slide (~4s). */
export const slideDurationInFrames = 4 * fps;

/** Public repo URL — not a custom domain. */
export const REPO_URL = "github.com/kkrishguptaa/nines";
