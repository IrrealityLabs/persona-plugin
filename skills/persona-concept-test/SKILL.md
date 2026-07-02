---
name: persona-concept-test
description: Validate a product, feature, or positioning *concept* with the personas before building it — describe the concept in a short brief, get reactions on appeal, believability, differentiation, and willingness to use/pay. Use when the user says "/persona-concept-test", "concept test this", "before I build this, what would the personas think", "validate this idea", or has an unbuilt concept and wants directional feedback.
---

# Persona Concept Test

Run a concept past the personas before it exists. The personas react to a short written brief, scoring it on appeal, believability, differentiation, and intent. Output: per-criterion scores + thematic feedback + a "build it / refine it / kill it" verdict per persona.

## When to use vs. alternatives

- Use `persona-concept-test` when the thing doesn't exist yet — you're testing the *idea*, not an asset.
- Use `persona-ab-test` when you have built variants of an existing thing.
- Use `persona-jtbd-interview` when the question is *whether* this concept solves a real switch trigger.
- Use `persona-survey` for narrow follow-up questions on a concept that already passed initial validation.

## Sample size

- **Sweet spot:** 5–8 personas. Below 4 = directional only.
- Default to all personas; if the user named some, use those. If the roster is much larger than ~8, ask the user which to include rather than auto-selecting (the personas the concept actually targets are a useful relevance cue for what to suggest).

## Inputs

- **The concept brief** — a short (200–500 word) description covering:
  - What it is (in plain language).
  - Who it's for.
  - The problem it solves.
  - How it works (just enough to be evaluable).
  - Pricing or business model, if part of the concept.

  If the user gives a vague pitch ("an AI tool for marketers"), push back — concept tests on vague concepts surface noise. Help them write a brief good enough to evaluate before launching.

- **Optional comparison** — name 1–3 existing alternatives. Forces the persona to position the concept against what already exists.

## Workflow

### Phase 1 — Validate the brief

Apply a brief-quality check before fanning out:
- Plain language, no jargon the persona wouldn't immediately decode.
- A specific use case, not a feature list.
- Honest about what it *won't* do — gaps are part of the concept.
- Mentions price/business model if relevant.

If the brief fails any of these, suggest a tightening before running.

### Phase 2 — Select personas

Default to all personas; if the user named some, use those. If the roster is much larger than ~8, ask the user which to include rather than auto-selecting. If the concept names a specific user type, suggest the personas closest to that type as a relevance cue for what to ask.

### Phase 3 — Fan out

Spawn one subagent per persona, parallel. Each prompt:
- Persona doc path.
- The concept brief.
- The named comparison products, if any.
- The `persona-ask` Ground, think, then talk (Grounding → Thinking → Talking) contract.
- Concept-test response format below.

Concept-test response format:
```
## Grounding (private — orchestrator only; not aggregated)
The persona-doc sections that bear on this, cited first: § <Section>: "<…>" + a confidence read [high|medium|low|off-pattern].

## Thinking (private — orchestrator only)
Private reasoning over that grounding: what this persona would genuinely conclude, where the evidence is thin.

## Verdict
Build it | Refine and retest | Don't build — one line on why.

## Scores (1–7, with reason)
- **Appeal** (would I find this interesting): N — why
- **Believability** (do I think it would actually work as described): N — why
- **Differentiation** (does it stand out from what exists): N — why
- **Personal fit** (would *I* use this): N — why
- **Willingness to pay/use** (if there's a price, would I pay it): N — why

## What's strong
"Quoted reaction" — what about the concept resonated.
**References (persona doc):** § <Section>: "..."

## What's broken or missing
"Quoted reaction" — what would stop me from buying/using, even if I liked the idea.

## What would I want to see in v1
The minimum thing the concept needs to include for me to take it seriously.

## Comparison reaction (if alternatives given)
How this concept lands vs. <named alternatives> from my perspective.
```

(Grounding + Thinking are per-persona audit fields — kept with the orchestrator, never aggregated; only the public verdict, scores, and feedback are rolled up below. The overall-confidence read lives in Grounding now; the 1–7 appeal/believability/etc. scores stay public answer data.)

### Phase 4 — Synthesize

```
# Concept test: <concept name, short>

## Verdict tally
N build | N refine | N kill. If split, surface the split clearly.

## Score summary (1–7, mean across personas)
- Appeal: X.X
- Believability: X.X
- Differentiation: X.X
- Personal fit: X.X
- Willingness: X.X
[show as monospace bar chart]

## Strongest signal — appeal vs. willingness gap
The gap between "I find this interesting" (appeal) and "I'd actually pay" (willingness) is the single most useful signal a concept test produces. Call it out specifically.

## What multiple personas flagged as broken
The cross-persona objections — these are the things to fix before retest.

## What multiple personas wanted in v1
The cross-persona must-haves — these are the scope clarifications.

## Persona splits
Where the concept landed very differently for different personas. Often surfaces a positioning question — which persona are you really for?

## Recommended action
Build / refine / kill — with the reasoning that the panel best supports. If split, give decision criteria, not a verdict.
```

### Phase 5 — Render the report

Write `report.html` to `./.persona-research-runs/concept-test-<YYYY-MM-DD>-<slug>/` per
the shared spec in `skills/persona-research/references/html-report.md` — self-contained
(inline CSS/JS, data embedded, opens with a double-click): the question, method + N
caveat, the verdict tally and per-criterion score summary, one card per persona with
their verbatim public answers + confidence and collapsible grounding, and the insights.
Tell the user the path.

## Notes

- Personas have no skin in the game and no purchase pain. They will over-rate appeal and under-rate friction. Discount appeal scores; weight believability and broken/missing feedback more.
- A concept that scores 6/7 on appeal but 3/7 on willingness-to-pay is the *most common* persona-test result and the most useful — it says "people like the idea but won't act on this version." That's the gap to close.
- Don't concept-test with personas as a replacement for real customer concept-testing. Use it to *pre-filter* — kill obviously broken concepts cheaply, refine the survivors, then validate with real customers.
