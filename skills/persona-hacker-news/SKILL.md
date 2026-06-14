---
name: persona-hacker-news
description: Simulate a Hacker News comment thread from your personas — submit a title and link/post, have each persona post a top-level comment in the HN voice (technical, opinionated, often skeptical), then optionally simulate one round of replies. Outputs an HN-style threaded transcript plus an analysis of where the thread would have gone. Use when the user says "/persona-hacker-news", "simulate Hacker News on this", "what would HN say about this", "post this to fake HN", or wants the specific dynamics of a technical / skeptical / contrarian comment thread.
---

# Persona Hacker News

Simulate an HN thread: a submission, top-level comments from each persona, optionally a round of replies. The personas adopt HN comment conventions — technical, skeptical-by-default, often pedantic, willing to challenge premises and the title itself — *to the extent their persona doc supports it*. Non-technical personas comment as themselves; the simulation is "what would the HN front-page reaction look like if these specific personas all happened to see this," not "make every persona sound like a stereotypical HN commenter."

## When to use vs. alternatives

- Use `persona-hacker-news` to pressure-test a technical post, product launch, or contrarian take in HN's specific voice and dynamics.
- Use `persona-social-listening` for organic mention across platforms.
- Use `persona-council` for adversarial deliberation among the personas themselves.
- Use `persona-focus-group` for a less adversarial group-discussion dynamic.

## Sample size

- **Sweet spot:** 5–10 personas for top-level comments; reply round multiplies cost.
- Default to all personas; if the user named some, use those. If the roster is much larger than ~8, ask the user which to include rather than auto-selecting (the submission topic is a useful relevance cue for what to suggest).

## Inputs

- **Submission** — the title + the URL/content the personas are reacting to. Could be a blog post, a Show HN, a product launch, a contrarian essay, a paper. The personas need enough to react to — paste the content if behind a paywall.
- **Submission type** (optional) — Show HN / Ask HN / regular link. Affects comment patterns.
- **Reply round** (optional, default off) — whether to simulate one round of replies (each persona replies to one other persona's comment). On = 2× cost.

## Workflow

### Phase 1 — Fetch and frame the submission

Read the link contents yourself (don't make each persona fetch). Compose the submission as it would appear on HN: title + a 1–2 sentence summary + the full content as context.

If the user pasted content directly, use that. If it's a URL, fetch and summarize for inline use.

### Phase 2 — Top-level comments (parallel)

Spawn one subagent per persona. Each prompt:
- Persona doc path.
- The submission (title + content).
- HN comment conventions briefing:
  > "This is a Hacker News comment thread. Write your top-level comment the way you specifically would post it. HN comment norms — to apply *only* where they fit your persona's actual voice:
  > - Lead with the substantive take, not pleasantries.
  > - It's normal to challenge the premise or title.
  > - Anecdotes from your own experience are valued ('I worked on a similar system...').
  > - Pedantry, technical correction, and 'well actually' are common — but only if the persona is technical.
  > - Asking a sharper question instead of asserting an opinion is also a valid comment.
  > - 1 short paragraph to 3 paragraphs. Don't bullet-list unless you really would. No emoji."
- Important: "If your persona is non-technical or wouldn't actually be on HN, comment as yourself — don't try to fake technical voice. The output is more useful if some commenters are clearly outside HN's typical audience."
- `persona-ask` reviewer contract.
- HN comment response format below.

HN comment response format:
```
## <persona slug>
<the comment, formatted as it would appear>

---
**References (persona doc):**
  - § <Section>: "<quote>"
**Confidence:** [high|medium|low] + one-line reason.
**HN-voice fit:** [strong|partial|forced] — whether this persona would credibly post on HN as themselves. Forced = the simulation pushed them into voice that doesn't match their doc.
```

### Phase 3 — Reply round (optional)

If reply round is on:

For each persona, identify the comment they'd most likely reply to (the orchestrator picks — usually the one most directly relevant to the persona's stated positions, or the one most provocative). Spawn one subagent per persona, prompt:
- Persona doc path.
- The original submission.
- The full top-level thread (all personas' top-level comments).
- The specific comment they're replying to.
- Instruction: "Write one reply. Could be agreement, disagreement, expansion, a sharper question. Same HN-voice guidance as before. Keep it shorter than a top-level comment — replies on HN are typically tighter."

Replies are appended to the thread under their target.

### Phase 4 — Synthesize

```
# HN simulation: "<title>"

## Submission
<title + 2-sentence summary of content>

## Thread
Render as a flat HN-style thread:

<persona-slug-1> | comment text
  ↳ <persona-slug-3> reply text
<persona-slug-2> | comment text
...

## Predicted thread shape
- **Overall tone:** rallying / mixed / hostile / pedantic / dismissive — one sentence.
- **Top sub-threads:** which comments would attract the most replies on real HN, and why (substance / provocation / vulnerability).
- **Likely top-voted comment:** the one most likely to rise to the top, with reasoning. HN votes for: substantive technical content, well-reasoned dissent, sharp/witty observations, useful anecdotes.
- **Likely downvoted:** comments that would draw flags or "this isn't what HN is for" replies, if any.

## What HN would do to the submission
Did the comments converge on what the *post itself* was about, or did they go meta (debating the title, the premise, the existence of the topic)? "HN derails by tangent" is a common pattern; surface it if it happened.

## Persona-by-persona fit
For each persona: did the HN-voice constraint distort their input? Personas marked `forced` on HN-voice fit had their reactions diluted — discount their feedback in your interpretation.

## Useful signal
Strip away the HN performance — what substantive critiques came up that you'd want to address regardless of whether you're actually posting to HN? Those are the takeaway. The HN-voice wrapping is the cosmetic; the underlying objections are the real findings.
```

## Notes

- Real HN comments are written by a self-selected audience that skews technical, contrarian, and male. Your persona panel may not match that demographic — that's a *feature* of this simulation, not a bug. Use it to ask "what would HN find that my actual audience would miss?" and vice versa.
- Personas marked `forced` HN-voice fit are giving you contaminated signal in that comment but useful signal in the meta-question: "would this content even reach this persona via HN?" If most personas were `forced`, your audience isn't really an HN audience — flag this and recommend social-listening on a more apt platform instead.
- Don't run this method to validate that "HN will love your post." HN's reception is high-variance and substantially driven by timing, hooks, and who happens to be on the homepage at submission time — variables this simulation doesn't model. Use it for *substantive* feedback shaped by HN-style critique norms.
