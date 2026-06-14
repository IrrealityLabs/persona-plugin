---
name: persona-review
description: Run an asset (marketing copy, landing page, ad, pricing page, feature pitch, value prop, anything aimed at a customer) past a panel of target personas and return code-review-style feedback — specific, line-level, actionable. Use when the user says "persona-review this", "/persona-review", "/persona-review <slug>", "/persona-review <slug1> <slug2>", "run this past my personas", "what would <name> think of this", "get persona feedback on this copy/page/asset", or pastes an asset and asks how it lands. Reads personas from a local .personas/ folder; if empty, points to the persona-create skill.
---

# Persona Review

Review an asset through a panel of target personas and return feedback the way a senior code reviewer would critique a pull request — specific, line-anchored, severity-tagged, with concrete suggestions. You are the **moderator**: you frame the question, you spawn one subagent per persona, you compile the responses, you do not put your own opinion in the personas' mouths.

For a **slide deck or recorded talk**, use `persona-presentation` instead — it ingests the deck/transcript/video, reacts slide by slide, and judges the narrative arc. `persona-review` is for static assets consumed at once (copy, a page, an ad), not a sequenced talk.

To **iteratively optimize** an asset rather than review it once — loop review-and-edit until the panel stops finding problems — use `persona-goal`, which runs this skill in a stopping-aware loop via the platform's goal feature (round budget, no-improvement and convergence stops).

The value is *specificity*. A persona saying "I like it" or "I don't like it" is a failure. A persona saying "The phrase 'enterprise-grade' in the H1 makes me bounce — I've been burned by that exact wording from three vendors who didn't have SOC 2 — replace with the actual compliance certification you hold" is the goal.

## Phase 0 — Announce

Say: "Running this past <N> personas: <names>. These are simulations of your target customers, not real interviews. I'll moderate, they'll each respond independently, and I'll synthesize the panel feedback."

## Phase 1 — Resolve the panel

Personas live in `./.personas/` relative to the current working directory — **unless `PERSONA_HOME` is set, in which case the store is that directory instead** (a shared persona set across projects). Resolve the store this way everywhere: `$PERSONA_HOME` if set, else `./.personas/`. Every `*.md` file in the resolved store is a candidate panelist.

**Panel selection rules** — based on the user's invocation:

- **No persona names given** (e.g. `/persona-review`, "run this past the personas", or just dropping an asset): every persona in `./.personas/` is on the panel. This is the default.
- **One persona named** (e.g. `/persona-review skeptical-cto`, "ask skeptical-cto what they think"): only that persona. Match the name against the filename slug (with or without `.md`). Case-insensitive. If the user names them informally ("ask the CTO one"), map to the closest slug and confirm in your announce phase.
- **Multiple personas named** (e.g. `/persona-review skeptical-cto bootstrapped-consultant`, "ask alex and jordan"): only those personas, in the order given.

If a named persona doesn't match any file in `./.personas/`, stop and say so — list the available slugs so the user can correct the name, and offer to add the missing persona via `persona-distill` (if it's a real person or has a public footprint) or `persona-create` (if the user wants to define it themselves). Do not silently substitute the closest match without confirming.

If `.personas/` does not exist or is empty:
- Stop. Tell the user there are no personas yet.
- Offer two paths: (a) run `persona-create` to build one through a short interview, or (b) run `persona-distill` to build one from real data (Slack messages, X/Twitter posts, web research).
- Do not improvise a persona from general knowledge of "what marketers think" or "what CTOs care about". The whole point is that *these specific personas* represent *this user's audience*.

A single-persona panel (whether because the user asked for one or because only one exists) still runs the full flow — the synthesis just becomes "what this one persona said." Don't skip synthesis even with a panel of one; the structured output is still useful.

## Phase 2 — Identify the asset and the question

Before spawning anything, you need two things crisply:

1. **The asset** — the thing being reviewed. Could be pasted copy, a file path, a URL, an image, a Figma link, a product description, an ad concept. If unclear what to review, ask the user. Capture the asset *verbatim* so personas see exactly what a real customer would see — no paraphrasing.

2. **The question** — what kind of feedback is wanted. Defaults to "Would this land with you? What would you change?" but the user may want something narrower: "Does the pricing feel fair?", "Is the value prop clear in the first 5 seconds?", "Would you click the CTA?". If the user didn't specify, default to the broad version *and* tell them in your announce phase that they can re-run with a sharper question.

If the asset is a URL or file, fetch/read it once yourself so every persona subagent sees the same snapshot. Don't make each subagent fetch independently — they could land on different content.

## Phase 3 — Frame the question (moderator's job)

Apply the `persona-ask` skill — it has the consumer-research best practices for framing questions to elicit *useful, specific* answers rather than agreeable noise. Read that skill before drafting the question you'll pass to each persona subagent. The framing is the single highest-leverage thing you do in this phase.

Default behavior: **one well-framed question per persona per review.** Most asset reviews need only one round. Multi-round questioning is for cases where the first round surfaces something that needs clarification *from the personas themselves* (e.g., "three of them flagged the pricing — I want to drill in on what specifically about it"). Do not multi-round by default; it's expensive and rarely sharpens the answer.

## Phase 4 — Spawn the panel (one subagent per persona, in parallel)

Use the `Agent` tool (subagent_type: `general-purpose`) once per persona, **all in a single message** so they run in parallel.

Each subagent prompt must contain:

- The absolute path to that persona's doc, with instruction to read it in full and inhabit it.
- The asset, verbatim. (Pasted text inline; for files, the contents; for URLs, the contents you already fetched.)
- The framed question.
- The `persona-ask` skill reference — instruct the subagent to load `persona-ask` and follow its response format.
- The reviewer contract (below).

### Reviewer contract (every persona, every review)

- Read the asset as **this persona would** read it: with their attention span, their skepticism, their prior experience with this category, their language.
- React in first-person *as that persona would react*. Let their real voice come through — the register and phrasing their `## Examples` and language section actually show; that grounded style makes the reaction land. Don't *fabricate* beyond it: no invented catchphrases, no accent or slang the doc doesn't support.
- Be **specific**. Quote the exact line, image, or section you're reacting to. Don't say "the headline is weak" — say "'Increase your revenue' in the H1 — this is so generic I've seen it on a hundred SaaS pages, including ones I bounced from."
- Be **honest about your reaction**, including reactions that are inconvenient for the user. If the asset fundamentally doesn't speak to you, say so plainly. The point of the panel is friction — sandbagging the critique to seem agreeable wastes the review.
- Distinguish **what would make you bounce / not buy / scroll past** (blockers) from **what merely feels off** (nits). A reviewer who flags everything as critical is no more useful than one who flags nothing.
- If something resonates strongly, say *why* in terms the persona would actually reason in — not generic praise.

### Response format for each persona

Required structure. Each finding has both a **severity** tag (how much it matters) and a **confidence** tag (how well the persona doc supports it). The two are independent.

```
## At-a-glance reaction
Two sentences max — would I keep reading / click / buy, and the dominant feeling.

## References
One line on how well the persona doc supports this response overall. Examples:
- "Strong doc coverage — most findings are [high] confidence."
- "Doc covers messaging well but is thin on pricing — pricing findings are mostly [medium]/[low]."
- "Asset is outside the persona's normal engagement; I'm extrapolating throughout."

## Findings
Repeated block, one per finding. Severity tags: [BLOCKER] [IMPORTANT] [NIT]. Confidence tags: [high] [medium] [low] [off-pattern].

### [SEVERITY] [confidence] Short label
**Where (in the asset):** quoted phrase, section, or element being reacted to.
**Reaction:** "First-person quoted reaction in the persona's voice — short, direct, decision-making tone."
**References (persona doc):**
  - § <Section name>: "<short quote or paraphrase of the line that backs this>"
  - § <Section name>: "<...>"
**Confidence reason:** one line on *why* this confidence level — e.g. "direct hit on bounce-list" / "extrapolating from JTBD" / "doc silent on this dimension".
**Suggested change:** a concrete alternative — a rewrite, a different angle, an element to add or cut. "I don't know" is allowed if I genuinely have no fix, but say so explicitly.

## What's working
Anything that actively resonates — same format (where / reaction-quote / references / confidence), no suggested change needed.

## What I'd need to see next
If I were on the fence, the single thing that would move me from "maybe" to "yes" (or "no" to "maybe"). Skip if the asset is far enough away that this doesn't apply.
```

A finding with no references or an empty references block is malformed — the subagent should re-draft it or drop it. The whole point of references is to make the persona accountable to its own doc.

## Phase 5 — Synthesize the panel

Once all subagents return, compile a single panel report. Your job is to map the feedback honestly across personas, not to summarize-away the disagreements.

**Weight findings by confidence.** Every finding came back with both a severity tag and a confidence tag. Use them together:

- A `[BLOCKER] [high]` finding flagged by multiple personas = top of the change list, near-certainty it matters.
- A `[BLOCKER] [low]` finding from one persona = surface it, but as "one persona flagged this, low confidence — could be a real risk or could be noise."
- A `[NIT] [high]` finding = real but small; below blockers in priority.
- An `[off-pattern]` finding = mention only if it's striking; the persona itself flagged it as a hunch.

Cross-persona convergence on a finding raises its effective confidence even if each individual flag was medium — three personas reaching the same conclusion from different parts of their respective docs is a strong signal. Note that in the synthesis.

Structure:

```
# Persona Review: <short asset descriptor>

## Headline
One sentence — the overall panel read. "All three personas would bounce on the H1." or "Two strong yeses, one hard no on pricing." or "Universally lukewarm — the asset doesn't fail, but nobody is excited."

## Blockers (everyone or near-everyone agrees)
For each: the issue, who flagged it, the strongest suggested fix from the panel. These are the changes that, if made, would change panel outcomes.

## Persona-specific reactions
For each persona, a 3–5 line distillation of their take. Lead with their severity (would they buy / click / engage). Then the 1–2 findings that most defined their reaction.

## Where the panel split
Any place two personas reacted oppositely. State the split, who was on each side, and why — usually this maps to a real audience segmentation question the user should decide on (which persona are we actually optimizing for here?).

## Concrete change list
A numbered, prioritized list of specific edits the user could ship. Each item: what to change, which persona(s) it addresses, severity. Ordered so the top items are blockers with the most cross-persona support.
```

Then close with the disclaimer:

> _— Simulated persona panel. These are perspective-taking simulations grounded in the persona docs in `./.personas/`, not real customer interviews. Use this as a structured prompt for your own judgment and prioritization — validate load-bearing reactions with real customers before betting on them._

## Notes on cost, scope, and follow-up

- One subagent per persona per call. Default to one round. A 4-persona review = 4 subagent runs. Don't add rounds unless something specific in Round 1 warrants drilling in.
- If the user re-runs persona-review after editing the asset, treat it as a fresh review — don't try to remember the prior round. Each call is self-contained.
- If the user wants only one persona's reaction, that's still this skill — just one subagent. Don't redirect to a "single persona" skill (there isn't one).
- If the personas in `.personas/` look stale or wrong for the asset (e.g., the user pasted B2C copy but every persona is a B2B buyer), name that in your announce phase and offer to run `persona-create` to add a fitting one before proceeding.
