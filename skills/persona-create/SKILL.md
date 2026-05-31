---
name: persona-create
description: Create personas for the persona-review / persona-research family — the best-practice walkthrough for building a high-quality, research-grounded persona doc. Supports four modes — (1) interview the user about their target audience, (2) bulk-import from a survey-response spreadsheet (one row per persona, one column per question), (3) start from a user-supplied ICP / customer research doc, (4) batch-generate many unique, non-duplicated personas from a single description — every one strictly fitting its criteria while spanning a deliberate diversity frame. Use when the user says "create a persona", "add a persona", "make a new persona", "/persona-create", "build personas from this CSV", "import these survey responses", "create 10 personas who are…", "generate a batch of personas fitting this description", "make a bunch of unique personas for X", or when persona-review / persona-ask runs but ./.personas/ is empty.
---

# Persona Create

The best-practice skill for creating new personas. You, the assistant, are the expert on what makes a persona good — not the user. Walk them through the right inputs, ask the right questions, enforce the quality bar, write the doc.

A persona is **a reviewer brief, not a marketing-deck cardboard cutout.** Downstream skills (`persona-review`, `persona-ask`, the `persona-research` family) lean hard on each persona's specifics; a thin or generic persona produces thin or generic study outputs no matter how good the methodology is.

## What the research actually says about personas

Persona docs that produce useful LLM simulation are *not* what most product / marketing playbooks would have you write. The research on LLM-persona accuracy and bias points to a different shape than the conventional "Sarah, 34, mother of two, likes yoga" persona-poster. Several findings, all of which shape the structure below:

1. **Behavioral + contextual signals do most of the work.** An AskRally study of 64 personas predicting actual product adoption found that **Behavioral + Contextual attributes alone hit the best F1 (0.617) using only 10 features** — vs. 25 features in a kitchen-sink persona. Psychographics *actively hurt* accuracy by adding noise. Demographics alone failed to identify true negatives. *Implication:* foreground what the persona does and why; deprioritize personality archetypes.
2. **Interview-grounded text is the single biggest accuracy lever.** Stanford's *Generative Agent Simulations of 1,000 People* (Park et al. 2024) showed that personas grounded in a 2-hour interview transcript hit **85% of human test-retest accuracy** — vs. **71–74% for demographic-only baselines**. Real verbatim self-narrative beats every other input. *Implication:* if you have real customer interviews, use them as source material directly; don't summarize.
3. **LLM-generated persona prose is the most dangerous step.** "LLM Generated Persona is a Promise with a Catch" (arXiv 2503.16527) tested ~1M personas across formats: LLM-written descriptive prose performed *worst*, and produced systematic biases — leftward political drift, positivity inflation, **omission of life challenges and hardship.** *Implication:* prefer structured/tabular fields over free-text generation. Negative experiences must be sampled in deliberately.
4. **Variance compression is the dominant failure mode.** Across Argyle, Bisbee, Sarstedt, the silicon-respondents literature: LLM personas under-disperse — same persona returns near-identical answers, narrow distributions, missing extremes, no "don't knows." *Implication:* the persona doc has to *embed* variance signals (contradictions, mood states, recent surprises) so the simulation can produce them.
5. **Big Five (numeric scalers + behavioral anchors) is the only personality framework with replicable LLM steering.** Research shows numeric scaler prompts ("Extraversion: 7/10") achieve r > 0.85 with measured trait expression. MBTI has 47% test-retest reliability and produces polarized, unreliable LLM outputs; Big Five explains ~2× the variance of MBTI on real behavior. *Implication:* include Big Five with numeric scores and 1-line anchors. Skip MBTI, DISC, Enneagram.
6. **5–10 *diverse-register* speech examples beats either fewer-of-a-kind or longer-of-a-kind.** Few-shot literature converges on 3–5 examples as the sweet spot, but persona work benefits from coverage of different *registers* (work vs. casual, calm vs. frustrated, peer vs. authority). *Implication:* require 5–10 examples, deliberately varied — not 10 versions of the same voice.
7. **Default LLMs skew high-Agreeableness, high-Conscientiousness, low-Neuroticism, socially-desirable, positive, progressive.** Without explicit counter-steering, every persona drifts toward this default — even ones that shouldn't. *Implication:* counter-steer explicitly in the doc when the persona should be disagreeable, disorganized, anxious, or socially incorrect.
8. **Prompt-based "be neutral" / "answer honestly" instructions DO NOT WORK and often backfire.** "Answer honestly" preambles +44% bias; "objective analyst" priming +38% bias; reverse-coding +134% bias. *Implication:* don't paper over LLM biases with "be unbiased" instructions in the persona doc. They will harm accuracy.
9. **Caricature lives in broad topics; specifics reduce it.** Same source: minority-identity personas are caricatured more than majority ones, and broad/abstract topics produce more caricature than narrow specific ones. *Implication:* if a persona spans an underrepresented group, the persona doc needs more *concrete behavioral and situational specifics* (not more identity markers) to counteract the caricature pull.

These findings are *built into the template and the quality bar below*. The skill is not just "fill out these sections"; it's "fill these sections in a way that reflects what's been shown to actually work."

A short references list lives at the bottom of this file.

## What a good persona doc covers

Read this in full before doing anything else. These are the criteria you're holding the work to.

### Primary signal (does most of the predictive work)
- **Behavioral** — what they *actually do*. Current stack and tools. Past attempts. How they decide. Frequency of relevant activity. Recent purchases / switches. Strongest evidence for accurate simulation.
- **Contextual** — the *situation* in which they engage. Trigger that puts them in market. Constraints (budget / time / expertise / political-capital). The environment they're evaluating from. Job-to-be-done specifics.

### Required supporting signal
- **Demographics** — who they are *on paper*. Role, life stage, geography. **Necessary scaffolding but the least load-bearing dimension.** Keep tight. Don't make this the focus.
- **Big Five personality** — five numeric scores (1–10 scale) plus one-line behavioral anchors per trait. **Counter-steer the LLM defaults** explicitly when the persona is *not* a high-A / high-C / low-N person.
- **Verbatim speech samples** — 5–10 examples from real customer language, deliberately covering different registers (formal/casual, calm/frustrated, peer-to-peer/authority-facing, written/spoken).
- **Negative-experience anchors** — explicit recent setback, current frustration, hard constraint, past failure. **Required**, not optional. Counteracts positivity drift.

### De-emphasized
- **Psychographics** (values, aspirations, lifestyle adjectives) — AskRally evidence shows these *hurt* accuracy by adding noise. Keep brief or omit. If you include, ground in observed behavior, not in abstract values.

### Required honesty
- **Known gaps** — what we *don't* know about this persona. Personas without a Known-gaps section turn into confident hallucinations downstream. Make this honest, not padding.

### Quality bar — push back on these

- **"A young professional who wants to grow."** Demographics with zero behavioral or contextual signal. Insist on specificity.
- **"Sarah, 34, mother of two, likes yoga."** Marketing-deck snapshot. Reject; demographics alone are the lowest-evidence dimension.
- **No verbatim language samples.** Insist on at least 5 real-register samples — not paraphrases, not invented.
- **No negative experiences.** Required field. If the persona has no current frustrations or recent setbacks, you've written a marketing fantasy, not a customer.
- **Universal persona that "represents all our users."** Personas are *segments*, not averages. Push to narrow or split.
- **Persona dimension dominated by LLM-generated prose.** If the user wants you to "just make up the rest," resist — extra LLM-generated text is the documented dangerous step. Default to short structured fields.

## Four modes — pick based on what the user has

### Mode 1: Interview (default)
The user knows their audience but doesn't have it written down. You ask ~6 structured questions, do light segment research, draft, save.

### Mode 2: Bulk import from spreadsheet
The user has structured respondent data — survey results, customer research exports — and wants one persona per row.

> If the user has survey *distributions* and wants a **statistically representative synthetic population** (sampling more — or different — respondents than they actually surveyed, preserving the marginals and correlations), that's `persona-copula`: it fits a Gaussian copula, samples a synthetic respondent table, then feeds that table back into this Mode 2 to write the docs. Use Mode 2 directly only when you want one persona per *real* row.

### Mode 3: Pre-supplied research / interview transcripts
The user pastes (or points at) detailed customer research, ICP definitions, or *real interview transcripts*. **This is the highest-fidelity mode** — Stanford evidence is unambiguous. If the user has real interview transcripts, route here even if they didn't ask for it.

### Mode 4: Batch generate from a description
The user gives **one description** and wants **many** personas from it ("create 10 potential Jaguar buyers aged 40–60 who value British heritage", "make a batch of unique churned-trial users"). Every persona must *strictly satisfy the description's criteria*, and the set must be *diverse and non-duplicated* rather than N variations on the mode. This is the breadth mode — it populates a representative-feeling panel fast when you have no survey data and no time to interview.

> If the user has actual **survey data or distributions**, prefer `persona-copula` — it samples a statistically representative population from the real joint distribution. Mode 4 is the qualitative analogue for when all you have is a description: diversity is engineered by design (a spanning frame), not measured. And per the research below, generating persona prose from a description is the **lowest-fidelity** creation path — use it for breadth and hypothesis generation, and be honest in each doc's Known gaps that it's description-generated, not data- or interview-grounded.

In ambiguous cases, ask which mode. Default to Mode 1 if the user just says "create a persona" (singular) with no other signal. Route to Mode 4 when they ask for **several / a bunch / N** personas from a single description. Route to Mode 3 if they mention real customer interviews. Route to Mode 2 / `persona-copula` if they have a data file.

## Mode 1 workflow — Interview

### Phase 1 — Announce and confirm

Say: "I'll create one persona by interviewing you (~6 questions), doing a short segment research pass, then drafting the doc and saving it to `./.personas/`. The doc will cover behavioral / contextual / demographic / Big Five / speech-sample / known-gaps fields — these are the dimensions the research on LLM-persona accuracy points to."

One persona per run. Multiple personas means multiple runs.

### Phase 2 — Interview via AskUserQuestion

Use `AskUserQuestion`. Batches of 1–4 per call, ~6 questions total across 2–3 batches.

Always provide concrete, opinionated options. Specific options force sharper choices. Cover, in this priority order:

1. **Behavioral — what they actually do.** Current tools / stack / alternative. Past attempts and what they bounced from. Frequency.
2. **Contextual — JTBD.** The outcome they're hiring something to achieve. Trigger event. Constraints.
3. **Negative experience.** What's currently frustrating them. A recent setback. A pattern they keep hitting that doesn't work. **Required — don't skip.**
4. **Demographic anchor.** Role, company stage / life stage. Keep tight.
5. **Big Five — coarse calibration.** Ask the user where this persona sits relative to a typical-person baseline on each Big Five dimension. Don't make them score 1–10 (cognitive overhead); ask "more or less <trait> than average, and how much" and you map to numeric. Explicitly probe for *low-A, low-C, high-N* signals because the LLM default biases the other way.
6. **Speech samples — language and register.** "Give me 2–3 real phrases this persona uses. Different registers if you have them — what they'd say to a peer vs. to a boss vs. when frustrated." Capture verbatim. You'll generate 2–7 more in Phase 4 based on these anchors.

Probe for specifics when vague. If the user says "they care about ROI," follow up: "What ROI claim feels believable to them vs. made-up? On what timeframe?"

### Phase 3 — Research the segment

Spawn one `general-purpose` subagent to enrich with public signal about this *type* of person.

Skip if the user says "skip research", the user pasted extensive research, or the persona is too internal/narrow.

Subagent prompt: pass interview answers. Use `WebSearch` / `WebFetch` for:
- Consumer-behavior or industry research on how this segment decides.
- Real quotes from real members in forums (Reddit, Indie Hackers, HN), podcast transcripts, interview write-ups — for the speech samples especially.
- Common pain points and language patterns across multiple sources.
- Category conventions they're exposed to (the SaaS landing-page patterns a CTO has seen 100 times).
- Segmentation nuances where the persona splits sharply.

Explicitly skip generic buyer-persona templates, AI-written listicles, "Ultimate Guide to X" content.

The subagent returns a markdown summary sectioned by persona-doc dimension, each finding cited with a URL. If research contradicts the user, surface the conflict in Phase 4.

### Phase 4 — Draft and confirm

Synthesize interview (primary) + research (secondary) into the template below. **For the speech samples specifically:** start from the user's verbatim phrases, then add 2–7 more drawn from research findings to reach 5–10, ensuring register coverage (peer / authority / frustrated / casual / written / spoken). Mark each sample with its register.

**Counter-steer the Big Five defaults explicitly.** If the persona is below 5 on Agreeableness, Conscientiousness, or above 5 on Neuroticism, the doc must include specific behavioral anchors that *show* this — because the LLM will otherwise default upward / downward.

Show the draft. Ask if anything's wrong, missing, or overstated *before* saving. Drafts almost always need at least one correction.

### Phase 5 — Name and save

See **Naming and save** section below.

## Mode 2 workflow — Bulk spreadsheet import

For when the user already has structured respondent data and wants one persona per row.

### Phase 1 — Get the file and confirm structure

Ask for the file path. CSV preferred. For XLSX, ask the user to convert (`xlsx2csv file.xlsx > file.csv`) — don't try to parse XLSX directly.

Read first 2–3 rows. Confirm:
- **Row identity** — which column identifies each respondent (becomes the slug).
- **Question semantics** — which columns capture behavioral vs. demographic vs. contextual vs. open-ended language. Ask if any are ambiguous.
- **Free-text columns** — flag these specifically. They're where verbatim speech samples come from. If absent, the personas will be weaker on the speech dimension.
- **Skipped rows** — internal tests, blanks.

### Phase 2 — Stage per-respondent assets

For each non-skipped row:
1. Determine slug (per naming rules).
2. `./.personas/assets/<slug>/`
3. `survey-source.json`:
   ```json
   {
     "slug": "<slug>",
     "source_file": "<path>",
     "source_row_index": <N>,
     "imported_at": "<ISO>",
     "answers": { "<header>": "<value>", ... }
   }
   ```
4. `source-metadata.json` with import context.

Tell the user the count + slug list before fanning out.

### Phase 3 — Fan out persona generation

Dispatch one `general-purpose` subagent per row, parallel batches of ~8. Each prompt:
- Path to `survey-source.json`.
- The full persona doc template (below).
- The quality bar (above).
- The "what the research says" principles — especially: do not fabricate speech samples from multiple-choice data; do not invent missing dimensions; mark them in Known gaps.
- Big Five inference: if the spreadsheet doesn't have personality columns, the subagent leaves Big Five at "not measured" in Known gaps rather than guessing.
- Each subagent returns the doc body (no frontmatter — orchestrator adds it).

### Phase 4 — Assemble and save in batch

For each returned doc:
- Compose frontmatter: `name: <slug>`, `description: <derived one-line>`, `last_distilled_at: <today>`, `sources: [survey-import]`.
- Write to `./.personas/<slug>.md`.

Tell the user how many personas were saved. Recommend spot-checking 2–3 random ones — bulk imports always need cleanup on edge cases (sparse rows, free-text in structured columns).

## Mode 3 workflow — Pre-supplied research / interview transcripts

For when the user pastes substantial pre-existing customer research, ICP work, or **real interview transcripts**.

If real interview transcripts are present: this is the highest-evidence persona source per the literature. Treat the transcript as the primary signal; only ask clarifying questions for fields the transcript doesn't address.

1. Read the source material in full.
2. Identify how many distinct personas it contains. Make multiple if multiple are present; don't merge.
3. For each persona, draft per the template, **pulling speech samples verbatim from the source** (this is the highest-fidelity case for speech-sample sourcing).
4. **Ask only the clarifying questions needed to fill gaps** (`AskUserQuestion`). Common gaps: Big Five calibration (real research rarely captures this), negative-experience specificity, current-constraints. Don't run the full Mode 1 interview.
5. Confirm + save per shared rules.

## Mode 4 workflow — Batch generate from a description

For when the user gives one description and wants many unique personas from it. The whole mode rests on one idea: **a good batch is a constraint set the personas all satisfy, crossed with a diversity frame along which they all differ.** Pin both down explicitly *before* generating — that is what makes them strictly on-criteria *and* non-duplicated. Hoping the LLM diversifies on its own is the documented failure mode (variance compression, homogenization); diversity here is designed, then verified.

### Phase 1 — Decompose the description into constraints + diversity axes

Read the description and split it into two lists. Show both back to the user and confirm before generating — this is the highest-leverage step in the mode.

1. **Hard constraints (non-negotiable — every persona must satisfy all of them).** The criteria in the description, made explicit and checkable. E.g. for "potential Jaguar buyers aged 40–60 who value British heritage":
   - *Potential* buyer, **not** an existing Jaguar owner.
   - Age 40–60.
   - Can plausibly afford a luxury vehicle (infer the income floor; confirm).
   - British-heritage appreciation is a genuine purchase motivator.
   If the description is vague on a constraint that matters ("high income" — how high? "in market" — for what timeframe?), ask once. Loose constraints produce off-criteria personas.

2. **Diversity axes (where they must differ).** The dimensions the description leaves *open* — these are the uniqueness budget. **Foreground behavioral and contextual axes** (per the research, those carry the predictive signal), not just demographic ones:
   - Behavioral: current vehicle / brand they're switching from, how they decide (gut vs. research vs. spouse-approval), what actually triggers a purchase.
   - Contextual: the trigger moment (lease ending, kids left home, promotion, midlife pivot), constraints (garage space, charging access, brand-image worries).
   - Motivational: *why* the shared criterion holds for them — heritage-as-status vs. heritage-as-craftsmanship vs. heritage-as-nostalgia. (Same constraint, different reasons → very different personas.)
   - Plus lighter axes: profession, life stage, geography, EV stance, and Big Five spread.

Also get **N** (ask if unspecified). Flag cost above ~25 (each persona is a subagent run). Above a few dozen from a thin description, diversity gets forced — say so and suggest fewer, or richer constraints.

### Phase 2 — Build the spanning plan (the anti-duplication mechanism)

Before generating anything, lay out an **N-row plan**: one row per persona, each assigning a *distinct combination* of diversity-axis values, with every row still satisfying all hard constraints. This is quota/grid sampling by hand — the goal is to **span** the allowed space, deliberately including the extremes and the awkward-but-valid combinations, not cluster near the obvious archetype.

- Vary the **motivation** behind the shared criterion across rows (the single biggest guard against clones — same constraint, different *why*).
- Vary **negative experiences** deliberately (different current frustration / recent setback per persona) — it's a required field *and* a strong differentiator, and it counters the LLM's positivity drift across the batch.
- Spread **Big Five** across rows — don't let all N drift to the default high-A / high-C / low-N; assign some disagreeable, disorganized, anxious profiles where the constraints allow.
- Show the plan as a compact table (persona → its defining cell). Let the user edit it. The plan *is* the uniqueness guarantee; the docs just flesh out each cell.

### Phase 3 — Ground once, then generate in parallel

- **One shared research pass first** (optional but recommended): spawn a single `general-purpose` subagent to gather real segment signal — pain points, decision patterns, and especially verbatim language — for *this* audience (per Mode 1 Phase 3). Pass its findings to every generator so the batch is grounded in real language, not pure invention. Skip only if the user says skip or the segment is too internal/narrow.
- **Then fan out**: one `general-purpose` subagent per persona, in parallel batches of ~8 (as Mode 2). Each prompt contains:
  - The **full hard-constraint list**, with an instruction to treat it as non-negotiable — if its assigned cell would violate a constraint, adjust the cell, never the constraint.
  - Its **assigned diversity cell** from the spanning plan (the specifics that make this persona unique).
  - The shared research findings.
  - The persona doc template, the quality bar, and the "what the research says" principles — especially: prefer structured fields over invented prose; only use speech samples grounded in the research pass (mark invented ones); counter-steer Big Five to the assigned profile.
  - Each subagent returns the doc body (no frontmatter).

### Phase 4 — Verify: constraint compliance + de-duplication

Before saving, run two checks (orchestrator, or a single verification subagent over all drafts):

1. **Constraint compliance** — every persona satisfies every hard constraint. Any that drifted off-criteria (the most common failure: a generator softened a constraint to fit its cell) is regenerated, not kept. Report any that needed a redo.
2. **De-duplication** — no two personas are near-twins. Compare defining traits, slugs, JTBD, and speech samples. If two collapse onto the same point, push them apart along an unused diversity axis (or regenerate one cell). The spanning plan makes dupes rare; this catches the stragglers.

### Phase 5 — Assemble, name, save, report

- Frontmatter per persona: `name: <slug>`, derived one-line `description`, `last_distilled_at: <today>`, `sources: [batch-description]` (add `web-research` if the shared research pass ran).
- **Evocative, distinct slugs** from each persona's defining cell (`heritage-nostalgic-empty-nester`, `status-switching-audi-owner`) — never `persona-1`.
- Save all to `./.personas/`. Report the count, the slug list, and the **diversity frame you used** (the axes and how you spread them) so the user can see the spanning logic. Recommend spot-checking 2–3, and note honestly that these are description-generated (lowest-fidelity tier) — point to `persona-copula` (if data exists) or Mode 3 (interviews) to upgrade fidelity later.

## Persona doc template (every mode)

```markdown
---
name: <kebab-case-slug>
description: <one-line summary — used downstream to describe the persona at a glance>
last_distilled_at: <YYYY-MM-DD>
sources: [interview]              # or [interview, web-research], [survey-import], [icp-doc], [interview-transcript], etc.
---

# <Display name — short, memorable, evocative of the defining trait>

## At a glance
2–3 sentences. Who they are, what they're trying to do, the single most defining trait that shapes how they'd react in this category.

## Behavioral (primary)
*What they actually do.* Highest-evidence dimension per AskRally — this is what makes simulations predictive.
- **What they're trying to get done (JTBD):** the outcome in concrete terms, including the success metric they'd use.
- **What they use / have tried:** current stack, past attempts, what they bounced from. Name specific products / tools.
- **How they decide:** solo / convinces-a-boss / committee. Who else is involved. What evidence they need.
- **Frequency / cadence:** how often this comes up for them.

## Contextual (primary)
*The situation and moment they'd encounter this.* Co-primary with behavioral per AskRally.
- **Trigger:** what puts them in market.
- **Constraints:** budget / time / expertise / political-capital limits.
- **Environment:** where and how they'd evaluate (mobile in 30 seconds vs. desktop deep-dive vs. team review meeting).

## Demographics
*Who they are on paper.* Scaffolding, not focus. Keep tight: role, company / life stage, geography or career stage if relevant.

## Big Five personality
Numeric scales (1–10) plus a one-line behavioral anchor per trait. **Counter-steer the LLM defaults** — LLMs default to high-A, high-C, low-N; if this persona is otherwise, the anchors must show it concretely.

- **Openness:** N — <one-line anchor: how this shows up in their behavior>
- **Conscientiousness:** N — <anchor>
- **Extraversion:** N — <anchor>
- **Agreeableness:** N — <anchor>
- **Neuroticism:** N — <anchor>

## What makes them bounce
Specific patterns, claims, design choices, pricing structures that trigger distrust or disengagement. Quote real language wherever possible.

## What would actually convince them
Evidence, social proof, demo flow, structural arguments, or guarantees that move them from "skeptical" to "I'll try it." Concrete.

## Negative experiences and constraints (required)
*Per Stanford "Promise with a Catch" — LLMs systematically omit hardship; this section forces them in.*
- **Current frustration:** what's actively annoying them right now in this space.
- **Recent setback:** a specific failed attempt or letdown in the past 6–12 months.
- **Persistent constraint:** a hard limit (budget / time / capability / political) they can't easily resolve.
- **Pattern they keep repeating that doesn't work:** the workaround they know is wrong but haven't fixed.

## How they actually talk
5–10 verbatim speech samples covering different registers. Mark each with its context. Sourced from real research / interviews / customer language wherever possible — invented samples are weaker signal but allowed if marked as such.

| # | Register | Sample |
|---|---|---|
| 1 | Peer (casual) | "..." |
| 2 | Authority (formal) | "..." |
| 3 | Frustrated | "..." |
| 4 | Selling internally | "..." |
| ... | ... | ... |

Plus:
- **Terms they use:** (3–6 words / phrases that appear naturally in their language)
- **Terms they avoid / dislike:** (3–5 words that trigger skepticism)
- **Where they spend time:** (specific communities, channels, sources they trust — not generic categories)

## Psychographics (de-emphasized)
*AskRally evidence: psychographics add noise more than signal. Keep brief or omit. Include only if directly grounded in observed behavior.*

If kept: 2–4 sentences max. Values that are *visible in their behavior* (not aspirational); beliefs about this category they've stated or strongly implied. Skip lifestyle adjectives and personality archetypes.

## Known gaps (required)
What we don't know yet about this persona. Per the literature, an explicit gaps section is the strongest defense against downstream hallucination. Include:
- Dimensions where the source material was thin.
- Tensions between user-stated and research-found signal.
- Topics or scenarios the persona doc doesn't ground.
- For low-literacy / non-WEIRD personas: a note that Big Five scores are an outside-rater approximation, not a validated self-report.
```

## Naming and save (shared)

**Naming rules:**

1. **If the user named the persona** (in request / interview / spreadsheet slug column): use that. Lowercase, kebab-case.
2. **If not, you pick a slug** based on who the persona is — evocative of their defining trait. `bootstrapped-consultant.md`, `skeptical-series-a-cto.md`, `enterprise-it-buyer.md`. Never `persona-1.md` or generic placeholders.
3. **Collisions:** append a meaningful disambiguator (`skeptical-cto-enterprise.md` vs `skeptical-cto.md`) — not `-2`. Confirm with the user.
4. **Tell the user the slug** in one short line before saving so they can override.

**Save:**
1. Ensure `./.personas/` exists.
2. Set `name:` in frontmatter to match the filename slug.
3. Write the file.
4. Tell the user the file path. Offer next steps: persona-review, a persona-research study, or define an audience grouping via persona-audience.

## Anti-patterns (do not do these)

- **Adding "answer honestly" / "be unbiased" / "respond objectively" preambles** to the persona doc. Documented to *increase* bias (+38–134% across studies). Don't.
- **Letting the LLM "enrich" the persona** with extended invented backstory. Documented as the most damaging step (Stanford). Keep generated prose minimal; prefer structured fields.
- **Adding more demographic fields** to "make the persona richer." Demographics are scaffolding, not signal — beyond the minimal anchor, more demographics is cargo-culted.
- **Using MBTI, DISC, or Enneagram** instead of Big Five. 47% test-retest reliability for MBTI; Big Five explains ~2× the variance. Use Big Five.
- **Heavy identity-marker loading** (especially minority-group markers) without paired behavioral / contextual specifics. The caricature literature shows minority personas are disproportionately distorted — counteract with concrete behavioral / situational detail, not by adding identity emphasis.
- **Writing a "voice / style" section** for downstream skills to mimic. Downstream skills explicitly avoid voice mimicry. Speech samples are for showing *what* they talk about and in *what register*, not for dialect / accent / catchphrase fabrication.
- **Inflating speech samples to fake variety.** 10 samples of the same register is worse than 5 samples in genuinely different registers.
- **Skipping the negative-experiences section.** It's required. A persona without current frustrations or recent setbacks is a marketing fantasy.
- **(Mode 4) Batch-generating without a spanning plan.** Asking for "10 personas fitting X" and generating them in one undirected pass produces 10 near-clones huddled around the obvious archetype — the documented homogenization failure. Decompose into constraints + diversity axes and lay out the spanning plan *first*.
- **(Mode 4) Softening a hard constraint to make a persona "work."** The constraints are the criteria the user asked for; they're non-negotiable for every persona. If an assigned diversity cell can't satisfy them, change the cell, not the constraint — and verify compliance before saving.

## Notes

- One persona per run for Modes 1 and 3. Modes 2 and 4 are the batch modes; spot-check regardless. Mode 4 differs from Mode 2 in that there's no source row per persona — uniqueness is engineered via the spanning plan, so the plan and the dedup pass are load-bearing, not optional.
- Do not invent details the user didn't give and research didn't surface. Extrapolation → **Known gaps**, not as fact.
- If the user has interview transcripts, that's Mode 3 with the highest fidelity available. Use them.
- Downstream skills will produce variance-compressed outputs even with a perfect persona (this is an LLM-level constraint, not a persona-doc constraint). The persona doc can help by including contradictions, mood-state notes, and recent-surprise anchors that give the simulation material to vary from.

## References

The persona-doc structure and quality bar above are grounded in:

- Park, J. S. et al. (2024). *Generative Agent Simulations of 1,000 People*. https://arxiv.org/abs/2411.10109 — interview-grounded personas hit 85% of human test-retest accuracy.
- Li, Chen, Namkoong, Peng (2025). *LLM Generated Persona is a Promise with a Catch*. https://arxiv.org/abs/2503.16527 — descriptive LLM-prose personas worst; positivity / progressive / homogenization biases documented; negative experiences must be explicit.
- AskRally (2024). *What's Predictive in a Persona*. https://askrally.com/article/whats-predictive-in-a-persona — behavioral + contextual wins on F1; psychographics adds noise; demographics scaffolding only.
- AskRally (2024). *Removing Political Bias in AI Reduces Other Biases*. https://askrally.com/article/removing-political-bias-ai-reduces-other-biases — bias transfers across domains; calibration matters.
- Argyle, L. et al. (2023). *Out of One, Many*. https://arxiv.org/abs/2209.06899 — algorithmic fidelity; backstory detail improves fidelity.
- Bisbee et al. (2024). *Synthetic Replacements for Human Survey Data? The Perils of LLMs*. — temporal instability; prompt-sensitivity; variance compression.
- Cheng et al. (2023). *Bias Runs Deep: Implicit Reasoning Biases in Persona-Assigned LLMs*. https://arxiv.org/abs/2311.04892 — persona assignment leaks stereotypes into all downstream answers.
- Cheng et al. (2023). *CoMPosT: Characterizing & Evaluating Caricature in LLM Simulations*. https://arxiv.org/pdf/2310.11501 — minority-identity personas disproportionately caricatured; broad topics maximize caricature.
- *Mitigating Social Desirability Bias in Random Silicon Sampling* (2025). https://arxiv.org/html/2512.22725 — "answer honestly" backfires (+44%); analytical-persona priming backfires (+38%); reverse-coding +134%; third-person reframing −23.8% divergence.
- *Persistent Instability in LLM Personality Measurements* (2026). https://arxiv.org/html/2508.04826v3 — Big Five steering noisy even at 400B+; CoT increases trait variance; multi-turn degrades trait fidelity in <50B models.
- *Scaling Personality Control in LLMs with Big Five Scaler Prompts* (2025). https://arxiv.org/pdf/2508.06149 — numeric scaler format achieves r > 0.85 with measured traits.
- Frontiers Comp. Neuroscience (2026). *Critical analysis of MBTI-based LLM persona profiling*. — MBTI 47% test-retest; Big Five explains 2× the variance.
- Sarstedt et al. (2024). *Using LLMs to Generate Silicon Samples in Consumer and Marketing Research*. *Psychology & Marketing*. — variance compression; magnitude unreliable, direction reliable.
- Hu & Collier (2024). *Quantifying the Persona Effect in LLM Simulations*. https://arxiv.org/pdf/2402.10811 — persona axes only help when they actually predict the outcome in real data.
- Liu et al. (2025). *Race and Gender in LLM-Generated Personas: 41-occupation audit*. https://arxiv.org/html/2510.21011v1 — provider safety scores don't predict bias direction.

Treat the above as the evidentiary backbone of this skill. When a future user pushes back on a quality-bar choice ("why is psychographics deprioritized?"), the answer is in this list.
