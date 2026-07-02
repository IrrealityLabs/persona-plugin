---
name: persona-roast
description: Get brutally honest, unfiltered, no-punches-pulled feedback from the personas on an idea, plan, asset, pitch, or product. Explicitly prompts personas to tear it apart — every objection they'd ordinarily soften comes out sharp. Output is a roast per persona plus the most lethal critiques synthesized. Use when the user says "/persona-roast", "roast this", "be harsh", "tear this apart", "what would the personas hate about this", "no diplomacy please", or wants the worst-case critical reception before they ship.
---

# Persona Roast

A study type designed for one purpose: surface every critique your personas would *normally* soften, hedge, or omit. The prompt explicitly licenses harshness. Output is brutal, specific, and disproportionately useful — it surfaces the objections that polite formats miss.

Critically: this is **the harshest version of each persona**, not a generic harsh persona. A polite enterprise architect persona shouldn't suddenly tweet like an X shitposter. The prompt asks for *their unsoftened honesty*, not a fake roaster voice.

## When to use vs. alternatives

- Use `persona-roast` to pressure-test before launch, find the strongest objections you've been avoiding, or stress-test a pitch by getting the worst-case reception.
- Use `persona-review` for structured, balanced asset critique (with positive findings too).
- Use `persona-council` for adversarial *deliberation* among personas (they debate each other).
- Use `persona-concept-test` for structured concept validation with scores and verdicts.

The roast is best paired with another method: roast first to find what's broken, then `persona-review` or `persona-concept-test` to evaluate the fixes.

## Sample size

- **Sweet spot:** 3–6 personas. Roast output is dense and overlapping — beyond 6, the value plateaus and the synthesis gets noisy.
- Default to all personas; if the user named some, use those. If the roster is much larger than ~5, ask the user which to include rather than auto-selecting — if narrowing is needed, suggest a diverse spread by reading the personas' docs (the thing being roasted is a useful relevance cue too).

## Inputs

- **The thing being roasted** — an idea, pitch, asset, plan, copy, product description. The more concrete the thing, the sharper the roast. Vague ideas produce vague roasts.
- **Optional framing** — what the user *thinks* is strong about it. The roast specifically attacks the user's confidence — knowing where they feel confident helps the personas aim.
- **Sensitivity floor** (optional) — if there's a topic the personas should not roast (e.g. the founder's personal credibility — only roast the product), say so. Default: no floor, everything is on the table.

## Workflow

### Phase 1 — Brief and warn

Tell the user what's about to happen:

> "Roasting <thing> with N personas. The personas will not soften or balance — every objection they have comes out sharp. Expect this to sting. The output is most useful if you read it once for the hits and once for the substance underneath."

If the thing being roasted is personal (someone's pitch, their writing, their product) and you sense the user wants validation rather than critique, ask once: "Do you actually want the harshest version, or do you want balanced feedback? I can switch to persona-review if balance would be more useful." Some people *say* they want a roast and then don't actually want it. Confirm.

### Phase 2 — Per-persona roast (parallel)

Spawn one subagent per persona. Each prompt:
- Persona doc path.
- The thing being roasted.
- The roast contract:
  > "You're being asked to give your *unsoftened* take on this. The normal review skills ask you to be balanced and constructive — this one doesn't. Specifically:
  > - **No softening.** If you'd reject it, say so flatly. No 'I love the ambition, but...' preambles.
  > - **No balance.** You don't need to find something nice to say. If nothing about this works for you, say so.
  > - **Specific, not vague.** 'This is bad' is useless. 'The opening line promises X but the body delivers Y, and that contradiction is what kills my interest' is useful.
  > - **Be the harshest version of *yourself*** — not a generic mean person. Stay in your persona's actual voice and decision-making patterns; just unfilter the criticism that would normally come out diplomatic. A polite persona being harsh sounds different from a sharp persona being harsh.
  > - **Aim at the user's confident parts**, if you can tell what those are. The roast is most useful when it punctures what the creator thinks is strong, not when it agrees with what they already worry about.
  > - **Stay on the work.** Roast the idea, the asset, the product. Don't roast the person."
- `persona-ask` reviewer contract — Ground, think, then talk (Grounding → Thinking → Talking) still applies; even a roast must be grounded.
- Sensitivity floor (if any).
- Response format below.

Response format:
```
## <persona slug>'s roast

### Grounding (private — orchestrator only)
The persona-doc sections that bear on this, cited first: § <Section>: "<…>" + a confidence read [high|medium|low|off-pattern]. Evidence before reasoning — even a roast must be grounded.

### Thinking (private — orchestrator only)
Private reasoning over that grounding: what this persona would genuinely conclude, where the evidence is thin.

### Headline
One sentence — the single most damning thing about this.

### What's actually broken
3–5 specific objections, each:
- **Quoted target:** the line / element / claim being roasted.
- **Why it fails:** unsoftened reasoning, grounded in your persona doc.
- **What it tells me about whoever made this:** the implication the persona draws.

### What you think works that doesn't
The aspect the creator probably feels confident about that this persona is unimpressed by. (Skip if not obvious.)

### What you'd need to even reconsider
The bar this would have to clear for you to take it seriously — not a polite "what to fix," a high bar.
```

### Phase 3 — Synthesize

```
# Roast: <thing, short>

## The lethal critiques
The 3–5 objections that came up across multiple personas — these are the things that would actually kill this in the wild. For each: who flagged it, the most cutting version of the objection, and (honestly) whether it's correct.

## The persona-specific kills
Per persona: the single sharpest critique they had that nobody else made. Sometimes these are the most useful — they're segment-specific objections that won't show up in generic feedback.

## What survived the roast
Anything no persona attacked, despite the no-balance prompt. This is real signal — these are the elements that hold up even when nobody's looking for things to like.

## Where personas were *forced* to roast something they didn't really hate
If any persona's roast came back at [low] confidence or felt like they were straining to be harsh, flag it. That's signal that this thing didn't actually land badly with them — they just produced output because the prompt asked them to.

## The single most actionable critique
The one objection that, if fixed, would change the most personas' reception. Often more useful than the volume of critiques — the rest may evaporate when this one is addressed.

## What to do with this
Re-read the roast in a day, not now. Half of it is noise; half of it is real. The half that still stings in 24 hours is the part to address.
```

### Phase 4 — Render the report

Write `report.html` to `./.persona-research-runs/roast-<YYYY-MM-DD>-<slug>/` per the
shared spec in `skills/persona-research/references/html-report.md` — self-contained
(inline CSS/JS, data embedded, opens with a double-click): the question, method + N
caveat, the burns grouped by target, one card per persona with their verbatim public
answers + confidence and collapsible grounding, and the insights. Tell the user the
path.

## Notes

- **The roast is not gospel.** It's calibrated to surface negative signal, which means it over-weights critique by design. Don't make decisions purely from the roast — use it to find what's broken, then evaluate fixes with a balanced method.
- **Pair with persona-review on the fixed version.** Roast → fix → review is a stronger loop than roast alone.
- **Roast-resistance is a feature.** A piece of work that survives the roast (no lethal critiques, only nits) is significantly better-tested than work that's only been balanced-reviewed.
- If the user is fragile / the work is personal, the roast can be counterproductive — that's why Phase 1 confirms intent. A user who actually wanted validation gets a worse outcome from a roast than from a balanced review.
- Don't roast a real person's character. If the thing being roasted is "Sarah's pitch", roast the pitch, not Sarah. The Phase 2 prompt enforces this but watch for it in the output and trim if needed.
