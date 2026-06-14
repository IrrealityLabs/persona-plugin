---
name: persona-turf
description: Run TURF analysis (Total Unduplicated Reach and Frequency) with the personas — given a list of candidate options (features, messages, channels, plan tiers), find the smallest subset that "reaches" the largest share of personas, where each persona is reached if at least one option in the subset appeals to them. Use when the user says "/persona-turf", "do a TURF analysis", "which 3 of these 10 features should I bundle", "what's the smallest set that pleases the most people", or has a portfolio question.
---

# Persona TURF

TURF answers a specific question: *given N candidate options, what's the smallest subset of K that covers the largest share of the panel*, where coverage means at least one option in the subset resonates with each persona. Classic uses: which 3 features to highlight in a pricing tier, which 4 ad concepts to actually produce, which 5 use-cases to put on a homepage.

## When to use vs. alternatives

- Use `persona-turf` when the goal is *portfolio coverage* — picking a set, not a single winner.
- Use `persona-ab-test` when picking *one* winner from competing variants.
- Use `persona-max-diff` when ranking items by importance for a single user — TURF optimizes *across* users.
- Use `persona-conjoint` when trade-offs between *attributes* matter, not selection of discrete options.

## Sample size

- **Sweet spot:** 8+ personas. TURF reach is meaningful when you can see real differences between subsets.
- **Works with fewer:** 4–7 personas produces directional results — call out the small sample.
- Below 4: the math degenerates (every option "reaches" most people); switch to `persona-ab-test` or `persona-max-diff`.

## Inputs

- **Candidate options** — 5–20 distinct items (features, messages, channels, plan benefits, etc.). Each labeled with a short name and a 1–2 sentence description.
- **K** — how many to pick (typically 2–5). Run for a range (e.g. K=2, 3, 4) to show the reach curve.
- **Reach criterion** — what counts as "reached." Default: persona rates the item ≥5 on a 1–7 scale of "this matters to me / I'd use this / this would influence my decision." User can override (e.g. "rate ≥6" for a stricter bar).

## Workflow

### Phase 1 — Validate options

- 5+ options, ≤20. Below 5, TURF isn't useful — just pick what matters. Above 20, switch to `persona-max-diff` for prioritization first, then run TURF on the top-rated subset.
- Each option distinct enough to be meaningfully separable. Personas can't tell apart near-duplicate options.

### Phase 2 — Sample

Default to all personas; if the user named some, use those. If the roster is much larger than ~15, ask the user which to include rather than auto-selecting (the option-domain is a useful relevance cue for what to suggest).

### Phase 3 — Per-persona rating fan-out

Spawn one subagent per persona, parallel. Each prompt:
- Persona doc path.
- The full options list with descriptions, in a randomized order per persona.
- Rating instruction: "Rate each option on a 1–7 scale of <reach criterion>. For each rating ≥5, quote the part of your persona doc that backs it. For each rating ≤3, briefly say why this doesn't apply / doesn't appeal to you."
- `persona-ask` Ground, think, then talk (Grounding → Thinking → Talking) contract.
- TURF rating response format below.

TURF rating response format:
```
## Grounding (private — orchestrator only; not tallied)
The persona-doc sections that bear on these ratings, cited first: `§ <Section>: "<…>"` + a confidence read [high|medium|low|off-pattern] + reason.

## Thinking (private — orchestrator only)
Private reasoning over that grounding: what this persona would genuinely conclude, where the evidence is thin.

## Ratings
- <Option 1 name>: [N] — short reason if rating ≥5 or ≤3
- <Option 2 name>: [N] — ...
...

## What I'd add if it were on the list
Anything that would have rated ≥5 that wasn't included. Catches blind spots.
```

### Phase 4 — Compute reach

(Per-persona **Grounding** and **Thinking** are audit fields — orchestrator-only and **not** tallied; only the public Ratings feed the reach math.)

For each persona, mark options "reached" (rating ≥ threshold).

For each K in the requested range (typically K=1 through min(8, N_options)):
- Find the **K-subset that maximizes the count of reached personas** (greedy is fine: pick the option that reaches the most, then the option that adds the most new reach, etc.).
- Report: reach % (personas reached / total), the chosen subset, the marginal lift each option adds.

The **reach curve** (K on x-axis, reach % on y-axis) is the headline artifact. The point where the curve plateaus is the natural "good enough" K.

### Phase 5 — Synthesize

```
# TURF analysis: <option domain>

## Reach curve
K=1: <option> covers X%
K=2: <option, option> covers Y% (+Z% marginal)
K=3: <option, option, option> covers ... (+...)
[show as monospace chart]

## Recommended K
The K where marginal reach drops below ~10% or absolute reach exceeds ~85%. State the recommendation as a sentence: "K=3 (<option, option, option>) reaches X% of the panel; the 4th option adds only Y% marginal."

## The carry-everyone subset
The K-subset that maximizes reach.

## The personas left uncovered
Which personas were NOT reached by the recommended subset, and what they wanted instead. Often these are real audience segments to either ignore (intentionally not your target) or add a dedicated option for.

## What personas asked for that wasn't on the list
Aggregated from the "what I'd add" field. Real signal for product/messaging gaps.

## Sample-size caveat
"N=<N> personas; TURF assumes <larger N> for stable reach estimates. Results are <directional|robust> at this sample size."
```

## Notes

- TURF is a *coverage* tool. The single-best option isn't always in the best K=3 subset — sometimes a less-loved option fills a gap that the top option misses. The synthesis should make this explicit when it happens.
- Greedy TURF (pick the best, then the best marginal-add, etc.) is good enough for the persona counts we have. Full optimization across all combinations is unnecessary.
- A flat reach curve (every K adds about the same amount) means the options aren't differentiated for this panel — flag it; TURF can't help.
- A steep curve that plateaus fast at low reach (e.g. K=2 reaches 50% then K=10 only reaches 60%) means the panel is fragmented — your options don't speak to most personas. The action isn't "ship more options," it's "rethink the option set entirely."
