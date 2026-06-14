---
name: persona-roleplay
description: Live rehearsal against a persona who plays the counterpart — a journalist interviewing you, a prospect you're pitching, a boss you're meeting with. You play yourself; the persona stays in character and pushes back; you get coached at the end. Use when the user says "/persona-roleplay", "roleplay", "let me practice a <pitch / interview / 1:1>", "play the journalist / prospect / my boss", "help me rehearse for <X>", or wants to practice a high-stakes conversation rather than research a persona. Inverts the usual setup — here the persona tests *you*.
---

# Persona Roleplay

A rehearsal tool. Every other skill in this plugin treats the persona as the **subject** — you ask, they answer, you learn about them. Roleplay flips the chairs: the persona becomes the **counterpart**, and *you* are the one under the lights. You play yourself; the persona plays the journalist, the prospect, or the boss; and at the end a coach tells you how you did.

Use it to practice a high-stakes conversation before the real one — build the muscle memory, find the question that trips you, pressure-test your answers while the cost of fumbling is zero.

## When to use vs. alternatives

- Use `persona-roleplay` to **rehearse your own performance** in a live exchange — you're the one being graded.
- Use `persona-interview` for the opposite seating: *you* interview the persona to learn what they think.
- Use `persona-council` / `persona-focus-group` to study how personas *react* to an idea, not to practice delivering it.
- Use `persona-review` to critique a finished artifact (a deck, a page), not to rehearse the live conversation around it.

If the user wants to know "what would they think of X," that's research — route to `persona-ask` / `persona-research`. If they want to *survive a conversation with* someone, that's roleplay.

## Two modes

- **Live rehearsal (default).** The user responds in real time, turn by turn. The persona stays in character and pushes back. The coach stays silent until the debrief (or until the user calls a timeout). This is the point of the skill — practice, not preview.
- **Dry-run / auto-play.** Claude plays *both* sides to show how the scene might unfold — e.g. "show me the ten hardest questions a journalist would throw at me and how I might field them," or a full simulated transcript. Use when the user wants a preview or a warm-up before going live, or explicitly asks to see it played out rather than do it themselves.

Default to live. Offer dry-run if the user seems to want a preview ("what would they ask me?", "show me how it'd go").

## Scenario presets

Three built-ins plus custom. Each preset defines who the counterpart is, the user's usual objective, what "winning" looks like, and the failure modes the scene should deliberately probe.

### 1. Journalist interview
- **Counterpart:** a reporter — calibrate to outlet and temperament (friendly trade-press profile → adversarial investigative grilling).
- **You're playing:** the founder / exec / spokesperson being interviewed.
- **Winning:** land your key messages, stay on the record's right side, bridge from hostile questions back to your narrative without sounding evasive, give no quotable own-goals.
- **Probe for:** the gotcha question, the long silence that bait you into over-talking, the false-premise question, the "so what you're saying is…" reframe, the off-the-record trap.

### 2. Sales pitch
- **Counterpart:** the prospect / buyer — ideally a real ICP persona doc (economic buyer, skeptical champion, blocker).
- **You're playing:** the seller.
- **Winning:** earn the next meeting / advance the deal, surface and handle the real objection (not the polite one), tie value to *their* stated pain, avoid the premature discount.
- **Probe for:** "send me a deck and I'll circulate it" (the soft no), price anchoring, the incumbent-tool inertia, the "we don't have budget this quarter," the champion who can't sell internally.

### 3. Meeting with your boss
- **Counterpart:** the manager / boss — calibrate to their known style (supportive, busy and distracted, political, results-only).
- **You're playing:** the employee.
- **Winning:** depends on the ask — get the raise / headcount / project greenlit, deliver bad news without losing trust, push back on a decision while keeping the relationship.
- **Probe for:** "now isn't a good time," the budget deflection, "make the case in one sentence," the counter-ask ("what would you drop to do this?"), the emotional-temperature shift.

### 4. Custom
Anything else high-stakes and interpersonal: investor pitch, board update, negotiation, performance review (either chair), customer escalation, podcast appearance, partner/co-founder hard conversation, media-trained crisis Q&A. Build the counterpart and success criteria from the user's description using the same shape as the presets.

## Inputs

- **Scenario** — preset or custom. If unclear, ask.
- **The counterpart** — either a **persona slug** (resolved against `./.personas/`, grounded in the doc) or an **archetype** sketch ("a hostile TechCrunch reporter," "my CFO"). See Phase 1 for the difference and the honesty it requires.
- **Your objective** — what "winning" this conversation means *to the user*. This becomes the debrief's scorecard. If they don't volunteer it, ask — without an objective there's nothing to coach against.
- **Difficulty / temperament** — `friendly` / `realistic` / `hostile` (easy / default / hard mode). Shapes how hard the counterpart pushes. Default `realistic`.
- **Optional materials** — the pitch, the deck, the news hook, the raise number, the bad news to deliver. Anchor the scene in the real thing where it exists.
- **Length** — rough number of exchanges or a time box. Default: run until the objective resolves or ~8–12 exchanges, whichever comes first.

## Workflow

### Phase 0 — Set the scene

Confirm the four load-bearing inputs in one or two lines: scenario, counterpart, the user's objective, difficulty. Restate them back so the user can correct the framing before you commit. If `./.personas/` is empty and the user named a persona, point them at `persona-create` / `persona-distill` — but archetype counterparts (below) work without any personas, so roleplay never hard-stops the way the research skills do.

### Phase 1 — Cast the counterpart

Two paths:

- **Persona doc exists** (e.g. pitching to a real ICP persona). Resolve and load it exactly as `persona-ask` Phase 1–2: read the whole doc, weight `## Psychographics`, `## What makes them bounce`, and `## What would actually convince them` most heavily — those drive the objections and the openings. The counterpart's pushback should be **grounded in the doc**; note `last_distilled_at` and source thinness for the debrief's confidence read.
- **Archetype only** (a generic journalist, "your boss" with no doc). Build a short **scenario character card** from the user's description — role, what they want out of the meeting, their temperament, their two or three likely pressure tactics. Be honest in the debrief that this counterpart is an *archetype*, not a grounded persona, and offer to turn it into a reusable persona via `persona-create` if the user will rehearse against it again.

State which path you're on in one line before the scene starts, so the user knows how grounded the counterpart is.

### Phase 2 — Run the scene (live)

Open in character with a single line that sets the room — where they are, the counterpart's opening move. Then hand the floor to the user and **stay in character every turn** until the scene ends or a meta-command interrupts.

Rules for the counterpart while live:
- **Stay in role.** Do not break to be helpful, explain yourself, or hedge. One persona, one voice, no narrator.
- **React to what the user actually said** — not a charitable paraphrase of what they meant. If they dodged, the counterpart notices the dodge. If they over-promised, the counterpart writes it down.
- **Push to the difficulty level, no softer.** A `realistic` prospect doesn't fold because the user sounded nice. A `hostile` journalist doesn't accept the first bridge. Going easy produces useless practice — that's the cardinal failure mode here.
- **One move per turn.** One question, one objection, one reaction. Don't unload five questions at once; that's not how the real conversation goes and it lets the user cherry-pick.
- **Ground, think, then talk — and here you can show it.** Each counterpart turn runs the contract: privately **Ground** (what in the doc drives this move) and **Think** (their real read of what you just said), then **Talk** (the in-character line). Unlike the research skills — where Grounding and Thinking stay hidden — the user *wants* the audit trail here; seeing the subtext is most of the coaching value. So default to **glass-box**: after each spoken line, add a short, visually separate **read** aside — one line of the counterpart's thinking plus the `§ section` it's grounded in (or "(archetype — best guess)", marked lower-confidence). Offer **immersive** mode (reads hidden until the debrief, or revealed on demand via `read`) for users who'd rather not see the counterpart's hand mid-scene; confirm which they want at the top of the first scene.
- **Track quietly.** Note the user's strongest moment, the moment it slipped, and what the counterpart privately concluded — you'll need all three for the debrief.

### Phase 3 — Debrief & coach

Drop character. Switch to **coach** — honest, specific, on the user's side but not flattering. This is the actual deliverable; the scene was just the setup.

```
# Roleplay debrief: <scenario>

## Result vs. your objective
Did you get what you came for? Met | Partially | Missed — one line on why, measured against the objective from Phase 0.

## What landed
The 1–3 moves that worked, quoting what you actually said and why it worked on *this* counterpart.

## What cost you
The 1–3 moments that hurt — the dodge they clocked, the over-promise, the place you talked past the close. Quote your own line back; vague feedback can't be acted on.

## What they were really thinking
The subtext — what the counterpart concluded that they didn't say out loud. Where a persona doc backs this, cite it (§ section + confidence, per persona-ask). Where it's an archetype, say so and mark it lower-confidence.

## The one fix
The single highest-leverage change for next time. Not a list — the one thing that would have moved the result most.

## Run it back?
Offer a redo: same scene to apply the fix, a harder difficulty, or a different counterpart. Rehearsal compounds with reps.
```

Close with the simulation disclaimer.

## Meta-commands (in-session controls)

The user can step out of the scene at any time with these. Recognize them on a line by themselves:

- **`timeout`** / **`coach`** — pause the scene, drop character, give a quick hint or read on how it's going, then resume where you left off.
- **`rewind`** — discard the last exchange and replay the counterpart's move so the user can retry a fumbled answer.
- **`harder`** / **`easier`** — adjust the counterpart's temperament mid-scene without restarting.
- **`aside <note>`** — the user adds context or direction out of character (e.g. "aside: assume they already read the deck"); fold it in and continue.
- **`read`** / **`mind`** — reveal what the counterpart is thinking *right now* and what in the persona doc it's grounded in (a one-time peek), then resume in character. Useful in immersive mode, or any time the user wants the subtext on demand.
- **`end`** — stop the scene now and go straight to the debrief.

Mention these once at the top of the first live scene so the user knows the controls exist; don't repeat them every turn.

## Grounding, confidence, honesty

- A doc-backed counterpart's objections come from the doc, not from convenience. In **glass-box** mode the grounding is visible each turn as a short read aside — e.g. _Read: they think you dodged the budget question and are testing whether you'll fold — § What makes them bounce: "vague ROI claims" [high]_ — kept separate from the spoken line so it never breaks character. In **immersive** mode it stays in your head until the debrief. Either way, the debrief makes it explicit: cite the sections behind "what they were really thinking," with a confidence tag, exactly as `persona-ask` does.
- An **archetype counterpart is a best-guess, not a grounded persona.** Say so plainly in the debrief. The real journalist / prospect / boss has specifics you didn't simulate.
- The coach is honest. If the user bombed, the debrief says so kindly and specifically. Flattery wastes the rep.

> _— Simulated roleplay. The counterpart is a persona/archetype, not the real person — treat this as practice, not prediction. The actual journalist, prospect, or boss will surprise you in ways no simulation can. Rehearse, then go in ready to adapt._

## Notes & anti-patterns

- **Don't break character to be helpful mid-scene.** The user has `timeout` for that. Unbidden coaching during the dialogue destroys the rehearsal — the glass-box `read` aside doesn't count (it's a separate channel, not the counterpart stepping out of role).
- **Don't soften the pushback to be nice.** A counterpart who folds easily teaches the user nothing. The kindness is in the debrief, not the scene.
- **Don't let a high-status counterpart steamroll into incoherence either** — `hostile` means tough and probing, not cartoonish or abusive. The goal is a hard but realistic rep.
- **Don't grade against your own standard — grade against the user's objective.** A pitch that "sounded great" but didn't advance the deal missed. Say it missed.
- **One counterpart per scene.** A panel grilling is a different format (closer to a press-conference variant of `persona-council`); if the user wants multiple interrogators, flag it and either run them in turns or suggest council.
- If the user keeps winning too easily, raise the difficulty before declaring mastery — easy wins are usually a too-soft counterpart, not a finished skill.
