# Web search source

How to mine the public web for what a persona target has **actually said** — interview
answers, podcast quotes, their own blog posts, talk transcripts, forum replies — and save
it as `./.personas/assets/<slug>/web.jsonl`. No API key required; uses the built-in
`WebSearch` and `WebFetch` tools.

**The one rule: collect only the person's own words.** Third-party commentary, reporter
paraphrase, and "what others say about them" are not collected — you can't trust what
other people say about someone, and it pollutes the persona's voice. Third-party *pages*
are still fair game as places to find direct quotes; what gets saved is only the quotes.

Each row is the universal asset format:

```jsonl
{"context": "Decoder podcast, on how the company thinks about AI tooling", "question": "How do you decide what to build?", "answer": "We don't want net-new behavior — meet developers where they are.", "source": "https://theverge.com/decoder/..."}
```

- `answer` — their words, **verbatim**. Short quotes (respect source copyright); never paraphrase into this field.
- `question` — the interviewer's question or prompt, verbatim where available; empty if unprompted (their own blog post, a talk).
- `context` — what was happening: the publication/show, topic, date if known.
- `source` — the URL.

## When to use

- The persona target is a public figure or has a substantial public footprint (their blog, their interviews, their conference talks).
- The persona is an abstract type and you want to ground it in *what real members of that type say in public* — e.g. Indie Hackers forum posts, Reddit threads, podcast transcripts.
- As a multiplier on top of Slack or X — adds external public speech to the corpus.

## Phase 1 — Disambiguate the target

Before searching, make sure you and the user are talking about the same person/type.

- If the target is a **named real person**, do one quick disambiguating search (e.g. `"Sarah Chen" CMO Acme`) and confirm with the user which of the top results is the right person. People with common names need a clarifying detail (employer, role, city, recent project). Don't assume.
- If the target is an **abstract type** (e.g. "the typical bootstrapped consultant"), ask the user for 2–4 *exemplar names* — specific real people who fit the type. The web search then aggregates across those exemplars rather than searching the abstract noun phrase, which produces only generic listicle content.

If you can't confirm the target unambiguously, stop and ask. Don't distill a persona from web results that might be the wrong person.

## Phase 2 — Fan out research subagents

Use the `Agent` tool (`subagent_type: general-purpose`) to run **3–5 research subagents in parallel**, each mining a different surface for the person's own words:

1. **Their own writing.** Personal site, blog, Substack, Medium, company posts they authored. Search: `"<name>" blog OR essay OR "I think" OR "I believe"`.
2. **Interviews and podcasts.** Search: `"<name>" interview OR podcast OR "talked to"`. Pull transcripts where available — these yield real question→answer exchanges, the highest-value rows.
3. **Conference talks, panels, and videos.** Search: `"<name>" talk OR keynote OR "<name>" site:youtube.com`. Pull transcripts or quote-rich writeups.
4. **Recent trajectory (last ~12 months).** A deliberate recency sweep, working backward roughly month by month: `"<name>" <Month YYYY>`, recent interviews, announcements, posts. This captures who the target is **now**, not a stale snapshot. Push the **most recent 1–3 months hardest** — fresh launches and specifics are exactly what a web persona is most likely to miss. It's fine for a stretch to be quiet; note that honestly rather than padding. Flag where a recent quote contradicts an older one (people change their minds; the distillation should see the change, not silently average over it).

**Two weightings decide whether the persona rings true — both are common, costly failure modes for web personas:**

- **Spoken ≥ written.** Essays and blog posts overweight a person's *pet* themes and any memorable framework they coined — on the page they "go harder" on a few topics than they do in person. Spoken sources (podcast and video interviews, conference Q&A, panels) show what they *actually* emphasize and how they actually sound — looser, more concrete, more anecdotal. Aim for a corpus where spoken quotes are at least as heavy as written ones; if you can only find writing, note it in the metadata so the distiller knows not to treat blog frameworks as the person's universal lens.
- **Concrete over abstract.** Deliberately hunt the quotes with specifics: named products/things they shipped, concrete examples and tools, origin stories and anecdotes, the actual numbers they cite (with their characteristic hedges). Stated positions are easy to find and easy to fake; the concrete specifics are what a thin persona misses — search for them on purpose.

For an abstract type aggregated from exemplars, give each subagent 1–2 exemplars and the same brief.

### Subagent prompt template

Each research subagent should be instructed to:

- Run 3–6 targeted web searches using `WebSearch`, then `WebFetch` 5–10 of the most substantive results.
- Skip pages that are: link aggregators, search-result mirrors, or thin content (under ~500 words).
- **Return only the person's own words**, as asset rows. Reporter framing and third-party characterization are not collected — if a profile piece quotes the person directly, take the quote and leave the framing. Keep each quote short and verbatim; capture the interviewer's question verbatim when there is one.
- Return JSONL rows only, no preamble — one per line:

  ```jsonl
  {"context": "<show/publication, topic, date if known>", "question": "<verbatim prompt, or empty>", "answer": "<their verbatim words>", "source": "<url>"}
  ```

- After the rows, one short footer line: `sources reviewed: N · quotes found: N · dead-ends: <note>` plus a flag if the surface was writing-only (no spoken sources found).

Run them in parallel — all `Agent` calls in a single message.

## Phase 3 — Assemble web.jsonl

Concatenate the subagents' rows into `./.personas/assets/<slug>/web.jsonl`, dropping exact duplicates (same answer + source). Then write `web-metadata.json`:

```json
{"slug": "...", "source": "web", "pulled_at": "<ISO>", "disambiguation": "<how the target was identified>",
 "rows": 123, "sources_reviewed": 45, "spoken_vs_written": "<balance note>", "subagents": 4}
```

This file is the input to the fan-out distillation — the same universal rows as `slack.jsonl` and `x.jsonl`, so the distiller treats every source identically.

## Quality bar

- If the searches turn up almost nothing the person actually said (minimal public footprint), say so — don't fabricate a thick persona from thin source material. Offer to switch sources (Slack? X? email?) or accept a known-sparse persona.
- If two quotes contradict each other on a position, keep both rows with their sources. The distillation will reconcile or flag the tension; you shouldn't pre-resolve it here.
- Aim for the strongest ~100–300 rows, not everything — quote-rich interviews beat exhaustive coverage of thin pages.
