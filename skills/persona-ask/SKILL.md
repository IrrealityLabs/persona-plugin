---
name: persona-ask
description: Ask a single persona a question and get their grounded, referenced response. Use when the user says "ask <name>", "what would <name> think", "get <name>'s take", "what would <name> say about this", "/persona-ask <name>", or otherwise wants one specific persona's perspective on a question, idea, or asset. Resolves the persona slug against ./.personas/ first — stops and points to persona-distill / persona-create if the named persona doesn't exist. Also loaded internally by the persona-review panel subagents for question-framing and response-shape best practices.
---

# Persona Ask

Two modes:

- **Direct invocation** — the user named a persona ("ask sarah-chen what she thinks of this pricing page", "what would skeptical-cto say about this CTA?"). Follow Phases 1–3 below.
- **Internal load by persona-review / persona-research family** — a panel or research subagent loads this skill to apply the *Framing the question* and *Shaping the response* sections below. Such a subagent already has the persona resolved by the caller and skips Phases 1–3.

## Tallying responses (when the question is votable / rateable)

When the question being asked is structured for aggregation — voting, rating on a scale, ranking, picking from options — the synthesis should include a **tally**, not just narrative summaries. Detect the question type and apply the right aggregation:

- **Vote / pick** ("which one would you choose?"): tally counts per option, plus the dominant rationale per option. Show as a ranked list with vote counts and percentages.
- **Likert / scale** ("rate 1–7"): report distribution, mean, median. Show as a monospace bar chart (`▓▓▓▓░░░░░░ 4/10`).
- **Yes/no** ("would you do X?"): tally yes / no / unsure. Surface the unsures with their conditions.
- **Ranking** ("order these by importance"): for each item, the panel-average rank. Plus the items with highest variance (where personas disagreed most about rank).
- **Open-ended where themes can be clustered** ("why?"): cluster responses into 2–5 themes, count personas per theme.

**Confidence-weighting:** when personas attached different confidence levels to their answers, compute a confidence-weighted view alongside the raw tally. Treat `[high]` as weight 1.0, `[medium]` as 0.66, `[low]` as 0.33. If the weighted tally meaningfully differs from raw, surface both. Otherwise just show raw.

**Detect tally-eligible questions automatically:**
- If the question contains "rate", "score", "1–7", "1 to 10", "scale", "pick", "choose", "vote", "rank", "order", or presents N options to select from — auto-tally.
- If the question is "what do you think about X?" — open-ended, theme-cluster (still a tally-style aggregation, just thematic rather than numeric).
- If unsure, ask the user once: "Should I structure responses for tally (vote/rate) or narrative (qualitative)?"

**Always include a sample-size caveat:** "N=<N> personas. <Sample-size meaning at this N for the question type>." A vote of 3-to-2 across 5 personas is not the same as 60-to-40 across 1000 humans; the synthesis says so.

**The tally is part of the synthesis, not a replacement for it.** Even with a clean vote tally, include the references-and-confidence narrative for the top votes and the dissenters — *why* personas voted the way they did is usually more actionable than the count.

## Defaults (and when they're overridden)

- **One question per turn.** Even when you'd like to ask several, ask one cleanly, get the answer, then decide if a follow-up is warranted. Bundled multi-part questions consistently produce shallower answers.
- **Max five personas per direct invocation.** If the user names more than five in a single ask, pick the five most relevant to the question and tell the user which you picked and why (or ask which to drop). Direct asks past five become hard to synthesize and start to overlap with `persona-research` territory. If the user wants *many* personas merged into a single combined answer, that's `persona-of-thought`, not a direct ask.
- **Both defaults are overridden** when a `persona-research` child skill calls into this one — those skills declare their own sample size and question structure per methodology (e.g., a survey hits all personas with a fixed question set; Van Westendorp asks four questions per persona).
- **The user can override either default explicitly** ("ask all eight of them", "ask three questions in a row, I want a quick triage").

The whole skill is in service of one principle: **bad framing produces bad data, and the personas can't save you.** A persona simulation will be agreeable, confirming, and surface-level if the question lets it be. Tight framing — and ruthless grounding in the persona doc — forces a substantive answer.

## Phase 1 — Resolve the persona

The user names a persona. Match the name against the files in the persona store — `$PERSONA_HOME` if that env var is set, otherwise `./.personas/` relative to the cwd (resolve it this way everywhere the store is referenced below):

- Strip a leading `@` if present and lowercase the input. Compare against each `*.md` filename (with and without the `.md` suffix). Case-insensitive.
- Also try matching against the `name:` field in each file's frontmatter and the `description:` field for soft matches (e.g., user says "the cto" → `description` containing "CTO").
- If exactly one persona matches, that's the target.
- If multiple personas could match (e.g., user said "the cto" and there are two CTO personas), list the candidates and ask the user which.

**If no persona matches:** stop. Do not improvise — the value of this skill is that it answers as a *specific, defined* persona, not as Claude's best guess at what someone with that name might think.

Tell the user:
- The persona name they asked for isn't in `./.personas/`.
- List the personas that *are* available (filename slugs).
- Offer two paths to add one:
  - `persona-distill` if the target is a real person or has a public footprint to ground in (Slack messages, X posts, web research).
  - `persona-create` if the user wants to define the persona themselves through a short interview.

If `./.personas/` doesn't exist at all, say the same thing — there are no personas yet, point at both skills.

## Phase 2 — Load and inhabit the persona

Read the resolved persona file in full before doing anything else. Persona docs cover four dimensions plus a language sample — internalize all of it, weighting these for response generation:

- `## At a glance` — sets the dominant frame.
- `## Psychographics` — values, beliefs, fears. The highest-leverage section for *why* the persona would react a given way.
- `## Behavioral` — what they actually do, including JTBD, tools they've tried, decision-making mode. The strongest grounding for reactions tied to product evaluation.
- `## Contextual` — the situation and constraints they're operating in. Determines what's relevant to surface.
- `## What makes them bounce` — highest-signal section for negative reactions.
- `## What would actually convince them` — highest-signal section for positive reactions.
- `## How they actually talk` — verbatim phrases and language patterns. Use these to ground *how* the response sounds — register, vocabulary, the way they frame things. This is real style signal; lean on it. The only thing off-limits is inventing voice *beyond* what's here.
- `## Examples` — **the strongest grounding there is.** Real `{context, question, answer}` turns showing how this person *actually* responded to real prompts. When the question resembles one of these, let the matching example drive your substance, stance, level of detail, *and* phrasing — and cite it. These are observed ground truth, so they outrank the synthesized sections above when they conflict. Match what they'd say and decide *and how they'd say it* — sourced from the example, never a fabricated accent or catchphrase.
- `## Demographics` — context, lighter weight.
- `## Known gaps` — what you should *not* fabricate a position on.

Note the frontmatter `last_distilled_at` and `sources`. If the doc is many months old or distilled from a thin source, mention it briefly in the references section — older or thinner-sourced personas warrant more humility in the answer.

## Phase 3 — Frame the question and respond

Frame the user's question using the *Framing the question* checklist below — even direct asks benefit from quick reframing to elicit substance over agreement.

Then answer in the format from *Shaping the response* below. A single-persona ask uses the same per-finding format that persona-review uses — the difference is you produce one focused response, not a panel.

Default response structure for direct asks:

```
## <Persona display name>'s take

### Grounding
The persona-doc material this answer rests on, pulled first:
  - § <Section>: "<short quote or paraphrase>"
  - § <Section>: "<...>"
**Confidence:** [high|medium|low|off-pattern] — one line on how strong that support is.

### Thinking
2–4 lines of private reasoning over the grounding — what they'd genuinely conclude, where the evidence is thin. The audit trail behind the answer; in a panel it stays with the orchestrator, out of what other personas see.

### Talking
**At a glance:** two sentences max — the headline reaction.

"First-person quoted reaction from the persona — the substantive answer to the user's question."

### Follow-ups the persona would have
- Specific questions the persona would ask the user before committing, if any.
```

Close with a one-line disclaimer:

> _— Simulated <persona display name>, distilled from <sources>, last refreshed <last_distilled_at>. Substance-focused simulation, not the real person. Verify load-bearing claims before acting on them._

If the user asked a multi-part question, give one response per part rather than one merged response — each gets its own Grounding block.

## Framing the question (moderator-side)

### Quoted vs. unquoted: when to reframe vs. ask verbatim

The user's framing intent is signaled by quotation:

- **Quoted question** (e.g. `ask sarah "what would make you pay more for this?"`): **ask it verbatim**. The user has done the framing themselves and wants the persona to react to *exactly* that wording. Do not "improve" it, even if the framing checklist below would flag it. If the question is genuinely leading or double-barreled, you may add one short note alongside the response — "the framing was leading; the answer reflects that" — but the question itself stays as-given.
- **Unquoted question or research goal** (e.g. `ask sarah what would make her pay more` or `find out from sarah whether pricing is a blocker`): **you have license to reframe**. Apply the checklist below, draft a sharper version of the question, and use that. Tell the user the reframed version you used so they can audit it.

When in doubt — the user passed loose phrasing without quotes — reframe. The whole reason this skill exists is to elicit substantive answers; unquoted requests are an invitation to do that work.

### Framing checklist

Before you pass a question to the panel, run it through this checklist. Reframe until every check passes.

### 1. Is it leading?

A leading question presupposes the conclusion. The persona will trip on the presupposition rather than evaluate the asset.

| Bad | Better |
|---|---|
| "Doesn't this headline really capture the value prop?" | "When you read the headline, what's the first thing you understand the product does?" |
| "Would this convince you to buy?" | "Walk me through your reaction reading this — where does your attention go, where do you bounce?" |
| "How great is the pricing page?" | "If you landed on this pricing page, what's your next action?" |

### 2. Is it double-barreled?

Two questions in one produce a muddled answer to both. Split them.

> "Is the headline clear and would you click the CTA?" → ask in two passes, or focus on one ("Is the headline clear?") and let the persona surface the CTA reaction naturally if it matters to them.

### 3. Does it ask for behavior, not opinion?

"Do you like this?" is the weakest possible question. People (and persona simulations) are bad at predicting whether they'll like something but much better at describing what they'd *do*.

| Opinion (weak) | Behavior (strong) |
|---|---|
| "Do you like this landing page?" | "What's the first thing you'd click? When would you leave?" |
| "Is this messaging compelling?" | "If you forwarded this to a peer, what would you say in the message?" |
| "Does the pricing feel fair?" | "At this price, what would you need to be sure of before pulling out a credit card?" |

### 4. Is it specific to *this* asset?

A generic question gets a generic answer. Anchor the question to the actual asset.

> Bad: "What do you think of B2B landing pages like this?"
> Better: "The headline is 'Stop fighting your spreadsheet.' What does that make you think this product does, and how does that compare to what you'd actually want from a tool in this space?"

### 5. Does it leave room for "this doesn't apply to me"?

If the asset is for a different audience than this persona, you want the persona to *say so clearly* — not contort itself into being a target customer it isn't. Explicitly invite that as a valid response:

> "If this asset is aimed at a different customer than you, say so plainly — that's a real finding."

### 6. Does it permit pushback?

Personas (and simulations of them) drift toward agreement when permission to disagree isn't explicit. Add a one-liner:

> "Push back where your real reaction is negative — sandbagging the critique to seem agreeable wastes the review."

## Default question template

When in doubt, use this. It's deliberately broad but it bakes in all six checks:

> "Read this <asset type> as you would normally — at your normal speed, with your normal attention. Then tell me:
> (a) what you think it's offering,
> (b) what you'd do next (click, leave, skim more, share),
> (c) the specific places (quote them) where you reacted strongly — positive or negative — and why,
> (d) the single thing that, if changed, would most move your reaction.
> If this asset is for a different customer than you, say so plainly."

If the user gave you a narrower question ("does the pricing feel fair?"), use that as the *focus* but keep (b) and (c) — concrete behavior and specific quotes — in the prompt regardless. Those are what make the answer reviewable.

## Shaping the response (persona subagent–side)

When you, as a persona subagent, write your response, enforce these rules on yourself. The core discipline is **references and confidence**: every reaction must trace back to the persona doc, and every reaction must carry an honest confidence level so the moderator can weight findings in synthesis.

### Ground, think, then talk

Your response has three parts, in this order, and you return **all three**, clearly labelled so the orchestrator can split them:

1. **Grounding** — *first, before you form any view.* Pull the specific persona-doc material that bears on the question: cite each relevant section with a short quote or paraphrase (`§ <Section>: "<…>"`), and read how strong that support is — `[high|medium|low|off-pattern]`. Grounding-first is the point: anchor to what the doc actually says before reasoning, so the opinion comes from evidence, not vibes. If you can't ground it, say so — don't manufacture a position.
2. **Thinking** — your private reasoning *over that grounding*: what this person would genuinely conclude from it (not the agreeable take), and where the evidence is thin enough to cap your confidence.
3. **Talking** — your public answer: the first-person quoted reaction, in the format below.

**Grounding + Thinking are the audit trail** — they go to the orchestrator and, in a group, stay out of the digest other personas see; a loop reads them to know *why*. Only **Talking** is public, and what you put there is a choice: you needn't voice everything you concluded, because people in a room don't.

### The reaction is a quote; the persona doc is the receipt

Every finding has two parts that must be visually distinct in your output:

1. **The reaction itself, written as a first-person quote.** Wrap it in quotation marks. This is the persona "speaking" — short, direct, and in their decision-making voice (not their stylistic voice). Example: `"The pricing page hides the actual numbers behind 'Contact us' — I'm out. I've never once had a good experience with a vendor that does this."`

2. **References underneath, pointing to the persona doc.** Cite the section(s) of the persona doc that back the reaction, with a short quote or paraphrase of the relevant line. Format: `§ <Section>: "<short quote or paraphrase>"`. A reaction with no reference is a hallucination; reject it from your own response before submitting.

If multiple sections of the doc converge on the same reaction, cite all of them — convergence is what makes a finding load-bearing.

### Confidence label on every finding

Every finding gets a one-word confidence tag plus a short reason:

- **[high]** — the persona doc directly addresses this. The reaction maps to a specific item in a list ("Stock photos of diverse smiling teams" appears verbatim in the bounce list and the asset has one) or to a clearly stated position. The persona, if asked, would almost certainly say this.
- **[medium]** — extrapolated from related material in the doc. The doc doesn't address this specific asset element, but the persona's stated patterns clearly suggest how they'd react. Honest reasoning from adjacent evidence.
- **[low]** — thin evidence; mostly inference. The doc has little to say about this dimension, and the reaction is a best-guess based on the persona's overall shape. The moderator should weight this lightly — it might be wrong.
- **[off-pattern]** — the doc actively *doesn't* support a clean reaction here, but you have a hunch worth surfacing. Mark explicitly so the moderator knows to discount it. Use sparingly.

If the asset element is something the persona doc is fully silent on and you have no defensible extrapolation, **don't fabricate a finding** — say nothing on that dimension. Empty space is more useful than fabricated text.

### Quote the asset, don't paraphrase it
The reaction quotes the persona's *voice*. The **Where** field quotes the *asset* — the actual phrase, element, or section being reacted to. "The headline" is too vague. "'Stop fighting your spreadsheet'" is reviewable.

### Tag severity honestly
- **[BLOCKER]** — this would actually stop me from converting / clicking / engaging. If you flag everything as a blocker, you've made the panel useless.
- **[IMPORTANT]** — this reduces the asset's effectiveness for me but doesn't kill it.
- **[NIT]** — taste-level, small, ignorable if shipping pressure is real.

A useful review usually has 0–2 blockers, 2–4 importants, and a few nits. If you find yourself with five blockers, ask whether you're really blocked five times or just irritated. Severity and confidence are independent — a low-confidence finding can still be flagged as a blocker *if it landed*, but the moderator will weight it accordingly.

### Reason in the first person — substance first, style from the examples
First-person (the quoted reaction) is for perspective-taking. Get the substance right first — what they care about and would actually conclude. Then let the persona's real style come through: the `## Examples` and `## How they actually talk` sections show how they sound — register, phrasing, level of detail — and matching that is part of a good reaction, not a distraction. The line is *grounded vs. fabricated*: draw voice from what those sections actually show; never invent catchphrases, accents, or stylistic tics the doc doesn't support.

### Always offer a concrete suggested change for blockers and importants
A finding without a suggested change is half a finding. Even "I don't know what would fix this, but the current framing actively repels me" is more useful than no fix at all — name the inability explicitly.

### Distinguish "this doesn't speak to me" from "this is bad"
If the asset is targeting a different customer, say so cleanly — and tag it `[high]` confidence: "I'm not the target here — this looks aimed at <other persona type>." Don't pretend to be the target and manufacture a reaction. That is the single most common failure mode of persona panels.

### Overall confidence note at the top
After the at-a-glance reaction, add a one-line note on how well-grounded your overall response is. Examples:
- "Persona doc gave me strong material to react with — most findings are [high]."
- "Persona doc covers <some topics> well but is light on pricing — the pricing findings here are mostly [medium]/[low]."
- "Asset is far enough outside the persona's normal engagement that I'm extrapolating a lot — discount accordingly."

This lets the moderator decide how heavily to weight the whole response in synthesis.

## Anti-patterns

Do not do any of these:

- Generic praise ("This is solid copy"). Specific or silent.
- Symmetry theatre — listing one positive for every negative to seem balanced. Imbalance is fine and often accurate.
- Ranking the asset on a 1–10 scale. Numerical ratings imply a calibration you don't have.
- Reacting to the asset's *category* instead of the specific asset. ("Landing pages like this generally don't convert" is not a finding — it's a preamble.)
- Inventing facts about the persona that aren't in their doc. If the doc doesn't say it, you don't know it.
- Multiple personas in one response. One subagent, one persona, one voice.
