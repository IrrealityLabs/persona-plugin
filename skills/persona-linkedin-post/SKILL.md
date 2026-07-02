---
name: persona-linkedin-post
description: Simulate a LinkedIn reaction to a post from your personas — show them a post they'd plausibly see on LinkedIn, have each one comment / react / repost / scroll past the way they actually would. LinkedIn dynamics are professional, longer-form, more sincere, with strong identity-signaling and weaker dunking than X. Outputs the reaction thread plus engagement-shape analysis. Use when the user says "/persona-linkedin-post", "simulate LinkedIn reactions", "what would my personas say on LinkedIn", "would this work as a LinkedIn post", or wants the specific dynamics of LinkedIn (thoughtful comments, "agreed, my experience...", professional positioning) rather than X's snark or HN's technical critique.
---

# Persona LinkedIn Post

Simulate LinkedIn engagement: personas "see this post in their feed" and react the way they'd actually react on LinkedIn. The dynamics differ meaningfully from X and HN — and matching the channel correctly matters because LinkedIn rewards different content shapes.

LinkedIn-specific dynamics:

- **Sincere over snarky.** Sarcasm and dunking are rare; what plays on X dies on LinkedIn.
- **Longer comments.** 100–500 character comments are normal; tweet-length terse replies look low-effort.
- **Professional identity signaling.** Comments often signal the commenter's *own* expertise — "in my 15 years at <company>, I've seen this play out as..." Replies are partly to OP, partly to the commenter's network.
- **Anecdotes and personal experience valued.** "Reminds me of when I..." is high-engagement content.
- **Engagement actions:** scroll past, react (like / celebrate / support / love / insightful / curious), comment, repost (with or without commentary), share via DM.
- **Repost-with-thoughts** is LinkedIn's quote-tweet equivalent and the strongest amplification action.
- **Algorithmic boost** rewards comments early in the post's life — a long thoughtful comment from a senior persona in the first hour matters more than the same comment a day later (but we don't model timing).
- **"Hot takes" do exist** but are softened — "controversial opinion" is itself a content trope, signaled before delivery.

The simulation should respect that LinkedIn has a *lot* of silent scrollers and a smaller set of professional-comment-leavers than X. Not everyone comments.

## When to use vs. alternatives

- Use `persona-linkedin-post` for posts you might publish on LinkedIn — thought leadership, company announcements, hiring posts, industry takes.
- Use `persona-x-post` for X-targeted content (different voice, different stakes).
- Use `persona-hacker-news` for posts targeting the HN audience specifically.
- Use `persona-social-listening` for organic mention across platforms.

## Sample size

- **Sweet spot:** 6–12 personas. Engagement is power-law on LinkedIn too; need enough personas to see the distribution.
- Default to all personas; if the user named some, use those. If the roster is much larger than ~8, ask the user which to include rather than auto-selecting (when suggesting, you can lean toward personas relevant to the post topic — read their `## At a glance` lines).

## Inputs

- **The post** — body text. LinkedIn posts run from ~50 to ~3000 characters; the "see more" cutoff is around 200 chars, so the first two lines matter most.
- **Media** (optional) — image / carousel / video / document upload. Carousels (multi-slide PDFs) currently get strong algorithmic boost.
- **Author context** (optional) — what does the OP's profile look like? VP at a F500, founder of a small startup, senior IC, recruiter. Affects who'd engage and how.
- **Post type** — text-only / image / carousel / video / link / repost-with-thoughts. Default: text-only.

## Workflow

### Phase 1 — Frame the post

Compose the post as it would appear on LinkedIn:
- Body text in full.
- First-two-lines preview (everything above the "...see more" cutoff at ~210 chars).
- Media description if relevant.
- Author context one-liner.

### Phase 2 — Per-persona reaction (parallel)

Spawn one subagent per persona. Each prompt:
- Persona doc path.
- The post (as it would appear on LinkedIn).
- LinkedIn behavior briefing:
  > "You're scrolling LinkedIn and this post appears in your feed. Decide what you'd actually do:
  > **(A) Scroll past** — would not engage. Honest answer if the post isn't for you or doesn't move you.
  > **(B) React only** — pick a reaction (like / celebrate / support / love / insightful / curious). Silent endorsement that registers but doesn't comment. The reaction you'd pick signals *type* of endorsement.
  > **(C) Comment** — public comment to OP. LinkedIn comments are typically 1–4 sentences; anecdote-shaped, professionally framed, often signaling your own expertise alongside reacting to OP.
  > **(D) Repost** — share to your own network. Either silent repost (just amplify) or repost-with-thoughts (your own framing on top). Repost-with-thoughts is the strongest amplification.
  > **(E) Share via DM** — send to specific people without making it public. Note this — it doesn't appear in the public thread but it's real engagement.
  > Pick one. Don't pick (C), (D), or (E) unless you genuinely would — performative engagement when your persona doc wouldn't engage produces fake-looking data."
- LinkedIn voice constraints:
  - Comments: sincere, professional, anecdote-friendly. No emoji unless your persona doc supports it.
  - Reposts-with-thoughts: 100–400 characters of your own framing on top of the repost.
  - Stay in your persona's actual professional voice — a junior PM persona shouldn't sound like a VP.
- The `persona-ask` "Ground, think, then talk" contract (Grounding → Thinking → Talking).
- Response format below.

Response format:
```
## <persona slug>
**Grounding:** (private — orchestrator only; not posted) The persona-doc sections that bear on this, cited first: § <Section>: "<…>" + a confidence read [high|medium|low|off-pattern].
**Thinking:** (private — orchestrator only) Private reasoning over that grounding: what this persona would genuinely conclude, before deciding what to post publicly.

**Action:** scroll | react (<which>) | comment | repost (with-thoughts?) | DM-share
**Content (if comment / repost-with-thoughts):**
<the actual text>

**Reasoning:** one sentence on why this persona chose this action.

**LinkedIn-voice fit:** [strong|partial|forced] — would this persona credibly engage on LinkedIn? Forced = the simulation pushed them into voice that doesn't match their doc.
```

### Phase 3 — Synthesize

```
# LinkedIn simulation: "<post, short>"

## Headline
One sentence — the engagement shape this post would have. e.g. "Strong sincere engagement: 3 detailed comments, 2 reposts-with-thoughts, 5 reacts, 0 critical comments. High amplification potential within the senior-IC segment, limited reach to junior-leader segment."

## Engagement breakdown
- Scroll past: N (X%)
- React only: N (X%) — with reaction-type breakdown (like / celebrate / support / love / insightful / curious)
- Comment: N (X%)
- Repost (silent or with-thoughts): N (X%) — split out
- DM-share: N (X%)

## Comment thread
Render comments in order, with persona attribution. **Posted comment text only — each persona's private Grounding + Thinking are excluded from the rendered thread, kept with the orchestrator.**

## Repost activity
List the personas who'd repost, with their commentary (if with-thoughts). Reposts are LinkedIn's high-leverage action — these are who'd extend the post's reach.

## DM-share signal
Personas who'd share privately. Often higher-trust signal than public engagement — they're sending to specific people who'd care.

## Reaction-type analysis
LinkedIn's six reactions encode different responses (insightful ≠ love ≠ support). Distribution surfaces what *kind* of post this is landing as — informational vs. emotional vs. celebratory.

## Dominant takes from comments
Cluster comments into 2–4 themes. For each: how many personas, the strongest example.

## Audience-fit signal
Personas marked `forced` on LinkedIn-voice fit had distorted reactions. If a significant fraction were `forced`, your audience isn't really on LinkedIn for this kind of content — flag and recommend a different channel.

## Substantive signal
Strip away the LinkedIn-professional wrapping — what substantive engagement came through? The takeaway content beneath the channel voice is what travels regardless of where you post.

## Algorithmic-potential note
LinkedIn boosts posts with early high-quality comments. Of the comments above, which would be early-cohort engagement that could trigger algorithmic boost? This is heuristic, not modeled — but flag the comments that look "engagement-starting" vs. "engagement-extending."
```

### Phase 4 — Render the report

Write `report.html` to `./.persona-research-runs/linkedin-post-<YYYY-MM-DD>-<slug>/` per the
shared spec in `skills/persona-research/references/html-report.md` — self-contained
(inline CSS/JS, data embedded, opens with a double-click): the question, method + N
caveat, the simulated posts/replies threaded, one card per persona with their verbatim
public answers + confidence and collapsible grounding, and the insights. Tell the user
the path.

## Notes

- **LinkedIn's dunking is rare and reads badly.** If a persona's reaction comes back snarky / dismissive in tone, that's *more* notable than the same reaction on X — it suggests the post is genuinely off-key.
- **Reposts-with-thoughts are the highest-leverage engagement on LinkedIn** — they extend reach into the reposter's network with the post pre-validated. Multiple reposts is a stronger viral signal than comment volume.
- **"Insightful" is the most-signal LinkedIn reaction** — used by people who want to publicly endorse intellectually without committing to a comment. High insightful-to-other-reaction ratio = the content is intellectually credible to the audience.
- The first two lines (above "see more") are doing most of the work. If most personas scroll past, ask whether the first two lines hook them — re-running with a stronger opener is often the highest-leverage fix.
- LinkedIn-native voice is genuinely different from X. Don't reuse X copy as LinkedIn copy without adaptation; this skill can help test whether a piece needs that adaptation.
