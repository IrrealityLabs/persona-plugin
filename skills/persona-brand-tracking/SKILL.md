---
name: persona-brand-tracking
description: Run brand-tracking research with the personas — measure aided and unaided recall, brand associations, NPS-style intent, and category awareness. Designed to be re-run periodically to track shifts over time. Use when the user says "/persona-brand-tracking", "measure brand awareness", "unaided recall", "what comes to mind when you say <category>", "NPS the personas", "brand health check", or wants a structured awareness measurement.
---

# Persona Brand Tracking

Direct measurement of brand awareness and perception. The persona panel is asked the canonical brand-tracking questions: unaided recall, aided recall, associations, NPS / recommend intent. Run as a baseline; re-run later to track shifts.

This is the *direct* counterpart to `persona-social-listening`, which measures salience indirectly through organic posts. Brand tracking measures what's top-of-mind when asked; social listening measures what shows up unasked.

## When to use vs. alternatives

- Use `persona-brand-tracking` to measure direct awareness, associations, and recommend intent across the panel.
- Use `persona-social-listening` for organic mention salience in context.
- Use `persona-survey` for narrow custom questions about a specific brand.
- Use `persona-concept-test` for a new brand or new positioning that doesn't yet exist in the panel's awareness.

## Sample size

- **All personas** by default. Brand tracking benefits from breadth.
- Below 5: directional only.

## Inputs

- **Category** — what space you're measuring within (e.g. "customer support software", "energy drinks", "AI coding assistants"). The category frames every question.
- **Target brand** — the brand under measurement.
- **Competitor set** (optional but recommended) — competitors to also probe in aided recall and associations.
- **Survey scope** — which sections to run. Default: all four (unaided / aided / associations / NPS). Skip sections that don't apply (e.g. NPS doesn't fit pre-launch brands).

## Workflow

### Phase 1 — Sample

Use all personas if ≤15; else `persona-sample` for 10 with the category as topic filter.

### Phase 2 — Fan out the four-section survey (parallel)

Spawn one subagent per persona. Each prompt:
- Persona doc path.
- The category framing (kept consistent across personas).
- The full question set (all sections, in canonical order — unaided always before aided to avoid priming).
- `persona-ask` reviewer contract.
- Brand-tracking response format below.

**Canonical question order — do not vary:**

#### Section 1: Unaided recall (always first)
> "When I say <category>, which brands or names come to mind? List as many as occur to you naturally, in the order they came to mind. Stop when you've genuinely run out — don't pad."

#### Section 2: Aided recall (only after unaided is captured)
> "Have you heard of each of these? <list: target brand + competitors, randomized order>. For each: yes (know it well), maybe (heard of it, fuzzy), no (never heard of it)."

#### Section 3: Associations (for target brand and key competitors)
> "When you think of <brand>, what comes to mind? List 3–6 words or short phrases — what they stand for, what they do, what kind of customer they're for, how you'd describe them to a friend. Don't think hard, list the first associations."

Repeat for competitors that the user wants associations on (typically 2–3 competitors max — beyond that the survey gets long).

#### Section 4: Recommend intent (NPS-style)
> "On a scale of 0–10, how likely would you be to recommend <brand> to someone in your situation who was looking in this category? 0 = definitely wouldn't, 10 = definitely would. Then in one sentence: what would change your answer (up or down)?"

Repeat for competitors if requested.

### Brand-tracking response format

```
## Unaided recall (Section 1)
Listed brands, in order they came up:
1. <brand>
2. <brand>
...
Stopped at <N>. Confidence: [high|medium|low]

## Aided recall (Section 2)
- <brand>: yes / maybe / no — one phrase if "maybe"
- ...

## Associations
### Target brand: <brand>
- <association 1>
- <association 2>
- ...
(3–6 items)

### Competitor: <brand>
- ...

## Recommend intent
- <brand>: <0–10>. Reason: <one sentence>. Confidence: [high|medium|low]
- <competitor>: ...

## References (persona doc)
The 2–3 most load-bearing references that grounded the answers, especially for the recommend-intent reasoning.
```

### Phase 3 — Aggregate

**Unaided recall:**
- Per brand: % of personas who mentioned it; average position in the list.
- **First-mention rate** = % who listed the brand first. The strongest unaided-awareness signal.
- Per persona: list length (a proxy for category fluency).

**Aided recall:**
- Per brand: yes / maybe / no distribution.
- **Awareness % = yes + maybe.**

**Associations:**
- Cluster associations into themes per brand (3–5 themes). Name each.
- Surface contradictions: associations that conflict ("premium" + "cheap" both showing up).
- Compare target vs. competitors on the same dimensions — where do they differ in what they stand for?

**NPS:**
- Per brand: average score, distribution (promoters 9–10, passives 7–8, detractors ≤6), NPS = % promoters − % detractors.
- For target: dominant reasons cited at each tier.

### Phase 4 — Synthesize

```
# Brand tracking: <brand> in <category>

## Unaided recall
- <brand>: X% mentioned, avg position N, first-mentioned by M personas
- <competitor>: X% / pos N / first M
- [bar chart]

## Aided recall (% who know it)
- <brand>: X% awareness (Y% strong + Z% fuzzy)
- ...

## Associations
For <brand>: the 3–5 dominant themes, with sample associations and the personas they came from.
For competitors: same. Surface where competitors' associations diverge meaningfully from yours.

## Contradictions and mixed signals
Anywhere the associations were contradictory (personas split on what the brand stands for) — this is positioning ambiguity, often actionable.

## NPS
<brand>: NPS = N (M% promoters, P% passives, D% detractors)
Promoter pattern: <dominant reasons>
Detractor pattern: <dominant reasons>
Compare to competitors if measured.

## Headline takeaway
One sentence — the strongest signal for action. e.g. "Our aided awareness is strong (75%) but we ranked third on first-mention recall — the brand is *known* but not *top-of-mind* in this category."

## Tracking notes (re-run reference)
List the exact question set used and the sample size — re-running with the same setup later allows direct comparison of shifts.

## Sample-size caveat
"N=<N> personas; brand tracking on a panel of this size shows *direction* but not statistical significance. To detect shifts at this scale, look for changes ≥15-20 percentage points between runs."
```

## Notes

- **Do not reverse unaided and aided order.** Aided recall primes the persona; if you ask aided first, unaided is contaminated. Always unaided first.
- The most useful single number from brand tracking is usually **first-mention rate** — it correlates more strongly with real top-of-mind awareness than total-mention rate.
- NPS scores from personas tend to skew positive (no actual product pain). Discount the absolute number; focus on the *reasons cited at each tier*.
- For tracking over time: save the run's question set and persona sample alongside the results, so a re-run is comparable. Differences in panel composition between runs muddy the comparison.
- An association cluster that surfaces frequently but doesn't match what the user *thinks* the brand stands for is the most actionable finding — it's positioning drift visible in data.
