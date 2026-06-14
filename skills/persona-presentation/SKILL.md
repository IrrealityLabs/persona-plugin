---
name: persona-presentation
description: Get slide-by-slide audience feedback on a presentation from your personas, then a curated change list. Feed it any mix of a deck (PPTX / PDF / Keynote / Slides export), a run-of-show or table of contents, and/or a transcript or video of you presenting — the personas sit through the whole talk as your audience, react segment by segment, and the panel feedback is synthesized into prioritized fixes. Use when the user says "/persona-presentation", "review my deck / pitch / talk", "what would my audience think of this presentation", "give me slide-by-slide feedback", "test this pitch deck on the personas", or uploads a deck/transcript/recording and asks how it lands.
---

# Persona Presentation

The personas are your **audience**. They sit through the talk — as a deck, an outline, a transcript, a recording, or any combination — and react the way that specific audience would: where they lean in, where they check their phone, where the argument loses them, what they'd remember walking out. You are the **moderator**: you normalize the inputs into one ordered set of segments, spawn one subagent per persona, and curate the panel's reactions into a prioritized change list.

The value is *audience-specificity*. The same deck lands completely differently on an investor, a technical buyer, and an internal exec. "Slide 7 is confusing" is weak. "Slide 7 — you spent 90 seconds on architecture, but I'm the economic buyer; I'd already decided by slide 4 whether this clears my ROI bar, and this slide doesn't touch it, so you lost me here" is the goal.

## When to use vs. alternatives

- Use `persona-presentation` to test a **talk or deck** — something delivered slide/section by section to an audience — and get slide-anchored feedback plus a narrative-arc read.
- Use `persona-review` for a static asset with no sequence (a landing page, an ad, one-pager).
- Use `persona-user-test` for a live product surface (URL flow) or a non-presentation video.
- Use `persona-roleplay` to *rehearse delivering* the pitch live against one counterpart, rather than collect audience feedback on the built deck.

If the user wants to practice giving the talk, that's `persona-roleplay`. If they want the audience's read on the talk itself, that's this skill.

## Inputs — any combination

Feed it one or more of these. More inputs = richer feedback, but any single one works.

| Input | What it unlocks | Mode |
|---|---|---|
| **Deck** — PPTX / PDF / Keynote / Google Slides export | Per-slide visual + content reactions | Deck mode |
| **Run of show / table of contents** — a text outline, no slides yet | Structure + planned-content feedback *before* you build | Outline mode |
| **Transcript** — what you said (or plan to say), text | Delivery + content, aligned to slides if a deck is present | Delivery mode |
| **Video** — a recording of you presenting | Delivery + content from frames; slides captured if it's a screen-share | Delivery mode |

Combinations stack: **deck + transcript** is the richest (each slide gets both "what they saw" and "what you said"); **deck alone** gives content + arc; **outline alone** is the cheap pre-design pass; **video alone** gives a directional read of the whole experience.

Delivery feedback (from transcript or video) is **directional** — personas reason from text and frames, not from watching you live. They'll catch pacing-by-word-count, filler, a slide you dwelled on too long, a claim that landed flat. They'll miss vocal tone, timing, and room energy. Mark it as directional in the output, same caveat as `persona-user-test` video mode.

## Sample size

The **audience** is the panel. 3–6 personas. Below 3 you lose the cross-audience pattern; above 6 the per-slide synthesis gets unwieldy. The selection question is "who is this talk actually *for*?" — pick the personas who match the real audience (investors for a raise, practitioners for a conference talk, the buying committee for a sales deck). If the user named personas, use those; otherwise default to all personas in `./.personas/`. If the roster is broader than the real audience, the orchestrator picks the matching personas by reading their docs (or asks the user who's in the room).

## Workflow

### Phase 0 — Announce, and pin down the audience and the goal

Two things must be crisp before anything else:

1. **The audience** — who is in the room. If the personas in `./.personas/` aren't a clean match for the real audience, say so and offer `persona-create` / `persona-distill` to add a fitting one.
2. **The goal of the talk** — what it's trying to *do*: raise the round, close the deal, get the project greenlit, teach a concept, change a belief. Every reaction gets judged against this goal, so without it the feedback is just taste. If the user didn't say, ask.

Then announce: "Running your <talk> past <N> personas as your audience: <names>. They'll react segment by segment, I'll synthesize. These are audience simulations, not a real dry-run."

If `./.personas/` is empty or missing, stop and point at `persona-create` / `persona-distill` — none of this works without personas.

### Phase 1 — Ingest and normalize into an ordered segment list

Everything becomes one ordered list of **segments**. A segment is one unit of the talk — usually one slide — carrying whatever inputs you have for it: `{ index, title, slide_image?, slide_text?, spoken_text?, caption }`. Render/extract **once**; every persona reacts to the same segments.

Save artifacts under a per-run dir, e.g. `./.persona-research-runs/<timestamp>/`.

**Deck (PPTX / Keynote / Google Slides):** convert to PDF, then to per-slide images. Pull slide text + speaker notes if you can.
```bash
# PPTX/Keynote → PDF (LibreOffice); Google Slides: export to PDF/PPTX first
libreoffice --headless --convert-to pdf --outdir ./run deck.pptx   # or: soffice ...
# PDF → one PNG per slide
pdftoppm -png -r 110 ./run/deck.pdf ./run/slides/slide        # → slide-1.png, slide-2.png, ...
# Optional: slide text + speaker notes (if python-pptx is available)
python3 -c "from pptx import Presentation; [print(f'--- {i+1} ---', *[sh.text_frame.text for sh in s.shapes if sh.has_text_frame], (s.notes_slide.notes_text_frame.text if s.has_notes_slide else '')) for i,s in enumerate(Presentation('deck.pptx').slides)]"
```

**PDF deck:** skip the conversion — `pdftoppm` straight to images. (You can also read pages directly with the Read tool's PDF `pages` param to pull text/structure.)

**Run of show / table of contents (text):** parse into ordered segments — one per line/section. `title` = the item; `slide_text` = any description. No image. This is Outline mode: feedback is about structure and planned content, not visuals.

**Transcript (text):**
- If it has slide markers or timestamps (`Slide 4:`, `[00:12:30]`, `[next slide]`), split on them and map each chunk's `spoken_text` to the matching segment.
- If it's plain prose with a deck present, align best-effort by topic and **state the alignment method + confidence** in the announce ("aligned transcript to slides by topic match — medium confidence; correct me if a slide is mismapped").
- If there's no deck, the transcript *is* the segments — split by topic/paragraph.

**Video:** chunk and extract frames like `persona-user-test` video mode.
```bash
ffmpeg -i talk.mp4 -c copy -map 0 -segment_time 120 -f segment ./run/chunks/chunk-%03d.mp4
for c in ./run/chunks/*.mp4; do ffmpeg -i "$c" -vf "fps=1/10" "./run/frames/$(basename "${c%.*}")-%03d.jpg"; done
```
Frame rate: talking-head ≈ 1 frame/30s; screen-share of slides ≈ 1 frame/5–10s (so each slide is captured). If a screen-share, the frames double as slide images. Pair with a transcript when available.

**No rendering tools?** If `libreoffice`/`pdftoppm`/`ffmpeg` aren't installed, fall back to text-only segments (slide text, notes, transcript) and tell the user the personas are reading the talk, not seeing it — visual-design reactions will be absent. Offer the install one-liners (`brew install libreoffice poppler ffmpeg` on macOS).

### Phase 2 — Select the audience

If the user named personas, use those; otherwise default to all personas in `./.personas/`. If the roster is broader than the real audience, the orchestrator picks the personas who match who's actually in the room by reading their docs (or asks the user). Aim for ~4–5.

### Phase 3 — Cost check

Use `persona-research/references/cost-estimator.md`. **Default dispatch is one subagent per persona, each seeing the whole talk** (see Phase 4 for why) — so the base cost is ~N_personas runs, each carrying all slide images + text. Estimate: ~(slides × ~1.7K image tokens + text) per persona. A 30-slide deck × 5 personas ≈ 5 runs × ~60–80K tokens ≈ moderate. Video adds frame tokens per chunk and may force chunked dispatch (see Notes) — estimate it like user-test video mode and confirm before launching if it'll exceed ~$50 or the deck is image-heavy and >60 slides.

### Phase 4 — Spawn the panel (one subagent per persona, in parallel)

Default: **one subagent per persona, each receiving the full ordered segment list.** A presentation is consumed as a whole — the audience sits through all of it — so a persona that sees every segment in one pass can judge the *narrative arc* (does it build, where does attention sag, does the close pay off the open) that per-slide fan-out would destroy. This is also far cheaper than slides × personas. Only fall back to chunked dispatch (per-persona-per-chunk, carrying running notes) when the inputs genuinely don't fit one context — a long video, or a very large image-heavy deck (see Notes).

Each subagent prompt contains:
- The persona doc path — read in full, inhabit it, you are this audience member.
- The full ordered segment list: each segment's image (inline), slide/notes text, and spoken text, with its index + caption, **in order**.
- The talk's **goal** (from Phase 0) and the audience framing — "you are sitting in the audience for this; react as you actually would."
- The `persona-ask` Ground, think, then talk (Grounding → Thinking → Talking) contract (load it) — ground every finding before reasoning, severity tagged honestly, no generic praise, quote the exact slide/line.
- The presentation response format below.

**Presentation response format (per persona):**
```
## Grounding (private — orchestrator only; not aggregated)
The persona-doc sections that bear on this, cited first: § <Section>: "<…>" + a confidence read [high|medium|low|off-pattern]. One line on how well my persona doc supports these reactions overall.

## Thinking (private — orchestrator only)
Private reasoning over that grounding: what this persona would genuinely conclude, where the evidence is thin.

## At-a-glance
Would this talk achieve its goal *for me*? One line. Plus my engagement arc in a word or two ("hooked early, lost me mid, recovered at the ask").

## Slide-by-slide
One block per segment I had a real reaction to (skip the ones I'd have no reaction to — silence is data, don't pad).

### Slide <n>: <title>
**Saw / heard:** what was on the slide and/or what you said (quote it).
**Reaction:** "First-person, decision-making voice — what went through my head here."
**References (persona doc):** § <Section>: "<quote/paraphrase>"
**Engagement:** leaned in | neutral | drifted | lost — one word.
**Clarity:** clear | had to work | confused.
**Confidence:** [high|medium|low] + reason.
**Suggested change:** concrete — cut it, tighten to one line, move earlier, add the number I needed, reframe for me. "No fix, but it repelled me" is allowed if honest.

## Narrative arc (whole-talk)
- **The hook:** did the open earn my attention in the first slide or two?
- **The through-line:** could I state your core argument in one sentence? If not, where did it fragment?
- **The close / ask:** did it land, and did I know exactly what you wanted from me?
- **Pacing:** where did the talk drag or rush *for me*?

## Delivery (only if transcript/video given — mark directional)
Filler, slides you dwelled on past their value, a claim that landed flat, energy dips I can infer from the words/frames. Flag as directional.

## Where you lost me
The single segment where, if I were really in the room, my attention or buy-in dropped most — and why. "Didn't lose me" is valid.

## The one change
If you could change only one thing to move *me* toward the goal, this is it.
```

A finding with no persona-doc reference is malformed — the subagent drops or re-grounds it.

### Phase 5 — Synthesize and curate

Compile one panel report. Weight by severity × confidence × cross-persona convergence, exactly as `persona-review` Phase 5. Don't summarize away disagreement — where two audience personas split, that's a real targeting decision. Each persona's Grounding + Thinking stay with you as per-persona audit fields — never aggregated into the report; only the public reactions are synthesized.

```
# Presentation feedback: <talk descriptor>  ·  Goal: <the goal>

## Headline
One sentence: does the talk achieve its goal for this audience, and the dominant pattern. ("Strong hook, but you lose the buyers on the technical middle and the ask is buried.")

## Slide-by-slide heat map
A compact per-slide read: engagement (lean-in / neutral / drift / lost) and clarity across the panel, who flagged what. Make the sag points visible at a glance — e.g. a monospace strip:
`S1 ▔ S2 ▔ S3 ▁ S4 ▁ S5 ▔ ...`  (▔ engaged · ▁ lost) with a one-line key.

## Where you lost the room
The 1–3 segments where multiple personas drifted or got confused — the highest-leverage slides to fix. Who, why, the strongest suggested fix.

## Narrative arc
Hook / through-line / close, synthesized. Can the panel state your core argument in one sentence? Where did the story fragment or drag?

## Delivery (only if transcript/video — directional)
Cross-persona delivery notes, marked directional.

## Per-persona read
For each persona: 3–5 lines — would the talk achieve its goal for them, their engagement arc, the 1–2 reactions that defined their experience.

## Where the panel split
Any place audiences reacted oppositely — usually a "who is this talk really for?" decision for the user to make.

## Curated change list
Numbered, prioritized, slide-anchored. Each item tagged: **Cut · Tighten · Reorder · Rewrite · Add**, which slide(s), which persona(s) it serves, and severity. Ordered so the top items are the room-losing blockers with the most cross-persona support. This is the deliverable — the user should be able to work straight down it.
```

Close with the disclaimer:

> _— Simulated audience panel, grounded in the persona docs in `./.personas/`. Not a real dry-run or focus group; delivery feedback from a transcript/video is directional (the personas read frames and words, they don't watch you present). Use this to prioritize edits, then pressure-test the talk with real people before it matters._

## Notes

- **Why whole-deck-per-persona, not per-slide-per-persona:** a deck is one continuous experience. Fanning out per slide multiplies cost by the slide count *and* blinds each subagent to the arc, which is half of what makes a talk work. Reserve chunked dispatch for inputs that can't fit one context.
- **When to chunk anyway:** a video longer than ~10–15 min, or a deck so large/image-heavy it overflows a single subagent's context. Then dispatch per-persona-per-chunk, carry the persona's running notes forward (talks are temporal), and reassemble the arc in synthesis — same machinery as `persona-user-test` video mode. Cap parallel chunks at ~4 to stay under rate limits.
- **Outline mode is the cheapest, earliest win.** If the user only has a run of show, run it — structure feedback before slides exist saves the most work. Say plainly that there's no visual/delivery read yet.
- **Alignment honesty.** When you map a transcript to slides by topic rather than explicit markers, state the confidence and invite correction. A mis-aligned transcript produces confident-but-wrong per-slide delivery notes.
- **Don't pad.** A persona with no reaction to a slide should say nothing about it. Twelve "this slide was fine" lines bury the three that matter.
- Re-runs after edits are fresh reviews — each call is self-contained; don't try to remember the prior deck.
