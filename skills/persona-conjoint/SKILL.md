---
name: persona-conjoint
description: Run conjoint analysis with the personas — estimate the relative importance of product attributes (price, features, support level, brand, etc.) by having personas choose between bundled profiles. Outputs part-worth utilities per attribute level and importance rankings. Use when the user says "/persona-conjoint", "do a conjoint", "what trade-offs matter most", "how should I price this against features", or has a multi-attribute decision.
---

# Persona Conjoint

Conjoint analysis estimates how much each *level* of each *attribute* contributes to a persona's choice — by forcing them to choose between bundles, you can back out the implicit weights they apply. Classic uses: pricing tier design, feature bundling, plan comparison.

This is *the* quant-heavy method in the catalog — it works at scale with hundreds of respondents. With a persona panel you get directional estimates, not statistically robust utilities.

## When to use vs. alternatives

- Use `persona-conjoint` when the question is about *trade-offs between attributes* (e.g. "is more storage worth $5/mo more?").
- Use `persona-ab-test` when comparing finished variants holistically.
- Use `persona-van-westendorp` when the question is only about price.
- Use `persona-max-diff` when ranking items on a single dimension.
- Use `persona-turf` when picking a subset for portfolio coverage.

## Sample size

- **Sweet spot:** 30+ for real conjoint; the panel will rarely have this.
- **Persona-panel reality:** 5–15 personas produces *directional* utilities. Surface this loudly in the output.
- Below 5: skip conjoint, run `persona-ab-test` on the 2–3 most plausible bundles instead.

## Inputs

- **Attributes and levels** — typically 3–5 attributes, each with 2–4 levels.
  Example: Price (\$10, \$25, \$50), Plan (Basic, Pro, Enterprise), Support (email-only, chat, dedicated), Annual discount (none, 10%, 20%).
- **Profile count** — how many bundles to test per persona. Default 8–12. Above 15 = fatigue.
- **Comparison format** — pairs (Choose A or B) or full-profile rating. Pairs are easier for personas to reason about; default to pairs.

## Workflow

### Phase 0 — Cost warning

Conjoint × pairwise gets expensive. 8 personas × 12 pairs = 96 subagent runs. **Always warn** and confirm before launching. Use the cost estimator. Reduce profile count if cost is prohibitive.

### Phase 1 — Validate the design

- Attributes should be *independent* — don't include both "monthly cost" and "annual cost" as separate attributes, they're the same axis.
- Levels within an attribute should be *meaningfully different* — a Price attribute with levels $10 / $11 / $12 won't produce signal.
- Generate the profile set. Two options:
  - **Full factorial** (every combination): only feasible with very small attribute counts (e.g. 3 attrs × 2 levels = 8 profiles). Most cases need:
  - **Fractional factorial** (a balanced subset that estimates main effects): use a standard orthogonal design. With 4 attributes × 3 levels = 81 full combinations; an orthogonal subset of 9 captures main effects.
- For pairwise: generate ~12 random pairs from the profile set (or use a balanced incomplete-block design if you want to be rigorous).

If you don't know how to generate a balanced design and the user wants rigor, say so — recommend they use a real conjoint tool for the design step, then run choice through the personas.

### Phase 2 — Sample

Default to all personas; if the user named some, use those. If the roster is much larger than ~8, ask the user which to include rather than auto-selecting (when suggesting, lean toward personas relevant to the product domain — read their `## At a glance` lines).

### Phase 3 — Per-persona choice fan-out

Spawn one subagent per persona, parallel. Each prompt:
- Persona doc path.
- All comparison pairs (or full profiles), in randomized order per persona.
- For each pair: present both profiles side-by-side as attribute-level tables.
- Choice instruction: "For each pair, pick A or B (or 'neither' if both are unacceptable). Briefly note which attribute drove the choice."
- `persona-ask` Ground, think, then talk (Grounding → Thinking → Talking) contract.
- Conjoint response format below.

Conjoint response format:
```
## Grounding (private — orchestrator only; not tallied)
The persona-doc sections that bear on these choices, cited first: `§ <Section>: "<…>"` + a per-pair confidence read [high|medium|low|off-pattern].

## Thinking (private — orchestrator only)
Private reasoning over that grounding: what this persona would genuinely conclude, where the evidence is thin.

## Pair 1: <profile A summary> vs <profile B summary>
**Pick:** A | B | neither
**Driver:** which attribute drove the choice; one sentence

## Pair 2: ...
...

## Reflection
Across all pairs, which attribute mattered most to me overall and why. (This is a sanity check on the part-worth math.)
```

### Phase 4 — Compute utilities

(Per-persona **Grounding** and **Thinking** are audit fields — orchestrator-only and **not** tallied; only the public Pick per pair feeds the part-worth math.)

For each attribute level, estimate the part-worth utility: how much choosing the level affected the probability of choosing the profile.

Simple approach (good enough for panel scale):
- For each persona, count how many times each level was in the *chosen* profile vs. the *rejected* profile across all pairs.
- Part-worth ≈ (chosen count − rejected count) / total pairs that included this level.
- Importance of an attribute ≈ range of part-worths across its levels.
- Normalize importances to sum to 100% across attributes.

If you can shell out to a real conjoint package (e.g. R's `conjoint` or Python's `pyconjoint`), prefer that for the math — it'll handle the math more rigorously than the rule-of-thumb above.

Aggregate across personas: report the panel-average part-worths and importance %, plus the variance (where personas disagreed strongly is itself a finding).

### Phase 5 — Synthesize

```
# Conjoint analysis: <product>

## Attribute importance (% of choice influence)
- Price: X%
- Plan: Y%
- Support: Z%
[bar chart in monospace]

## Part-worth utilities by level (panel average)
- Price = $10: +X
- Price = $25: +Y
- Price = $50: −Z
[per attribute]

## What this means in plain language
2–3 sentences turning the utilities into a recommendation: "Price is the dominant driver (45%) and a $25 tier outperforms both $10 and $50. The panel doesn't differentiate strongly between support levels — this is not the lever to pull."

## Where personas disagreed
Attributes or levels where the variance was high — surface the split, which often maps to segmentation (e.g. "consumer personas were price-elastic; B2B personas valued dedicated support 3x more").

## Recommended bundle(s)
The 1–3 highest-utility profiles based on the math, with reach % per `persona-turf`-style logic if multiple bundles emerge.

## Sample-size caveat
"N=<N> personas; conjoint methodology assumes 30+ respondents for stable utilities. Treat these as <directional|preliminary> — confirm with a quant study on real customers before betting on the bundle."
```

### Phase 6 — Render the report

Write `report.html` to `./.persona-research-runs/conjoint-<YYYY-MM-DD>-<slug>/` per the
shared spec in `skills/persona-research/references/html-report.md` — self-contained
(inline CSS/JS, data embedded, opens with a double-click): the question, method + N
caveat, the attribute importances and part-worth utilities, one card per persona with
their verbatim public answers + confidence and collapsible grounding, and the insights.
Tell the user the path.

## Notes

- Personas will weight price more honestly than real respondents in conjoint — they have no purchase pain. Discount panel price-sensitivity findings slightly.
- "Neither" choices are signal — if a persona rejects many pairs, your attribute levels probably don't cover their needs. Surface this rather than dropping the "neither" choices.
- If the panel-average importances are all near-equal (e.g. each attribute around 25%), that means either the attributes are well-balanced for these personas (rare and useful) or the panel is too small to differentiate (common). Note both possibilities.
