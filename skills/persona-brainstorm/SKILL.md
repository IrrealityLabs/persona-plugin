---
name: persona-brainstorm
description: Run a collaborative ideation session where personas generate ideas and build on each other's across rounds (yes-and, not critique) — output is a deduped, clustered, ranked idea set, not a consensus or a verdict. Use when the user says "/persona-brainstorm", "brainstorm X with the personas", "have the personas generate ideas for Y", "what would my personas come up with", "ideate on this as a group", or wants idea *generation* with cross-pollination rather than evaluation of something that already exists.
---

# Persona Brainstorm

A generative session: personas produce ideas, then build on, combine, and extend each other's across 2–3 rounds. The dynamic is **additive** — yes-and, not tear-down. The output is a ranked, clustered idea set with the build-chains shown, not a single answer or a vote.

Subagents are stateless and can't message each other. You (the orchestrator) are the channel: pool the ideas each round, hand the pool back so the next round can build on it.

## When to use vs. alternatives

- Use `persona-brainstorm` to **generate and grow ideas** as a group (features, names, campaigns, solutions to a problem).
- Use `persona-high` for solo, off-the-wall *divergent* ideation — wilder, less buildable, no cross-pollination.
- Use `persona-focus-group` to *react to / evaluate* something that already exists (convergent, not generative).
- Use `persona-council` to *pressure-test* a decision adversarially (tears ideas down, doesn't grow them).
- Use `persona-of-thought` for *one* fused answer from independent perspectives (no building on each other).

Brainstorm is the only method here whose dynamic is *additive cross-pollination*. If you catch the panel slipping into critique ("that won't work because…"), you've drifted into focus-group/council territory — steer back to building.

## Sample size

- **Sweet spot:** 3–7 personas, 2–3 rounds. Default 5×2.
- Below 3, too few angles to cross-pollinate. Above 7, the idea pool gets unwieldy and rounds get expensive.
- Cognitive diversity matters more than topical fit (as in council): if a large roster needs narrowing, pick a span of `## At a glance` lines and say which you picked.

## Inputs

- **The challenge** — a "how might we…" or an open prompt ("names for this feature", "ways to cut onboarding time in half"). The broader the prompt, the more divergence; tighten it if you want buildable specifics.
- **Optional constraints** — must-haves / must-avoids that every idea has to respect.
- **Round count** (default 2, cap 3).
- **Persona selection** — named → those; otherwise all if ≤7, else ask which to include.

## Workflow

### Phase 0 — Confirm cost

Personas × rounds = subagent runs (5 × 2 = 10; 7 × 3 = 21). Use `persona-research/references/cost-estimator.md`. Warn above ~15.

### Phase 1 — Select

Named personas → exactly those. Otherwise all if ≤7; if more, pick a cognitively diverse 5–7 by reading `## At a glance` lines and say which and why.

### Phase 2 — Round 1: diverge

Spawn one subagent per persona, in parallel. Each prompt:
- Persona doc path; the challenge and any constraints.
- The `persona-ask` reviewer contract — including *Ground, think, then talk* (return **Grounding** + **Thinking** + **Talking**), with grounding + confidence on the *reasoning*, not on each idea.
- **Generate with Verbalized Sampling, not your first instinct.** Ask the persona to produce a *probability-weighted spread* of ideas — some obvious, some from the low-probability tail — and keep the unusual-but-valid ones, not just the archetypal answer. This is the mode-collapse counter that keeps Round 1 from returning five versions of the same idea (see `persona-create`, finding #10).

Round 1 response format:
```
## Grounding (private — for the orchestrator; kept out of the pool digest)
The persona-doc signal your ideas draw on: `§ <Section>: "<…>"`.

## Thinking (private — for the orchestrator; kept out of the pool digest)
What angles your doc pushes you toward, what's been overdone, where the unusual ideas might be.

## Ideas
- **<short title>** — one line. What it is, and why *this persona* would reach for it (tied to their behavioral/contextual signal).
- … (aim for 3–6, deliberately spanning obvious → unusual)
```

### Phase 3 — Round 2+ : build

Compile the **idea pool** from the prior round — every idea's title + one-line, deduped, with the proposing persona. (Never include anyone's `Grounding` or `Thinking`.) Re-spawn each persona in parallel, with:
- Their own prior ideas + the full pool.
- An explicit **additive** directive: "Build on the pool. Combine two ideas into a stronger one, push an idea further, or fill a gap nobody hit. *Yes-and* — do not critique or rank. Credit the idea(s) you built from."

Round 2+ response format:
```
## Grounding (private — for the orchestrator)
The persona-doc signal behind your builds: `§ <Section>: "<…>"`.

## Thinking (private — for the orchestrator)
Which pool ideas have the most room to grow, what combination or extension you see that others missed.

## Built ideas
- **<short title>** — one line. *Builds on:* `<title(s)>` from <persona>. What you added or combined.
- … (1–4; quality of build over quantity)

## One wildcard
A single idea further out than you'd normally pitch — the tail of your distribution.
```

### Phase 4 — Convergence check

Stop when a round adds little genuinely new (builds are just re-phrasings), or at the 3-round cap. Brainstorm hits diminishing returns fast — 2 rounds is usually enough. Run at least 2 (Round 1 diverges, Round 2 builds — one round alone isn't a brainstorm).

### Phase 5 — Synthesize

Output is an **idea set**, not a recommendation:

```
# Brainstorm: <challenge>

## Top ideas (clustered)
2–5 clusters by theme. Per cluster: the idea in its strongest (most-built) form, who shaped it, and the build-chain if it grew across rounds (`A → combined with B → C`).

## Wildcards worth keeping
The 2–3 low-probability ideas that survived — the ones a single-pass brainstorm would have dropped. Say which persona's tail they came from.

## Cross-persona pull
Where multiple personas independently converged on a direction (a signal it's robust), vs. ideas that lived with one persona (contingent on that viewpoint).

## What to take to real ideation
The 1–2 ideas worth developing with humans, and the open question each still has.
```

Close with the standard simulation disclaimer.

## Notes

- **Diverge before you converge.** Don't let Round 1 self-censor toward "good" ideas — that kills the tail. Ranking and clustering happen only in synthesis.
- **Additive, not evaluative.** The whole point is building. If the panel critiques, you're running a focus group by accident — re-steer to yes-and.
- **Wildcards are the deliverable, not noise.** The reason to run a *panel* brainstorm rather than ask one model for a list is the spread across genuinely different viewpoints; protect the unusual ideas through to the synthesis.
- Wrappable by `persona-multiverse` — it's a dynamic study (the build rounds are the social layer; the control run is Round 1 only).
