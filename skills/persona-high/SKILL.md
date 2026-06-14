---
name: persona-high
description: A divergent-thinking method — prompt each persona to respond as if they're in an altered state (stoned, drunk, tripping on mushrooms, dosed on ayahuasca, etc.), randomizing the substance per persona to maximize cognitive diversity. The goal is *idea generation*, not analysis — surface off-the-wall, free-associative, lateral takes that the normal sober simulation would never produce. Use when the user says "/persona-high", "get weird with this", "give me wild ideas", "what would the personas say if they were stoned", "I need creative divergence", or wants brainstorm-style lateral input rather than rigorous analysis.
---

# Persona High

A creativity / divergent-thinking method. Each persona is prompted to respond as if they're in an altered state — stoned, drunk, mushrooms, ayahuasca, etc., randomized per persona. The output is free-associative, lateral, weird, often half-coherent — and occasionally produces an idea the sober-simulation panel would never surface.

This is a deliberately playful method. It's named for the cultural reference point but it's really an *associative-thinking creativity heuristic*, in the lineage of:

- **Oblique Strategies** (Brian Eno's randomization cards)
- **Random-word brainstorming** (force-fitting unrelated stimuli)
- **Six Thinking Hats — Green Hat** (deliberately generative mode)
- **Crazy 8s sketching** (rapid divergence under time pressure)

The "drugs" framing produces more interesting output than "be creative" because it gives the simulation a *concrete frame* for what divergent means — looser logical chains, more emotional / sensory takes, more willingness to follow tangents, less self-censoring.

**This is for idea generation, not evaluation.** The output is the front half of brainstorm → cull. Pair with `persona-review`, `persona-roast`, or `persona-concept-test` for the cull.

## When to use vs. alternatives

- Use `persona-high` when you're stuck for ideas and need divergent / lateral input.
- Use `persona-council` for adversarial debate (convergent).
- Use `persona-roast` for harsh critique (convergent, negative).
- Use `persona-ethnographic` for narrative depth from one persona.
- Use `persona-focus-group` for naturalistic group discussion.

## Sample size

- **Sweet spot:** 4–8 personas. Each persona's altered output is dense and weird; beyond 8 the synthesis becomes hard.
- Default: all personas if ≤6. If the user named personas, use those. If the roster is larger than ~6, don't auto-sample — the orchestrator picks ~5 for *maximum diversity* by reading the personas' `## At a glance` lines (divergent thinking wants different-minded personas, not topical relevance), or asks the user to name the subset.

## Inputs

- **The prompt / topic / question** — what you want weird ideas about. The more concrete, the better the divergence. "How could we re-imagine the onboarding flow?" works better than "ideas about our product."
- **Substance distribution** (optional) — explicitly assign substances per persona, or let the orchestrator randomize. Default: randomize across cannabis / mushrooms / ayahuasca / alcohol / DMT / LSD / no-substance-just-tired (the wildcard).
- **Intensity** (optional) — light buzz vs. peak experience. Default: medium — coherent enough to be useful, loose enough to be interesting.

## Workflow

### Phase 1 — Frame and confirm

This is a deliberately unusual method. Acknowledge it:

> "Running a divergent-thinking pass — each persona will respond as if in an altered state, randomized across substances, to maximize the chance of off-the-wall ideas. The output is for *brainstorming*, not analysis. Expect weird; cull later. Proceed?"

This is also a method that's not appropriate for every context (e.g. workplace tools where this framing might land badly). The user can always say no.

### Phase 2 — Assign substances

For each persona in the panel, assign a substance from this set (randomize unless the user specified):

| Substance | What it produces in divergence terms |
|---|---|
| Cannabis (medium) | Tangents, food metaphors, observational humor, "wait, what if..." |
| Cannabis (strong) | Couch-locked observational depth; long pauses, slow but profound |
| Alcohol (drunk-but-coherent) | Confident bad ideas, dating-style storytelling, sentimentality, occasional unexpected truth |
| Psilocybin mushrooms | Pattern-recognition overload, ego-loosening, "everything is connected" framing |
| LSD | Visual / synesthetic metaphors, time dilation, deep dives into single details |
| Ayahuasca | Mythic / archetypal framing, ancestral / spiritual angle, gut-truth declarations |
| DMT | Brief intense visions, language at the edge of coherence |
| Nitrous (whippits) | One-sentence cosmic insights, then nothing |
| Just sleep-deprived (the wildcard) | Loose associations without the substance framing — useful where the drug framing doesn't fit |

If a persona's profile makes a substance assignment absurd (a teetotaler grandma persona on DMT reads wrong), swap to "just sleep-deprived" — same divergence effect, less narrative weirdness.

### Phase 3 — Per-persona divergent reaction (parallel)

Spawn one subagent per persona. Each prompt:
- Persona doc path.
- The brainstorm topic.
- The substance assignment for this persona.
- The divergent-thinking briefing:
  > "You're <persona name> at a campfire / on a couch / in the living room, three hours into being <substance>. The topic of <topic> comes up. Riff. Don't analyze. Free-associate. Follow tangents. Don't self-censor — the worst-sounding idea might be a good one in disguise. Stay in your persona's underlying perspective (their values, their context, their concerns) but loosen the logical chains.
  > Length: 100–400 words of genuine free-association. Half-finished thoughts are fine. Going off-topic is allowed if the tangent is interesting. End by surfacing the 2–3 wildest takes from your riff explicitly so the listener doesn't miss them.
  > Voice notes: cannabis makes you observational and food-curious. Mushrooms make you pattern-seeking. Ayahuasca makes you declarative and gut-truth-oriented. Don't fake the voice — let the substance just loosen *your* voice. Stay you, just freer."
- `persona-ask` reviewer contract — Ground, think, then talk (Grounding → Thinking → Talking) still applies; even weird ideas should be traceable to the persona doc, just more loosely.
- Response format below.

Response format:
```
## <persona slug> (on <substance>)

### Grounding (private — orchestrator only)
Light grounding: which persona signal the ideas spring from — § <Section>: "<quote that grounds the riff in the persona's actual perspective>" + a confidence read [high|medium|low|off-pattern] (low is expected and fine here).

### Thinking (private — orchestrator only)
Private reasoning over that grounding: what this persona's loosened perspective would genuinely riff toward, where the thread is thin.

### The riff
<100–400 words of free-association on the topic, in this persona's loosened voice>

### The wildest takes
1. <one-line capture of the most off-the-wall idea>
2. <...>
3. <...>

### What's underneath the weirdness
2–3 sentences pulling out the *actual* insight or signal that the riff produced, in normal voice. This is the bridge from divergent to usable.

### Substance-fit
[worked|forced|threw the persona off] — if the substance assignment broke the simulation, flag it.
```

### Phase 4 — Synthesize

```
# Divergent ideation: <topic>

## The collected wildest takes
All "wildest takes" from across personas, flat-listed. Read these first — most of them are useless, a few will be unexpectedly good. The whole point is the cheap-to-produce, easy-to-cull list.

## Bridges to the real insight
For each persona, the "what's underneath" — the actual signal extracted from the riff. These translate the weird back into usable.

## Themes across personas
Even in divergent mode, patterns emerge. Cluster the riffs into 2–4 themes — what underlying perspective different personas converged on, despite the substance randomization.

## Ideas worth pulling forward
Your synthesis as orchestrator: the 3–5 ideas from across the riffs that are actually worth seriously considering. Justify each briefly.

## Methods to evaluate the survivors
Suggest the next step — usually persona-concept-test, persona-review, or persona-roast on the candidates you want to take seriously.

## Caveat
This was divergent ideation, not analysis. The outputs are *prompts for your own creative thinking*, not findings. Don't let any single weird take drive a decision — that's not what this method is for.
```

## Notes

- **The point is the cull.** Generating 30 weird ideas is cheap. Evaluating which 2 are actually good is the user's job, possibly with a follow-up method. Don't try to pre-filter the riffs into "good" and "bad" — the user benefits from seeing the noise too.
- **"Substance-fit: forced" is a signal** that the method isn't right for this persona. Don't insist; swap to "sleep-deprived" wildcard or skip that persona for this method.
- **This method is not for serious decisions.** It's for the front-half of brainstorming, when you're trying to expand the space of options. Use the convergent methods (roast / concept-test / review) for actual evaluation.
- The substance framing is a *creative-prompting heuristic*, not literal simulation of drug effects. Don't take the output as accurate about how someone on that substance actually thinks. It's about producing divergence in this specific simulation context.
- Some workplace / professional contexts may find the framing inappropriate. If the user is using this in a corporate setting where the drug framing won't land, suggest "just sleep-deprived" across all personas — same effect, fully workplace-safe.
- Don't run this on personas representing identifiable real people (e.g. distilled from a colleague's Slack). Reserve for archetype personas where there's no real person to attribute the riff back to.
