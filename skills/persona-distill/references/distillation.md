# Distillation — fan-out spec

Operational spec for turning the contents of `./.personas/assets/<slug>/` into a persona doc at `./.personas/<slug>.md`.

The current Claude session is the **orchestrator** — it chunks the corpus, dispatches workers and reducers via the `Agent` tool, assembles the final doc, and writes it. Subagents do not write the persona doc; the orchestrator does.

## Inputs

Any combination of these files in `./.personas/assets/<slug>/`:

- `slack-messages.jsonl` — one JSON record per line; standalone or thread (see `slack-source.md`).
- `x-posts.jsonl` — one JSON record per line; post / reply / quote (see `x-source.md`).
- `web-research.md` — pre-distilled markdown (see `web-search-source.md`).
- `metadata.json` — source metadata across all dumps; tells you what's present.

## Output

A single file: `./.personas/<slug>.md`.

A good persona doc covers **four dimensions + a verbatim language sample**: demographics, psychographics, behavioral, contextual, and how-they-actually-talk. Each shows up as a dedicated section. If any dimension is thin in the doc, the panel's reactions in that area will be weak.

```markdown
---
name: <slug>
description: <one-line summary — used by persona-review to describe the panel>
last_distilled_at: <ISO timestamp>
sources: [slack, x, web]   # any subset that was used
distilled_from:
  pulled_at: <ISO timestamp>
  counts: {slack_messages: N, x_posts: N, web_sources: N}
  target: <free-text description of who this persona is>
---

# <Display name>

## At a glance
2–3 sentences synthesizing across facets — orchestrator-written.

## Demographics
*Who they are on paper.* Role, company stage if visible, life stage if visible, geography or career stage if relevant. Tight — context, not the focus.

## Psychographics
*What they value, believe, and fear.* The values that shape their decisions, beliefs about this category, aspirations and anxieties — observed in their writing.

## Behavioral
*What they actually do.*
- **What they're trying to get done:** the job-to-be-done, in concrete terms.
- **What they use / have tried:** products and approaches they've engaged with publicly, with source pointers.
- **How they decide:** solo / convinces-a-boss / committee, plus what evidence they need.

## Contextual
*The situation in which they engage.* Triggers, constraints (budget, time, role), environment.

## What makes them bounce
Specific patterns, claims, design choices that trigger pushback. **Indirect prose only** — never verbatim from the source corpus.

## What would actually convince them
Evidence / proof / structural arguments that move them, based on observed reasoning patterns.

## How they actually talk
- **Verbatim phrases they use:** real phrases from the corpus, *only* where the phrase is generic enough to be common in the segment and not a personally identifying utterance. If unsure, paraphrase.
- **Terms they use:**
- **Terms they avoid:**
- **Where they spend time** (communities, sources they cite or engage with):

## Known gaps
Topics the corpus is silent on, where extrapolation would be guessing.
```

## Decide whether to fan out

Rough heuristic:

- **Combined corpus < ~50KB** → skip fan-out. Read everything in one pass, draft the doc directly. Fast and accurate for small corpora.
- **Combined corpus ≥ ~50KB** → fan out per the stages below. A year of someone's active Slack runs 5–10MB; a year of X posts runs 1–3MB. These do not fit in a single agent's working context, period.

If sources are mixed sizes (e.g. small `web-research.md` + huge `slack-messages.jsonl`), still fan out — the workers handle the big file, the reducers fold in the small one.

## Two-stage fan-out

### Stage 1 — Workers (parallel, in batches of ~8)

Chunk the corpus:

- For `.jsonl` files: split into ~100-record chunks (≈100K tokens each).
- For `web-research.md`: pass the whole file to *every* worker as supplementary context (it's small and already distilled).
- For mixed corpora: chunk the largest file; replicate smaller files into each worker's prompt.

Dispatch one worker subagent per chunk, all in a single message so they run in parallel. Use `Agent` with `subagent_type: general-purpose`.

Each worker prompt contains:

- The chunk (inline if small; file path + chunk range if large).
- The full list of **facets** below.
- The **persona target description** from metadata.
- The **worker contract** (below).
- A request to return structured findings — one finding per claim, tagged by facet.

#### Worker contract

- **One pass over the chunk.** Extract evidence; do not synthesize across the corpus (the reducers do that).
- **Substance, not voice.** Describe patterns in indirect prose. Do not quote the source text verbatim. A finding like `claim: "frames feature decisions around reversibility"` is good; `claim: "said 'is this reversible'"` is not.
- **Citation as pointer.** For each finding, attach `evidence: [{source: "slack"|"x"|"web", ref: "<channel/date or url or tweet-id>"}]`.
- **Negative findings count.** If the chunk shows the persona *not* engaging with something you'd expect them to, that's a finding for the "Known gaps" facet.
- **Return JSON only**, schema below — no preamble, no Markdown wrapping.

```jsonc
[
  {"facet": "demographics", "claim": "...", "evidence": [{"source": "...", "ref": "..."}]},
  {"facet": "psychographics", "claim": "...", "evidence": [...]},
  {"facet": "behavioral", "claim": "...", "evidence": [...]},
  {"facet": "contextual", "claim": "...", "evidence": [...]},
  {"facet": "bounce", "claim": "...", "evidence": [...]},
  {"facet": "convince", "claim": "...", "evidence": [...]},
  {"facet": "language", "claim": "...", "evidence": [...]}
]
```

Facet definitions:
- `demographics` — observable on-paper signals: role, company stage, life stage, geography.
- `psychographics` — values, beliefs, fears, motivations evidenced by what they push for or push back on.
- `behavioral` — JTBD evidence, products/tools they engage with, decision-making mode and who else is in the loop.
- `contextual` — triggers, constraints, environments in which they engage with this category.
- `bounce` — patterns / claims / structures they push back on.
- `convince` — evidence / framings / proofs that move them.
- `language` — terms they use, terms they avoid, communities they cite. The single facet where (carefully) preserving verbatim phrasing is acceptable if the phrasing is generic to the segment, not personally identifying.

### Stage 2 — Reducers (one per persona-doc section, in parallel)

Seven reducers, one per facet — `demographics`, `psychographics`, `behavioral`, `contextual`, `bounce`, `convince`, `language`. (`At a glance` and `Known gaps` are assembled by the orchestrator, not delegated.)

Dispatch all seven in a single message so they run in parallel. Each reducer subagent gets:

- All workers' findings tagged with its facet.
- The persona target description.
- The **reducer contract** (below).
- The exact section format expected (from the persona doc template above).

#### Reducer contract

- **Dedupe.** Same claim made by multiple workers with different evidence → one claim, evidence merged.
- **Weight by evidence count.** A claim with one source is a hint ("appears to lean toward..."); three sources is a pattern (state it plainly); one source labelled "rarely, but..." is honest. Don't overclaim from thin evidence.
- **Reconcile tensions explicitly.** If two findings genuinely contradict (e.g. early posts say one thing, later posts say another), describe the tension or the shift over time — don't paper over it.
- **No verbatim text.** Same as worker contract. If any verbatim-leak slips through, the orchestrator's final sweep should catch it.
- **Output a finalized section** in the exact format the persona doc expects for that facet. No preamble, no frontmatter, no extra commentary.

## Stage 3 — Final assembly (orchestrator)

After all seven reducers return:

1. **Read the six sections.**
2. **Draft `At a glance`** — 2–3 sentences synthesizing across all facets. This is the orchestrator's synthesis, not delegated. Lead with the single most defining trait.
3. **Draft `Known gaps`** — what the corpus is silent on. Look at facets where the reducer returned thin output, and note them explicitly so the persona-review panel surfaces the gap rather than papering over it.
4. **Verbatim-leak sweep.** For each section, take a few distinctive 4–6-word substrings and grep them against the underlying corpus files. Any match means a verbatim leak — rewrite that span in indirect prose. (For Slack/X JSONL: grep the `text` fields. For web-research.md: grep the file directly.)
5. **Assemble frontmatter** from metadata.json + current timestamp.
6. **Write `./.personas/<slug>.md`.**

## Quality bar

- Every claim in the persona doc should be defensible from the assets. The orchestrator can spot-check by picking 3 strong claims (one from a `bounce` finding, one from a `convince` finding, one from a `language` finding) and tracing them back to evidence.
- If a section is uncanny — putting opinions in the persona's mouth that the data doesn't back — re-run that one reducer with the critique. Don't ship a section you wouldn't defend to the persona's face.
- "Known gaps" is not failure; it's accuracy. Don't pad it away.
