---
name: persona-van-westendorp
description: Run a Van Westendorp Price Sensitivity Meter with the personas — each persona answers four price questions (too cheap, cheap, expensive, too expensive) for a product or service. Outputs the four price curves, the optimal price point, and the range of acceptable prices. Use when the user says "/persona-van-westendorp", "price this", "find the right price", "what should I charge", or has a pricing decision and wants directional guidance.
---

# Persona Van Westendorp

The PSM (Price Sensitivity Meter) asks four price-perception questions per respondent, then plots the cumulative curves to find:
- **OPP** (Optimal Price Point) — where "too cheap" and "too expensive" curves cross
- **IPP** (Indifference Price Point) — where "cheap" and "expensive" curves cross
- **PME** (Point of Marginal Expensiveness) — where "expensive" and "too expensive" cross
- **PMC** (Point of Marginal Cheapness) — where "cheap" and "too cheap" cross
- **Range of acceptable prices** — between PMC and PME

A real PSM needs ~50+ respondents for clean curves. With a persona panel of 5–10, the curves are jagged but the *range* and *OPP* are usually directionally right.

## When to use vs. alternatives

- Use `persona-van-westendorp` when the question is "what should I charge?" with no specific candidates.
- Use `persona-conjoint` when price trades off against other attributes (price-feature bundles).
- Use `persona-ab-test` when comparing specific price points (e.g. $19 vs $29 vs $49).
- Use `persona-concept-test` when willingness-to-pay is one signal among many for a new concept.

## Sample size

- **Sweet spot:** 30+. Won't have it.
- **Persona-panel reality:** 5–10 personas produces *directional* OPP and *rough* range. Surface this loudly.
- Below 5: don't run; use `persona-ab-test` on 3 candidate prices instead.

## Inputs

- **The product/service** — clearly described in 2–4 sentences. The personas need to know what they're pricing.
- **Currency** (default USD) and **billing model** (one-time, monthly, annual, per-seat, etc.).
- **Optional anchors** — comparable products/services and their prices. Often useful — without anchors, personas may name implausible prices.

## Workflow

### Phase 1 — Validate the brief

The product description must be specific enough to price. "An AI tool" is too vague. "A Slack-installed AI assistant that summarizes channels for $X/user/month" is priceable.

Surface this if the brief is vague. Don't let personas guess at what they're pricing.

### Phase 2 — Sample

Default to all personas; if the user named some, use those. If the roster is much larger than ~8, ask the user which to include rather than auto-selecting — and when suggesting, lean toward personas who'd plausibly buy this (read their `## At a glance` lines), since pricing reactions from personas outside the target segment add noise, not signal.

### Phase 3 — Per-persona fan-out

Spawn one subagent per persona, parallel. Each prompt:
- Persona doc path.
- The product description, billing model, anchors.
- The four PSM questions, asked in this canonical order:
  1. **Too expensive:** "At what price would this product be SO expensive that you would not consider buying it?"
  2. **Expensive:** "At what price would this product be expensive, but you'd still consider buying it because you see value?"
  3. **Cheap:** "At what price would this product be a bargain — a great deal for the money?"
  4. **Too cheap:** "At what price would this product be so cheap that you'd doubt its quality and not buy it?"
- `persona-ask` Ground, think, then talk (Grounding → Thinking → Talking) contract — and add: "Quote the part of your persona doc that grounds your price intuition — what comparable spend, budget anchor, or value calculus is doing the work."
- Van Westendorp response format below.

Response format:
```
## Grounding (private — orchestrator only; not tallied)
The persona-doc sections that bear on these prices, cited first: `§ <Section>: "<…>"` (comparable spend, budget anchor, value calculus) + a per-question confidence read [high|medium|low|off-pattern].

## Thinking (private — orchestrator only)
Private reasoning over that grounding: what this persona would genuinely conclude, where the evidence is thin.

## Too expensive
**Price:** $X / <unit>
**Why:** "First-person reasoning, tied to budget/anchor/value reference."

## Expensive
**Price:** $X / <unit>
**Why:** ...

## Cheap (bargain)
**Price:** $X / <unit>
**Why:** ...

## Too cheap (quality doubt)
**Price:** $X / <unit>
**Why:** ...

## Sanity-check
For my four numbers: is too-cheap < cheap < expensive < too-expensive? If not, which inversions and why.
```

### Phase 4 — Validate per-persona answers

Discard responses where the four numbers don't satisfy `too-cheap < cheap < expensive < too-expensive`. Flag the inversion as a finding — usually means the persona doesn't have a coherent price model for this product (a real signal: maybe the product is too unfamiliar to price). Don't silently drop; report counts.

### Phase 5 — Compute curves and key points

(Per-persona **Grounding** and **Thinking** are audit fields — orchestrator-only and **not** tallied; only the four public prices feed the curves.)

For each of the four questions, build a cumulative distribution function:
- For too-expensive and expensive: cumulative % who would consider the product at or below this price.
- For too-cheap and cheap: cumulative % who would consider the product at or above this price.

Plot all four on the same axis (price on x, cumulative % on y).

Find the intersections:
- **PMC** = too-cheap × cheap
- **OPP** = too-cheap × too-expensive (the "optimal price point")
- **IPP** = cheap × expensive (the "indifference price point")
- **PME** = expensive × too-expensive

**Acceptable range** = PMC to PME.

For small samples, the curves are step functions, not smooth — find the nearest intersection or the midpoint of the bracket.

### Phase 6 — Synthesize

```
# Van Westendorp PSM: <product>

## Price points (panel of N)
- **OPP (Optimal Price Point):** $X — where too-cheap and too-expensive curves cross
- **IPP (Indifference Price Point):** $X — where cheap and expensive cross
- **Acceptable range:** $X (PMC) to $X (PME)

## Plain language
"The panel suggests a price of around $X, with reasonable acceptance between $X and $X. Below $X, personas would doubt quality; above $X, they'd reject as too expensive."

## Curves
[Show all four curves as monospace ASCII charts or, if too jagged with small N, just the four medians per question]

## Where personas anchored
The 2–4 most-cited reference points across the panel (comparable products, current budgets, prior spend). This is often the *most* actionable output — pricing perception is mostly about anchors.

## Inversions (if any)
Personas whose four prices were not monotonic — typically means they don't have a coherent model for this product. List them.

## Persona splits
Where the price ranges split sharply by persona segment (e.g. consumer vs. enterprise often differs by 10x).

## Sample-size caveat
"N=<N> personas; Van Westendorp methodology was designed for 50+ respondents. The OPP and range here are *directional* — best for narrowing a 10x price spread to a 2x spread, not for finalizing a price point. Validate with real customers (a few real prospects with budget context will sharpen this fast)."
```

### Phase 7 — Render the report

Write `report.html` to `./.persona-research-runs/van-westendorp-<YYYY-MM-DD>-<slug>/`
per the shared spec in `skills/persona-research/references/html-report.md` —
self-contained (inline CSS/JS, data embedded, opens with a double-click): the question,
method + N caveat, the four price curves and the acceptable range, one card per persona
with their verbatim public answers + confidence and collapsible grounding, and the
insights. Tell the user the path.

## Notes

- Personas anchored on something concrete (their current spend on a comparable) will produce useful answers. Personas with no anchor will produce noise. Always surface the anchors.
- A *huge* gap between PMC and PME (e.g. PMC=$10, PME=$500) means the panel doesn't share a mental model for what this product is worth. The product positioning is the problem, not the price.
- Don't use the OPP as the price. Use it as the *center* of a tighter A/B test (`persona-ab-test` on 3 prices near the OPP).
