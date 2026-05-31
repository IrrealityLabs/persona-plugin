---
name: persona-user-test
description: Run a usability/user-testing study with personas reacting to a real UI flow — drive through a URL with `agent-browser`, capture screenshots at each step, and have personas react to each screen. Also supports video (chunked via ffmpeg). Use when the user says "/persona-user-test", "have the personas walk through this site", "user test this flow", "test this video on the personas", or wants behavioral reactions to a real product surface rather than copy critique.
---

# Persona User Test

The personas walk through a real UI (URL) or a video, screen by screen / frame batch by frame batch, and react. Outputs annotated transcript per persona plus a synthesized usability report.

Two modes:
- **URL mode** — drives a browser through a task flow with the `agent-browser` CLI (same tool `compound-engineering/ce-test-browser` uses), captures screenshots at each step.
- **Video mode** — chunks the file with ffmpeg, extracts frames per chunk, hands frames to per-chunk persona subagents.

## When to use vs. alternatives

- Use `persona-user-test` when there's a *real product surface* to react to (live URL or recorded video).
- Use `persona-review` for static-asset critique (copy, images, mocks) without a flow.
- Use `persona-presentation` for a slide deck or recorded talk — it gives slide-by-slide + narrative-arc feedback, not screen-by-screen UX friction.
- Use `persona-ab-test` to compare two or more flows / pages against each other.

## Sample size

- **URL mode:** 3–5 personas. Below 3, you lose the cross-persona pattern. Above 5, screenshots × personas × screens compounds fast.
- **Video mode:** 3–5 personas typical. Strongly recommend ≤3 for videos >15 minutes.

## Prerequisites

### URL mode

- A running site at a known URL (local dev server or live).
- `agent-browser` CLI installed. Check with `command -v agent-browser`; if missing, point the user at the compound-engineering `/ce-setup` flow (or `npm install -g @every/agent-browser` if they're not in that ecosystem) and stop until installed.

### Video mode

- A local video file.
- `ffmpeg` installed. Check `command -v ffmpeg`; if missing, point them at `brew install ffmpeg` (macOS) or platform equivalent and stop.

## Cost warning — always run before launching

Calculate before launching, using `persona-research/references/cost-estimator.md`:

- **URL mode:** N_screens × N_personas subagent runs. Each run ~15–25K tokens plus screenshot image tokens (~1500–2000 each). 5 screens × 5 personas ≈ 500K tokens ≈ ~$10.
- **Video mode:** chunks × personas runs. Each run carries ~12 frame images plus persona reasoning. 30-min video × 5 personas ≈ 2.4M tokens ≈ ~$40–60. 1-hour × 8 personas ≈ ~$200+.

**Hard cap suggestion:** stop and re-confirm if estimate exceeds $50, or video > 60 minutes, or personas × chunks > 100 runs.

## Workflow — URL mode

### Phase 1 — Define the task flow

The user must specify *what they want the personas to do*. "Click around" is too vague. Specific examples:
- "Land on /, sign up, complete onboarding, reach first dashboard."
- "Land on the pricing page, pick a plan, hit checkout."
- "Try to find the export-data setting."

Get this crisp. Without a task, the reactions are about aesthetics, not usability.

### Phase 2 — Capture the flow

Drive through the flow once with `agent-browser`, capturing one screenshot per logical step. Save screenshots into a per-run directory (e.g. `./.persona-research-runs/<timestamp>/screens/01-landing.png`, etc.) along with a one-line caption per screen describing what action was taken to get there.

Don't re-drive the browser once per persona — drive once, screenshots are the source. Personas all see the same flow.

### Phase 3 — Sample personas

Use `persona-sample` for 5 with the task description as the topic. Override to all if user wants all and count is ≤5.

### Phase 4 — Per-persona reactions (parallel)

Spawn one subagent per persona. Each prompt includes:
- Persona doc path.
- The task flow description.
- All screenshots (inline images) with captions, in order.
- The `persona-ask` reviewer contract.
- The user-test response format below.

User-test response format:
```
## At-a-glance
Did I complete the task / would I have? Where, on a scale of 1–7, would I rate the ease of this flow for me?

## Step-by-step reactions
### Step 1: <caption>
**Reaction:** "Quoted first-person reaction."
**References:** § <persona doc section>: "..."
**Friction:** none | minor | blocker — one sentence on what caused it (if any).
**Confidence:** [high|medium|low]

[repeat per step]

## Where I would have abandoned
The screen + reason, if I would have left somewhere. "Would not have abandoned" is a valid answer.

## What would have made me convert/complete
The single most impactful change.
```

### Phase 5 — Synthesize

```
# User test: <task>

## Completion rate
N of M personas would have completed the task. Where the others dropped.

## Friction map by screen
For each screen: which personas flagged friction, severity, dominant reason. Heat-map style.

## Abandonment points
Where multiple personas would have left, and why.

## Top changes
3–5 prioritized changes, sorted by # of personas affected × severity.

## Per-persona sentiment trajectory
For each persona: their 1–7 ratings per step, surfacing where each one's experience diverged.
```

## Workflow — video mode

### Phase 1 — Chunk and extract frames

```bash
mkdir -p ./.persona-research-runs/<timestamp>/chunks
# Split into 2-min chunks
ffmpeg -i <video> -c copy -map 0 -segment_time 120 -f segment \
  ./.persona-research-runs/<timestamp>/chunks/chunk-%03d.mp4

# Per chunk: extract 1 frame every 10s (12 frames per 2-min chunk)
for chunk in chunks/*.mp4; do
  ffmpeg -i $chunk -vf "fps=1/10" frames/${chunk%.*}-%03d.jpg
done
```

Adjust frame rate based on video content density. For talking-head: 1 frame every 30s is fine. For UI walkthroughs: 1 frame every 5–10s.

### Phase 2 — Per-chunk × per-persona reactions

For each chunk, spawn one subagent per persona (so total runs = chunks × personas). Each prompt includes:
- Persona doc path.
- The chunk's frame images, in order.
- A one-line summary of what the chunk is about (you provide based on video metadata or the user's brief).
- Running notes from the persona's prior chunks (carry forward — videos are temporal).
- User-test response format adapted for video (replace "step" with "moment", drop screen-by-screen, do moment-by-moment).

### Phase 3 — Synthesize

Same shape as URL mode synthesis, but:
- "Completion" → "stayed engaged through the end" — track where each persona's engagement waned.
- "Step-by-step friction" → "sentiment timeline" — chart whose attention dropped where.
- "Abandonment" → "where they'd have stopped watching."

## Notes

- `agent-browser` reads HTML and screenshots — it can't simulate a user's actual cursor or detect things only visible during interaction (hover states, animations). Flag this limitation in the output if relevant.
- Video reactions are an approximation. Personas don't *watch* in real-time; they reason from frames. They will catch big-picture content reactions; they will miss subtle pacing / vocal-tone signals that affect real-viewer engagement. Mark video results as more directional than URL-mode results.
- For long videos, batch chunks rather than running them all in parallel — the rate limits will bite. 4 chunks in parallel is a reasonable cap.
