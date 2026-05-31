---
name: persona-multiverse
description: Meta-skill — wraps any dynamic-system study (focus group, council, town, market, x-post / linkedin-post / hacker-news with reply rounds) and runs it N times. One run is the *control* (social-influence dynamics stripped out, personas act independently); the rest are full dynamic runs with the same starting conditions but non-deterministic outcomes. Synthesizes across runs to surface what was consistent, what was rare, and how social-influence dynamics changed the outcome. Use when the user says "/persona-multiverse", "run this in multiple universes", "wrap this study in a multiverse", "what's the variance of this outcome", "is this outcome reliable or did the social dynamics drive it", or wants to spend more tokens for a more honest measure of an outcome's reliability.
---

# Persona Multiverse

A **meta-skill**, not a study type. It wraps a dynamic-system study and runs it N times to surface what's *reliable* vs. *contingent on social dynamics*. The output isn't a new kind of finding — it's a more honest version of the wrapped study's finding, with explicit treatment of variance.

The principle, from Salganik / Dodds / Watts (2006): in any system where participants can see and react to each other, outcomes become **unpredictable and unequal**. Small differences in early signals get amplified. The "winner" in one run might lose in another with the same starting conditions. A single dynamic-system run is just *one draw from the distribution of possible outcomes* — running multiple draws lets you see the distribution.

The control universe — same setup minus the social-influence layer — is the reference: what does this outcome look like *without* the dynamic amplification? The gap between control and dynamic-average is the "social-influence delta" — the part of the outcome that's about cross-persona dynamics, not the underlying input.

## When this applies (and when it doesn't)

Multiverse only makes sense wrapping a **dynamic-system** study — one where personas see and react to each other's outputs. The wrappable studies:

| Study | Dynamic mechanism | Control modification |
|---|---|---|
| `persona-focus-group` | Rounds 2+ see Round 1 digest | Run only Round 1 (parallel independent) |
| `persona-council` | Debate rounds see prior positions | Run only Round 1 (parallel independent positions) |
| `persona-town` | Personas observe and speak to neighbors | Disable conversation / observation — solo agents |
| `persona-market` | Social-influence condition shows running counts | Independent condition — no count visibility |
| `persona-x-post` (reply round on) | Phase 3 sees Phase 2 thread | Skip Phase 3 — only top-level reactions |
| `persona-linkedin-post` (reply round on) | Same | Same |
| `persona-hacker-news` (reply round on) | Same | Same |

For **non-dynamic studies** (`persona-survey`, `persona-ab-test`, `persona-ask`, `persona-interview`, `persona-van-westendorp`, `persona-conjoint`, `persona-max-diff`, `persona-turf`, `persona-brand-tracking`, `persona-roast`, `persona-concept-test`, `persona-tree-test`, `persona-user-test`, `persona-ethnographic`, `persona-diary-study`, `persona-jtbd-interview`, `persona-grounded-theory`, `persona-social-listening`, `persona-high`), wrapping in multiverse just burns tokens to produce roughly the same answer N times (each persona reasoning fresh from their doc). If the user tries to multiverse-wrap a non-dynamic study, stop and tell them — the method isn't applicable; suggest running the study once instead.

`persona-market` is a special case: it's *already* a multi-world method by design. Multiverse-wrapping `persona-market` is redundant unless the user wants to compose multiple market runs into a meta-distribution (rare; usually adjust the world count inside `persona-market` directly).

## Sample size and cost

- **Default:** 4 universes (1 control + 3 dynamic).
- **Cost = wrapped study cost × N.** A focus-group run that cost ~15 subagent runs becomes ~60. A council run that cost ~28 becomes ~112. Always confirm.
- Multiverse is **always more expensive than the wrapped study alone.** The whole point is paying more tokens for a more honest answer.

## Inputs

- **The study to wrap** — which child skill, with its full input set (the question, the asset, the personas, etc.). Pass through verbatim to each universe except for the control modification.
- **Universe count (N)** — default 4. Below 3 you can't meaningfully estimate variance; above 6 is usually wasteful.
- **Universe split** — default 1 control + (N−1) dynamic. User can override (e.g. all-dynamic, no control — useful if they already have a control baseline from a prior run).
- **Seed differentiation** — by default, dynamic universes share the same starting inputs and diverge only via subagent non-determinism. Optional: small perturbations to starting conditions (different persona seeded with information first, different starting positions in town, etc.) to amplify the "different draw" effect.

## Workflow

### Phase 0 — Validate applicability

If the user asked to wrap a non-dynamic study, stop and explain. Suggest running the underlying study once.

If the user asked to wrap `persona-market`, ask if they really want this — the inner skill already supports multiple worlds natively. They may be better off increasing the inner skill's world count.

### Phase 1 — Cost confirmation

Estimate cost: `wrapped_study_cost × N`. Use `persona-research/references/cost-estimator.md`. Always warn before launching — this is one of the most expensive things in the catalog.

Make the trade-off explicit:
> "Multiverse wrapping <study> in <N> universes will cost ~<estimate>. The single-universe answer to this question is <estimate of one>. The marginal value is variance estimation — you'll learn how reliable the outcome is, not a different outcome. Proceed?"

### Phase 2 — Plan the universes

For each of the N universes, prepare an invocation of the wrapped study:

- **Control universe (universe 0):** apply the control modification from the table above (e.g. for `persona-focus-group`, set rounds = 1; for `persona-town`, set conversation_disabled = true; for channel sims, set reply_round = false).
- **Dynamic universes (1..N−1):** identical inputs, no modification. Each run will diverge from the others through subagent non-determinism.

Write a manifest file at `./.personas/assets/multiverse-runs/<run-id>/manifest.json` describing the planned universes and their configurations.

### Phase 3 — Execute universes

Run each universe to completion. Where possible, parallelize the universes themselves (they share no state across universes). Some studies — `persona-town` especially — are slow per-universe; running them in parallel is essential to keep total wall-clock time manageable.

Within each universe, the wrapped study's existing parallelism (persona-level) still applies.

Save each universe's full output to `./.personas/assets/multiverse-runs/<run-id>/universe-<N>/` — the same artifacts the wrapped study would produce, just scoped per universe.

### Phase 4 — Cross-universe synthesis

This is where the meta-skill earns its keep. The synthesis has four required sections:

#### A. What was consistent across dynamic universes

The outcomes that appeared in most or all of the dynamic universes. These are the *reliable* findings — when something shows up in 3 of 3 (or 4 of 4) runs with different non-determinism, it's not artifact.

Examples:
- "In all 3 focus-group universes, personas converged on the pricing concern by Round 2."
- "All 3 town universes showed the message reaching ≥80% of personas by tick 12."
- "All 3 council universes split 4-3 on endorsement, though the *which* 4 vs. which 3 varied."

#### B. What was rare or variable across dynamic universes

Outcomes that appeared in only some universes. These are the *contingent* findings — they depended on which way the social-influence dynamic broke. Surface them explicitly *as variable*, not as findings.

For each: how many of N universes produced this outcome, and what conditions in those universes drove it (which persona spoke first, which item got an early lead, which position was articulated more sharply).

Examples:
- "In 1 of 3 focus-group universes, a quote from persona-X early in Round 2 reframed the discussion entirely. Did not happen in the other 2."
- "In 2 of 3 town universes, the message bottlenecked at persona-Y; in 1 of 3, persona-Z carried it instead."

#### C. How the control differed from the dynamic average

The control gives you the outcome *without* social-influence amplification. The gap between control and dynamic-average reveals what the social layer is doing.

Look at:
- **Which findings only appeared in dynamic runs and not in control** — these are *socially constructed* findings, not present in the raw individual reactions.
- **Which findings appeared in control but were drowned out in dynamic** — outcomes the personas would have produced independently but that got displaced by herding.
- **Magnitude differences** — same direction in control and dynamic, but more extreme in dynamic? That's social amplification on top of a real signal. More extreme in dynamic with no signal in control? That's a social artifact.

In Salganik's terms: which "songs" became hits *only* because of the herd dynamics, vs. which were genuinely good?

#### D. The honest single-line takeaway

After all that, the synthesis still ends with one actionable sentence. Examples:

- "Reliable: <consistent finding>. Use this. Variable: <rare finding>. Don't rely on this — it might or might not happen in the real world. Social-influence delta: <what the dynamics added>."
- "The outcome was almost entirely social-influence-driven (high cross-dynamic variance, control showed no winner). Decision: this needs real-customer validation, the simulation can't predict reliably."
- "The outcome was robust (low variance, dynamic and control agreed). Decision: ship."

### Phase 5 — Output structure

```
# Multiverse: <wrapped study + topic>

## Configuration
- Wrapped study: <skill name>
- Universes: 1 control + N−1 dynamic
- Total subagent runs: <number>

## Consistent across dynamic universes (reliable findings)
<bullet list, each with the % of universes it appeared in>

## Variable across dynamic universes (contingent findings)
<bullet list, each with the universe-count and the conditions that drove it>

## Control vs. dynamic
- Findings present only in dynamic runs (socially constructed):
- Findings present in control but lost in dynamic (displaced by herd):
- Magnitude shifts (where dynamic amplified or dampened a real signal):

## Variance score
A rough single number: "X of N dynamic universes produced substantively the same headline conclusion." High = robust outcome. Low = unpredictable, social-influence-driven.

## The honest takeaway
<one sentence>

## Per-universe full outputs
Pointers to the per-universe artifacts on disk: `./.personas/assets/multiverse-runs/<run-id>/universe-<N>/...`
```

## Notes

- **Multiverse buys you variance estimation, nothing else.** It will not give you a *better* answer to the wrapped study's question — it tells you how trustworthy the answer is. If the user has a low-stakes question, run the wrapped study once. If they're betting real budget on the outcome, the multiverse cost is often justified.
- **The control is the most informative single universe.** If you can only run two, run a control + one dynamic. That gives you a directional read on the social-influence delta without N=3+ for full variance.
- **Don't average across universes for narrative outputs.** A focus-group "average transcript" is meaningless — each transcript is a coherent run. The synthesis surfaces *patterns across coherent runs*, not interpolations.
- **Social-influence-driven outcomes are not necessarily wrong.** If the question is "what would actually win in the wild?", herd dynamics *are* part of the answer — real markets have them. The multiverse just makes the herding *visible* so you know what you're getting. If the question is "what's genuinely best on the merits?", the control universe is the answer to trust.
- The Salganik / Dodds / Watts paper is the foundational reference for the inequality + unpredictability + social-influence dynamic. Same paper cited by `persona-market`. The intuition transfers to any social-feedback system; that's why this meta-skill exists.
