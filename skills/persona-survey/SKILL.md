---
name: persona-survey
description: Run a structured survey across multiple personas — a fixed question set asked to each persona independently, then aggregated. Use when the user says "/persona-survey", "survey the personas about X", "ask everyone these questions", or wants breadth across the panel rather than depth on one viewpoint.
---

# Persona Survey

A fixed question set, run independently across multiple personas, with quantitative aggregation for closed questions and thematic clustering for open ones.

## When to use vs. alternatives

- Use `persona-survey` when you have specific questions you want answered consistently across many personas.
- Use `persona-interview` for depth on one persona.
- Use `persona-ab-test` when the question is "which of these wins?"
- Use `persona-max-diff` when the question is "which of these N items matters most?"
- Use `persona-focus-group` when you want personas to see each other's answers.

## Sample size

- **Sweet spot:** 5–10 personas.
- **All available** by default. If `./.personas/` has more than 10, call `persona-sample` to pick the most topically-relevant 10 — unless the user explicitly wants all.
- Works with as few as 3, but say so in the output (small sample = directional).

## Inputs

- **Question set** — 3–15 questions. Mix of:
  - **Closed:** multiple-choice, Likert scale (1–5 or 1–7), yes/no, ranking
  - **Open-ended:** "Why?", "How would you describe…", "What would you change?"
- **Target sample** — defaults to all personas; user can override with explicit slugs or a topical filter (e.g. "just the B2B ones").
- **Optional asset** to react to.

## Workflow

### Phase 1 — Validate the question set

Before launching, sanity-check the questions:
- Each question should be unambiguous, non-leading, and answerable with the persona-doc info (or honestly answerable as "don't know"). Apply the `persona-ask` framing checklist.
- For Likert scales, define the endpoints in plain language ("1 = would never use, 7 = would pay for it today").
- For multiple-choice, include "none of these" / "other" options unless the choice is genuinely closed.
- Aim for ≤15 questions. Survey fatigue is real even for personas — beyond 15 the later answers get terse.

If the user gave a vague brief ("survey them about pricing"), help them turn it into 5–10 concrete questions before fanning out.

### Phase 2 — Sample

If the available persona count exceeds 10 or the user asked for relevance filtering, call `persona-sample` with the survey topic and N. Otherwise use all personas.

### Phase 3 — Fan out

Spawn one `general-purpose` subagent per persona, all in a single message so they run in parallel. Each prompt:
- Persona doc path.
- The full question set, in order.
- The `persona-ask` reviewer contract — references + confidence on every answer.
- The required response format below.

Each persona answers all questions in one pass (not one subagent per question — that's wasteful).

### Required response format per persona

```
## <persona slug>

### Q1: <question text>
**Answer:** <for closed Q's: the chosen option / scale value; for open: 1–3 sentences>
**Confidence:** [high|medium|low]
**Why:** brief reasoning, citing persona doc sections where load-bearing

### Q2: ...
...
```

### Phase 4 — Aggregate

For each question:

**Closed questions:**
- Tally responses (distribution).
- Report mean / median for scale questions.
- Show the distribution visually (`▓▓▓▓░░░░░░ 4/10 chose X`).
- Note confidence-weighted distribution if confidences vary meaningfully — e.g. "3 of 5 picked Option A, but two of those three flagged it [low] confidence."

**Open-ended questions:**
- Cluster answers into 2–5 themes. Name each theme in 3–5 words.
- For each theme: how many personas, the strongest 1–2 quoted reactions, the personas attached.
- Flag genuine outliers (one persona saying something nobody else said) — don't average them away.

### Phase 5 — Synthesize

```
# Survey results: <topic, short>

## Sample
N personas (of M available), selected by: <"all" | persona-sample with reason>.

## Headline
One sentence — the dominant pattern across questions.

## Per-question results
[Q1 summary, distribution, themes for open Q's, notable outliers]
[Q2 ...]
...

## Cross-question patterns
Things that only become visible by looking across questions — e.g. "personas who picked Option A on Q3 consistently rated price as more important on Q7."

## Sample-size caveat
"N=<N> personas; survey methodology assumes <larger N>. Results are <directional|robust> at this sample size. To strengthen: add personas via persona-distill or persona-create."
```

## Notes

- Don't run the same persona twice in the same survey. Don't merge multiple personas into a synthetic "average respondent" — show distributions instead.
- If the user wants to run the survey on a *segment* of personas (e.g. "just the B2B ones"), use `persona-sample` with the segment as the topic, or let the user list slugs explicitly.
- Re-running the same survey at a later date is fine and useful for tracking shifts — save the question set somewhere reusable (the user's own notes; this skill doesn't persist surveys).
