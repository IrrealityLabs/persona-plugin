---
name: persona-diary-study
description: Run a diary study with a persona — they "log" observations across multiple simulated days, capturing the temporal pattern of how a behavior, decision, or product use unfolds over time rather than a single snapshot. Use when the user says "/persona-diary-study", "run a diary study", "track <persona>'s behavior over time", "what does a week of <persona>'s decisions look like", or wants longitudinal signal rather than point-in-time reaction.
---

# Persona Diary Study

The persona logs observations across N simulated days (typically 7), each entry capturing what happened, what they thought, what they did differently than yesterday. Output is a temporal narrative — how a behavior, decision, or product use *evolves over time*.

This is the persona equivalent of a real diary study, where real participants log their behavior on a recurring basis. Real diary studies surface things one-time interviews miss: gradual habit formation, repeated friction at the same point, behaviors people don't realize they have until they see them written down.

## When to use vs. alternatives

- Use `persona-diary-study` when the question is *temporal* — how something unfolds, repeats, or evolves over days/weeks.
- Use `persona-ethnographic` for a single deep narrative on one day or workflow.
- Use `persona-interview` for cross-sectional Q&A.
- Use `persona-jtbd-interview` for reconstructing one past decision moment.

## Sample size

- **Sweet spot:** 1–3 personas, 5–14 days each. Diary studies generate dense per-persona content; comparing across many personas is hard.
- Default: 1 persona × 7 days = 7 subagent runs.

## Inputs

- **Persona slug** — required (one at a time; if multiple, run sequentially).
- **Topic / focus** — what they're "logging." e.g. "your daily interactions with your CRM tool" / "how you handle email each day" / "how you decide what to work on each morning."
- **Day count** — default 7. Cap at 14.
- **Optional trigger event** — something the user wants to "happen" mid-study (e.g. "on day 4, you switch to a new tool — log what happens after"). Useful for studying transitions.

## Workflow

### Phase 1 — Set up the diary frame

Build a brief one-paragraph framing for the persona that they'll see at the start of every day's entry: who they are, what they're logging, what level of detail is expected.

### Phase 2 — Sequential daily entries

For each day from 1 to N:

Spawn one subagent (sequential, not parallel — each day builds on prior days). Each prompt:
- Persona doc path.
- The diary frame (constant).
- **All prior days' entries**, in order. The persona "remembers" their week.
- Today's day number, and any trigger events occurring today.
- Instruction: "Write your diary entry for day N. Cover: what happened today (specific to the topic), how it felt, what (if anything) you did differently than recent days, any patterns you're noticing in yourself. Aim for ~200 words. First-person."
- `persona-ask` reviewer contract.
- Diary entry response format below.

Diary entry response format:
```
## Day N
*(Day-of-week if helpful for context.)*

### What happened
2–4 sentences on the day's relevant events, in narrative form.

### How it felt
1–2 sentences on emotional / motivational state.

### What I did differently than recent days
Either: a specific change, or "same as the last few days" with a one-line note on whether that's good or bad.

### Patterns I'm noticing
What's becoming a habit, what's recurring as friction, what I keep forgetting / avoiding. Skip on day 1 (no patterns yet).

### References & confidence
**References (persona doc):** § <Section>: "..."
**Confidence:** [high|medium|low] + one-line reason.
```

### Phase 3 — Synthesize across days

After all days are logged:

```
# Diary study: <persona> × <topic>, <N> days

## Headline
One sentence — the dominant pattern across the week.

## Day-by-day arc
Brief (2–3 lines per day) of what happened and how the persona was tracking.

## Patterns that emerged
Things that recurred but the persona didn't notice on day 1:
- Habits forming (with the day they first appeared)
- Friction that kept happening at the same point
- Workarounds the persona started adopting

## Trajectory
Is the persona's relationship with this thing getting better, worse, or flat across the week? Evidence.

## Trigger event response (if any)
If a trigger event was injected, how the persona responded and how long the effect lasted.

## Implications
2–4 takeaways for the user's question — what this temporal pattern says about how to design / market / support around this persona's behavior.

## Confidence
A diary study from a persona simulation is *more* prone to monotony than a real one — the persona may write similar entries day after day if not prompted by changing context. Note if entries felt forced or repetitive; weight low.
```

## Notes

- **Sequential, not parallel.** Each day reads prior days. This costs more in tokens (each day's prompt carries growing context) and runs slower than parallel methods, but the temporal coherence requires it.
- **Inject variation if days feel monotonous.** Real diaries have interruptions — a sick day, a deadline, a weekend. If the persona's day 4 entry looks like a near-duplicate of day 3, prompt day 5 with a mild variation ("today is a slower day" / "you missed yesterday because of a deadline — what's happening today?").
- The most useful diary-study output is usually **what changed without the persona noticing** — surface this explicitly. If the persona reports "same as yesterday" but their stated frustration intensity quietly climbed across days, that's the signal.
- For long studies (10+ days), consider running half the days, reviewing, then deciding whether to continue. Diary studies have a soft plateau where additional days stop adding insight.
