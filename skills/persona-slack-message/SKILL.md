---
name: persona-slack-message
description: Simulate Slack reactions from your personas to a message — in a specific channel context (team-internal, community Slack, customer Slack), with the right Slack-native dynamics (emoji reactions, thread replies, "🧵", DMs). Outputs the simulated thread plus an analysis of how the message would actually land. Use when the user says "/persona-slack-message", "simulate Slack reactions", "how would my team take this in Slack", "what would happen if I posted this in <channel>", or wants Slack-specific dynamics rather than X / LinkedIn / email.
---

# Persona Slack Message

Simulate Slack engagement. The personas "see this message in <channel>" and react. Slack dynamics are very different from public platforms — much more dependent on *who* is in the channel and what kind of channel it is.

Slack-specific dynamics:

- **Channel context dominates.** A message in a team-internal #engineering channel reads completely differently than the same message in a customer Slack community or a company-wide #announcements. Always pin the channel context first.
- **Emoji reactions are first-class.** Often the *only* reaction. :100:, :eyes:, :pray:, :thumbsup:, custom emoji. People react silently far more than they reply.
- **Threaded replies.** Most substantive responses happen in threads, keeping the main channel uncluttered. A flat-channel reply ("not in thread") is a status move — usually wrong, sometimes deliberate.
- **DMs.** People often DM rather than thread, especially if their reaction is sensitive (concerned, contrarian, gossipy). DM-traffic is the *invisible* iceberg under any Slack post.
- **Async + lurkers.** Most channel members never react at all. Engagement is a small fraction of channel readership.
- **Internal vs. external.** In internal team channels, criticism is candid and short. In customer/community Slack, criticism is more measured and politeness norms kick in.

Sample-size note: Slack engagement is even more lurker-heavy than X or LinkedIn. Expect most personas to lurk.

## When to use vs. alternatives

- Use `persona-slack-message` for messages going into a Slack channel — internal team announcements, customer-community posts, beta-cohort updates, internal proposals.
- Use `persona-x-post` / `persona-linkedin-post` for public-platform messages.
- Use `persona-email` for 1:1 or small-group async written communication.

## Sample size

- **Sweet spot:** 5–10 personas. Slack benefits from breadth — the lurker-rate makes small samples noisy.
- Default to all personas; if the user named some, use those. If the roster is much larger than ~8, ask the user which to include rather than auto-selecting.

## Inputs

- **The message** — the actual Slack message text. Slack messages can be a few words or a long block (uncommon but possible).
- **Channel context** (required, not optional) — what *kind* of channel is this?
  - **Internal team channel** (e.g. #engineering, #marketing-team) — candid, short, technical/operational.
  - **Internal company-wide channel** (e.g. #announcements, #general) — more measured, signaling-aware.
  - **Customer / community Slack** (e.g. a partner Slack, your beta-tester channel) — politeness norms higher, customer-vendor dynamic active.
  - **DM** — 1:1, no audience, most candid.
  - **Multi-person DM / huddle invite** — small private group, candor between public-channel and DM.

  The channel context fundamentally changes simulated reactions. Don't skip this input.
- **Sender context** (optional) — who's sending? CEO, peer, junior, external person. Affects how personas receive it.
- **Message type** — announcement / question / proposal / request-for-feedback / status update / drama / ops issue. Affects what counts as engaging vs. lurking.

## Workflow

### Phase 1 — Frame the message and channel

Compose the scene clearly:
- The message text.
- The channel name and type.
- The sender context.
- The implicit social contract (e.g. "in #engineering, criticism is normal" / "in #customer-community, you're representing your company").

### Phase 2 — Per-persona reaction (parallel)

Spawn one subagent per persona. Each prompt:
- Persona doc path.
- The framed message + channel context.
- Slack behavior briefing:
  > "You're in <channel>; this message just appeared. Decide what you'd actually do:
  > **(A) Nothing — keep scrolling/working.** Realistic for most channel members on most messages.
  > **(B) Emoji reaction only** — pick the emoji you'd actually add (or 'none if I had to'). Common emoji: :+1:, :100:, :eyes:, :pray:, :thinking_face:, :wave:, :raised_hands:, :tada:, :heart:, :rocket:, :thumbsdown:, :no_entry:.
  > **(C) Thread reply** — reply in-thread to the message. Substantive responses go here. 1–4 sentences typically.
  > **(D) Channel reply (not in thread)** — reply directly in the channel. Status move — usually means 'this is important enough to be visible to everyone' or 'I'm too distracted to thread'. Less common.
  > **(E) DM the sender** — private reaction. Pick this if your reaction is sensitive, contrarian, or specifically for the sender's ears only. Note this — it doesn't appear publicly but is real engagement.
  > **(F) DM someone else about this message** — gossip / coordination / 'did you see this?' DMs. Often invisible to the sender but important social signal.
  > Pick one (or multiple — e.g. emoji + thread reply, or thread + DM). Don't pick the comment options unless your persona would actually engage; lurking is the most common response."
- Channel-context constraints:
  - Internal team channel: candid, short, can use jargon.
  - Internal company-wide: more measured, brand-aware.
  - Customer/community: politeness up, vendor-customer dynamic in play.
  - DM: most candid.
- The `persona-ask` "Ground, think, then talk" contract (Grounding → Thinking → Talking).
- Response format below.

Response format:
```
## <persona slug>
**Grounding:** (private — orchestrator only; not posted) The persona-doc sections that bear on this, cited first: § <Section>: "<…>" + a confidence read [high|medium|low|off-pattern].
**Thinking:** (private — orchestrator only) Private reasoning over that grounding: what this persona would genuinely conclude, before deciding what to post publicly.

**Action(s):** nothing | emoji (<which>) | thread reply | channel reply | DM-sender | DM-other
(can be multiple, e.g. ":eyes: + thread reply")

**Content (if any reply):**
[Thread] <text>
[Channel] <text>
[DM to sender] <text>
[DM to other (specify who, e.g. 'a teammate in the same role')] <text>

**Reasoning:** one sentence on why this persona chose this action set.

**Slack-channel-fit:** [strong|partial|forced] — would this persona credibly engage in this kind of Slack channel? Forced = the simulation pushed them into voice/behavior that doesn't match.
```

### Phase 3 — Synthesize

```
# Slack simulation: <channel context> — "<message snippet>"

## Headline
One sentence. e.g. "Mostly lurked (6 of 8 personas), 2 emoji reactions (:eyes: + :+1:), 1 thread reply (concerned), 3 DMs to other people. The message would 'land quietly' visibly but generate background DM-discussion."

## Engagement breakdown
- Nothing (lurked): N
- Emoji only: N — with emoji breakdown
- Thread reply: N
- Channel reply (not threaded): N
- DM the sender: N
- DM someone else: N

## Visible thread
Render the in-channel reactions and threaded replies as they'd appear in Slack. **Sent message content only (channel/thread/DM text) — each persona's private Grounding + Thinking are excluded from these renders, kept with the orchestrator.**

## Invisible thread (DMs)
The DMs — both to the sender and to third parties. This is the iceberg-under-the-water signal. For DM-someone-else: who they'd DM and what about. Often more useful than the visible thread for surfacing the *actual* reception.

## Reaction-emoji analysis
What the emoji pattern signals. :eyes: + :thinking_face: = "people are processing." :100: + :rocket: = full endorsement. :pray: = "fingers crossed." Surface the dominant emoji-mood.

## Dominant sentiment by audience segment
If the personas split into segments (internal team vs. external community, senior vs. junior, etc.), surface where reactions diverged by segment.

## What people would actually say in DMs
Concretely. This is often the most actionable finding — DM critique surfaces objections the channel-public would never say.

## Audience-fit signal
Personas marked `forced` on Slack-channel-fit had distorted reactions. Common cause: persona doc doesn't reflect anyone who'd be in this specific channel — flag and consider whether the channel context is realistic for your audience.

## Slack-message-specific advice
Sometimes the issue isn't the message, it's the channel choice. If the simulation suggests lots of DM-traffic and little public engagement, consider sending this message somewhere else (a smaller channel, a DM, a real meeting) or restructuring it.
```

### Phase 4 — Render the report

Write `report.html` to `./.persona-research-runs/slack-message-<YYYY-MM-DD>-<slug>/` per the
shared spec in `skills/persona-research/references/html-report.md` — self-contained
(inline CSS/JS, data embedded, opens with a double-click): the question, method + N
caveat, the simulated posts/replies threaded, one card per persona with their verbatim
public answers + confidence and collapsible grounding, and the insights. Tell the user
the path.

## Notes

- **The DM iceberg is the most-undersold output of this method.** Slack messages get critiqued and dissected in DMs that the sender never sees. Surfacing the would-be DM reactions is the single most useful thing this simulation does.
- **Channel context is load-bearing — don't let the user skip it.** A simulated reaction without channel context produces noise. Ask if it's missing.
- **Internal vs. external is a huge axis.** A message that lands fine internally can read tone-deaf in customer Slack, and vice versa. Re-running with the same message in different channel contexts is a useful exercise.
- For messages that would generate a lot of DM-the-sender traffic, that's signal that the message asks a question (or implies one) that people want resolved 1:1 before publicly engaging. Often means the message was missing context the audience needed.
- Slack-native voice is short and direct. If a simulated reply runs long (3+ sentences), question whether the persona is being prompted into LinkedIn-comment voice instead of Slack-native voice.
