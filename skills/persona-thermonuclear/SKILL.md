---
name: persona-thermonuclear
description: The maximum-effort idea exploration — point the entire persona arsenal at one idea and stretch it in every direction at once. Not a critique and not a vote; a no-holds-barred divergent-then-convergent exploration that generates stretch directions, fans out generative + reactive + adversarial passes across all personas over multiple rounds, and synthesizes an exhaustive idea map. This is the most expensive skill in the plugin — opt-in only. Use when the user says "/persona-thermonuclear", "go thermonuclear on this idea", "explore this idea as hard as possible", "stretch this idea in every direction", "maximum exploration", "throw everything at this idea", or wants the biggest possible AI-persona exploration of a concept before committing.
---

# Persona Thermonuclear

The nuke. Every other skill points *one* lens at an idea — brainstorm generates, council attacks, focus-group reacts, roast burns. This one fires **all of them, on the idea *and* on deliberately mutated versions of it, across many personas, over multiple rounds** — then converges hard. The goal is not to judge the idea or pick a winner; it's to **explore the idea's full possibility space** and come back with the strongest reframings, the fatal objections, the protected wild-cards, and the few bets worth making.

It is deliberately maximal and deliberately expensive. It is **not** in the README and **not** a default `persona-research` method — reach for it only when an idea is important enough to justify the spend.

## When to use vs. alternatives

- Use `persona-thermonuclear` when you want **the maximum** — to wring an idea dry before betting on it, or to break out of a stuck framing.
- Use `persona-brainstorm` for collaborative idea *generation* (one generative lens).
- Use `persona-council` to pressure-test a *decision* adversarially (one attacking lens).
- Use `persona-focus-group` for *reactive* group dynamics (one reactive lens).
- Use `persona-roast` for a fast brutal gut-check.

Thermonuclear is what you get when you run all of those, *plus* stretch the idea itself, *plus* loop until it stops producing anything new. If a single lens will do, use the single lens — this is for when nothing less than everything will satisfy you.

## The discipline (brainstorming best practices, enforced)

Maximal effort without discipline is just noise. This skill bakes in what actually makes exploration productive:

- **Diverge before you converge.** Phases 1–4 are pure generation — *no judgment, no ranking, no killing ideas*. Convergence and culling happen only in Phase 5–6. Mixing them early collapses the space.
- **Verbalized Sampling against mode collapse.** Everywhere the model generates (stretch directions, ideas, mutations), prompt for a *probability-weighted spread* of candidates and deliberately keep the low-probability tail — the unusual-but-valid ones — not the first/most-typical answer (see `persona-create`, finding #10). This is the single biggest lever against an exploration that just restates the obvious.
- **Yes-and, then no-but.** Generative passes are additive — build on and combine, never critique. The critique comes later, concentrated, in the survival phase.
- **Quantity breeds quality.** Push for volume in divergence; the strongest reframes usually arrive late, after the obvious ones are exhausted.
- **Maximize cognitive diversity.** Use every persona, and the most *different* ones carry the most weight. A homogeneous panel produces a narrow exploration no matter how many rounds you run.
- **Protect the wild-cards.** The reason to run *this* rather than ask one model for a list is the spread across genuinely different minds. Carry the weird, low-probability ideas all the way to the synthesis — they're the deliverable, not noise.
- **Survive, don't average.** The strongest emergent ideas get adversarially stress-tested at the end (steelman vs. red-team), not blended into a mush of consensus.
- **Ground, think, talk.** Every persona turn follows the `persona-ask` contract — private **Grounding** (what in their doc drives this) + **Thinking**, then the public contribution — so even a maximal run stays auditable.

## Panel selection

Named personas → those. Otherwise **all of them** — thermonuclear wants breadth. Two extra moves unique to this skill:

- **Widen first if the roster is thin or homogeneous.** Cognitive diversity *is* the exploration surface. If you have few personas, or they cluster, offer to spin up a spanning set with `persona-create` batch (a contrarian, an outsider to the category, a future user, an adjacent-market user) before launching. This is free and local.
- **Assign lenses to personas by temperament.** A skeptical persona red-teams better; an optimist generates further; an outsider sees the adjacent market. Use the docs' `## At a glance` to cast roles in later phases.

## Cost — confirm before launching, always

This is the most expensive thing the plugin does: (personas) × (stretch directions) × (passes) × (rounds). A serious run is easily **hundreds of subagent calls**. Use `persona-research/references/cost-estimator.md`, show the estimate, and **get explicit confirmation**. Offer a dialable scope:

- **Tactical** (~1 control idea, ~5 directions, all personas, generative + 1 adversarial pass, 1 round) — a strong exploration for a real cost.
- **Strategic** (~8–12 directions, generative + reactive + adversarial, 2 rounds, survival phase) — the default "thermonuclear."
- **Unbounded** (loop-until-dry, widen the panel, every pass, every survivor stress-tested) — only on explicit request, and scale it to the user's stated budget if they gave one.

State the scope you're running and roughly what it will cost before any fan-out.

## Workflow

### Phase 0 — Frame the idea

Get the idea stated in one crisp sentence, plus what a "win" would look like and any hard constraints (so the stretch phase can deliberately *violate* them later). Confirm scope + cost (above).

### Phase 1 — Stretch the idea into directions (diverge)

Don't explore the idea as given — explore a *fan* of mutated framings. Generate stretch directions with Verbalized Sampling (prompt for a probability-weighted spread; keep the weird ones), seeded by these lenses:

- **Scale** — 10× / 0.1× the users; price → 0 or × 100; mass-market vs. ultra-niche.
- **Invert** — do the opposite; assume the core premise is false; who builds the anti-version.
- **Adjacent** — nearest-neighbor markets, users, jobs-to-be-done, channels.
- **Time-shift** — this in 10 years; this 10 years ago; what makes it inevitable vs. a fad.
- **Constraint flip** — infinite budget / zero budget / ship in a week / the obvious approach is banned.
- **Recombine** — mash it with an unrelated domain or a current trend.
- **Job-to-be-done** — what is it *really* hired for; what else competes for that job.
- **Pre-mortem / pre-triumph** — it's a year later and it failed (why?); now it wildly succeeded (why?).

Produce a deduped set of stretch directions (Strategic ≈ 8–12). This set is the exploration's spine.

### Phase 2 — Generative fan-out (diverge, additive)

For each direction, fan out personas to generate against it — reuse `persona-brainstorm`'s additive, yes-and discipline (build on / combine / extend; no critique; Verbalized Sampling for diversity; one wild-card each). Personas run in parallel; pool their public ideas per direction. This is the bulk of the spend and the bulk of the value.

### Phase 3 — Reactive cross-pollination (diverge → first heat)

Feed the pooled ideas back so personas react to and build on *each other across directions* — `persona-focus-group` dynamics, but generative rather than evaluative. New ideas that only emerge from collision belong here. Still additive; still no culling.

### Phase 4 — Escalation rounds (loop until dry)

Repeat Phases 1–3 on the *most generative* material — re-stretch the strongest mutations, push further out. Stop when a round produces little genuinely new (the builds are restatements) or the scope budget is hit. Track a simple "new-direction" count per round so you can see the tail flatten. Cap rounds to the chosen scope.

### Phase 5 — Survival (converge — now the critique)

Only now does judgment enter. Take the strongest emergent ideas/reframes and stress-test each hard:

- **Steelman vs. red-team** — one pass builds the most ambitious defensible version (`persona-council` endorsers); one pass tries to kill it (`persona-roast` / council rejecters / a pre-mortem). Majority-kill ⇒ it doesn't survive.
- **"What would have to be true"** — for each survivor, the assumptions it rests on, and which are testable.

Keep the wild-cards in the running unless they're genuinely refuted — novelty earns a pass through this gate.

### Phase 6 — Synthesize the idea map

The deliverable is an exhaustive but *organized* map, not a transcript:

```
# Thermonuclear exploration: <idea>

## Strongest reframings
The 2–5 most powerful ways the idea got recast (often more valuable than the original framing). For each: the reframe, who/what surfaced it, and why it's stronger.

## The exploration map
Each stretch direction explored and the one thing it surfaced — so the user can see the whole space that was covered (and what was thin).

## Emergent ideas (clustered + ranked)
Ideas grouped by theme, ranked by cross-persona support × novelty. Show build-chains where an idea grew across rounds.

## Wild-cards worth keeping
The 3–5 low-probability ideas that survived. Which persona's tail each came from. These are the point.

## Kill-shots
The fatal objections that survived the survival phase, and — for the ideas worth saving — what would have to be true to overcome each.

## The bets
The 1–3 directions actually worth pursuing, each with its single biggest open question and the real research/experiment that would settle it.
```

Close with the standard simulation disclaimer.

## Notes & anti-patterns

- **Don't converge early.** The most common failure is the model starting to rank/cull in Phase 2. Generation and judgment are separate phases for a reason — hold the line.
- **Don't let it collapse to consensus.** A thermonuclear run that ends in everyone agreeing has failed; surface the genuine forks and the surviving disagreement.
- **This is exploration, not validation.** It maps what's *possible* and *plausible* through your personas — it does not tell you the idea is *right*. Every output is a hypothesis for real customers, not a verdict (and it does not measure how accurate the personas themselves are).
- **Honor the cost ceiling you quoted.** If the run is bigger than confirmed, stop and re-confirm — don't silently escalate the nuke.
