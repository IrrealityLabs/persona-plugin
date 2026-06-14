---
name: persona-email
description: Simulate how your personas would respond to an email — would they reply, would they reply right away, what would they say, and what tone. Email is 1:1 (or small CC) and has no scroll-past option — recipients have to decide actively how to respond. Outputs per-persona response plus an analysis of response shape. Use when the user says "/persona-email", "simulate email reactions", "how would my personas reply to this email", "would this email actually get a reply", or wants email-specific dynamics (response rate, response speed, formality, tone) rather than public-platform engagement.
---

# Persona Email

Simulate email replies. Email is the most direct of the channels in this catalog — there's a specific recipient, no audience, no scroll-past affordance (technically; in practice, most email gets ignored). The interesting questions are: *would* they reply at all, how *fast*, in what *tone*, and *what* would they actually say.

Email-specific dynamics:

- **Reply / don't reply / archive** — the three real actions. Archive without reading is the email equivalent of scrolling past.
- **Response latency.** Some emails are answered in minutes; some take days; many are never answered. The latency itself is signal.
- **Tone matching.** Recipients usually match the sender's formality level (or downgrade by one notch — informal email gets a casual reply; formal gets professional-warm).
- **Forwarding / CC dynamics.** A recipient might forward to someone else rather than reply, especially in B2B contexts.
- **Subject-line-as-filter.** Many emails get triaged by subject alone. Test the subject line, not just the body.
- **Calls-to-action.** Emails with a specific ask perform very differently from FYI emails. Recipients evaluate the cost of the requested action.
- **Cold vs. warm.** Cold outreach has a fundamentally different reception than email from a known sender. The simulation needs to know which.

## When to use vs. alternatives

- Use `persona-email` for emails you'd actually send — cold outreach, customer comms, internal asks, sales follow-ups, founder updates to investors.
- Use `persona-slack-message` for Slack-channel-context messages.
- Use `persona-x-post` / `persona-linkedin-post` for public-platform content.

## Sample size

- **Sweet spot:** 4–10 personas. Email responses are individual — the panel size is about variance, not aggregation.
- Default to all personas; if the user named some, use those. If the roster is much larger than ~5, ask the user which to include rather than auto-selecting — when suggesting, favor personas who'd actually be in the recipient set for this kind of email (read their `## At a glance` lines).

## Inputs

- **Subject line** — required. Often more important than the body.
- **Body** — the email text.
- **Sender context** — required. Cold outreach (sender unknown to recipient) vs. warm (existing relationship). For warm: roughly what the relationship is (vendor, peer, friend, employee, manager, etc.).
- **CTA** (call to action) — what the sender wants the recipient to do. Reply with info / agree to a meeting / make a decision / no action (FYI). If the email has no CTA, that's itself notable.
- **Send context** (optional) — time of day / day of week, if it's a deliberate sending choice. Affects realism of latency predictions.

## Workflow

### Phase 1 — Frame the email

Compose the email as it would appear in an inbox:
- Sender name + sender context one-liner (cold vs. warm, what the relationship is).
- Subject line.
- Body.
- Implicit CTA (what the sender wants).

### Phase 2 — Per-persona reaction (parallel)

Spawn one subagent per persona. Each prompt:
- Persona doc path.
- The framed email.
- Email behavior briefing:
  > "This email just appeared in your inbox. Decide:
  > **(A) Archive / delete without reading the body** — your reaction to the subject line + sender alone. Realistic for cold outreach you don't have time for.
  > **(B) Read but don't reply** — register and move on. May come back to it later (mark as unread) or just ignore.
  > **(C) Reply** — write the response you'd actually send. Estimate the response latency (within an hour / today / this week / much later) and explain why.
  > **(D) Reply, but only after thinking about it** — same as (C) but with explicit deliberation. Often relevant for asks that require a decision.
  > **(E) Forward to someone else** — the email isn't really for you but is for someone in your network. Specify who and what you'd say in the forwarding note.
  > **(F) DM/Slack/text the sender about it** — sometimes the right reply isn't email. If you'd shift channels, say so.
  > Pick one. Don't pick (C) or (D) unless you actually would — most email goes unanswered, and inflating reply rates produces fake data."
- Email voice constraints:
  - Match the formality the sender set (or downgrade one notch).
  - Length proportional to the email and the recipient's investment in the relationship.
  - Stay in your persona's actual voice.
- `persona-ask` reviewer contract.
- Response format below.

Response format:
```
## <persona slug>
**Action:** archive | read-no-reply | reply | reply-after-thinking | forward | switch-channel

**Reply latency (if replying):** within an hour | today | this week | later than a week | indefinite

**Subject-line reaction:** what your gut response to the subject was, before opening — even if you did open.

**Reply text (if any):**
<the actual reply, formatted as email — Subject: Re: ..., greeting, body, sign-off>

**OR if forwarding:**
**Forward to:** <who>
**Forward note:** <what you'd say in the forward>

**OR if switching channel:**
**To:** <which channel>
**Message:** <what you'd say there instead>

**Reasoning:** one sentence on what drove the action.

**References (persona doc):**
  - § <Section>: "<quote>"

**Confidence:** [high|medium|low]
**Email-fit:** [strong|partial|forced] — would this email credibly land with this persona? Forced = the simulation pushed a reply that wouldn't actually happen.
```

### Phase 3 — Synthesize

```
# Email simulation: subject "<subject>"

## Headline
One sentence. e.g. "Predicted reply rate 2/5 (40%). Average latency among repliers: ~24h. Subject line filtered out 1 persona before opening; CTA was the biggest blocker for the 2 non-repliers who did read."

## Action breakdown
- Archived without opening: N
- Read, no reply: N
- Replied (with latency distribution)
- Replied after thinking: N
- Forwarded: N (to whom)
- Switched channel: N (where)

## Predicted reply rate
The single number that matters for a cold or semi-cold email. For B2B context, 5-30% is normal cold-outreach reply rate; below 10% means the email isn't landing.

## Latency distribution
For the repliers: how fast. Fast = high engagement; slow = low priority / needs thinking.

## Subject-line analysis
Reactions to the subject line specifically. If multiple personas would archive without opening, the subject is the failure point — fix that before testing the body again.

## Reply content patterns
Cluster the actual replies into 2–4 themes — what people are answering with. Surface specifically:
- **Yes-and-engaged replies:** the desired outcome shape.
- **Polite-decline replies:** common cold-outreach reception; signal that the email asks for too much too soon.
- **Push-back / counter-question replies:** the email is engaging but the CTA is off.
- **Auto-pilot replies:** ones that look performative and don't really commit to anything.

## Forwarding signal
Personas who'd forward this rather than reply. In B2B, forwarding is sometimes the *desired* outcome (you wanted to reach the right person, not necessarily this person). Surface what they'd forward and to whom — often more useful than the reply itself.

## What would change the response rate
The single most impactful change to subject / body / CTA / sender context that would shift more "read-no-reply" → "reply." Often a CTA scope reduction or a subject-line specificity bump.

## Audience-fit signal
Personas marked `forced` on email-fit had distorted reactions. Common cause: the email doesn't realistically reach this persona via email (they're a different generation, different role, different channel).
```

## Notes

- **Subject lines do most of the work.** If the simulation shows lots of archive-without-open, fix the subject before iterating on the body.
- **Cold email reply rates are honest at panel scale**, more so than other engagement metrics — emails are 1:1 and forced-choice, so the action is more comparable to real human behavior. But results are still directional, not predictive.
- **Latency is undervalued signal.** A reply within an hour is qualitatively different from a reply in a week — speed maps to priority, not just availability. Surface the distribution.
- **Forwarding may be the win condition.** For sales emails especially, "this person forwarded me to the right buyer" is often a better outcome than a reply. Don't penalize forwards as non-engagement.
- For internal emails (employee-to-employee, manager-to-team), the dynamics differ — replies are expected, latency is shorter, the question is more about tone and substance than reply-rate. The skill handles this via the sender-context input but the lens shifts.
- **Auto-pilot replies are a failure mode**, not a success. A reply like "Thanks, I'll take a look" with no commitment isn't engagement — it's politeness. Flag them as such.
