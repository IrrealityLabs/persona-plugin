# Web search source

How to gather public web content about a persona target — interviews, blog posts, podcast transcripts, forum threads, conference talks — and aggregate it into `./.personas/assets/<slug>/web-research.md`. No API key required; uses the built-in `WebSearch` and `WebFetch` tools.

## When to use

- The persona target is a public figure or has a substantial public footprint (their blog, their interviews, their conference talks).
- The persona is an abstract type and you want to ground it in *what real members of that type say in public* — e.g. Indie Hackers forum posts, Reddit threads, podcast transcripts.
- As a multiplier on top of Slack or X — adds external public writing to the corpus.

## Phase 1 — Disambiguate the target

Before searching, make sure you and the user are talking about the same person/type.

- If the target is a **named real person**, do one quick disambiguating search (e.g. `"Sarah Chen" CMO Acme`) and confirm with the user which of the top results is the right person. People with common names need a clarifying detail (employer, role, city, recent project). Don't assume.
- If the target is an **abstract type** (e.g. "the typical bootstrapped consultant"), ask the user for 2–4 *exemplar names* — specific real people who fit the type. The web search then aggregates across those exemplars rather than searching the abstract noun phrase, which produces only generic listicle content.

If you can't confirm the target unambiguously, stop and ask. Don't distill a persona from web results that might be the wrong person.

## Phase 2 — Fan out research subagents

Use the `Agent` tool (`subagent_type: general-purpose`) to run **3–6 research subagents in parallel**, each focused on a different surface area. Splitting the work parallelizes the search and keeps each subagent's context focused.

Suggested splits for a named individual:

1. **Their own writing.** Personal site, blog, Substack, Medium, company blog posts they authored. Search: `"<name>" blog OR essay OR "I think" OR "I believe"`.
2. **Interviews and podcasts.** Search: `"<name>" interview OR podcast OR "talked to"`. Pull transcripts where available.
3. **Conference talks and videos.** Search: `"<name>" talk OR keynote OR "<name>" site:youtube.com`. Pull transcripts or detailed summaries.
4. **Social discussion *about* them.** What others say they believe, where they've taken public positions, controversies, endorsements. Search: `"<name>" said OR argued OR "according to"`.
5. **Their company / project pages, if relevant.** What the org they're associated with publicly stands for — useful as context, weighted lower than first-person content.
6. **Recent trajectory (last ~12 months).** A deliberate recency sweep, working backward roughly month by month: `"<name>" <Month YYYY>`, recent interviews, announcements, posts, news. This captures the *arc* and current focus so the synthesized body reflects who the target is **now**, not a stale snapshot. It's fine for a stretch to be quiet — note that honestly rather than padding. Flag any shift from older positions (people change their minds; the distillation should see the change, not silently average over it). Push the **most recent 1–3 months hardest** — new launches, announcements, role changes, and fresh product specifics are exactly what a web persona is most likely to miss, and the gap is what makes it sound out of date.

**Two weightings decide whether the persona rings true — both are common, costly failure modes for web personas:**

- **Spoken ≥ written.** Essays and blog posts overweight a person's *pet* themes and any memorable framework they coined — on the page they "go harder" on a few topics than they do in person. Spoken sources (podcast and video interviews, conference Q&A, panels) show what they *actually* emphasize and how they actually sound — looser, more concrete, more anecdotal. Aim for a corpus where spoken content is at least as heavy as their writing; if you can only find writing, say so in the assembled file, so the distiller knows not to treat blog frameworks as the person's universal lens.
- **Concrete over abstract.** Deliberately hunt the specifics that make an answer ring true: named products/things they shipped or launched, concrete examples and tools, origin stories and biographical anecdotes, the actual numbers/stats they cite (with their characteristic hedges). Positions and frameworks are easy to find and easy to fake; the concrete specifics are what a thin persona misses — search for them on purpose, don't just collect stated opinions.

For an abstract type aggregated from exemplars, give each subagent 1–2 exemplars and the same five-surface brief.

### Subagent prompt template

Each research subagent should be instructed to:

- Run 3–6 targeted web searches using `WebSearch`, then `WebFetch` 5–10 of the most substantive results.
- Skip pages that are: link aggregators, search-result mirrors, or thin content (under ~500 words).
- **Extract substance for the body; capture a few real quotes for the examples.** For each useful source, return a 3–6 sentence summary of *what the persona target thinks, says, or does*, plus the URL — distilled, not pasted (no long verbatim passages, respect source copyright). **But** when a source carries the person's *own on-record words* — a stated position, a characteristic claim, or a real question→answer exchange (an interviewer's question and their reply) — capture it **short, verbatim, and attributed** and mark it as a candidate for the persona's `## Examples`. For a public figure their on-record statements *are* the substance, and these real exchanges are the strongest few-shot grounding the distillation can use.
- **Tag whose voice each finding is in:** the person's **own words** (self), a **reporter's paraphrase**, or a **third party's characterization**. Self-statements are the highest-confidence signal for positions — don't launder a critic's or reporter's framing into a stated position of the persona.
- Note where the source contradicts other sources (people's stated positions change over time; flag the shift).
- Return a single Markdown section, no preamble, format:

  ```markdown
  ### Surface: <which surface this subagent covered>
  
  - **<short pattern claim>** [self|reporter|third-party] — distilled in 3–6 sentences. [source: <url>]
  - **<short pattern claim>** [self|reporter|third-party] — distilled in 3–6 sentences. [source: <url>, <url>]
  - ...
  
  **Candidate examples** (verbatim on-record exchanges, if the surface had any — else omit):
  - context: <what prompted it> · question: "<verbatim prompt/interviewer question>" · answer: "<their verbatim on-record reply>" [source: <url>, <date if known>]
  
  **Sources reviewed:** <total count>, **sources cited:** <count>, **dead-ends:** <brief note>
  ```

Run them in parallel — all `Agent` calls in a single message.

## Phase 3 — Assemble web-research.md

Compile the subagent outputs into a single file at `./.personas/assets/<slug>/web-research.md`:

```markdown
# Web research: <target>

**Distilled at:** <ISO timestamp>
**Disambiguation:** <how the target was identified — important if name was ambiguous>
**Total sources reviewed:** <sum across subagents>
**Subagents run:** <count>

## Surface: Their own writing
<subagent 1 output>

## Surface: Interviews and podcasts
<subagent 2 output>

## Surface: Recent trajectory (last ~12 months)
<recency-sweep subagent output — most recent first>

...
```

This file is the input to Phase 3 of `persona-distill` (the fan-out distillation) — same as `slack-messages.jsonl` and `x-posts.jsonl` for those sources. The distillation step treats `web-research.md` as just another corpus chunk. The `[self|reporter|third-party]` tags tell the distiller whose voice a claim is in (weight `self` highest for stated positions), and the **Candidate examples** the subagents surfaced are the verbatim on-record exchanges the distiller draws on when selecting `## Examples` — the one place verbatim belongs.

## Quality bar

- If the surface searches turn up almost nothing substantive (e.g. the target has minimal public footprint), say so — don't fabricate a thick persona from thin source material. Offer to switch sources (Slack? X?) or accept a known-sparse persona.
- If two subagents return contradictory claims about the persona's position on a topic, keep both with their sources. The Phase 3 distillation will reconcile or flag the tension; you shouldn't pre-resolve it here.
- Cap the file at ~5,000 words. If it's larger, the subagents over-extracted — re-run with tighter "extract substance, not snippets" emphasis.
