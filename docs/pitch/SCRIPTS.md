# Nines — pitch deck script + Remotion video package

Audience: Push to Prod judges (Anthropic architects + AI ops).  
Tone: technical, honest, visual-first. Not CEO fluff.

**Built assets:** Remotion app at [`remotion/`](remotion/) — compositions `PitchDeck` + `DemoReel`. See [`remotion/README.md`](remotion/README.md).

**Assets in this folder**

| File piece | Use |
| --- | --- |
| §1 Pitch deck **script** | What you say + what each slide shows (~90s) |
| §2 Pitch deck **prompt** | Paste into Cursor to generate the deck (code / slides) |
| §3 Demo video **script** | Ad-lib VO over Remotion B-roll (~60–75s) |
| §4 Remotion **prompt** | Paste into Cursor to generate the motion background |
| §5 Wald vs Wilson | One visual you must be able to explain |

---

## 1. Pitch deck script (~90 seconds)

**Rule:** one idea per slide. Never put the live terminal on a slide — that is the demo.

### Slide 1 — Title (0:00–0:08)
**Visual:** Giant word **NINES**. Sub: *reliability compiler for Claude*. Tiny: Apache 2.0 · `github.com/kkrishguptaa/nines`.  
**Say:**  
> Agents are right most of the time. Shipping needs a number — and a system that refuses when it can’t prove it.

### Slide 2 — The gap (0:08–0:18)
**Visual:** Left: “ask Claude once → hope.” Right: blank where “declared reliability” should be.  
**Say:**  
> Today you pick a model and hope. Nothing lets you declare a reliability target and *spend compute until the math clears it* — or stop honestly.

### Slide 3 — One call (0:18–0:28)
**Visual:** Code card only:

```python
receipt = run(task, target=0.8, budget=Budget(...))
# target_met  → ship
# else        → human
```

**Say:**  
> One public seam. You name the bar and the budget. You get a receipt — green ship or red escalate. Never a silent best-guess when nothing passed.

### Slide 4 — Pipeline (0:28–0:42)
**Visual:** Horizontal flow (animate left→right):

`task → synthesize checker → canary → diverse fan-out → gate → Wilson → receipt`

Callouts under nodes: *independent* · *known-bad* · *model×effort×framing* · *lower bound ≥ target*.

**Say:**  
> Verifier first — from the task alone. Canary kills checkers that accept garbage. Then diverse solvers. Every candidate gated. `target_met` only if the **Wilson lower bound** clears your target.

### Slide 5 — Why Wilson, not Wald (0:42–0:55)
**Visual:** See §5 diagram. Caption: *Wald lies at 0/n and n/n — exactly where agent demos live.*  
**Say:**  
> Textbook Wald intervals collapse at perfect or zero passes. Wilson stays honest at the edges. Fifteen perfect trials → lower bound about **0.80**. That’s why our attempt counts are 15 / 25 / 40 for 0.7 / 0.8 / 0.9 — not arbitrary.

### Slide 6 — Cost of evidence (0:55–1:05)
**Visual:** Tiny table:

| Bar | Attempts (perfect) | ≈ LLM calls | ≈ $ |
| --- | ---: | ---: | ---: |
| 0.7 | 15 | 17 | 0.02 |
| 0.8 | 25 | 27 | 0.06 |
| 0.9 | 40 | 42 | 0.13 |

Footer: *machinery ≈ 2 calls; the rest is the evidence you bought.*

**Say:**  
> Setup is almost free — two calls, three if canary regenerates. The rest is sampling. You’re paying for evidence, and you choose how much.

### Slide 7 — The product moment (1:05–1:18)
**Visual:** Split screen. Left green: `is_palindrome` · `target_met: true`. Right red: `parse_money` · `target_met: false` · `opus 5/8 · sonnet 7/8 · haiku 1/9`.  
**Say:**  
> Easy task: you didn’t gain a better answer — you gained **knowing**. Hard task: the pool fails, and we **refuse**. Everyone else will show something working. We can show a product declining to lie.

### Slide 8 — Claims / non-claims (1:18–1:30)
**Visual:** Two columns.

**Claimed:** orchestration · independent verifier + canary · budgeted fan-out · Wilson-gated measurement.  
**Not claimed:** novel model · production SLA · multi-tenant isolation.  
**Caveat (one line):** we measure *checker-pass rate*, not ground truth — Stroebl-style; canary reduces that risk, doesn’t erase it.

**Say:**  
> We’re infrastructure around Claude — Apache 2.0, embeddable. Judges: ask us anything about the receipt. Demo next.

**Q&A lines (memorize):**
- *15/15?* Easy task + early stop. Gain is knowing. Hard task next.
- *39/40?* Knife-edge — that’s why Wilson, not vibes.
- *Imperfect verifier?* We raise Stroebl ourselves; canary is the honesty gate.

---

## 2. Prompt — generate the pitch deck (Cursor)

```text
Build a hackathon pitch deck for Nines (github.com/kkrishguptaa/nines) as code-driven slides.

Constraints:
- Audience: Anthropic / AI infra judges, NOT generic startup CEOs.
- 8 slides matching docs/pitch/SCRIPTS.md §1 exactly (titles + visual intent).
- Visual-first: big typography, one idea per slide, almost no bullet walls.
- Include an animated or static pipeline (slide 4) and a Wald-vs-Wilson diagram (slide 5) per §5.
- Slide 7 must contrast green receipt vs red refuse (parse_money per-model rates).
- Color: dark charcoal ground, off-white type, one sharp accent (amber or electric blue — pick one and stick). Avoid purple gradients, Inter, and “AI SaaS” clichés.
- Stack preference: Remotion or HTML/CSS printable deck, or reveal.js — pick one, keep it in-repo under docs/pitch/deck/.
- Speaker notes = the “Say:” lines from §1.
- Do not invent claims beyond docs/claims.md and README.md.
```

---

## 3. Demo video script — ad-lib VO (~85s)

**Format:** You talk over Remotion B-roll (no face required). Terminal demo can be a short cut-in at the end *or* live on stage instead — video should sell the *idea*, stage sells the *run*.

| Time | On screen (Remotion) | You say (loose — ad-lib around this) |
| --- | --- | --- |
| 0:00–0:05 | Wordmark **NINES** | “Your agent is right most of the time. That’s not a shipping bar.” |
| 0:05–0:16 | Compounding bars: 20 steps @ 95% → **≈36%** end-to-end | “Errors compound. Twenty steps at ninety-five percent each finish around thirty-six percent. High-stakes work stays manual.” |
| 0:16–0:23 | Single-shot path | “Ask once and you get an answer — not measured reliability.” |
| 0:23–0:42 | How Nines works: setup → canary → fan-out → gate → Wilson → receipt | “Nines compiles reliability. Independent checker. Canary. Diverse solvers. Gate every candidate. Escalate until Wilson clears the bar — or refuse.” |
| 0:42–0:52 | Wald collapses; Wilson keeps ~0.80 at 15/15 | “Wald lies at perfect streaks. Wilson keeps an honest lower bound.” |
| 0:52–1:02 | Green receipt | “Easy task: you gained knowing — a receipt it’s safe to ship.” |
| 1:02–1:14 | Red receipt + model chips | “Hard task: the pool splits. We refuse. No silent best-guess.” |
| 1:14–1:25 | End · GitHub | “Declare the bar. Buy the evidence. Or get an honest no.” |

**If you only remember four beats:** compound → how it works → clear → refuse.

---

## 4. Prompt — Remotion background / motion (Cursor)

```text
Create a Remotion composition for a ~70s Nines demo video B-roll (voiceover recorded separately).

Storyboard beats (match docs/pitch/SCRIPTS.md §3 timings):
1. 0–5s   Title: NINES / reliability compiler
2. 5–16s  Problem: compounding 20×95% → ≈36% (PRD math)
3. 16–23s Single-shot hope path
4. 23–42s How Nines works (setup + sample loop visualization)
5. 42–52s Wald vs Wilson
6. 52–62s Green Receipt
7. 62–74s Red Receipt
8. 74–85s End card with GitHub URL

Design:
- Dark charcoal (#0E1116), paper white type, single accent (amber #F5A524 OR blue #3B82F6 — one only).
- Motion: crisp snaps + short ease, not bouncy; 2–3 signature moves max (pipeline draw-on, interval whiskers, receipt flip).
- No stock purple AI gradients, no emoji, no Inter.
- Typography: distinctive grotesk or mono for code (e.g. IBM Plex Mono for receipts).
- Export: 1920×1080, 30fps, silent (VO added later).
- Keep composition props data-driven so numbers (15/15, 0.80, costs) are editable constants.

Place project under docs/pitch/remotion/ (or apps/nines-reel/ if you prefer app layout).
```

---

## 5. Wald vs Wilson — explain this once, clearly

**Wald (textbook):**
\[
\hat p \pm z\sqrt{\hat p(1-\hat p)/n}
\]
At \(\hat p = 1\) (or 0), the square root is **0** → interval width **0** → “100% certain” after any perfect streak. Agent demos live exactly here. Wald is lying.

**Wilson (what Nines uses):**
\[
\begin{aligned}
\text{center} &= \frac{\hat p + z^2/(2n)}{1 + z^2/n} \\
\text{half} &= \frac{z}{1+z^2/n}\sqrt{\frac{\hat p(1-\hat p)}{n} + \frac{z^2}{4n^2}}
\end{aligned}
\]
Even at 15/15, the lower bound is only ≈ **0.80** (z≈1.96).  
So: **15 → ~0.80**, **25 → ~0.87**, **40 → ~0.91**.  
That table *is* the product: attempt counts are the minimum \(n\) where a perfect run can clear 0.7 / 0.8 / 0.9.

**Visual for slide + Remotion:** two number lines under “15 passes / 15 trials”. Wald: a single point at 1.0. Wilson: a thick interval from ~0.80 to 1.0 with the *lower* end highlighted as the gate.

---

## Stage pairing (optional)

1. Play the 70s video **or** skip straight to live.  
2. Live: `python examples/demo_arc.py --models opus,sonnet` — clean win → refuse.  
3. If asked about 15/15, deliver the stage line in `docs/demo-commands.md`, then point at the red receipt.
