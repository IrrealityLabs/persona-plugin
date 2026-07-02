---
name: persona-refresh
description: Rebuild a persona's `./.personas/<slug>.md` from its existing assets WITHOUT re-pulling any sources — re-synthesize the body and re-select the `## Examples` (corrections and observations prioritized). Use when the user says "/persona-refresh", "refresh <persona>", "rebuild <persona>", "re-pick the examples", "regenerate the doc from the assets", or after adding corrections/observations and wanting the whole doc updated. To pull fresh source data (new Slack/X/web), use persona-distill instead.
---

# Persona Refresh

Regenerate a persona's doc from whatever is already in its assets folder — no new pull. The `.md`
is a disposable projection of the immutable assets, so refreshing is always safe and never loses
data. Use it after adding corrections/observations, to re-roll the example selection, or when the
synthesized body has drifted from the underlying data.

The difference from `persona-distill`: distill *pulls* fresh source data into the assets first;
refresh skips the pull and just re-projects the existing assets.

## Two intensities

- **Full (default):** re-synthesize the body *and* re-select `## Examples`.
- **Light (examples only):** re-select `## Examples`, leave the body untouched. This is what
  `persona-correct` and `persona-observe` trigger; invoke it here when the user says "just
  re-pick the examples" or only wants the example set refreshed.

## Phase 1 — Resolve the persona and confirm assets

Match the named persona against `./.personas/`. Confirm `./.personas/assets/<slug>/` exists and
has content. If there are no assets, stop and point to `persona-distill` (there's nothing to
project from).

## Phase 2 — Re-project the assets → `.md`

Follow `skills/persona-distill/references/distillation.md`, treating the **existing assets as the
corpus — do not pull anything**. That means:

- **Full refresh:** run the distillation fan-out / single-pass over the current assets to
  re-synthesize the body (paraphrased, no verbatim), then select up to ~30 of the best asset
  rows verbatim for `## Examples`, prioritizing `corrections.jsonl` and
  `observations.jsonl` and choosing the rest for coverage and variety. Overwrite the `.md`.
- **Light refresh:** read the current `.md`, re-select only the `## Examples` section from the
  assets (same prioritization), and rewrite just that section — leave the body as-is.

Update the frontmatter `last_distilled_at`.

## Phase 3 — Confirm

Close with: "Rebuilt `./.personas/<slug>.md` from its assets (N examples). Run `persona-review`
to use it." For a light refresh: "Re-picked `<slug>`'s examples (N) from its assets; body
unchanged."

## Notes

- Refresh never pulls and never deletes assets — it only regenerates the `.md`.
- Selecting which turns become examples is the distiller's judgment (see distillation.md), not a
  script, and it's intentionally not deterministic — a fresh refresh can surface different
  examples, with corrections/observations always prioritized.
- To bring in new source data, use `persona-distill`.
