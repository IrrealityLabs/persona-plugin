---
name: persona-x-post
description: Simulate an X (Twitter) reply thread from your personas — show them a post they'd plausibly see in their feed, have each one reply / quote-tweet / like / scroll past the way they actually would on X. Outputs the reply thread plus an analysis of engagement shape (ratio risk, viral potential, dominant takes). Use when the user says "/persona-x-post", "simulate X replies on this", "what would my personas tweet back", "would this go viral / get ratio'd on X", or wants the specific dynamics of an X thread (hot takes, dunks, quote-tweet performance) rather than HN's technical-critique voice or LinkedIn's professional voice.
---

# Persona X Post

Simulate an X reply thread: the personas "see this post in their feed" and react the way they'd actually react on X. Some reply, some quote-tweet, some like-and-scroll, some do nothing. The output is the resulting thread plus an analysis of how it would actually perform (ratio risk, who'd amplify vs. dunk, what the dominant take would be).

X has its own dynamics, distinct from HN:

- **Shorter, sharper.** 280-char replies. Hot takes, not essays.
- **Performance, not just substance.** People reply for their *audience*, not just the OP. A reply that gets quote-tweeted by a big account matters more than a "good point."
- **Algorithm-aware.** Personas know that controversial replies surface; tepid ones don't. Affects what gets posted.
- **Ratio dynamics.** A bad post draws more replies than likes — "ratio'd" — and that itself becomes the story.
- **Tribal signaling.** Many replies aren't to OP — they're to the persona's *own* followers, signaling identity and side-taking.
- **Quote-tweet vs. reply vs. silence.** Three distinct moves with very different meanings. Replies are conversational; quote-tweets are public performance; silence/like is endorsement without amplification.

The simulation must respect that some personas would just keep scrolling. Forcing every persona to comment produces a fake-looking thread.

## When to use vs. alternatives

- Use `persona-x-comments` for posts you might actually publish on X — launch tweets, hot takes, contrarian threads, product announcements.
- Use `persona-hacker-news` for technical posts where the audience is HN, not X.
- Use `persona-social-listening` to measure organic brand mention rates in *cold* (un-prompted) persona posts.
- Use `persona-council` for adversarial deliberation among personas without the X-performance overlay.

## Sample size

- **Sweet spot:** 6–12 personas. X engagement is power-law — many will silent-scroll, a few will engage strongly. You need enough to see the distribution.
- Default to all personas; if the user named some, use those. If the roster is much larger than ~8, ask the user which to include rather than auto-selecting (when suggesting, you can lean toward personas relevant to the post topic — read their `## At a glance` lines).

## Inputs

- **The post** — title-style hook + body text. If it's a thread, paste the thread.
- **Media** (optional) — image / video / link card description. X engagement varies hugely with media.
- **Author context** (optional) — is the OP a known account, a small account, or an alt? Affects how personas react. Default: assume a mid-sized account in the persona's broader space.
- **Quote-tweet round** (optional, default off) — simulate one round of quote-tweets from personas who would publicly amplify or dunk on the post. Adds cost.

## Workflow

### Phase 1 — Frame the post

Compose the post as it would appear on X:
- 280-char limit per post; if it's a thread, number the parts.
- Include the media description if any.
- One-line author context.

If the user pasted something longer than a tweet (an essay, a blog post), tell them and ask: should this be a *thread* (each chunk as a numbered tweet), a *link card* (just the title + your summary as the post), or a *quote-tweet of an external link*? Each has different X dynamics.

### Phase 2 — Per-persona reaction (parallel)

Spawn one subagent per persona. Each prompt:
- Persona doc path.
- The post (as it would appear on X).
- X behavior briefing:
  > "You're scrolling X and this post comes up in your feed. Decide what you'd actually do:
  > **(A) Scroll past** — would not engage. Most posts get this from most people. Honest answer if the post isn't for you.
  > **(B) Like and scroll** — silent endorsement, no public comment. Common for in-group posts you agree with but don't need to amplify.
  > **(C) Reply** — public comment to OP. Subject to 280-char limit. Could be agreement, disagreement, joke, sharper question, anecdote.
  > **(D) Quote-tweet** — publicly amplify with your own framing. Used to broadcast to *your* audience, not to converse with OP. Could be endorsement ('this'), dunk, addition, or sub-tweet.
  > Pick one. Don't pick (C) or (D) unless you genuinely would — performative engagement when your persona doc wouldn't reply produces fake-looking thread data."
- Hard constraints:
  - 280 char limit for replies and quote-tweets.
  - Voice should be consistent with your persona doc — no fake-X-influencer voice if your persona isn't one.
  - Emoji / GIFs / "based" / "this" / etc. only if the persona doc supports that voice.
- The `persona-ask` "Ground, think, then talk" contract (Grounding → Thinking → Talking).
- X-comments response format below.

X-comments response format:
```
## <persona slug>
**Grounding:** (private — orchestrator only; not posted) The persona-doc sections that bear on this, cited first: § <Section>: "<…>" + a confidence read [high|medium|low|off-pattern].
**Thinking:** (private — orchestrator only) Private reasoning over that grounding: what this persona would genuinely conclude, before deciding what to post publicly.

**Action:** scroll | like | reply | quote-tweet
**Post (if reply or quote-tweet):**
<the actual tweet text, ≤280 chars>
[for quote-tweet: indicate the quote framing, e.g. "Quote-tweeted with this:"]

**Reasoning:** one sentence on why this persona chose this action.

**X-voice fit:** [strong|partial|forced] — would this persona credibly post on X? Forced = the simulation pushed them into voice that doesn't match their doc.
```

### Phase 3 — Quote-tweet round (optional)

If enabled, second pass: each persona who didn't act in Phase 2 (or who did) sees the *replies and quote-tweets* from Phase 2. Subagent prompt:
- Persona doc path.
- The original post.
- The Phase 2 thread — the **posted replies + quote-tweets only**, with persona attribution stripped (they're seeing it as "X strangers" on their timeline). The Phase 2 private Grounding + Thinking are never included; only public posts propagate.
- "Now, with the discourse forming around this post visible in your feed, would you weigh in? Same four-action choice."
- Same response format as Phase 2 (lead with private Grounding + Thinking, then the public action/post).

This catches the *meta*-engagement: personas who wouldn't reply to the original but *would* dunk on a bad reply, or amplify a great one.

### Phase 4 — Synthesize

```
# X simulation: "<post, short>"

## Headline
One sentence — what the thread would actually look like. e.g. "Mostly silent-scroll (5/8), 2 replies (one positive, one critical), 1 dunk quote-tweet. Low engagement, low ratio risk, no viral signal."

## Engagement breakdown
- Scroll past: N (X%)
- Like only: N (X%)
- Reply: N (X%)
- Quote-tweet: N (X%)

The scroll-past rate is signal — high = post isn't for these personas, low = it's hitting.

## The thread (chronological)
Render the replies in order, then quote-tweets separately. **Posted text only — each persona's private Grounding + Thinking are excluded from the rendered thread, kept with the orchestrator.**

Replies:
@<persona-slug-1>: <text>
@<persona-slug-2>: <text>
...

Quote-tweets:
@<persona-slug-3> QT'd: <quote text>
@<persona-slug-4> QT'd: <quote text>

## Ratio risk
The reply-to-like ratio shape. If replies >> likes among engagers, the post is structured for ratio. Surface what specifically drew the critical replies.

## Dominant takes
Cluster the replies + quote-tweets into 2–4 takes (the dominant framings the audience would converge on). For each: how many personas held it, the strongest sample.

## Viral signal
Would any of the quote-tweets or replies plausibly themselves go viral? X discourse is often driven by reply-of-reply more than the original. Surface candidates — these are the *takes that escape into broader timelines*.

## Who'd amplify / who'd dunk / who'd ignore
Three lists. Often the most actionable persona-segmentation signal from X simulation — your real amplifiers and detractors map to these.

## Audience-fit signal
Personas marked `forced` on X-voice fit had distorted reactions. If a significant fraction were `forced`, your audience isn't really on X for this kind of content — flag and recommend social-listening on a more apt platform.

## Substantive vs. performative critique
Strip away the X performance — what substantive critiques came up that you'd want to address regardless of where you post? Those are the takeaway. The X-voice wrapping is the cosmetic; the underlying objections are the real findings.
```

## Notes

- **Honor scroll-past.** A simulation where every persona replies is a tell that the prompt is forcing engagement. Real X threads have engagement rates of 1–5% on most posts; expect most personas to scroll past most things.
- **Don't write fake-influencer voice.** If a persona's doc says they're a quiet enterprise architect, their X reply should sound like a quiet enterprise architect's tweet, not like an X-native shitposter.
- Quote-tweets are the highest-leverage simulated output for *predicting reach* — they're the action that escapes the OP's bubble. If multiple personas quote-tweet, that's a stronger viral signal than reply count alone.
- "Going viral" is fundamentally driven by who happens to see it, timing, algorithmic boost, and luck — variables this simulation does not model. Use this method for *substantive* feedback shaped by X-style reactions, not as a viral predictor.
- The `forced` X-voice flag is critical signal — surface it prominently. If 6 of 8 personas in your audience aren't really X-native, you may be over-investing in X as a channel for this content.
- Re-running on subsequent drafts of a launch tweet is a high-leverage use case — small wording changes can flip a post from "scroll past" to "engage" for specific personas.
