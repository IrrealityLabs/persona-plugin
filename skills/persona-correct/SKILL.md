---
name: persona-correct
description: Correct a persona when it answers something wrong (or you know it would). Records the right answer as a `{context, question, answer}` turn in `./.personas/assets/<slug>/corrections.jsonl` (immutable, append-only) and does a light refresh that pins it into the persona's `## Examples` so the persona stops making that mistake. Use when the user says "/persona-correct", "no, <persona> would actually say…", "that's wrong, <persona> wouldn't…", "correct <persona>", or "fix that answer" — typically right after a persona-ask. To add general real data (not a fix), use persona-observe; to rebuild the whole doc, use persona-refresh.
---

# Persona Correct

When a persona just answered wrong — or you know how it *should* answer — record the correct
answer as ground truth. It's saved to the persona's assets and pinned into its `## Examples`, so
the next time a similar question comes up the persona has the real answer in front of it.

A correction is just a `{context, question, answer}` turn where the `answer` is what the persona
*should* have said. We store the corrected (right) answer — not the wrong one.

The assets folder is **immutable and append-only**; corrections persist there and survive every
rebuild of the `.md`.

## Phase 1 — Resolve the persona

Match the named persona against `./.personas/` (same rules as `persona-ask`). If it doesn't
exist, stop and point to `persona-create` / `persona-distill`.

## Phase 2 — Capture the correction as a turn

- **question** — what was asked. If this follows a `persona-ask`, reuse that question; otherwise
  ask the user what prompt this corrects.
- **context** — the relevant setup/situation, if any (optional).
- **answer** — the **correct** response: what the persona should have said. This comes from the
  user. Capture it verbatim in their words; don't smooth it into generic prose.

If the user only says "that's wrong" without giving the right answer, ask what the persona would
actually say — a correction needs the corrected answer.

## Phase 3 — Append to the assets

Append one JSON line to `./.personas/assets/<slug>/corrections.jsonl` (create if needed):

```json
{"context": "<situation, or empty>", "question": "<what was asked>", "answer": "<the correct answer, verbatim>"}
```

Append only — never rewrite existing lines.

## Phase 4 — Light refresh (examples only)

Drop the correction into the persona's `## Examples` section verbatim, **leaving the body
untouched**. Corrections are prioritized, so it should make the cut; if `## Examples` is already
at ~30, evict one non-prioritized (distilled) example to make room. Do not re-synthesize the body.

## Phase 5 — Offer the full refresh

Close with: "Correction saved to `<slug>` and pinned into its examples. Want me to update the
rest of the doc to reflect it? (`persona-refresh`)" — only rebuild the body if the user says yes.
A single correction usually shouldn't churn the whole synthesis; default to light.

## Notes

- One correction per run is fine; the user can run it again.
- Format is exactly `{context, question, answer}` — we don't store what the persona said wrong.
- The distiller prioritizes `corrections.jsonl` when selecting examples, so corrections stick
  across refreshes.
- To add real data that isn't a fix (a CSV of exchanges, something you observed), use
  `persona-observe`.
