---
name: persona-grounded-theory
description: Run grounded theory analysis with the personas — iterate data collection and analysis through open / axial / selective coding to build a theory from the bottom up rather than testing a hypothesis. The persona panel serves as the source of "interview transcripts"; the skill orchestrates theoretical sampling, constant comparison, and saturation-checking. Use when the user says "/persona-grounded-theory", "do grounded theory on X", "build a theory from these personas", "let's discover the pattern, not test it", or has an open research question with no a-priori hypothesis.
---

# Persona Grounded Theory

Grounded theory builds an explanation *from* the data, instead of testing a hypothesis against it. The data here = persona responses to questions about an open research area. The output = a theory: a set of core categories and the relationships between them, supported by an evidence trail back to specific persona quotes.

Five concepts, structured as a hierarchy:

```
                THEORY (the explanation)
                   ▲
            CORE CATEGORY (selective coding)
                   ▲
           CATEGORIES (axial coding)
                   ▲
              LABELS (open coding)
                   ▲
             EXAMPLES (raw responses)
```

You build upward by **constant comparison**: examples → compared → produce labels; labels → compared → produce categories; categories → compared → produce a core category that organizes them; the core category and its relationships are the theory.

You interleave with **theoretical sampling**: you don't decide who to ask up front — you sample iteratively, choosing the next personas to probe based on what the emerging categories *don't yet explain*. You stop when sampling stops producing new categories (saturation).

## When to use vs. alternatives

- Use `persona-grounded-theory` when you have an **open research question** and want a theory built from evidence — "why do customers in this space behave this way?", "what really drives churn here?", "what's the unspoken pattern across these complaints?"
- Use `persona-survey` when you already have hypotheses and want to test them.
- Use `persona-interview` for depth on one viewpoint without theory-building.
- Use `persona-focus-group` / `persona-council` for group dynamics, not coding.

## Sample size and cost

- **Sweet spot:** 5–12 personas, ~2–5 questions each, with 3–4 iteration cycles. Total subagent runs: 30–150.
- **Always warn on cost** — see `persona-research/references/cost-estimator.md`. This is one of the more expensive methods because of multi-phase coding.
- Below 4 personas, theoretical sampling has no room to maneuver. Switch to a smaller method.

## Inputs

- **Research question** — open-ended, not a yes/no. "What drives indie SaaS founders to switch billing platforms?" is good. "Will indie founders switch to Stripe?" is hypothesis-testing.
- **Initial seed personas** (optional) — 2–4 personas to start with. If unspecified, the orchestrator picks an initially-diverse 3 by reading the personas' `## At a glance` lines in `./.personas/` and choosing ones that span the widest range of contexts/viewpoints.
- **Saturation guess** (optional) — how many cycles to budget. Default: stop after no new categories emerge for 2 cycles, hard cap 5.

## Storage layout

Everything goes into `./.personas/assets/grounded-theory-runs/<run-id>/`:

```
<run-id>/
├── question.md                # the research question, fixed
├── examples/                  # one file per persona response, raw
│   └── <persona-slug>__<question-id>.md
├── labels.jsonl               # open coding output (cumulative)
├── categories.jsonl           # axial coding output (cumulative, updated each cycle)
├── core-categories.jsonl      # selective coding output
├── memos.md                   # orchestrator memos as theory emerges
└── theory.md                  # final write-up
```

Per-cycle artifacts live in subdirectories `cycle-1/`, `cycle-2/`, etc.

## Workflow

### Phase 0 — Set up

Generate a `run-id` (timestamp). Create the storage layout. Write `question.md` with the research question.

Start a `memos.md` — this is where you, the orchestrator, jot theory hunches as they form. The discipline of writing memos through the cycles is what separates a real grounded theory from a list of clusters.

### Phase 1 — Initial theoretical sampling

If the user didn't name initial personas, read the `## At a glance` lines of the personas in `./.personas/` and pick an initially-diverse 3 yourself — for grounded theory, prefer cognitive/contextual diversity over topical overlap; we want to surface variation early.

Tell the user the initial seed and explain why those 3 span the widest variation.

### Phase 2 — Cycle (repeat until saturation)

Each cycle has four steps: collect data, open code, axial code, decide next.

#### Step A — Collect data (one or more questions per sampled persona)

For each persona in the current cycle's sample:
- Draft 2–4 open-ended questions tied to the research question. Cycle 1: broad starter questions ("Tell me about the last time you considered <thing>"). Cycle 2+: questions targeted at gaps the emerging categories don't yet explain.
- Apply the `persona-ask` framing checklist. Questions should be non-leading and behavioral.
- Each persona subagent answers under the Ground, think, then talk (Grounding → Thinking → Talking) contract from `persona-ask`. **Each (persona, question) response leads with two private fields, before the spoken answer:**
  - **Grounding:** (private) The persona-doc sections that bear on this, cited first: `§ <Section>: "<…>"` + a confidence read [high|medium|low|off-pattern].
  - **Thinking:** (private) Private reasoning over that grounding: what this persona would genuinely conclude, where the evidence is thin.
  - Then the spoken first-person answer ("Talking").

  Grounding + Thinking lead **every** response (every cycle, every persona), not just cycle 1. They're the audit trail — orchestrator-only. **Code only the spoken answer:** open coding (Step B) clusters the Talking part; the Grounding and Thinking fields are not coded into labels/categories.
- For each (persona, question) pair, spawn a subagent and save the response to `examples/<slug>__<question-id>.md`.

Cycle-1 starters that work well for grounded theory:
- "Walk me through what happens when you encounter <situation>."
- "What's the part of <topic> you wish people understood better about you?"
- "When have you been surprised by your own reaction to <topic>?"

#### Step B — Open coding (constant comparison)

For each example written in Step A, spawn a coding subagent. Each prompt:
- The example response. **Code only the spoken answer (the Talking part); ignore the Grounding and Thinking fields — they're audit material, not data to cluster.**
- The full `labels.jsonl` so far (so they can re-use labels rather than coining new ones for the same idea).
- Instruction: "Code this example. For each distinct meaning unit in it, propose a short label (3–6 words) describing what's going on. If an existing label fits, reuse it. Output JSON list: `[{label, quote_from_example, persona_slug, confidence}]`."

Append all new (label, evidence) tuples to `labels.jsonl`. Don't dedupe blindly — different examples can support the same label with different evidence; keep both.

#### Step C — Axial coding (compare labels → categories)

After Step B, fan out one **axial-coding subagent** with the *full* labels.jsonl. Prompt:
- The labels and their evidence (compressed if large — keep label + count + sample evidence per label).
- The current `categories.jsonl` (so categories can be refined rather than re-invented).
- The research question.
- Instruction: "Group these labels into categories. A category is a higher-level theme that 3+ labels share. For each category, list the labels it contains, the dominant pattern across them, and 1–2 outlier labels that 'sort of' fit (these often signal where the category needs refinement next cycle). Output JSON: `[{category_name, description, member_labels, outlier_labels, supporting_personas_count}]`."

Write the result to `cycle-N/categories.jsonl` and update the cumulative `categories.jsonl`.

#### Step D — Saturation check and next-cycle decision

After axial coding, check for saturation. Two signals:

1. **New-category rate.** How many categories appeared in cycle N that didn't exist in cycle N−1? If this number is 0–1 for two cycles in a row → approaching saturation.
2. **Coverage.** Are there examples whose labels still don't fit any category cleanly? If yes → categories aren't complete; keep going.

Decide:

- **Continue:** pick next-cycle personas via theoretical sampling. Look at the categories list: which categories have the *fewest* supporting personas, or which were flagged with outliers? Read the `## At a glance` lines of the personas in `./.personas/` not yet sampled and pick 2–3 whose docs suggest they'd have relevant input to those underdeveloped categories. Tell the user which you picked and which category each is meant to develop.
- **Graduate to selective coding** (Phase 3) when saturation signals fire OR hard cap (5 cycles) reached. Tell the user.

Write a memo to `memos.md` per cycle: what categories are looking solid, what hunches you have about the eventual theory, what you'd want to probe next.

### Phase 3 — Selective coding

Once you graduate from axial coding:

Spawn one **selective-coding subagent** with the *full* categories.jsonl. Prompt:
- All categories with their descriptions, member labels, and supporting personas.
- The research question.
- The memos written across cycles.
- Instruction: "Find the **core category** — the single category or higher-level concept that the other categories naturally relate to. It should be central enough that most other categories can be described as 'a kind of', 'a cause of', 'a consequence of', or 'a condition for' this core. If a single core is too forced, two or three core categories with explicit relationships are acceptable. For each core category: name, description, and the relationships from each of the other categories to it. Output JSON."

Write to `core-categories.jsonl`.

### Phase 4 — Write the theory

Spawn one final synthesis subagent (or write it yourself if the material is small enough). Inputs:
- Research question, core-categories, categories with descriptions, key memos.

Output to `theory.md`:

```markdown
# Grounded theory: <topic>

## Research question
<...>

## The theory in one paragraph
Plain-language statement of what the analysis explains. Lead with the core category and its key relationships.

## Core category / categories
For each core: name, what it is, why it organizes the others.

## Supporting categories and their relationships
For each non-core category: how it relates to the core (kind-of / cause-of / consequence-of / condition-for / variant-of). Include 1–2 representative labels and a quote per category to ground it.

## Evidence trail
For load-bearing claims, point back to specific examples (`examples/<slug>__<q>.md`). The reader should be able to verify the theory by tracing claims back to data.

## What this theory does NOT explain
Outliers, edge cases, and contradictions that didn't fit. Honest about the theory's boundaries.

## How the theory was built
Brief: N personas across N cycles, M examples, K labels coded into J categories. Saturation reached at cycle X because <reason>.

## Confidence and provenance
This theory was built from persona simulations, not real interview transcripts. The theory is best read as a hypothesis to test with real research, not as a finding from real research. Specifically:
- Where the persona docs were thin (cite known-gaps from the relevant persona docs), the theory's coverage of that area is weakest.
- A theory built from N personas is fundamentally bounded by the variance present in those personas. If they shared a blind spot, so does the theory.
```

## Notes

- **Coding is interpretive.** Two careful coders working from the same examples will produce different labels. That's fine for grounded theory; the discipline is the constant comparison and the audit trail, not perfect inter-rater agreement.
- **Resist over-coding.** A label per sentence is too granular; a label per response is too coarse. Aim for 3–8 labels per example.
- **The orchestrator's memos are part of the methodology.** Don't skip them. They're how the theory takes shape in your head before the final write-up.
- Reading recommendation for the user: Charmaz, *Constructing Grounded Theory*, for the constructivist version (most usable for product/marketing research). Strauss & Corbin for the more procedural version. The Delve blog (`blog.delvetool.com`) has the most accessible practitioner-oriented walkthrough.
- A grounded theory from persona simulations is *necessarily* a hypothesis-generator, not a theory in the strong scientific sense. Treat the output as "the most interesting questions to take into real customer research," not as the conclusion of customer research.
