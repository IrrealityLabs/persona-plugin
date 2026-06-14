---
name: persona-town
description: Run a generative-agent simulation — drop the personas into a 2D town, let them move and talk to each other over discrete time ticks, and watch information (an idea, a rumor, a product) propagate through the population. Visualized in real-time via a Phaser.js HTML page. Use when the user says "/persona-town", "simulate the personas in a town", "see how an idea spreads", "generative agents", "if I tell <persona> about X, who does it reach", or wants the *dynamics of diffusion* rather than per-persona reactions. Inspired by Park et al. 2023's generative agents paper.
---

# Persona Town

A discrete-time simulation: each persona is an agent in a 2D grid town. Per tick, each persona decides what to do (move, talk to a nearby persona, observe). Conversations propagate information persona-to-persona. The orchestrator advances time and merges the agents' choices into a shared world state. A Phaser.js HTML page polls the world state and renders the town in real-time.

The interesting output is not any single persona's behavior — it's **diffusion patterns**: who tells whom, what idea variants emerge as the message gets retold, who never hears the message at all. The classic example from the generative agents paper: Klaus mentions his birthday party; track who Maria tells; observe a small social graph forming.

## When to use vs. alternatives

- Use `persona-town` to study **diffusion / virality / social-graph effects** — how an idea, product, or rumor spreads.
- Use `persona-focus-group` or `persona-council` to study reactions in a single discussion (no movement, no time advancement).
- Use `persona-survey` to study static views across the panel.
- Use `persona-ethnographic` for one persona's narrative without group dynamics.

This is the most expensive method in the catalog. Always confirm cost before launching.

## Sample size

- **Sweet spot:** 5–15 personas. Below 5, you don't see meaningful network effects. Above 15, the simulation becomes both expensive and visually crowded.
- **Default ticks:** 24. One tick ≈ one hour of in-world time, so 24 ticks = a simulated day.

## Inputs

- **The seed event** — the thing being propagated. e.g. "Klaus mentions his birthday party is next Saturday." / "Sarah tells someone about a new tool she found." Be specific.
- **The initial holder(s)** — which persona(s) start with the information. Often just one.
- **Tick count** — default 24, can extend to 48 or 72 for slower-diffusion scenarios.
- **Town size** (optional) — default 20×15 grid. Larger = more random encounters, slower diffusion. Smaller = denser, faster.
- **Tracking question** — what the user wants measured. Default: "what % of the town knows about the seed event by tick N?" Can also track: variant drift (how the message changes in retelling), social graph (who told whom).

## Architecture (read this before launching)

```
./.personas/assets/town-runs/<run-id>/
├── world.json              # current world state — polled by the HTML viz
├── events.jsonl            # append-only log of every action
├── town.html               # the Phaser.js viz (copied from this skill's assets)
└── personas/
    ├── <slug>/
    │   ├── memory.jsonl    # this persona's running memory (what they've observed)
    │   ├── intent.json     # this tick's intended action
    │   └── persona-meta.json   # static: position, color, label
    └── ...
```

**Coordination model — single writer per file:**
- Each persona subagent writes only to its own `personas/<slug>/intent.json` and appends to its own `personas/<slug>/memory.jsonl`. No write conflicts between agents.
- The orchestrator (you) reads all `intent.json` files at end of tick, resolves conflicts (two agents wanting the same tile, two starting a conversation at the same time), and writes the merged result into `world.json` + `events.jsonl`.
- The HTML page is read-only — polls `world.json` every ~1s and re-renders.

Parallel agents work because they don't share writes. The orchestrator is the only multi-source writer (single-threaded).

## Workflow

### Phase 0 — Cost warning

Calculate before launching:
- Runs = personas × ticks. 8 personas × 24 ticks = 192 subagent runs.
- Per run: ~10–20K tokens (persona doc + memory + world snippet + reasoning). 192 × 15K = ~3M tokens.
- At Sonnet-blended rates: **~$30–60 for a typical run.** A 15-persona, 48-tick run: **~$150–250.**

**Always warn before launching.** Show the estimate and get explicit confirmation. Suggest reducing ticks or personas if cost-prohibitive.

### Phase 1 — Set up the run

Generate a `run-id` (e.g. ISO timestamp). Create the directory structure above. Copy `assets/town.html` from this skill into the run directory.

Lay out the town:
- Place buildings (a few rectangular obstacles) on the grid — pick a few and write to `world.json`. Keep this simple; sophistication doesn't add insight.
- Assign each persona a random starting position (not overlapping buildings or other personas).
- Assign each persona a stable color (hash their slug).
- Write `personas/<slug>/persona-meta.json` for each.
- Write the initial `world.json`:
  ```json
  {
    "tick": 0,
    "grid": {"cols": 20, "rows": 15},
    "buildings": [{"x":3,"y":3,"w":4,"h":3,"name":"cafe"}, ...],
    "personas": [
      {"slug":"sarah","x":5,"y":7,"color":"#ff8855","speech":null},
      ...
    ],
    "events": []
  }
  ```

### Phase 2 — Seed the initial knowledge

For the initial holder persona(s), append the seed event to their `memory.jsonl`:
```json
{"tick":0,"kind":"seed","content":"<seed event>","source":"original"}
```

### Phase 3 — Start the viz

Tell the user:
> "The town visualization is at `./.personas/assets/town-runs/<run-id>/town.html`. Open it in a browser to watch in real-time. You'll need to serve the directory over HTTP for the fetch calls to work — easiest: `cd <run-dir> && python3 -m http.server 8765` then open <http://localhost:8765/town.html>."

Don't launch the browser yourself — let the user do it. The simulation runs whether or not they're watching; the viz is purely an observer.

### Phase 4 — Tick loop

For each tick from 1 to `tick_count`:

#### Step A — Fan out per-persona subagents in parallel

One subagent per persona. Each prompt:
- Persona doc path.
- Current `world.json` (positions of all personas, buildings, current tick).
- This persona's `memory.jsonl` (their accumulated observations).
- The action choices: `move {dx, dy}` (one tile any of 8 directions), `speak {to: slug, content: "..."}` (only valid if adjacent or co-located with target), `observe` (stay in place, listen for nearby speech).
- A simple decision frame: "What would you do this tick, given who's around you and what you know? Decide and write your `intent.json` in this format: `{thinking: <private reasoning — why this action; logged by the orchestrator, never broadcast to other personas>, action: 'move'|'speak'|'observe', target: <slug or null>, content: <speech text or null>, dx: <int>, dy: <int>}`."
- The `persona-ask` reviewer contract — references + confidence on the *reasoning*, even if the action is mechanical. Apply *Think before you talk*: reason privately first, then choose your action and decide what (if anything) you'd actually say — a persona needn't repeat or pass on something they wouldn't.

The persona doc determines behavior: an introvert persona may speak less; a community-organizer persona may seek out others; a skeptical persona may not pass along messages they don't believe.

#### Step B — Orchestrator merges intents

Read every `personas/<slug>/intent.json`. Resolve:
- **Movement conflicts:** if two personas want the same tile, the first one (lexicographically by slug) wins. The other stays put.
- **Speech:** if persona A speaks to persona B, write the speech as a world event AND append to B's memory.jsonl as `{tick, kind:"heard", content, from: A.slug}`. Also append to A's memory as `{tick, kind:"said", content, to: B.slug}`.
- **Speech radius:** for v1, "adjacent or co-located" only — adjacency = within 1 tile (8 neighbors). No long-distance broadcasting.

#### Step C — Update world.json and events.jsonl

Write the new world state: positions updated, `speech` field populated for any persona who spoke this tick (clears next tick), tick incremented.

Append the tick's events to `events.jsonl` (one event per line) — include each persona's `thinking` on its action event so the run is auditable (why the diffusion went the way it did). `thinking` never enters another persona's `memory.jsonl`; only spoken `content` propagates.

#### Step D — Brief pause

Sleep ~3 seconds between ticks to let the viz catch up and to keep this from racing through expensive subagent calls without user awareness.

### Phase 5 — Diffusion analysis (after the run)

When ticks complete (or the user stops the run early), analyze diffusion:

```
# Town simulation: <seed event, short>

## Headline
N of M personas know about the seed event by tick T. (X%)

## Spread curve
Tick 0: 1 persona knows (the seed holder)
Tick 4: 3 personas know (+2)
Tick 8: 5 personas know (+2)
...
[ASCII line chart]

## Who told whom (social graph)
- <seed-holder> → <persona2> at tick 3
- <persona2> → <persona3> at tick 5
- <persona2> → <persona4> at tick 6
- <persona3> → <persona5> at tick 8 (notable: <persona3> embellished — see drift)
...

## Variant drift
How the message changed as it spread. For each notable variation: what changed, who introduced the variation, how far it propagated.

## Personas who never heard it
List them, with the closest they got (proximity, but no conversation triggered). Often interesting — *why* didn't they encounter the message? Personality, geography, or coincidence?

## Bottlenecks and amplifiers
Personas whose participation was load-bearing for diffusion ("everyone heard it via <slug>") vs. personas who heard it but didn't pass it on. The amplifiers in your real audience are often the ones to engage first; the dead-ends are who you can't reach via word-of-mouth.

## Confidence
This is a simulation, not real social-network behavior. Use the patterns as *hypotheses about viral mechanics*, not as a prediction of real spread. Note any persona that seemed to be acting out of character compared to their persona doc.
```

## Notes

- The simulation is **deliberately simple.** Sophisticated agent architectures (planning, memory hierarchy, etc.) are out of scope for v1. Personas decide per-tick from current world + memory + persona doc. That's it.
- Multi-step planning would help (e.g. "I'm going to walk to the cafe to find Maria") but for v1 we rely on the persona doc and emergent behavior.
- If a persona's persona doc strongly suggests they wouldn't share information (e.g. "skeptical, doesn't gossip"), respect that — the simulation will see lower diffusion through them. That's a real finding, not a bug.
- Stop the run early if patterns are clear by tick N/2 — no need to burn budget watching a flat-line spread curve continue to flatline.
- The Phaser viz is enrichment, not source-of-truth. The analysis comes from the files; the viz just makes the dynamics legible while it runs.
