---
name: persona-research
description: Run structured market research with your personas. Parent skill that catalogs the available study types (interview, JTBD interview, survey, focus group, council, user testing, presentation feedback, tree test, A/B test, concept test, TURF, conjoint, MaxDiff, Van Westendorp, brand tracking, social listening, ethnographic, diary study, grounded theory, town simulation, Hacker News / X / LinkedIn / Slack / email simulation, roast, divergent ideation) and helps you pick the right one for your question, then dispatches to the matching child skill. Use when the user says "/persona-research", "run a study", "do market research with the personas", "what method should I use for X", or describes a research question without naming the methodology.
---

# Persona Research

A catalog of market-research methodologies adapted to run against your saved personas (in `./.personas/`). Each child skill is one method. This parent skill is the menu — it helps you pick the right method for the user's actual question, briefs them on what it'll cost, and dispatches.

Every method ultimately uses the personas + `persona-ask` (framing + references + confidence). The methods differ in *structure*: how many personas, how many questions, whether they see each other's answers, what the output looks like.

Persona selection is the same across every method (see `persona-review` Phase 1): if the user names personas, use exactly those; otherwise use all personas in `./.personas/`. There's no automatic filtering or sampling — when a method would be unwieldy with a very large roster, it asks the user which personas to include (or, for methods that want a diverse subset, the orchestrator picks a spanning set by reading the personas' `## At a glance` lines).

Cost and time estimates come from **`references/cost-estimator.md`**, which pulls live model pricing where available (via LiteLLM's pricing JSON or `ccusage`) and falls back to documented approximations.

## When to use this skill vs. going direct

- **Use `persona-research`** when the user describes a *research question* without naming a method ("I want to understand how my personas would price this", "how do they react when they're in a group?", "which of these 12 features matter most?"). You pick the method.
- **Skip this skill** when the user names a method explicitly ("run a Van Westendorp", "do an A/B test on these two pages") — go straight to the child skill.
- **Use `persona-review`** for asset feedback / code-review-style critique. That's its own dedicated skill, not part of this catalog.
- **Use `persona-roleplay`** when the user wants to *rehearse a live conversation* (journalist interview, sales pitch, 1:1 with the boss) rather than research a persona. There the persona plays the counterpart and the user is the one being tested — the inverse of every method below. Its own dedicated skill, not part of this catalog.
- **Use `persona-ask`** for a single-persona quick question. Don't reach for a methodology when one persona and one question will do.
- **Use `persona-of-thought`** when the user wants *one* synthesized answer to a question (including an A/B choice) fused from many independent persona perspectives — a merged anonymous answer, not a study report or a per-persona panel. Its own dedicated skill, not part of this catalog.

## Method catalog

Pick by goal, not by name. Each row links to the child skill.

| Goal | Method | Child skill | Sample-size sweet spot |
|---|---|---|---|
| Deep qualitative on one viewpoint | 1:1 interview | `persona-interview` | 1 persona |
| Discover *why* someone switched (or didn't) | Jobs-to-be-done interview | `persona-jtbd-interview` | 1–3 personas |
| Broad structured Q's across personas | Survey | `persona-survey` | All available (cap ~10) |
| Group reaction with cross-talk | Focus group | `persona-focus-group` | 3–6 personas, 2–4 rounds |
| Adversarial debate / pressure-test | Council | `persona-council` | 4–7 personas, 3–4 rounds |
| Test a UI flow / page / video | User test | `persona-user-test` | 3–5 personas |
| Slide-by-slide feedback on a deck / talk | Presentation feedback | `persona-presentation` | 3–6 personas |
| Pick a winner between variants | A/B test | `persona-ab-test` | All available |
| Test a *concept* before building it | Concept test | `persona-concept-test` | 3–8 personas |
| Optimize the smallest set that pleases most | TURF analysis | `persona-turf` | 8+ personas ideal; works with fewer |
| Estimate trade-offs between attributes | Conjoint | `persona-conjoint` | 8+ personas ideal; works with fewer |
| Rank a long list by importance | MaxDiff | `persona-max-diff` | 5+ personas ideal |
| Find optimal price range | Van Westendorp | `persona-van-westendorp` | 8+ personas ideal; works with fewer |
| Measure brand awareness / associations | Brand tracking | `persona-brand-tracking` | All available |
| Walk through a typical day / workflow | Ethnographic | `persona-ethnographic` | 1–3 personas |
| Longitudinal narrative over time | Diary study | `persona-diary-study` | 1–3 personas |
| Test information architecture / navigation | Tree test | `persona-tree-test` | 3–5 personas |
| Measure organic brand mention in posts | Social listening | `persona-social-listening` | 8+ personas |
| Simulate an HN thread / technical critique | Hacker News simulation | `persona-hacker-news` | 5–10 personas |
| Simulate X (Twitter) replies on a post | X simulation | `persona-x-post` | 6–12 personas |
| Simulate LinkedIn reactions on a post | LinkedIn simulation | `persona-linkedin-post` | 6–12 personas |
| Simulate Slack reactions in a channel | Slack simulation | `persona-slack-message` | 5–10 personas |
| Simulate email replies (cold or warm) | Email simulation | `persona-email` | 4–10 personas |
| Get brutally honest critique | Roast | `persona-roast` | 3–6 personas |
| Divergent / lateral idea generation | "High" (altered-state brainstorm) | `persona-high` | 4–8 personas |
| Build a theory from open coding (iterative) | Grounded theory | `persona-grounded-theory` | 5–12 personas, multi-cycle |
| Simulate diffusion / virality through a town | Generative-agent simulation | `persona-town` | 5–15 personas |
| Test predictability via multi-world cultural market | Market simulation | `persona-market` | 6–12 personas × 3–5 worlds |

## How to pick a method

Use the two-step selector below: first figure out **what phase of the product lifecycle** the user is in, then narrow within the phase by **method category** (observational / conversational / testing / survey).

### Step 1 — Identify the phase

Three phases, each answering a different kind of question. Most projects move through them in order, but it's common to cycle back.

- **WHY (problem space)** — *why does this matter, what's the real job, what's broken?* Used before commitment to a solution. The user is exploring a need, validating a market, deciding what to build.
- **WHAT (solution space)** — *what should we build, what's the right shape, does this version actually solve it?* Used during design and pre-launch. The user has a candidate solution and is shaping it.
- **HOW (delivery / performance)** — *does it work in practice, do people find it, how does it perform vs. alternatives, what changes the result?* Used post-launch (or on a near-launch prototype). The user is optimizing what already exists.

If the user's question doesn't clearly fit one phase, ask: "Are you trying to understand the problem (WHY), shape the solution (WHAT), or optimize what exists (HOW)?"

### Step 2 — Pick the method within the phase

| Stage | Best fit | Also useful |
|---|---|---|
| **WHY** | | |
| Problem identification | `persona-ethnographic`, `persona-interview`, `persona-jtbd-interview` | `persona-diary-study`, `persona-survey` |
| Problem understanding | `persona-interview`, `persona-ethnographic`, `persona-jtbd-interview` | `persona-survey`, `persona-focus-group` |
| Problem prioritization | `persona-interview`, `persona-survey`, `persona-max-diff` | `persona-focus-group`, `persona-turf` |
| **WHAT** | | |
| Solution ideation | `persona-focus-group`, `persona-council`, `persona-interview` | `persona-ethnographic` |
| Solution design | `persona-interview`, `persona-focus-group`, `persona-concept-test` | `persona-user-test` (on prototype), `persona-tree-test` |
| Solution validation | `persona-concept-test`, `persona-jtbd-interview`, `persona-interview` | `persona-survey`, `persona-ab-test` |
| Solution value (pricing / willingness) | `persona-van-westendorp`, `persona-conjoint`, `persona-interview` | `persona-concept-test`, `persona-ab-test` |
| **HOW** | | |
| Solution usability | `persona-user-test`, `persona-tree-test` | `persona-ab-test`, `persona-survey` |
| Solution discoverability | `persona-user-test`, `persona-tree-test`, `persona-ab-test` | `persona-survey` |
| Performance / conversion | `persona-ab-test`, `persona-survey`, `persona-user-test` | `persona-brand-tracking` |
| Satisfaction | `persona-survey`, `persona-brand-tracking` | `persona-interview`, `persona-focus-group` |
| Disruption (what would unseat this) | `persona-ethnographic`, `persona-jtbd-interview`, `persona-survey` | `persona-council` |

### Method-category cheat sheet

If the user has a category preference instead of a stage:

- **Observational** (watching how they actually do things): `persona-ethnographic`, `persona-diary-study`
- **Conversational** (talking with them): `persona-interview`, `persona-jtbd-interview`, `persona-focus-group`, `persona-council`
- **Testing** (giving them something to react to): `persona-user-test`, `persona-presentation`, `persona-tree-test`, `persona-ab-test`, `persona-concept-test`
- **Survey** (structured questions at scale): `persona-survey`, `persona-max-diff`, `persona-van-westendorp`, `persona-conjoint`, `persona-turf`, `persona-brand-tracking`

### Other tie-breakers

After the stage + category narrows it to 2–3 candidates, pick by:

- **How many personas weigh in?** Deep on one → interview / JTBD / ethnographic / diary. Small group with cross-talk → focus group / council. Everyone independently → survey and the quant methods.
- **What's the artifact?** Insights and quotes → qualitative. Distributions / rankings / prices → quantitative. Annotated flows / sentiment over time → user test.

A wrong method produces a confident-looking wrong answer. When uncertain, ask one clarifying question instead of guessing.

## Sample size principle: always run, always be honest

Every method has a sweet spot. Most of these techniques were designed for hundreds or thousands of human respondents. With persona panels you usually have 3–10. **Always run with whatever you have**, and:

- In the announce phase, state the methodology's sweet spot and the actual sample.
- In the output, mark conclusions accordingly: a Van Westendorp on three personas produces a *direction*, not a price point. Say so.
- Suggest a concrete way to strengthen the result — usually "add N more personas via `persona-create` or `persona-distill` to bring the sample to <sweet spot>".

Do **not** refuse to run because the sample is small. Refusing is less useful than running honestly.

## Cost and time warnings

Before launching a method that will be expensive in tokens or wall-clock time, surface the estimate to the user and let them confirm. Use the cost rules of thumb in `references/cost-estimator.md`.

The expensive ones to flag specifically:
- **persona-user-test on video** — frames per chunk × persona reactions × duration adds up fast. Always estimate first, especially for video.
- **persona-focus-group / persona-council** at the top of their ranges (6 personas × 4 rounds = 24 subagent runs minimum).
- **persona-conjoint** with many profiles (10 personas × 15 profile pairs = 150 reactions).
- **persona-research** itself if you're chaining methods (e.g., "run a Van Westendorp, then a focus group, then a user test").

For cheap methods (single interview, small survey, simple A/B test) just launch — don't pre-estimate trivially small jobs.

## Dispatch

Once you've picked the method:

1. Tell the user which method and why (one sentence).
2. Tell the user the sample size you'll run with (and what the methodology prefers, if mismatched).
3. Tell the user the rough cost / time, if non-trivial.
4. Invoke the child skill, passing along the question, the asset(s) if any, and any persona-selection overrides.

If `./.personas/` is empty or missing, stop and offer `persona-distill` or `persona-create` first — none of these methods work without personas.

## Meta-skill: `persona-multiverse`

Not a study type — a **wrapper** that runs any dynamic-system study N times (default 4: 1 control + 3 dynamic) and synthesizes across runs to surface what was consistent vs. what was contingent on the social-influence dynamics. The control run strips out the dynamic layer (e.g. for focus-group → only Round 1; for council → only Round 1; for channel sims → no reply round; for town → no inter-persona observation). The synthesis reports reliable findings, rare/contingent findings, and the gap between control and dynamic-average.

Only applies to studies with a dynamic / social-feedback layer: `persona-focus-group`, `persona-council`, `persona-town`, `persona-x-post` / `persona-linkedin-post` / `persona-hacker-news` (with reply rounds on). Non-dynamic studies (survey, A/B test, interview, etc.) don't benefit — wrapping them in multiverse just burns tokens for the same answer N times.

Cost = wrapped study × N. Always confirm before launching. Reach for it when an outcome will drive a real decision and you want to know whether the dynamic-system reading is reliable or social-amplification artifact.

## Methods not yet implemented (worth knowing exist)

These are real methodologies you might be asked about that don't have a child skill yet. If the user asks for one, name it honestly and either propose the closest implemented method or offer to draft a new child skill:

- **Card sort** (IA categorization) — partially overlaps with `persona-tree-test`.
- **5-second test** (first-impression on a screen) — can be approximated by `persona-user-test` with a single screenshot.
- **Semantic differential** (paired-adjective brand perception) — adjacent to `persona-brand-tracking`.
- **Kano model** (feature classification: must-have / performance / delighter) — adjacent to `persona-max-diff`.
- **Heuristic evaluation** — expert-review method; not a great fit for persona simulation.
