# Nines pitch — Remotion

Code-driven **PitchDeck** (8 slides) + **DemoReel** (~85s silent B-roll) from [`../SCRIPTS.md`](../SCRIPTS.md).

## Setup

```bash
cd docs/pitch/remotion
npm install
npm run studio
```

In Studio, pick composition **PitchDeck** or **DemoReel**.

### Live pitch (deck)

1. Open **PitchDeck**
2. Fullscreen the preview
3. Advance with the timeline / J-K or scrub — each slide is ~4s; pause on a slide while you speak the **SAY ·** line at the bottom
4. Live product demo stays separate: `python examples/demo_arc.py --models opus,sonnet`

### Render the reel (VO later)

```bash
npm run render:reel
# → out/nines-reel.mp4  (1920×1080, 30fps, silent)
```

Optional: `npm run render:deck` exports the timed slide run as MP4.

## Design tokens

- Background `#0E1116`, paper `#F4F1EA`, accent amber `#F5A524`
- Display: Bricolage Grotesque · Mono: IBM Plex Mono (via `@remotion/google-fonts`)
- Numbers live in `src/data/copy.ts` (edit there, not in components)
- Brand URL: `github.com/kkrishguptaa/nines` only — **no** `nines.run` domain branding

## Claims

Do not invent metrics. Source: repo README + `docs/claims.md` + SCRIPTS.md.
