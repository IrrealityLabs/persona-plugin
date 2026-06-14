---
name: persona-jtbd-interview
description: Run a Jobs-to-be-Done switch interview with a persona — reconstruct the moment they hired (or fired) a product, the forces pushing them, and the anxieties holding them back. Use when the user says "JTBD interview <persona>", "/persona-jtbd-interview <slug>", "run a switch interview", or wants the Bob Moesta–style timeline of a purchase decision rather than open-ended exploration.
---

# Persona JTBD Interview

A structured Jobs-to-be-Done "switch interview" with one persona: walks back through a specific past hire-or-fire decision, mapping the four forces (push, pull, anxiety, habit) and the timeline from first thought to first use. More structured than a generic `persona-interview`; narrower in goal.

## When to use vs. alternatives

- Use `persona-jtbd-interview` when you want to understand *what triggers switching* for this segment — pricing pages, competitor positioning, churn-prevention design.
- Use `persona-interview` for open-ended depth on any topic.
- Use `persona-ethnographic` to walk through a typical day/workflow, not a specific decision.

## Sample size

1–3 personas, run sequentially. Three is the sweet spot — patterns across three switches teach more than one switch alone, but it's still a depth method, not a survey.

## Inputs

- **Persona slug(s)** — required.
- **The product or category** to interview them about. If the persona doc mentions specific products they've used or considered, anchor to one of those.
- **Hire or fire?** — interviewing about adopting something (hire) or abandoning something (fire). Default: hire.

## Workflow

For each persona, sequentially. Every persona subagent answers under the Ground, think, then talk (Grounding → Thinking → Talking) contract from `persona-ask`: **each turn leads with two private fields, before the spoken answer:**

- **Grounding:** (private) The persona-doc sections that bear on this, cited first: `§ <Section>: "<…>"` + a confidence read [high|medium|low|off-pattern].
- **Thinking:** (private) Private reasoning over that grounding: what this persona would genuinely conclude, where the evidence is thin.
- Then the spoken first-person answer ("Talking").

Grounding + Thinking lead **every** timeline stage and force turn, not just the first. They're the audit trail — orchestrator-only, kept out of the synthesis; only the spoken answers are clustered into the four-force map.

### Phase 1 — Establish the moment

Ask the persona to recall a specific instance of hiring (or firing) something in this category. Push for *specificity* — a real moment, not a generalization. If the persona doc doesn't ground a specific instance, work with the persona to construct a plausible one based on their stated context.

### Phase 2 — Map the timeline (the core of the method)

Walk backwards from the switch through five timeline stages, one subagent call per stage (carrying running transcript forward):

1. **First thought.** "When did you *first* notice the problem you eventually hired this product to solve? What was happening?" — the trigger moment, often earlier than people initially say.
2. **Passive looking.** "What did you do between first thought and actively shopping? Did you Google? Ask peers? Notice ads? How long was this period?"
3. **Active looking.** "When did you start seriously evaluating options? What changed? What did you do — make a shortlist, demo, ask for quotes?"
4. **Decision.** "What pushed you to pick *this* one? What were the final-3 alternatives and why didn't you pick them?"
5. **First use.** "What was the first time you actually used it like? What worked, what was harder than expected, when did you know it was 'in'?"

### Phase 3 — Map the four forces

One subagent call: ask the persona to enumerate, with the timeline as context:

- **Push of the current situation:** what about the status quo was making them uncomfortable enough to look?
- **Pull of the new solution:** what specifically attracted them to the chosen option?
- **Anxiety of the new solution:** what almost made them not switch? What were they worried about?
- **Habit of the present:** what about inertia / sunk-cost / familiarity pulled them to stay where they were?

### Phase 4 — Synthesize (after all personas)

If multiple personas, look for patterns across switches:

```
## Headline switch dynamic
One sentence — the dominant force balance for this segment.

## Timeline patterns
Where does the timeline cluster? (e.g., "all three said first-thought was 3+ months before action — your nurture content needs to find them then.")

## Four-force map
For each force, the strongest specific claims across personas — with persona attributions.

## Implications
2–4 concrete things this changes about how you'd market / price / onboard.

## What an actual customer interview should confirm
The 2–3 patterns that would meaningfully change strategy if confirmed against real customers. Personas can't replace this.
```

## Notes

- Personas reconstructing a past decision are *less* reliable than personas reacting to a present asset — they're inferring a memory they don't have. Mark JTBD interview findings as inherently more directional than other persona-research outputs.
- If a persona's stated decision contradicts their persona doc (e.g., a "skeptical CTO" persona ends up describing themselves as an early-adopter switcher), don't smooth the contradiction — flag it. Either the doc is wrong or the methodology pushed them somewhere unrealistic.
