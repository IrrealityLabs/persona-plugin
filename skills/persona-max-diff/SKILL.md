---
name: persona-max-diff
description: Run MaxDiff (Maximum Difference Scaling, aka best-worst scaling) with the personas — show each persona small sets of items and ask them to pick the most and least important from each set. Produces a robust ranked list of importance across the full item set. Use when the user says "/persona-max-diff", "MaxDiff this list", "rank these by importance", "prioritize this list", or has 6+ items to prioritize on a single dimension.
---

# Persona MaxDiff

MaxDiff is a forced-choice ranking method: instead of asking "rate each item 1–7" (which produces lazy clustering at 5/6 across the list), it asks "in this set of 4, which matters most and which matters least?" Repeated across many overlapping sets, the math produces a clean ranked list with meaningful spread.

Robust at small panel sizes — works better than rating scales when you have 5–10 personas, because the forced-choice format yields more signal per response.

## When to use vs. alternatives

- Use `persona-max-diff` when ranking 6–25 items by importance / preference / appeal on a single dimension.
- Use `persona-turf` when picking a *subset* for coverage (not ranking the whole list).
- Use `persona-ab-test` for 2–4 items only.
- Use `persona-conjoint` when items vary on multiple attributes you want to weigh separately.

## Sample size

- **Sweet spot:** 5+ personas. MaxDiff is one of the *most* sample-efficient quant methods, so it works well at panel scale.
- Below 4: still usable but report rankings as directional.

## Inputs

- **Items** — 6–25 distinct items (features, messages, benefits, values, pain points). Each labeled with a short name and a 1-sentence description.
- **Dimension** — what to rank on. "Most important to me" / "Most appealing" / "Most likely to influence my decision." Be specific.

## Workflow

### Phase 1 — Validate the list

- 6+ items (below 6, MaxDiff is overkill — use `persona-ab-test` or rate-each).
- ≤25 items (above 25, set design becomes painful — split into themed sub-lists or pre-filter via a coarser pass).
- Each item distinct from the others. Pre-clean near-duplicates.

### Phase 2 — Generate sets

Generate balanced sets of 4 items per question. Each item should appear in roughly the same number of sets across the questionnaire (the *balance* makes the math work — items seen more often will look more important).

Rule of thumb: total sets = (items × 3) / 4. So 12 items → 9 sets of 4, each item appears 3 times.

For a quick implementation, generate sets randomly with a uniform-coverage constraint: shuffle the list, take 4, shuffle, take 4, repeat until each item has been seen ≥3 times. Good enough for panel scale; rigorous balanced designs (BIBD) are overkill.

### Phase 3 — Sample personas

All personas if ≤12; else `persona-sample` for 8 with the dimension as topic filter.

### Phase 4 — Per-persona choice fan-out

Spawn one subagent per persona, parallel. Each prompt:
- Persona doc path.
- The sets (randomized order per persona).
- For each set: "From this set of 4, pick the one that is MOST <dimension> for you, and the one that is LEAST <dimension>. Briefly say why your most-pick won and your least-pick lost."
- `persona-ask` reviewer contract.
- MaxDiff response format below.

MaxDiff response format:
```
## Set 1: [<item>, <item>, <item>, <item>]
- **Most:** <item> — short reason
- **Least:** <item> — short reason
- **Confidence:** [high|medium|low]

## Set 2: ...
...

## Reflection
Across all sets, the 1–2 themes that drove my picks. Sanity check on the ranking.
```

### Phase 5 — Compute scores

For each item, the simple best-worst score:
- `score(item) = (# times picked most) − (# times picked least)`
- Normalize to [0, 1]: `(score + max_sets) / (2 × max_sets)`

Per-persona scores aggregate to panel scores by averaging.

If you have Python or R handy, more sophisticated estimators exist (Hierarchical Bayes for individual-level utilities), but for panel scale the simple BW score is fine.

### Phase 6 — Synthesize

```
# MaxDiff: <dimension>

## Ranked list (panel average, normalized 0–1)
1. <Item>: 0.92
2. <Item>: 0.85
3. <Item>: 0.73
...
[show as monospace bar chart]

## Top tier (clear winners)
The items with scores ≥0.75 and >0.15 gap from the next tier. These are the "clearly more important" items.

## Bottom tier (clear losers)
Items with scores ≤0.25. These are the "drop these" candidates.

## Middle tier (the noisy middle)
Items packed in the middle of the distribution. Personas didn't strongly differentiate these — don't read too much into rank-order within this tier.

## Where personas disagreed
Items with high variance across personas. Often reveals real audience splits — surface them, name which personas leaned which way.

## Cross-reference to reasons
For the top 3 and bottom 3 items, the dominant *why* (aggregated from personas' short reasons) — this turns the ranking into actionable insight, not just a numbered list.

## Sample-size caveat
"N=<N> personas; MaxDiff is sample-efficient but rankings within the middle tier should still be treated as directional."
```

## Notes

- MaxDiff produces the cleanest ranked list of any quant method at small sample sizes. If you have personas and need a ranked list, this is almost always the right method.
- The math relies on each item being seen multiple times. Don't shortcut the set generation — running 4 sets of 4 across 16 items will produce noise.
- A *flat* distribution (all items scoring around 0.5) means either the items are genuinely close in importance for this panel, or the personas don't engage strongly with the dimension. Look at the per-persona reflections to tell which.
- Use MaxDiff *upstream* of TURF and conjoint when you have lots of options — get a ranking first, then run the more expensive methods on the top half.
