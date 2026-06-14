---
name: persona-of-thought
description: Personas of Thought (PoT) — answer a question by having each persona respond independently from their own background, then combine the responses into a single anonymous joint answer written as if the personas collaborated on it. A diverse-perspective reasoning technique in the lineage of Chain-of-Thought / Tree-of-Thoughts — the persona diversity is a means to one more-robust answer, not a panel report. Use when the user says "/persona-of-thought", "personas of thought", "PoT this", "ask the personas and merge into one answer", "give me a joint anonymous answer from the personas", or wants a single synthesized answer to a question (including "which is better, A or B?") drawn from many perspectives. Reads personas from ./.personas/.
---

# Personas of Thought

A reasoning technique. Where Chain-of-Thought reasons in steps and Tree-of-Thoughts branches over candidates, **Personas of Thought** reasons across *people*: each persona answers the question independently from their own background and experience, and then the answers are fused into one anonymous joint response — as if those people had sat down and written a single collaborative answer together. The diversity of grounded viewpoints is what makes the merged answer better than asking once; the personas are the means, the single answer is the product.

> Technique by Mike Taylor — https://askrally.com/article/personas-of-thought

This is the one skill in the plugin whose deliverable is **a single merged answer, not a panel breakdown**. If the user wants per-persona reactions to act on, that's `persona-review`. If they want one well-reasoned answer informed by many perspectives, that's this.

## When to use vs. alternatives

- Use `persona-of-thought` when the user wants **one synthesized answer** to a question — open-ended ("how should we position this?") or a choice ("which ad is better, A or B?") — and the value is in fusing many grounded perspectives into a single response.
- Use `persona-review` for a structured, per-persona critique of an asset (severity tags, line-level findings you work down).
- Use `persona-survey` for a quantitative tally / distribution across personas — numbers, not a merged prose answer.
- Use `persona-council` when you want the personas to **debate each other** and surface disagreement. PoT personas answer *independently and never see each other* — the synthesis merges, it does not adjudicate a debate.
- Use `persona-ask` for one persona (or a few) with structured per-persona output.

The defining move of PoT: **independent answers → one anonymous joint paragraph.** Keep that property — don't let personas react to each other (that's council), and don't fragment the output back into a per-person list (that's review).

## Sample size

PoT is a wisdom-of-crowds technique — **more diverse voices make the merged answer more robust.** Default to **all personas in `./.personas/`** (the original technique used ten). Cap around 10–12 for cost/synthesis sanity; if the roster is larger, the orchestrator picks a diverse set by reading the personas' `## At a glance` lines (or asks the user to name a subset) and says which you used. Named personas or an explicit count override the default.

## Inputs

- **The question** — required. Anything answerable: a strategy question, an open prompt, or an either/or choice (the original example was "What's a better ad for Jaguar? A) Grace Space Pace  B) Copy Nothing").
- **Panel** — default all; or named personas; or, for a large roster, a diverse subset the orchestrator picks by reading the personas' docs.
- **Options (if any)** — if the question presents choices (A/B/…), capture them verbatim so every persona weighs the same options.

If `./.personas/` is empty or missing, stop and point at `persona-create` / `persona-distill`. The whole technique rests on having defined personas to swap in for the "invent ten personas" step of the original prompt.

## Workflow

### Phase 0 — Announce

"Running Personas of Thought across <N> personas: <names>. Each answers independently, then I combine them into one anonymous joint answer. Simulations of your audience, not real people."

### Phase 1 — Resolve the panel (this replaces "create the personas")

The original PoT prompt begins by *inventing* ten demographic personas. **Here you skip that step entirely** — the personas already exist in `./.personas/`. Resolve them with the same logic as `persona-review` Phase 1: named → those; otherwise → all personas (the default). If the roster is larger than the ~10–12 cap, the orchestrator picks a diverse N by reading the personas' `## At a glance` lines (or asks the user to name a subset), and says which you picked. That swap is the only change from the source prompt.

### Phase 2 — Frame the question

Run the question through the `persona-ask` framing checklist (load it) so it elicits substance, not agreement — *unless the user quoted an exact wording*, in which case ask it verbatim. Keep the original instruction's spirit: each persona will **answer critically from their perspective given their background and experience.**

### Phase 3 — Independent answers (one subagent per persona, in parallel)

Spawn one `general-purpose` subagent per persona, **all in one message** so they run in parallel and **never see each other's answers** (independence is the point). Each prompt contains:
- The persona doc path — read in full, inhabit it.
- The framed question and any options, verbatim.
- The instruction: *"Answer this question critically from your perspective, given your background and experience."*
- The `persona-ask` reviewer contract — Ground, think, then talk (Grounding → Thinking → Talking): first-person, the persona-doc material cited *first* plus a confidence read, then private reasoning, then the take; honest about disagreement, no generic praise, voice grounded in the doc's examples (not fabricated).

Each subagent returns a short, grounded answer that leads with Grounding, then Thinking, then the public Answer:
```
**Grounding:** (private) The persona-doc sections that bear on this, cited first — § <Section>: "<quote/paraphrase>" + a confidence read [high|medium|low|off-pattern] with a one-line reason.
**Thinking:** (private) Private reasoning over that grounding — what this persona would genuinely conclude, where the evidence is thin.
**Answer:** "First-person, critical take on the question — and, if options were given, which one and why."
```

### Phase 4 — Combine into a single anonymous joint answer

This is the deliverable, and it follows the source prompt closely:

> Combine the responses into **a single paragraph**, written as if these people had **collaborated on a joint, anonymous answer**. **Do not name any of the personas** in the combined response.

Rules for the merge:
- One coherent paragraph (or a tight few if the question is genuinely multi-part) in a single neutral collaborative voice — not a list, not "Persona A said… Persona B said…".
- **Anonymous** — no names, no "the CTO persona," no "one participant." It reads as one considered answer.
- **Faithful to the weight of opinion.** If the panel leaned toward option B, the joint answer leans toward B and carries the strongest shared reasons; surface a genuine minority view as a clause ("though some would push back that…") rather than erasing it. Don't manufacture false consensus, and don't average two opposite positions into mush.
- **Confidence-aware.** Lean on the high-confidence, well-grounded takes; let thin/low-confidence ones inform tone, not conclusions (same weighting principle as `persona-ask`).

Then, **below** the joint answer, add a compact grounding ledger — this rolls up each persona's private Grounding (cited material + confidence read), layered on top of the original technique so the merged answer is auditable:

```
---
**Under the hood** (not part of the joint answer)
- If the question had options: the split — e.g. "B 7 · A 2 · split 1" — with the dominant reason per side.
- One line per persona: their lean + confidence. (Named here only for *your* audit; they stay anonymous in the joint answer above.)
- Where the panel genuinely diverged, and what that disagreement is really about.
- Sample-size caveat: "N=<N> personas — a merged direction, not a measured result."
```

Close with the disclaimer:

> _— Personas of Thought across the panel in `./.personas/`. The joint answer is a synthesis of perspective-taking simulations grounded in their docs, not a real group of people. Treat it as a stronger-than-single-shot prompt for your own judgment, and validate anything load-bearing with real humans._

## Notes

- **Independence first.** The strength of PoT comes from each persona answering without contamination from the others. Spawn them in parallel; never feed one persona another's answer. If the user wants cross-talk, they want `persona-council`.
- **Keep the joint answer clean and singular.** The temptation is to hedge it into a bulleted committee memo. Resist — the technique's output is *one* answer the personas could have co-signed. The nuance lives in the ledger below it.
- **Options questions are a sweet spot.** "Which is better, A or B?" answered by ten grounded perspectives and merged into one verdict is exactly what this was built for (the original example chose between two Jaguar ad lines). Keep the options verbatim so the merge reflects a real vote, not a reinterpretation.
- For a large/varied roster, the diversity of the subset matters more than its size — when picking, the orchestrator favors value-distance (reading the `## At a glance` lines), as `persona-council` does.

## Appendix — the source prompt, adapted

The original Personas of Thought prompt, with only the persona-creation step swapped for your existing personas:

```
[Use my existing personas in ./.personas/ — do not invent new ones.]

Have each persona answer this question critically from their perspective,
given their background and experience:

  <QUESTION>
  [A) <option>]
  [B) <option>]

Finally, combine these responses into a single paragraph response as if these
people had collaborated in writing a joint anonymous answer. Do not name any
of the people in the combined response.
```
