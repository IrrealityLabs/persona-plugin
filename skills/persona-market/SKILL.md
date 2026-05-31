---
name: persona-market
description: Simulate a cultural market — give the personas a set of items (songs, products, posts, ideas, messages) and have them pick / rate / upvote across multiple rounds, optionally seeing each other's choices. Run multiple parallel "worlds" to show how social influence makes outcomes unpredictable — the same item can be a hit in one world and a flop in another, like Salganik, Dodds & Watts's 2006 cultural-market experiment. Outputs per-world winners, cross-world variance, and a dashboard showing the market evolution. Use when the user says "/persona-market", "run a market simulation", "predict which one will go viral", "test for social-influence dynamics", "multi-world simulation", or wants to know not just what wins but *how predictable* the winner is.
---

# Persona Market

A multi-world cultural-market simulation. Personas browse a set of items and pick / rate / upvote across rounds. Optionally, they see each other's prior choices (social-influence condition). The same setup runs in multiple parallel worlds. The interesting output is not which item won, but **how different the winners were across worlds** — the cross-world variance is a direct measure of how socially-driven vs. quality-driven the market is for this audience.

This replicates the structure of Salganik, Dodds & Watts (2006), "Experimental Study of Inequality and Unpredictability in an Artificial Cultural Market" (Science). Their finding: social-influence markets produce much more unequal and unpredictable outcomes than independent markets, even when underlying item quality is held constant.

Use this when picking between candidates where you suspect the outcome is more about *what catches on* than *what's best on the merits* — viral content, product names, features competing for adoption, messaging that needs to spread.

## When to use vs. alternatives

- Use `persona-market` when you have multiple candidates and want to know **how predictable the winner is** — not just who wins.
- Use `persona-ab-test` for a single-world independent vote on 2–4 variants.
- Use `persona-turf` for picking a *subset* that covers the audience.
- Use `persona-town` for spatial/social-graph diffusion (information spreading person-to-person).
- Use `persona-max-diff` for ranking a list on a single dimension.

A useful pairing: run `persona-ab-test` first (independent vote, what's "best" on merits), then `persona-market` (social-influence, what catches on). The gap between them is the social-amplification signal.

## Sample size

- **Sweet spot:** 6–12 personas × 3–5 worlds × 2–4 rounds. The number of worlds matters more than the persona count for variance estimation.
- Default: 8 personas × 4 worlds × 3 rounds = ~96 subagent runs. **Always confirm cost.**

## Inputs

- **Items** — 4–20 candidates. Each labeled with a short name + short description (≤2 sentences). Songs / product names / messages / features / posts — anything the audience would "pick" among.
- **Worlds** — how many parallel runs (3–8 typical). More worlds = better variance estimate; cost scales linearly.
- **Rounds per world** — typically 3. Each round, every persona makes a choice with current visibility into the world's running counts.
- **Condition:**
  - **Independent** — personas never see prior counts; they pick purely on their own evaluation. The baseline / control.
  - **Social influence (default)** — personas see the running count of picks per item from prior rounds within their world.
  - **Both (recommended for comparison)** — run independent + social-influence versions side-by-side. Doubles cost but the comparison is what the method is *for*.
- **Picks per round** — how many items each persona picks per round (default 1; for "rate everything" mode, all items rated 1–7 per round).

## Storage layout

Everything goes into `./.personas/assets/market-runs/<run-id>/`:

```
<run-id>/
├── items.json              # the candidate item list
├── config.json             # worlds, rounds, condition, etc.
├── worlds/
│   ├── world-1/
│   │   ├── state.json      # running counts per item; updated each round
│   │   ├── picks.jsonl     # one record per persona×round pick
│   │   └── snapshots/
│   │       └── round-N.json    # frozen state after round N
│   ├── world-2/
│   │   └── ...
│   └── ...
├── independent/            # if running both conditions, parallel structure
│   └── ...
└── dashboard.html          # auto-rendered dashboard for browsing the run
```

## Workflow

### Phase 0 — Cost warning

`N worlds × M rounds × P personas = total subagent runs.` Both conditions doubles it. **Always confirm before launching.** Use the cost estimator.

Suggest reducing rounds first (3 → 2), then worlds (4 → 3), then personas — keep at least 3 worlds for any meaningful variance estimate.

### Phase 1 — Set up the items and worlds

Validate the items: distinct, comparable, each described in ≤2 sentences. Reject near-duplicates and items that aren't actually in the same category.

Generate `run-id` (timestamp). Create storage layout. Write `items.json` and `config.json`.

Initialize each world with empty `state.json` (all items at 0 picks).

### Phase 2 — Run each world × round in parallel-where-safe

For each world, sequentially across rounds (rounds within a world must be sequential — round N's state depends on round N−1's picks):

For each round within a world, fan out one subagent per persona, in parallel. Each prompt:
- Persona doc path.
- The items list with descriptions.
- For social-influence condition: the world's current running counts (from `state.json`), formatted as e.g. "Current picks: <item-A>: 12 | <item-B>: 3 | <item-C>: 7 | …".
- For independent condition: no count visibility.
- Picks-per-round count (usually 1).
- Instruction: "Pick N item(s) you would actually choose / engage with / want. Brief reasoning per pick (one sentence)."
- `persona-ask` reviewer contract.
- Pick response format below.

Pick response format:
```
## Pick (round <N>, world <W>)
**Choice:** <item name(s)>
**Reasoning:** one or two sentences — why this stood out.
**Did the running counts influence me?:** yes / no / partially — honest answer (only relevant in social-influence condition).
**References (persona doc):** § <Section>: "..."
**Confidence:** [high|medium|low]
```

After all personas' picks for a round are in, the orchestrator:
1. Updates the world's `state.json` with the new cumulative counts.
2. Appends each pick to `picks.jsonl`.
3. Snapshots state after this round to `snapshots/round-N.json` (lets the dashboard show the evolution).
4. Moves on to the next round of this world (or the first round of the next world).

**Parallelism note:** within a single (world, round) cell, persona subagents run in parallel. Across (world, round) cells: world-N's round-M cannot start until round-M-1 is done. But different worlds at the same round number can run in parallel — they share no state. So a typical run can parallelize as `worlds × personas` per round.

### Phase 3 — Render dashboard

Copy the dashboard.html from this skill's `assets/` into the run dir. Tell the user how to view it (`cd <run-dir> && python3 -m http.server 8766` then open `http://localhost:8766/dashboard.html`). It reads the world state JSONs and renders:
- Per-world final ranking
- Cross-world comparison grid (which items won where)
- Round-by-round evolution per world
- Variance metric (how different the rankings were across worlds)
- If both conditions: side-by-side comparison

### Phase 4 — Synthesize

```
# Market simulation: <items, short>

## Headline
One sentence. e.g. "High social-influence variance: Item A won in 3 of 4 social-influence worlds but lost in the independent condition, suggesting it benefits from amplification rather than merit. Item C was the most consistent — top-3 in every world."

## Per-world winners
| World | 1st | 2nd | 3rd | Last |
|---|---|---|---|---|
| World 1 | Item A | Item C | Item B | Item E |
| World 2 | Item C | Item A | Item D | Item E |
...

## Cross-world variance
- **Most consistent items** (similar rank across worlds): these are the ones whose appeal is grounded in something real about the items, not amplification.
- **Most variable items** (very different ranks across worlds): these are the lottery tickets — could be hits or flops depending on what catches on first.
- **The "Salganik gap"** (if both conditions ran): for each item, the rank in the independent condition vs. the average rank in the social-influence condition. Items with a much higher rank in the social-influence average = social-amplification winners. Items that ranked higher in independent = quality-wins.

## What happened in early rounds
The first round in any world creates anchor effects. The picks that happened to lead after round 1 disproportionately won by round N. Surface which items got an early lead in each world and how that propagated.

## Personas-who-bucked-the-trend
In social-influence worlds, some personas pick *against* the running trend. Their picks are most informative — they signal genuine preference rather than social conformity. Pull out these picks specifically.

## Predictability score
A rough number: "Across N worlds, the winner was the same X times out of N." High predictability = the market is largely quality-driven for this audience. Low predictability = small early signals get amplified into different outcomes, you can't pick a winner reliably from this set.

## What this means for the decision
Concrete: if you're picking which item to bet on:
- If predictability is high, pick the consistent winner.
- If predictability is low, the bet is partly random — either pick the one most amplifiable (best first-round draw potential), seed with social proof to manufacture early lead, or run more worlds before deciding.
```

## Notes

- **The cross-world variance is the point.** A run with 4 worlds that all produced the same winner taught you something different than a run with 4 worlds that picked 4 different winners. The synthesis should make this distinction the headline finding.
- **Always run multiple worlds** (≥3). A single-world social-influence run is just a noisier `persona-ab-test`. The variance across parallel runs is what makes this method valuable.
- **The independent baseline matters.** Running social-influence alone tells you the herd dynamics; running independent alone tells you the merit ranking; running both tells you the *gap*, which is the actionable insight.
- **Personas can be honest about influence.** The "did the running counts influence me?" question often produces useful self-reflection. Personas who explicitly say "yes, I picked X because X was already leading" are revealing the social-influence mechanism in real time.
- **Anchor effects from round 1 are real and useful.** If you want to test "what wins when someone else has already given X early momentum," seed the world with non-zero starting counts in `state.json` for a specific item, then run as normal. This shows how robust the trend is.
- The Salganik / Dodds / Watts 2006 paper is excellent background — `https://www.princeton.edu/~mjs3/salganik_dodds_watts06_full.pdf`. The "Music Lab" experiment they ran is the foundational reference for this method.
