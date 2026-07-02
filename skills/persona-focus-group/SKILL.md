---
name: persona-focus-group
description: Run a multi-round focus group with personas that can see each other's prior answers — simulates a group discussion where positions evolve as participants react to peers. Up to 4 rounds, round-robin. Use when the user says "/persona-focus-group", "run a focus group on X", "what would the personas say if they could see each other's takes", or wants reactive dynamics rather than independent parallel responses.
---

# Persona Focus Group

A small group of personas discusses a topic across 2–4 rounds. After Round 1 (independent), each subsequent round shows each persona a digest of what the others said — so positions can evolve, converge, or split with peer pressure (the way real focus groups produce different dynamics than surveys).

Subagents are stateless and can't message each other directly. You (the orchestrator) are the channel between them: compile a digest each round, re-spawn personas with that digest in their prompt.

## When to use vs. alternatives

- Use `persona-focus-group` when the *group dynamic* matters — agreement amplifying, dissent emerging, ideas building.
- Use `persona-survey` for independent parallel responses without cross-talk.
- Use `persona-council` for adversarial debate specifically (sharper positions, defended).
- Use `persona-ethnographic` for one persona's narrative.

## Sample size

- **Sweet spot:** 3–6 personas, 2–4 rounds. 5×3 is the default if not specified.
- Below 3: not really a "group" — use interview or survey instead.
- Above 6: digest gets unwieldy; ask the user which 5–6 personas to include.

## Inputs

- **Topic / question** — the thing to discuss.
- **Optional asset** — copy, page, idea to react to.
- **Round count** (default 3, cap 4).
- **Persona selection** — if the user names personas, use those; otherwise default to all if ≤6, else ask the user which 5–6 to include.

## Workflow

### Phase 0 — Confirm cost

3 personas × 3 rounds = 9 subagent runs. 6 × 4 = 24. Use the cost estimator in `persona-research/references/cost-estimator.md`. Warn if above ~15 runs.

### Phase 1 — Select

If the user named personas, use exactly those. Otherwise use all if ≤6; if more than ~6 are available, ask the user which 5–6 to include — don't auto-trim the roster.

### Phase 2 — Round 1: independent reactions

Spawn one subagent per persona, all in a single message. Each prompt:
- Persona doc path.
- The topic and any asset.
- The `persona-ask` reviewer contract (references + confidence), including *Ground, think, then talk* — ground in the doc first, reason privately, then decide what you'd actually put on the table (you needn't voice everything you concluded; people in a room don't).
- The Round 1 response format below.

Round 1 response format:
```
## Grounding (private — for the orchestrator; kept out of the digest other personas see)
The persona-doc sections that bear on this, cited first: `§ <Section>: "<…>"` + a confidence read.

## Thinking (private — for the orchestrator; kept out of the digest)
Your private reasoning over that grounding: what you'd genuinely conclude, where you're thin.

## Position
2–3 sentences — the take, stated first.

## Reasoning
Why, tied to specific persona-doc sections. References inline.

## Open questions for the group
- [for: <persona-slug> | anyone] Things that would sharpen or change your position.

## Confidence
[high|medium|low] + one-line reason.
```

### Phase 3 — Round 2+ : reactive rounds

After each round, compile the **panel digest** — for each persona, their Position + condensed Reasoning + Open questions, plus question-routing (each open question routed to its addressee). Never include a persona's `Grounding` or `Thinking` — those stay with you; only what they chose to say goes in the digest.

Spawn the next round in parallel — each persona's prompt includes:
- Persona doc path, persona-ask contract.
- Their *own* previous-round response (so they can hold or move).
- The full panel digest (everyone else's positions).
- Questions routed *to them*.
- Round 2+ response format below.

Round 2+ response format:
```
## Grounding (private — for the orchestrator; kept out of the digest)
The persona-doc sections behind your stance this round: `§ <Section>: "<…>"` + a confidence read.

## Thinking (private — for the orchestrator; kept out of the digest)
Your private reasoning this round: what the others' positions actually do to your view, before you decide what to say back.

## Stance change
held | sharpened | updated | conceded | hardened — one line on what moved.

## Reaction
Direct engagement with the other personas — name them. Where you agree, say so. Where you disagree, make the objection concrete.

## Answers to questions routed to me
- [from <slug>] Answer, or "still open — would need the real customer."

## Position (current)
Restated, post-reaction.

## New open questions
Only genuinely new ones.

## Confidence
[high|medium|low] + one-line reason.
```

### Phase 4 — Convergence check

After each round, decide whether to run another. Stop when:
- No persona reported `updated`/`conceded`/`hardened` (positions stable), AND
- No open questions remain that another panelist could plausibly answer.

Hard cap: 4 rounds total. If still moving at the cap, stop and report the divergence as a finding — a persistent split is a real result.

Always run at least 2 rounds even if Round 1 looks aligned — surface agreement deserves one stress-test.

### Phase 5 — Synthesize

```
# Focus group: <topic>

## Headline
One sentence — the dominant group read after N rounds.

## Consensus
What the group actually agreed on, and how stable it is.

## Disagreements
Each unresolved split: who held what, why it didn't resolve (different priorities? different information? real values clash?). Don't paper over.

## How positions evolved
For each persona, a 2–3 line trajectory: where they started, where they ended, what moved them.

## Open questions for real humans
What the simulation couldn't settle. The real-customer research that would close it.

## Recommended action
If consensus is strong enough to act on, the action. If split, the decision criteria the user should use instead of a false verdict.
```

Close with the standard simulation disclaimer.

### Phase 6 — Render the report

Write `report.html` to `./.persona-research-runs/focus-group-<YYYY-MM-DD>-<slug>/` per the
shared spec in `skills/persona-research/references/html-report.md` — self-contained
(inline CSS/JS, data embedded, opens with a double-click): the question, method + N
caveat, the rounds and how positions moved, one card per persona with their verbatim
public answers + confidence and collapsible grounding, and the insights. Tell the user
the path.

## Notes

- Don't pre-filter for *agreement* — a panel of personas who all already agree teaches nothing. When you narrow, narrow for topic, not for agreement.
- A persona conceding a point in Round 2+ is a real finding, not a failure. Don't push back to undo it.
- Resist the urge to add more rounds when positions are stable. Diminishing returns set in fast.
