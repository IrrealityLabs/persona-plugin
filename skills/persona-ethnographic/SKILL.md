---
name: persona-ethnographic
description: Run an ethnographic-style narrative study with a persona — ask them to walk through a typical day, a complete workflow, or how they currently solve a problem end-to-end. Derive insights from the narrative, including pain points, workarounds, and unmet needs the persona might not state directly. Use when the user says "/persona-ethnographic", "walk me through <persona>'s day", "how does <persona> currently do X", "ethnographic study", or wants the *whole narrative* rather than answers to specific questions.
---

# Persona Ethnographic

The persona narrates a complete experience — a typical day, a current workflow end-to-end, the way they actually solve a problem today. You probe and analyze. Output is a narrative + insight extraction (pain points, workarounds, unmet needs, opportunities).

This is the persona equivalent of contextual inquiry / field research — you're trying to understand the *context* a product would slot into, not just what the persona thinks of the product.

## When to use vs. alternatives

- Use `persona-ethnographic` when you want context — the full picture around the problem, including what they *don't* say is a problem.
- Use `persona-interview` for structured Q&A on a defined topic.
- Use `persona-jtbd-interview` to reconstruct a specific past decision.
- Use `persona-diary-study` for time-extended narratives across multiple sessions.

## Sample size

- **Sweet spot:** 1–3 personas. Run sequentially. Three is the practical upper bound — ethnographic output is dense and hard to compare across many personas.
- One persona is fine if the goal is depth on one specific context.

## Inputs

- **Persona slug(s)** — required.
- **The activity / context to walk through** — be specific. "Tell me about your day" is too open; "walk me through how you currently handle customer support tickets from first ping to resolution" focuses the narrative usefully.
- **Optional adjacent context** — what the user is trying to build / understand, so you can probe in the right direction without leading the persona.

## Workflow

For each persona, sequentially:

### Phase 1 — Set up the narrative

Spawn one subagent. Prompt:
- Persona doc path.
- The activity to narrate, framed as an invitation: "I want to understand how you actually do <activity> today, in detail. Walk me through it as if you were narrating to a friend who's never seen you do this — start from the trigger that puts you in the activity, end when you'd consider it 'done.' Include the boring parts."
- The Ground, think, then talk (Grounding → Thinking → Talking) contract from `persona-ask`.
- Format: **each narrative turn (the initial narrative and every probe response) leads with two private fields, before the prose:**
  - **Grounding:** (private) The persona-doc sections that bear on this, cited first: `§ <Section>: "<…>"` + a confidence read [high|medium|low|off-pattern].
  - **Thinking:** (private) Private reasoning over that grounding: what this persona would genuinely conclude, where the evidence is thin.
  - Then the prose narrative, broken into stages ("Talking").

  Grounding + Thinking lead **every** turn, not just the initial narrative. They're the audit trail — orchestrator-only, kept out of the narrative summary/synthesis; only the prose narrative is public.

Get back the initial narrative. Expect 400–1000 words of structured story.

### Phase 2 — Probe for depth

Read the narrative. Identify 3–5 places where you'd want a real ethnographer to ask a follow-up:

- **Workarounds.** "You mentioned exporting to a spreadsheet — why that step? What would happen if you skipped it?"
- **Pain points the persona breezed past.** "You said 'and then I just deal with the backlog' — what does 'deal with' mean in practice?"
- **Tools used.** "When you said you 'check email,' what's your actual flow — inbox-zero? Triage by sender? Mobile or desktop?"
- **Decisions and judgment calls.** "How do you decide which tickets go to the engineering team vs. solving them yourself?"
- **Friction signals.** "You sighed in the narration where you mentioned the daily report — what specifically about that part is annoying?"

Spawn follow-up subagents (1–3 follow-ups per persona; resist more — narrative fatigue is real). Each follow-up carries the running narrative + previous probes into context.

### Phase 3 — Insight extraction

After the narrative + probes are complete, spawn one final subagent (still as the persona) with the full transcript:

> "Looking back at everything you described, reflect on:
> (a) What's the single most frustrating part of how you do this today?
> (b) If you could wave a wand and change one part, what would it be?
> (c) What's a workaround you've built that you wish you didn't need?
> (d) What's something you do that you don't even think of as a 'task' anymore but probably should?"

These reflection questions surface insights the in-narration persona often misses.

### Phase 4 — Synthesize (you, the orchestrator)

Per persona, then across personas if multiple:

```
# Ethnographic study: <activity>

## Narrative summary
A 3–5 sentence summary of the workflow the persona described, in their own terms.

## Stages
For each major stage in the narrative: name, what happens, the persona's tools / decisions / state of mind.

## Pain points (ranked by intensity)
For each: where in the flow it occurs, why it hurts, the persona's quoted reaction. Rank by how much friction the persona signaled.

## Workarounds
Things the persona does that exist *only* to compensate for a missing capability somewhere. These are gold for product opportunities — workarounds are unmet-need signal.

## Tools and stack
Everything the persona mentioned using, plus how they use it. Useful for ecosystem / integration thinking.

## Unmet needs
What the persona didn't say outright but the narrative implies. Frame as opportunities for design / product, with the supporting evidence from the narrative.

## Insights for <user's adjacent question>
If the user named what they're trying to build / understand, frame the takeaways for that — without forcing fit. If the narrative doesn't support a clean insight on that, say so.

## Confidence rollup
Aggregate from the per-turn Grounding fields: where in the narrative the persona was [high] confident vs. [low]. Low-confidence stretches are extrapolation from the persona doc and should be weighted accordingly.
```

The per-turn Grounding and Thinking fields are audit material, not narrative content — synthesize only the prose narrative into the sections above; the confidence rollup is the one place the grounding feeds the write-up.

If multiple personas, add a cross-persona section: where their workflows converge, where they diverge, what the divergence implies about audience segmentation.

## Notes

- Ethnographic narrative from a persona simulation is *less* reliable than from a real human ethnographic session. Personas extrapolate from their doc; they don't have lived experience. Mark the output as inherently directional — best for surfacing *hypotheses* about pain and opportunity, which you then validate with real customers.
- The single highest-value output of an ethnographic study is usually the **workarounds**. If the persona didn't surface any, your probes probably weren't sharp enough — try one more pass focused specifically on "what do you do that you wish you didn't have to?"
- Don't conflate "they didn't mention X" with "X doesn't matter to them." Persona docs have gaps; the narrative reflects those gaps. Note silence as a Known Gap, not evidence of irrelevance.
