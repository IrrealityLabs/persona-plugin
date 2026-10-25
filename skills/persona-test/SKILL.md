---
name: persona-test
description: Test a persona as it stands against its current judge — no training, just the score. The persona answers the held-out questions the real person answered, the judge trained by persona-calibrate picks which answer is real, and you get the Turing score (50% = indistinguishable) with the judge's reasoning per question. Use when the user says "/persona-test", "test <persona>", "how accurate is <persona> now", "re-score <persona>", or after editing a persona, adding data, refreshing it, or switching the persona or judge model.
---

# Persona Test

A quick, repeatable check: the current persona doc versus the persona's current judge. Nothing is
optimized, so it's cheap (cents) and safe to run in a loop — e.g. after every edit in `persona-goal`.

It needs a judge, which `persona-calibrate` trains and saves. No judge yet → run `persona-calibrate` first
(or `persona-clone` to build and calibrate in one go). Setup — a model API key in `.env`, `uv`, model
choices — is the same as `skills/persona-calibrate/SKILL.md` → "What it needs" and "Models".

## Run

```bash
uv run skills/persona-calibrate/scripts/calibrate.py test --persona <slug> \
  [--persona-model haiku|luna] [--judge-model opus|sol]
```

It reads the persona doc as it is now — including the instruction under `## Calibration`, if any — loads the
latest judge from `./.personas/assets/<slug>/calibration/`, and tests on the same held-out questions that judge
never trained on. It saves `report.json` to a new `…-test/` folder there and updates the score line in the
doc's `## Calibration` section.

Switching models is fine: the judge is a trained instruction, so `--judge-model sol` runs the same judge on
GPT Sol. Scores are comparable only with the same models.

## Report

The score and the believability (the judge's average probability that the persona's answer is the real
one; finer-grained than the score, so small changes show up), how they compare to the last line in
`## Calibration` before this run, and the judge's reasoning on
two or three cases — what still gives the persona away. If it dropped after an edit, say which held-out
answers flipped.
