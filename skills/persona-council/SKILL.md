---
name: persona-council
description: Convene an adversarial council of personas to pressure-test an idea — personas take positions, then debate each other across rounds, with a moderator synthesizing where they converge and where genuine disagreement remains. Use when the user says "/persona-council", "convene a council", "have the personas debate X", "stress-test this idea against everyone", or wants sharper friction than a focus group provides.
---

# Persona Council

A debate format: personas stake positions, then actively challenge each other across 3–4 rounds. Sharper and more adversarial than `persona-focus-group` — the prompt asks each persona to *push back* where their stated patterns indicate they would, rather than discuss-and-converge.

Structurally similar to `persona-focus-group` (orchestrator-compiled digest each round, parallel subagents), but the prompts reward dissent over agreement.

## When to use vs. alternatives

- Use `persona-council` to pressure-test a decision, find the strongest objections, stress-test a claim before committing.
- Use `persona-focus-group` for a more cooperative discussion dynamic.
- Use `persona-survey` for parallel independent answers without debate.

## Sample size

- **Sweet spot:** 4–7 personas, 3–4 rounds. Below 4, the debate has too few voices to surface diverse objections. Above 7, the digest gets unwieldy.
- Default: 5 personas × 3 rounds.

## Inputs

- **The proposal / claim / decision** to pressure-test.
- **Optional supporting material** — the doc, plan, design that supports the claim.
- **Round count** (default 3, cap 4).
- **Persona selection** — if the user names personas, use exactly those; otherwise use all personas in `./.personas/`. For council, *cognitive diversity* matters more than topical relevance: if a large roster needs narrowing, the orchestrator picks a value-spanning subset by reading each persona's `## At a glance` line. State which you picked and why.

## Workflow

### Phase 0 — Warn on cost

5 × 3 = 15 subagent runs; 7 × 4 = 28. Always confirm before launching.

### Phase 1 — Select for diversity

If the user named personas, use exactly those. Otherwise default to all personas in `./.personas/`. Council wants *cognitive diversity*, not topical relevance — so if a large roster needs narrowing, don't auto-sample: you (orchestrator) read the personas' `## At a glance` lines and pick the N that span the most ground (e.g., one optimist, one skeptic, one outside-the-target, etc.). State which you picked and why. If you'd rather not choose, ask the user to name the subset.

### Phase 2 — Round 1: stake positions

Spawn one subagent per persona, in parallel. Prompt difference vs. focus-group: explicitly direct the persona to take a *position*, not just react. "You're being asked to judge this proposal. Take the strongest position your decision-making patterns support — agreement or rejection, with stakes." Apply `persona-ask`'s *Ground, think, then talk* first: ground in the doc, reason privately, then stake the position you'd actually defend out loud.

Round 1 response format:
```
## Grounding (private — for the orchestrator; kept out of the digest)
The persona-doc sections that bear on this proposal, cited first: `§ <Section>: "<…>"` + a confidence read.

## Thinking (private — for the orchestrator; kept out of the digest)
Your private reasoning over that grounding: what you'd genuinely conclude, where you're thin.

## Verdict
Endorse | Reject | Conditional (state condition) | Decline (out of my domain)

## Argument
The strongest case for your verdict — tied to your decision-making patterns. References inline.

## Where I'd push back hardest
The single objection or condition you'd refuse to drop even under pressure.

## Confidence
[high|medium|low] + reason.
```

### Phase 3 — Debate rounds (2 through cap)

Compile the digest each round: each persona's Verdict + condensed Argument + pushback — never their `Grounding` or `Thinking`, which stay with you. Then re-spawn each persona with:
- Their own prior round response.
- The digest of others' positions.
- An explicit directive: "engage the opposing positions — by name. Name what's strong about them, name what's wrong about them. You may update or harden; do not soften out of politeness."

Round 2+ response format:
```
## Grounding (private — for the orchestrator; kept out of the digest)
The persona-doc sections behind your position this round: `§ <Section>: "<…>"` + a confidence read.

## Thinking (private — for the orchestrator; kept out of the digest)
Your private reasoning this round: what the opposing arguments actually do to your position, before you decide what to argue back.

## Verdict (current)
Held | Updated | Conceded | Hardened — one line on what moved.

## Engagement
For each opposing persona's position (name them): what's strong about their case, what you reject and why.

## Strongest opposing argument I haven't answered
Name it. If you don't think any exists, say so plainly.

## Pushback (current)
The condition or objection you still refuse to drop.

## Confidence
[high|medium|low] + reason.
```

### Phase 4 — Convergence + synthesis

Same convergence check as `persona-focus-group`: stop when positions stable AND no questions a panelist could resolve. Hard cap 4 rounds.

Synthesize as the **moderator**, not as a tiebreaker:

```
# Council: <proposal, short>

## Vote tally
N endorse | N reject | N conditional | N decline. Conditional/decline conditions enumerated.

## Strongest case FOR
Distilled from the endorsers — the best version of their argument.

## Strongest case AGAINST
Distilled from the rejecters — the best version, undiluted.

## What the council could not resolve
The genuine clash points — why each side held, what evidence would have settled it.

## Decision criteria (not a recommendation)
If the user has to decide despite the split: the criteria the council surfaced as load-bearing. Frame as "if X matters more, lean Y."

## Open questions for real humans
What the simulation can't settle.
```

Close with the standard simulation disclaimer.

### Phase 5 — Render the report

Write `report.html` to `./.persona-research-runs/council-<YYYY-MM-DD>-<slug>/` per the
shared spec in `skills/persona-research/references/html-report.md` — self-contained
(inline CSS/JS, data embedded, opens with a double-click): the question, method + N
caveat, the vote tally and strongest cases for and against, one card per persona with
their verbatim public answers + confidence and collapsible grounding, and the insights.
Tell the user the path.

## Notes

- The council should produce dissent. If Round 1 came back unanimous, that's a selection problem — either the panel was too aligned or the proposal is too obvious. Mention it. Don't manufacture artificial dissent.
- The moderator (you) does *not* break ties. If the council splits, the user decides — your job is to make the criteria crisp.
- Do not let a high-status persona (e.g. a "CEO" archetype) carry undue weight. Every council vote counts the same; the *quality* of arguments is the only weighting.
