---
name: persona-interview
description: Conduct a deep 1:1 qualitative interview with a single persona — 5–10 questions with adaptive follow-ups, in the style of a real customer interview. Use when the user says "interview <persona>", "do a deep interview with <persona>", "/persona-interview <slug>", or wants narrative depth on one viewpoint rather than breadth across many.
---

# Persona Interview

A 1:1 interview with one persona: 5–10 main questions, follow-ups where the answers open something interesting, transcript-and-themes output. Default depth method when the user wants to understand *why* and *how* from a single perspective.

## When to use vs. alternatives

- Use `persona-interview` when you need depth and narrative from one viewpoint.
- Use `persona-jtbd-interview` when the specific question is about switching behavior (why they picked / abandoned something).
- Use `persona-survey` when you need structured answers across many personas.
- Use `persona-focus-group` when you want personas to react to each other.

## Sample size

One persona. If the user names more than one, run them sequentially and produce one interview per persona — don't merge transcripts.

## Inputs

- **Persona slug** — required. Resolved via the same logic as `persona-ask` Phase 1; stop if missing.
- **Topic** — what the interview is about. If unclear, ask before starting ("What are you trying to learn from this interview?").
- **Optional asset** — a page, copy, product idea to anchor the interview around.

## Workflow

### Phase 1 — Resolve persona and prepare guide

Resolve the persona (see `persona-ask`). Load `persona-ask` for the framing checklist — the same anti-leading / behavior-over-opinion principles apply per question.

Draft a **5–10 question interview guide** before asking anything. Structure:
- **Opening (1–2 Q's):** broad, low-pressure. Get them oriented to the topic in their own terms.
- **Middle (3–6 Q's):** the meat. The questions you actually care about.
- **Closing (1–2 Q's):** "What haven't I asked that I should have?" / "What's the most important thing about this you'd want me to know?"

Don't ask the guide all at once. The interview is a *dialog* — you ask, they answer, you decide what to ask next based on the answer.

### Phase 2 — Conduct (one question per subagent call)

For each question:
1. Spawn one `general-purpose` subagent. Prompt: persona doc path, the running transcript so far, the next question, the `persona-ask` reviewer contract.
2. The subagent answers as the persona, in first-person, with references + confidence (per `persona-ask`).
3. Append the answer to the transcript.
4. Decide: is the answer interesting enough to deserve a follow-up? Look for:
   - Surprising claims you didn't expect.
   - Vague answers where the persona seems to be skimming.
   - Strong reactions (positive or negative) without explanation.
   - References to things you don't fully understand.
5. If yes, draft a follow-up and loop. Cap follow-ups at 2 per main question — beyond that the conversation drifts.

A typical interview = 5–10 main questions × 0–2 follow-ups = 8–20 subagent calls.

### Phase 3 — Synthesize

Produce two artifacts:

**Transcript** — the full Q&A in order. Keep it readable; this is the source-of-truth for the insights.

**Insight summary** — structured:
```
## Headline insight
One sentence — the single most important thing you learned.

## Themes (3–5)
For each: a name, 2–3 sentences describing the pattern, and the question-numbers it came from.

## Surprises
What was different from what you (or the user) would have predicted, with the relevant quote.

## What this persona would want next
Their stated or implied "what would actually move me" — if it came up.

## Open questions
What this interview *didn't* answer that would matter. Candidates for a follow-up interview, a different method, or a real-user interview.

## References & confidence rollup
Aggregate: where were answers [high] confidence (well-supported by the doc) vs [low]? If the persona was extrapolating a lot, the whole interview should be treated as directional.
```

Close with the standard simulation disclaimer.

## Notes

- A persona interview is not a transcript-of-a-real-conversation — there's no rapport, no body language, no ums. The persona is reasoning from a static doc, not remembering. The methodology gets you *substantive* depth, not *experiential* depth.
- If an answer comes back at `[low]` confidence on something the user really wanted to learn, surface that explicitly in the summary — "the persona doc is silent on X; we got a best-guess but it should be validated with a real customer."
- If the user wants more breadth, suggest running the same interview guide as a `persona-survey` against the rest of the personas. That's a natural escalation path.
