---
name: persona-ab-test
description: A/B (or A/B/C/D) test variants of an asset with the personas — each persona sees all variants, picks the one that would convert them, and explains why. Outputs per-variant vote tally, dominant rationales, and per-persona-segment splits. Use when the user says "/persona-ab-test", "A/B test these", "which of these wins", "have the personas pick", or has 2–4 versions of something and needs a panel verdict.
---

# Persona A/B Test

Compare 2–4 variants of an asset (headlines, hero images, pricing pages, CTAs, ads) against each other across the persona panel. Each persona sees all variants, picks one, and explains why.

## When to use vs. alternatives

- Use `persona-ab-test` when you have *finished* variants and want the panel to pick.
- Use `persona-review` to critique one asset for improvement (not pick between alternatives).
- Use `persona-goal` to *iteratively optimize* one asset in a loop (review → edit → re-score until it stops improving), rather than pick between fixed variants.
- Use `persona-max-diff` for prioritizing a *long list* (≥5 items) — A/B testing 8 things produces noisy results.
- Use `persona-concept-test` when the variants aren't built yet — test the *concept* before producing the asset.

## Sample size

- **All personas** by default — A/B testing benefits from breadth, not topical filtering.
- Works with as few as 3 personas; below 3 the vote tally isn't meaningful.

## Inputs

- **Variants** — 2–4 versions of the asset. Above 4, switch to MaxDiff. Each variant labeled (A, B, C, D).
- **The decision question** — "Which would make you click?" / "Which feels more trustworthy?" / "Which would you actually pay for?" Be specific — the question shapes what the panel evaluates.
- **Optional context** — what's running where (e.g. "this is the landing-page hero").

## Workflow

### Phase 1 — Validate the variants

Sanity-check before launching:
- Each variant should be *meaningfully different*. Two variants that differ in one comma will produce indistinguishable results. If the variants are near-identical, push back: "Variants A and B differ only in punctuation — the panel can't usefully distinguish these. Want to retest with sharper alternatives?"
- Variants should all be valid attempts at the same goal. Don't mix "the headline we like" with "a strawman bad headline" — the panel reads through that.
- Strip away any obvious A/B labeling within the variants themselves so personas don't anchor on the label.

### Phase 2 — Frame the question

Apply the `persona-ask` framing checklist. Default question:

> "Read all <N> variants in order. Then tell me: (a) which one you would pick if you encountered it in the wild and why, (b) which one would actually trigger the action [click / sign up / buy / share], (c) which one feels worst and why. Quote the specific phrases / elements that pushed your choice. If you'd reject *all* of them, say so — that's a valid answer."

If the user gave a narrower question, use it as the core but keep (b) — behavior over preference is what matters.

### Phase 3 — Fan out

Spawn one subagent per persona, all in parallel. Each prompt:
- Persona doc path.
- All variants, labeled, in randomized order per persona (to control for order effects — track which persona saw which order in case you re-run).
- The decision question.
- `persona-ask` reviewer contract.
- A/B test response format below.

A/B test response format:
```
## Pick
Variant <letter> | None of these (and why)

## Reasoning
"First-person quote — why this variant won for me."
**References (persona doc):**
  - § <Section>: "<...>"
**Confidence:** [high|medium|low] + reason.

## Specifically what worked
The phrase / element that pushed the choice — quoted from the variant.

## What killed the losers
For each non-picked variant: one sentence — what specifically lost it for me.

## What would beat them all
If none of these are great, a one-sentence sketch of a variant that would actually convert me. Skip if the winner is genuinely strong.
```

### Phase 4 — Aggregate

```
# A/B test: <decision question>

## Vote tally
- Variant A: N votes (X%)
- Variant B: N votes (X%)
- Variant C: N votes (X%)
- None: N votes (X%)

Show as a bar chart in monospace.

## The winning variant's dominant rationale
Distilled from the personas who picked it — what specifically worked.

## The losing variants' kill-reasons
Per variant: what most personas flagged as the problem.

## Persona splits
Where the vote split along persona lines (e.g. "B2B personas overwhelmingly picked Variant A; consumer personas picked Variant C"). This is often more valuable than the tally — it surfaces audience segmentation questions.

## "None" votes
If any persona rejected all variants, summarize their case. This is signal — if personas you're targeting reject everything, you don't have a winner, you have a rewrite.

## Confidence-weighted view
If picks varied in confidence, recompute the tally weighting [high] picks fully and [low] picks at 0.5. Surface only if the weighted tally meaningfully differs from raw.

## Sample-size caveat
If <5 personas, note the limit on confidence in the result.
```

## Notes

- Order effects matter even in persona-land. Randomize variant order per persona (track for repeatability).
- If one variant wins decisively but is a `[low]`-confidence win across the panel, treat it as directional — the panel agrees but doesn't strongly know why.
- "None of these" votes are not failures — they're the most actionable signal in the report when they appear. Don't bury them.
- For more than 4 variants, escalate to `persona-max-diff` — the format degrades fast beyond 4 options.
