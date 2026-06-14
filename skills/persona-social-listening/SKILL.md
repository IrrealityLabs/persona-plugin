---
name: persona-social-listening
description: Simulate social listening — have personas write social-media-style posts about a topic (not your brand) and measure whether, where, and how your brand surfaces organically in their posts. Outputs mention rate, sentiment when mentioned, share-of-voice vs. named competitors, and the context in which the brand came up. Use when the user says "/persona-social-listening", "simulate social listening", "do the personas mention us when talking about X", "what's our organic share of voice", or "how does our brand come up in conversation about Y".
---

# Persona Social Listening

The personas write social-media-style posts about a topic of your choosing. You **do not tell them what brands to mention.** Then you analyze the posts to see whether your brand showed up, how it was framed, and how it stacked up against named competitors who also appeared.

The whole point is *organic* — guiding the personas toward a brand mention defeats the purpose. The output is only meaningful when the brand has to earn its way into the post.

## When to use vs. alternatives

- Use `persona-social-listening` for **organic mention** measurement — share-of-voice, context of mention, what topics drive your brand into conversation vs. don't.
- Use `persona-brand-tracking` when you want to *directly ask* about your brand (aided / unaided recall). Direct asking measures top-of-mind awareness; listening measures *salience in context*.
- Use `persona-survey` for structured questions about specific brands.

## Sample size

- **Sweet spot:** 8+ personas, 2–4 topics, 1–3 posts per (persona, topic) cell. Mention rates need enough posts to be meaningful.
- Below 5 personas × 2 topics × 1 post = 10 posts: results are anecdotal, not patterns. Surface this.

## Inputs

- **Topics** — 1–5 topics to have the personas post about. Topics should be *adjacent* to your brand's space, not directly about it. ("Productivity habits" rather than "<your brand>." / "How I plan my week" rather than "Time-tracking apps.")
- **Brand under measurement** — the brand name(s) to look for. Include common variations (e.g. "Anthropic" + "Claude").
- **Competitor set** (optional but recommended) — named competitors to also detect, for share-of-voice comparison.
- **Platform style** — Twitter/X (short, punchy), LinkedIn (longer, professional), Reddit (conversational, more candid). Affects what the post will look like and what brand-mention patterns are likely. Default: Twitter/X.
- **Posts per (persona × topic) cell** — default 2. Higher = more signal per persona, more cost.

## Workflow

### Phase 1 — Validate the setup

Critical sanity check: is the topic adjacent to the brand without being *about* the brand?

- A topic like "how I handle email overload" is good for measuring whether a productivity-tool brand surfaces organically.
- A topic like "best productivity tools" is too leading — every persona will list tools, and your brand may show up just because it's a tool, not because it's salient.
- A topic like "what I had for breakfast" is too distant — brand mention rate will be near-zero and uninformative.

If the user's topic is too direct, suggest a more oblique adjacent topic. If too distant, suggest one closer to the brand's space.

### Phase 2 — Generate the posts

For each (persona, topic) cell, spawn one subagent per post (so total subagents = personas × topics × posts-per-cell). All in parallel batches of ~8.

Each prompt:
- Persona doc path.
- The topic, framed as a writing prompt: "Write a <platform-style> post (<length spec>) about <topic>. Write it the way *you* would post it — voice, length, what you'd actually choose to share. No prompting on what to include; this is a free post."
- Platform style spec (Twitter: ≤280 chars or short thread; LinkedIn: 100–300 words; Reddit: 50–400 words, conversational).
- **No mention of the brand under measurement, no mention of competitors, no list of tools the persona might use.** The post must be generated cold.
- The `persona-ask` "Ground, think, then talk" contract (Grounding → Thinking → Talking) — applied to the *reasoning* about what to post, not to the post content itself.
- Response format below.

Response format per post:
```
## Grounding (private — orchestrator only; not posted)
The persona-doc sections that bear on what this persona would post, cited first: § <Section>: "<quote backing why this is something they'd post>" + a confidence read [high|medium|low|off-pattern]. (Was the persona doc rich enough to produce a confidently-in-character post on this topic?)

## Thinking (private — orchestrator only)
Private reasoning over that grounding: what this persona would genuinely choose to share, before writing the post.

## Post (<platform>)
<the actual post text>

## Reasoning
1–2 sentences on why this persona would post this — what they'd want their network to see / discuss / learn.
```

### Phase 3 — Detect mentions

For each generated post, scan for:

- **Target brand mentions** — exact-match + reasonable variants. Case-insensitive. Surface false positives carefully (don't count "claude" in "claude monet"; do count "Claude" referring to the AI).
- **Competitor brand mentions** — same.
- **Generic category mentions without a specific brand** — e.g. "I use an AI assistant" without naming one. Count these separately as "category mentions."

For each detected mention, capture:
- The exact quote (with a few words of surrounding context).
- The post it came from.
- The persona that wrote the post.
- The sentiment (positive / neutral / negative / mixed) — judge from the surrounding sentence, not the brand name alone.

Run mention detection as a small per-post coding subagent (lightweight prompt) rather than relying on regex alone — language is too messy for exact-match to catch implicit mentions ("I just switched to that anthropic chatbot thing"). The subagent gets the **posted text only** (never the private Grounding + Thinking) + brand-and-variants list + competitor list and returns structured mentions.

### Phase 4 — Synthesize

```
# Social listening: <brand> across <N> topics

## Headline
One sentence. e.g. "Our brand mentioned organically in 4 of 32 posts (12.5%), all neutral-to-positive, concentrated in the 'workflow automation' topic. Competitor X dominated 'team collaboration' (40% mention rate)."

## Mention summary
- Total posts generated: N
- Target brand mentions: M (X%)
- Competitor mentions: <breakdown per competitor>
- Generic category mentions (no brand): K (Y%)
- No-mention posts: P (Z%)

## Mention rate by topic
Topic 1: brand X% / competitor breakdown / no-mention %
Topic 2: ...
[bar chart in monospace]

## Context of brand mentions
For each target-brand mention: the post, the surrounding context, the sentiment, the persona. This is the *qualitative* heart of the output — what is the brand getting credit/blame for in the wild?

## Share of voice (vs. competitors)
For posts that mentioned *any* brand in the category: the % split across your brand and competitors. Note: this only counts posts where some brand surfaced — not the same as raw mention rate.

## Sentiment when mentioned
Distribution: positive / neutral / negative / mixed for your brand. Same for competitors if mention counts allow.

## Topics where your brand was *missing*
Topics where you'd have expected to be mentioned (the topic is core to your brand's space) but you weren't. These are gap signals — places where your brand isn't salient even though it should be.

## Personas who mentioned vs. didn't
Which persona segments mentioned the brand vs. went elsewhere. Useful for segmentation — surfaces who's on-brand-aware vs. not.

## Sample-size caveat
"N=<N> posts across <N> personas; social listening on a panel of this size produces *directional* mention rates. Real social-listening tools sample millions of public posts — treat these patterns as hypotheses about salience, not as audience-wide measurements."
```

## Notes

- **Do not coach the personas toward the brand in any prompt, anywhere.** If you tell them what brands to consider, the data is contaminated. The whole methodology relies on cold generation.
- If a persona consistently fails to write in-character posts (low confidence, generic content), it's not a good fit for this method — their persona doc may be too thin on language patterns and what-they-share preferences. Note them; consider re-distilling.
- Mention rates from a persona simulation will *not* match real social listening rates. Personas have systematically different brand-recall patterns than real humans. The valuable comparison is *between conditions* (topic A vs. topic B; brand vs. competitor) within the same run — not absolute rates.
- If the brand was never mentioned, that's still a finding — flag what the personas talked about *instead*, and what their topic associations revealed. Sometimes the absence is more useful than a low-rate presence.
- Re-running with the same topics later (e.g. after a campaign) and comparing mention rates is the best use of this method — moves the analysis from "what's our rate" (which is noisy at panel scale) to "did our rate change" (which is meaningful even at panel scale).
