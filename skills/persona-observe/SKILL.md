---
name: persona-observe
description: Manually add real data about an existing persona — a CSV of exchanges, or freeform "here's something I've seen this person say or do." Normalizes the input into universal asset rows ({context, question, answer, source}), appends them to `./.personas/assets/<slug>/observations.jsonl` (immutable, append-only), and does a light refresh that folds them into the persona's `## Examples`. Use when the user says "/persona-observe", "I noticed <persona> do X", "log an observation about <persona>", "add this data to <persona>", "here's a CSV of things <persona> said", or "add these examples to <persona>". For fixing a wrong answer the persona gave, use persona-correct; to rebuild the whole doc from assets, use persona-refresh.
---

# Persona Observe

Add hand-supplied ground truth to an existing persona. Everything you add becomes a verbatim
`{context, question, answer}` turn in the persona's assets and shows up in its `## Examples` —
the strongest grounding the persona has. This is the manual counterpart to `persona-distill`'s
automated pulls.

The assets folder is **immutable and append-only** — you only ever add. The persona `.md` is a
projection of it, so folding new observations in never loses anything.

## Phase 1 — Resolve the persona

Match the named persona against `./.personas/` (same rules as `persona-ask`). If it doesn't
exist, stop and point to `persona-create` or `persona-distill` — observe adds *to* a persona, it
doesn't create one.

## Phase 2 — Gather the data into `{context, question, answer}` turns

Input shapes:

- **CSV** — ask for the path. Read the header and the first 2–3 rows. Map columns to
  `question` (the prompt/situation they responded to) and `answer` (what they actually said);
  `context` (prior exchange / setup) is optional. If the mapping is ambiguous, ask once. Each row
  becomes one turn. Skip rows missing a question or an answer.
- **Freeform** — the user describes something they know.
  - If it's an **exchange** ("someone asked them X and they said Y", "in standup they pushed back with…"), capture it as a turn: `question` = what prompted them, `answer` = what they said (verbatim if the user gives words), `context` = the situation.
  - If it's a **bare trait or fact** with no exchange ("they hate long meetings"), do **not** fabricate a Q&A. That's body material — tell the user, and offer to fold it into the synthesis via `persona-refresh`, or ask them to phrase it as something the person was actually asked and actually said.
- **A file you already have** — an email thread (`.eml`/`.mbox`), PDF, Word/Excel doc, screenshot, or exported chat JSON. For email, run `skills/persona-distill/scripts/parse-email.mjs`; otherwise read/convert it per `skills/persona-distill/references/file-import.md`. Then pull the exchanges out as `{context, question, answer}` turns, same as above.

Verbatim is fine and wanted here — `## Examples` is the verbatim section.

## Phase 3 — Append to the assets

Append each turn as one JSON line to `./.personas/assets/<slug>/observations.jsonl` (create the
file/dir if needed) — the same universal row every asset file uses. `source` says where the
observation came from: the file it was pulled from, or `user-reported, <YYYY-MM-DD>` for freeform.

```json
{"context": "<prior exchange or situation, or empty>", "question": "<what they responded to>", "answer": "<what they said>", "source": "<file path, or user-reported + date>"}
```

Append only — never rewrite or reorder existing lines.

## Phase 4 — Light refresh (examples only)

Fold the new turns into the persona's `## Examples` section verbatim, **leaving the body
untouched** (light refresh — no re-synthesis). If `## Examples` would exceed ~30, drop the
least-useful non-prioritized examples to make room; hand-added turns (corrections and
observations) take priority over distilled ones.

## Phase 5 — Offer the full refresh

Close with: "Added N observation(s) to `<slug>` and folded them into its examples. Want me to
rebuild the rest of the doc to reflect them? (`persona-refresh`)" — only re-synthesize the body
if the user says yes.

## Notes

- One persona per run.
- The format is the universal asset row — `{context, question, answer, source}` — no other fields.
- `observations.jsonl` is append-only and survives every refresh; it's hand-supplied ground
  truth, so the distiller prioritizes it when selecting examples.
- For "the persona answered this wrong, here's the right answer," use `persona-correct` instead —
  same format, saved to `corrections.jsonl`.
