---
name: persona-memetic-engineering
description: Engineer and test "memes" — creative / message / positioning units — against your personas as a fast, cheap synthetic RCT. Built on the Concept → Theme → Variant framework: it concentrates rigor at the Concept level (the one-way-door decisions), uses an orthogonal (pairwise) array to test many concepts and elements in few cells, scores them against the panel on a brand-performance metric (recall, sentiment, purchase intent, click-intent), reads which concepts and elements drive resonance via main-effects analysis, and composes a predicted winner to validate. Use when the user says "/persona-memetic-engineering", "memetic engineering", "creative testing with the personas", "map the message space", "which concept/angle resonates", "test these concepts/hooks", or wants structured combinatorial creative testing. Not in the README; an advanced skill. Based on Marketing Memetics (Concept-Theme-Variant, Creative Testing).
---

# Persona Memetic Engineering

A meme is a replicable idea-unit built to resonate and spread; a winning ad is the right *combination* of memes. This skill **engineers and tests those combinations against your personas as a synthetic randomized controlled trial** — cheap and fast enough to clear the whole backlog of ideas, so you reserve real ad spend (and real RCTs) for the survivors.

It exists because real creative testing has a structural problem: RCTs are the gold standard but they're **expensive, slow, and impractical at the rate ideas pile up** — "your backlog of ideas always fills up faster than you can test them" — so the process gets hijacked by the highest-paid person's opinion. A persona panel is the cheap synthetic RCT that breaks that bottleneck: test the basket of big ideas *first*, kill the dead ends, and only spend real budget proving the few that survive.

Structured and combinatorial — the opposite shape from `persona-thermonuclear` (open-ended idea exploration). **Not** in the README, **not** a default `persona-research` method.

## The map: Concept → Theme → Variant (and where to spend rigor)

The three altitudes are not equal — they map to Bezos's one-way vs. two-way doors, which tells you *where testing is worth it*:

- **Concept** — the *angle*: the big idea / value-prop / psychological hook (Travel: beach vs. city breaks; FinTech: payment alerts vs. split-the-bill; Gaming: ogres vs. dragons). These are **one-way doors** — consequential and hard to reverse; a wrong concept is an evolutionary dead end and can build your brand on quicksand. **This is where the panel earns its keep.** Generate a *basket* of big concepts and test them like an RCT.
- **Theme** — how a winning concept is *executed* (a Florida vs. a Spanish beach; pizza vs. coffee; realistic vs. cartoonish ogres). These are **two-way doors** — easily reversed, so they "can and should be made quickly by high-judgment individuals." Test lightly, within a proven concept.
- **Variant** — element-level tweaks (border colors, button text, ad formats). 1–2% differences that won't reach significance individually. **Don't test these against the panel** — in real deployment you "abandon science and let the algorithm decide."

So the discipline is *altitude*: **RCT the Concepts, judgment-call the Themes, leave the Variants to the algorithm.** Most of this skill's value is at the Concept level.

## The efficient test: orthogonal arrays

Even at the Concept/Theme level the space is combinatorial (concept × hook × format × …) and the classic "change one variable at a time" A/B approach can't keep up with the backlog. An **orthogonal (pairwise) array** tests many factors in a balanced subset where every pair of levels co-occurs — a fraction of full factorial. Because a creative test *has a numeric response* (how the panel scores each meme), you then run a **main-effects analysis**: average each level's score across the array, pick the winning level per factor, and **compose the best-of-each into a predicted winner**.

Honor the scientific-advertising rigor underneath it: a clean balanced design, honesty about significance (persona panels are small-N — results are *directional*), and a written test plan so wins aren't accidentally forgotten or misses repeated. And validate additivity — orthogonal arrays assume interactions are weak, so always test the composed winner head-to-head against the best real cell and flag any meme that beat or trailed its prediction.

## When to use vs. alternatives

- Use `persona-memetic-engineering` to **map and test a creative/message space** and find the winning concept + elements as a synthetic RCT.
- Use `persona-ab-test` / `persona-survey` / `persona-max-diff` for a *single* head-to-head, rating, or ranking — this skill orchestrates those as its scoring engine across a designed matrix.
- Use `persona-brand-tracking` for the *outcome metrics* (aided/unaided recall, sentiment, purchase intent) — use the same metrics here as the response you score.
- Use `persona-brainstorm` to generate raw ideas with no test structure; `persona-thermonuclear` for open-ended idea exploration.

## The discipline (baked in)

- **Concentrate rigor at the one-way doors.** Spend the panel on Concepts; don't burn it proving 1–2% variants.
- **Diverge on concepts with Verbalized Sampling.** Generate a probability-weighted spread and keep the low-probability tail — five versions of the obvious concept is a wasted RCT. The array then guarantees the weird concepts get balanced coverage.
- **Let the array buy throughput, not corner-cutting.** Its job is to clear more of the backlog per run — spend the savings on *more concepts*, not fewer personas.
- **Score a real brand-performance outcome**, not "do you like it" — recall, sentiment, purchase-intent, or click-intent (behavior beats opinion).
- **Be honest it's a synthetic RCT.** Directional, not gold-standard. Its purpose is to *triage the backlog* so real testing budget goes to the survivors — not to replace the real test.
- **Settle debates with it.** Its highest use is de-HiPPO-ing a concept argument cheaply before anyone spends.
- **Ground, think, talk.** Every persona reaction follows the `persona-ask` contract so the read is auditable.

## Panel selection

Named personas → those. Otherwise all of them — the personas *are* the test audience, and segment splits are a finding (a concept that wins one segment and bombs another is exactly what you want). Read main effects by persona, not just pooled.

## Cost and the risk dial

The orthogonal array is the cost control — a pairwise matrix is a fraction of full factorial. Cost ≈ (personas) × (array cells) × (funnel rounds). Set the **risk/reward dial** the way a real program sets test budget — a small basket of concepts for a safe read, a big one when you need a step-change win. Use `persona-research/references/cost-estimator.md`, show the estimate, confirm.

## Workflow

### Phase 0 — Brief, altitude, objective

Pin down the offer, the audience (which personas), the **altitude** (default **Concept** — that's where the value is), the **objective** (the brand-performance metric you'll score — recall / sentiment / purchase-intent / click-intent), and the **risk dial** (how big a basket of concepts to test).

### Phase 1 — Generate the basket (diverge)

At the Concept level, generate a basket of distinct big ideas with Verbalized Sampling (probability-weighted spread; keep the unusual ones). Show the basket and confirm before building the test.

### Phase 2 — Design the orthogonal test matrix

List the factors and levels (e.g. concept × hook × format). Lay out a **pairwise covering array** — the minimal balanced set of cells where every pair of levels co-occurs. Each cell is one concrete **meme**; use Verbalized Sampling to write the actual copy/concept so the units are real. State the array size vs. what full factorial would have cost.

### Phase 3 — Run the synthetic RCT

Present the array of memes to the panel and have each persona score the Phase-0 objective — rate-each (`persona-survey` Likert), forced-choice (`persona-ab-test`), or best-worst (`persona-max-diff`). Ground → Think → Talk; collect a score per (persona, meme).

### Phase 4 — Main-effects analysis

For each factor level, average its score across the cells it appears in → its main effect; the highest-scoring level per factor wins. **Compose the best-of-each into a predicted winner.** Flag **interactions** (cells well above/below their main-effects prediction — non-additive combos needing a direct test) and read **by segment**.

### Phase 5 — Validate, then funnel and recycle

- **Validate additivity:** test the composed winner head-to-head against the strongest real cell (`persona-ab-test`). If it loses, an interaction is carrying the result — trust the real cell.
- **Act:** recommend the winning concept(s) to roll into real campaigns; **drill the winner down one altitude** into a Theme-level array; leave Variants to the algorithm in real deployment.
- **Recycle:** when a winning concept eventually fatigues in market, come back to the top with a fresh basket.

### Synthesis output

```
# Memetic engineering: <offer / message space>

## The basket and the map
The concepts (and themes) tested, and which branch won — at the Concept altitude where it counts.

## Winning memes (main effects)
Per factor, the level that scored highest with its margin — and the composed best-of-each meme.

## Interactions to watch
Cells that beat or trailed their main-effects prediction — non-additive combos worth a direct test.

## By segment
Where concepts/elements split across personas — who to target with what.

## The composed winner (and its validation)
The predicted-best meme, whether it beat the top real cell head-to-head, and the version to run.

## What to spend a real RCT on
The 1–2 survivors worth proving with real audiences before budget — the whole point of triaging here.
```

Close with the standard simulation disclaimer.

## Notes & anti-patterns

- **Don't RCT the variants.** Element-level 1–2% tweaks are two-way doors / algorithm territory; spending the panel there is the most common waste.
- **Don't optimize a losing concept.** Win the one-way door first; descend only into winners.
- **Don't read a pairwise array as if it tested every combination.** It covers pairs, not triples — the composed winner is a *validated prediction*, not a measured result.
- **Don't pool away the segments.** A meme that wins on average but bombs with your core persona is often worse than one that wins decisively with the people who matter.
- **It triages; it doesn't prove.** This finds which engineered meme *your personas* prefer, cheaply and fast — a synthetic RCT to clear the backlog, not a substitute for the real RCT on the survivors.
