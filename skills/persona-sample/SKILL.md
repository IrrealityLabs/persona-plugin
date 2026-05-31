---
name: persona-sample
description: Internal helper. Filter the personas in ./.personas/ down to the most relevant N for a given study question using a combination of QMD semantic search and grep/regex keyword matching. Called by persona-research child skills when the methodology needs fewer personas than are available, or wants to pick a topically-relevant subset. Walks the user through installing and indexing QMD on first use. Not user-invocable directly.
user-invocable: false
---

# Persona Sample

Pick the right N personas for a study. Two ranking signals, combined:

- **QMD semantic search** — semantic similarity between the study question and each persona doc.
- **Keyword grep** — regex/keyword matching for explicit terms (product names, role titles, demographic flags) that appear in the question.

The combination matters because each signal misses something the other catches. Semantic search picks up "this is a CFO question" without the word "CFO" being present in the persona. Grep picks up that the question mentions "Stripe" and only two personas mention Stripe by name. Both together is reliably better than either alone.

## Phase 0 — Setup (first run only)

QMD is required for the semantic-search half. On first run:

### Check if QMD is available

Look at the available tool list for `mcp__qmd__status` / `mcp__qmd__vsearch` / `mcp__qmd__search`. If they're present, call `mcp__qmd__status` to verify the server is responding. Move on.

If the tools are not present, QMD isn't installed/configured. Tell the user — short, factual:

> "Installing QMD so personas can be semantically searched — this is a one-time setup."

Then walk them through installing QMD per its docs. The QMD project ships an MCP server; the typical setup is adding it to the user's Claude Code MCP config and restarting. If you don't know the exact command for their environment, point them at QMD's install docs and stop until they confirm it's installed.

If the user declines to install QMD, that's fine — fall through to the **QMD-unavailable fallback** at the bottom of this skill. Don't block sampling on QMD; just lose some quality.

### Check the personas index

If QMD is up, check whether the personas in `./.personas/` are all indexed. Use `mcp__qmd__status` (or `mcp__qmd__query` for the collection) to list indexed paths. Compare against `ls ./.personas/*.md`.

If any personas are missing from the index, tell the user — short:

> "Adding N personas to the QMD index — one-time."

Then add them via QMD's ingestion command/tool. Once indexed, proceed.

## Phase 1 — Filter

Inputs (from the calling skill):
- **Question / topic** — the study question, an asset summary, or whatever the methodology wants the sample to be relevant to.
- **N** — how many personas the caller wants. If unspecified, the caller's methodology has a default; ask the caller before sampling rather than guessing.
- **Required-include** *(optional)* — slugs the caller knows must be in the sample.
- **Required-exclude** *(optional)* — slugs the caller knows must not be.

Process:

### Step A — QMD semantic search

Call `mcp__qmd__vsearch` with the question against the personas collection. Take the top 2N results (the over-fetch matters — Step C re-ranks). Each result has a score; keep them.

### Step B — Keyword grep

Extract 3–8 distinctive keywords from the question. Skip stopwords and category-generic terms ("user", "customer", "product"). Prefer:
- Product names ("Stripe", "Notion", "Linear")
- Role titles ("CTO", "founder", "ops lead")
- Demographic / segment flags ("bootstrapped", "enterprise", "consumer")
- Topic anchors ("pricing", "onboarding", "checkout")

Run `grep -li` (case-insensitive, files-with-matches) against `./.personas/*.md` for each keyword. Score each persona by number of distinct keyword files it matched.

### Step C — Merge and rank

For each persona that appeared in *either* result, compute a combined score:
- Normalize each signal to [0, 1] (divide by max in that signal).
- Combined score = `0.6 * qmd_score + 0.4 * grep_score`.
- The 60/40 weighting favors semantic search — keyword grep is high-precision but low-recall.

Apply required-include (force-in) and required-exclude (force-out). Then take the top N.

### Step D — Tiebreak and floor

If fewer than N personas surface from the merged ranking (e.g., the question is generic and nothing scores meaningfully), fill the remainder from the alphabetically-sorted full persona list and **mark these as "non-targeted fill"** in the explanation. Don't pad silently.

## Phase 2 — Return

Return a structured result:

```yaml
sample:
  - slug: skeptical-cto
    score: 0.91
    why: "matched on 'pricing'; semantically close to 'budget vs perceived ROI'"
  - slug: bootstrapped-consultant
    score: 0.78
    why: "matched on 'pricing' and 'solo'; semantic"
  - ...
explanation: "Sampled 5 of 12 personas, prioritizing those whose docs mention pricing decisions and solo/SMB context. Two non-targeted fills (junior-designer, mobile-pm) included because methodology requires N=5 and only 3 personas scored meaningfully."
fallback_used: false   # true if QMD-unavailable fallback was used
```

The calling skill uses `explanation` verbatim in its announce phase so the user can see *why* these personas were picked.

## QMD-unavailable fallback

If QMD isn't installed and the user declined to install it, run **grep-only ranking**:

- Run Step B as above.
- Skip Step A; combined score = grep score.
- Apply required-include / required-exclude and tiebreak as normal.
- Mark `fallback_used: true` in the return.
- In the explanation, note that semantic search wasn't available: "Sample is keyword-only — without QMD, personas whose relevance is conceptual rather than lexical may be missed."

This is meaningfully worse for non-literal questions, but it's better than failing.

## When the caller has fewer personas than N

If `./.personas/` has fewer personas than the requested N, return all of them. The calling skill is responsible for noting the under-sample in its own output (per the sample-size principle in `persona-research`). Don't pad with fakes.
