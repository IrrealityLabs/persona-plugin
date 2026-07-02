# Distillation — fan-out spec

Operational spec for turning the contents of `./.personas/assets/<slug>/` into a persona doc at `./.personas/<slug>.md`.

The current Claude session is the **orchestrator** — it chunks the corpus, dispatches workers and reducers via the `Agent` tool, assembles the final doc, and writes it. Subagents do not write the persona doc; the orchestrator does.

## Inputs

The assets folder is **immutable and append-only** — pulls and corrections only ever get *added*, never rewritten or deleted. The persona `.md` is a disposable *projection* of this folder; distilling or refreshing regenerates it. So nothing the user curated in assets is ever lost, and the assets are the persona's real history.

**Every `.jsonl` file in `./.personas/assets/<slug>/` is the same universal asset row** —
`{context, question, answer, source}`, where `answer` is always the person's own verbatim
words, `question` is what prompted it (empty if unprompted), `context` is what was
happening, and `source` resolves back to the origin. The filename says where it came from:

- `slack.jsonl`, `x.jsonl`, `web.jsonl`, `email.jsonl` — pulled by the source extractors.
- `interview.jsonl` — the user's own answers from `persona-create`'s interview, or an imported interview transcript.
- Any other `<name>.jsonl` — imported files (see `file-import.md`).
- `corrections.jsonl` — rows from `persona-correct` (the right answer after a wrong one).
- `observations.jsonl` — rows from `persona-observe` (real data added by hand). Corrections and observations are known-good ground truth — **prioritize their rows when you select `## Examples`**.
- `metadata.json` / `<source>-metadata.json` — source metadata; tells you what's present and who the target person is.
- Non-`.jsonl` files (an imported PDF's text, a pasted transcript) are the raw artifacts rows were extracted from — reference material, not a second corpus; the rows are the input.

## Output

A single file: `./.personas/<slug>.md`, in two parts:

1. **The synthesized body** (`At a glance` … `Known gaps`) — paraphrased, indirect prose. **No verbatim source text** here, same as before. This is the generalist model of the person.
2. **`## Examples`** — up to ~30 verbatim `{context, question, answer}` turns **you select** from the assets (corrections prioritized). Verbatim *is the point* here; the no-verbatim rule applies only to the body above.

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
Capturing how this person sounds is a deliberate goal, not "style noise" to strip — a persona that talks like them is more immersive (better roleplay, higher stakes) and gives you their real verbiage for things like marketing. Capture it from the corpus; never invent a tic the source doesn't show.
- **Voice & style:** 1–2 sentences on how they actually sound — recurring phrasings, sentence shape, register range — distilled from the corpus (described, not quoted; verbatim lives in `## Examples`).
- **Verbatim phrases they use:** real phrases from the corpus, *only* where the phrase is generic enough to be common in the segment and not a personally identifying utterance. If unsure, paraphrase.
- **Terms they use:**
- **Terms they avoid:**
- **Where they spend time** (communities, sources they cite or engage with):

## Known gaps
Topics the corpus is silent on, where extrapolation would be guessing.

## Examples
Up to ~30 real `{context, question, answer}` turns **selected by the distiller** from the assets —
the most representative and varied exchanges that show how this person actually responds, with the
hand-supplied turns from `corrections.jsonl` and `observations.jsonl` prioritized. Verbatim by design — this is the one section where real
source text belongs, and it's loaded as few-shot exemplars at query time. Regenerated on every
distill/refresh (it's a projection of the assets, so overwriting is fine). Render each as:

---
**Context:** <the prior exchange / situation, or — if none>

**Asked:** <the question or prompt they were responding to>

**Replied:** <what they actually said, verbatim>
---
```

## Decide whether to fan out

Rough heuristic:

- **Combined corpus < ~50KB** → skip fan-out. Read everything in one pass, draft the doc directly. Fast and accurate for small corpora.
- **Combined corpus ≥ ~50KB** → fan out per the stages below. A year of someone's active Slack runs 5–10MB; a year of X posts runs 1–3MB. These do not fit in a single agent's working context, period.

If sources are mixed sizes (e.g. a small `web.jsonl` + a huge `slack.jsonl`), still fan out — chunk the big file; replicate the small ones into each worker's prompt.

## Two-stage fan-out

### Stage 1 — Workers (parallel, in batches of ~8)

Chunk the corpus: all files are the same row format, so split each `.jsonl` into ~100-row chunks (≈100K tokens each); small files ride along whole.

Dispatch one worker subagent per chunk, all in a single message so they run in parallel. Use `Agent` with `subagent_type: general-purpose`.

Each worker prompt contains:

- The chunk (inline if small; file path + chunk range if large).
- The full list of **facets** below.
- The **persona target description** from metadata.
- The **worker contract** (below).
- A request to return structured findings — one finding per claim, tagged by facet.

#### Worker contract

- **One pass over the chunk.** Extract evidence; do not synthesize across the corpus (the reducers do that).
- **Findings: described, not quoted.** In `findings`, describe patterns in indirect prose — *including* how they think and decide and how they sound (their register and recurring framings are real signal for the `language` facet). Don't quote the source text verbatim; that's what `examples` is for. A finding like `claim: "frames feature decisions around reversibility"` or `claim: "writes in clipped, declarative one-liners"` is good; `claim: "said 'is this reversible'"` is not.
- **Record frequency and provenance for any named framework or coinage.** When the person leans on a memorable framework, model, or coined phrase, note *how often* it actually shows up and *where* — one essay, or across many talks and interviews. A framework that appears in a single blog post is a footnote, not their operating system; say so, so the reducers don't over-generalize it. And capture the **concrete specifics** — named products, real examples, anecdotes, the numbers they cite — as first-class findings, not afterthoughts: they're the substance a web persona most often lacks.
- **Examples: nominate the best rows.** The chunk's rows already *are* verbatim `{context, question, answer}` turns — in `examples`, return up to ~10 of the strongest/most varied rows verbatim (crafting a sharper `question`/`context` framing from the row's fields is allowed; inventing words for `answer` is not). Favor rows where the persona *responds* to something over unprompted remarks. The orchestrator picks the final set.
- **Citation as pointer.** For each finding, attach `evidence: ["<row source string>", ...]` — the `source` field of the rows that back it.
- **Negative findings count.** If the chunk shows the persona *not* engaging with something you'd expect them to, that's a finding for the "Known gaps" facet.
- **Return JSON only**, schema below — no preamble, no Markdown wrapping.

```jsonc
{
  "findings": [
    {"facet": "demographics", "claim": "...", "evidence": [{"source": "...", "ref": "..."}]},
    {"facet": "psychographics", "claim": "...", "evidence": [...]},
    {"facet": "behavioral", "claim": "...", "evidence": [...]},
    {"facet": "contextual", "claim": "...", "evidence": [...]},
    {"facet": "bounce", "claim": "...", "evidence": [...]},
    {"facet": "convince", "claim": "...", "evidence": [...]},
    {"facet": "language", "claim": "...", "evidence": [...]}
  ],
  "examples": [
    {"context": "...", "question": "...", "answer": "..."}
  ]
}
```

Facet definitions:
- `demographics` — observable on-paper signals: role, company stage, life stage, geography.
- `psychographics` — values, beliefs, fears, motivations evidenced by what they push for or push back on.
- `behavioral` — JTBD evidence, products/tools they engage with, decision-making mode and who else is in the loop.
- `contextual` — triggers, constraints, environments in which they engage with this category.
- `bounce` — patterns / claims / structures they push back on.
- `convince` — evidence / framings / proofs that move them.
- `language` — how they sound (register, recurring phrasings, sentence shape), terms they use, terms they avoid, communities they cite. Capturing voice/style is wanted here — described as a pattern, grounded in the corpus, never invented. The single facet where (carefully) preserving verbatim phrasing is acceptable if the phrasing is generic to the segment, not personally identifying.

### Stage 2 — Reducers (one per persona-doc section, in parallel)

Seven reducers, one per facet — `demographics`, `psychographics`, `behavioral`, `contextual`, `bounce`, `convince`, `language` (fed the `findings` arrays from the workers). (`At a glance`, `Known gaps`, and `## Examples` are assembled by the orchestrator, not delegated — Examples from the workers' `examples` arrays.)

Dispatch all seven in a single message so they run in parallel. Each reducer subagent gets:

- All workers' findings tagged with its facet.
- The persona target description.
- The **reducer contract** (below).
- The exact section format expected (from the persona doc template above).

#### Reducer contract

- **Dedupe.** Same claim made by multiple workers with different evidence → one claim, evidence merged.
- **Weight by evidence count.** A claim with one source is a hint ("appears to lean toward..."); three sources is a pattern (state it plainly); one source labelled "rarely, but..." is honest. Don't overclaim from thin evidence.
- **Reconcile tensions explicitly.** If two findings genuinely contradict (e.g. early posts say one thing, later posts say another), describe the tension or the shift over time — don't paper over it.
- **Don't let one memorable framework become a universal lens.** A coinage or model the person stated a few times — especially in writing — gets captured where it belongs, but must not be threaded through every facet. Real people answer most questions through concrete examples and products, not a single grand framework. If a draft applies the same framework to unrelated topics, or reads as more systematic and self-referential than the corpus supports, it has over-fit to a few memorable artifacts — pull it back and lead with the person's concrete specifics and actual register.
- **No verbatim text.** Same as worker contract. If any verbatim-leak slips through, the orchestrator's final sweep should catch it.
- **Output a finalized section** in the exact format the persona doc expects for that facet. No preamble, no frontmatter, no extra commentary.

## Stage 3 — Final assembly (orchestrator)

After all seven reducers return:

1. **Read the six sections.**
2. **Draft `At a glance`** — 2–3 sentences synthesizing across all facets. This is the orchestrator's synthesis, not delegated. Lead with the single most defining trait.
3. **Draft `Known gaps`** — what the corpus is silent on. Look at facets where the reducer returned thin output, and note them explicitly so the persona-review panel surfaces the gap rather than papering over it.
4. **Verbatim-leak sweep — body only.** For each *body* section, take a few distinctive 4–6-word substrings and grep them against the `answer` fields of the corpus `.jsonl` files. Any match means a verbatim leak — rewrite that span in indirect prose. **Skip `## Examples`** — it is verbatim by design.
5. **Select `## Examples`.** From the candidate turns the workers nominated (or, for a small corpus, straight from the assets), choose up to ~30 verbatim `{context, question, answer}` turns. Read `corrections.jsonl` and `observations.jsonl` first and include those as a priority — they're hand-supplied ground truth. Fill the rest choosing for **coverage and variety** over redundancy — drop near-duplicates. Pick turns that exemplify *both* how they reason and decide (their thinking) *and* how they actually sound (their voice and register), across different topics. This is a judgment call, not a mechanical sample. Render each in the Context/Asked/Replied format from the template, and append as the final section.
6. **Assemble frontmatter** from metadata.json + current timestamp.
7. **Write `./.personas/<slug>.md`.**

## Quality bar

- Every claim in the persona doc should be defensible from the assets. The orchestrator can spot-check by picking 3 strong claims (one from a `bounce` finding, one from a `convince` finding, one from a `language` finding) and tracing them back to evidence.
- If a section is uncanny — putting opinions in the persona's mouth that the data doesn't back — re-run that one reducer with the critique. Don't ship a section you wouldn't defend to the persona's face.
- "Known gaps" is not failure; it's accuracy. Don't pad it away.
- **Concrete over abstract; their register, not a tidier one.** A persona that threads one framework through every answer, or sounds more systematic and buttoned-up than the corpus shows, has over-fit. The fix is breadth and concreteness — more spoken sources, more named products and anecdotes — **not** padding the doc with guesses. Mark what the corpus doesn't cover in `Known gaps` honestly; at answer time the persona extrapolates from what *is* there, in character, with the confidence tag showing it's an extrapolation.
