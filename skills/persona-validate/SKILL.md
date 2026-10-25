---
name: persona-validate
description: Validate a calibrated persona on questions it has never seen — run it through a 15-question market-research interview (or your own questions), answering each twice and keeping the answer its judge rates more human (best of 2), then review the answers for voice, consistency with the persona doc and invented facts. Produces a survey CSV plus a short review. Use when the user says "/persona-validate", "validate <persona>", "sanity-check <persona> on new questions", "run the validation survey", or after persona-calibrate to see how the calibrated persona behaves beyond the questions it was tested on.
---

# Persona Validate

`persona-calibrate` and `persona-test` score the persona on questions the real person already answered.
Validation asks the other question: **how does it hold up on questions nobody has real answers to?** It runs
the calibrated persona through an interview it has never seen, the way it will actually be used, then you
review the answers.

Each question is answered **twice**, and the persona's judge picks the more human-sounding of the two (best of
2) — the same judge `persona-calibrate` trained to spot this persona's tells. Every real answer goes into the
persona as an example, as in normal use.

It needs a calibrated persona (a judge in `./.personas/assets/<slug>/calibration/`). None yet → run
`persona-calibrate` first, or `persona-clone` to build and calibrate in one go. Setup — a model API key in
`.env`, `uv`, model choices — is in `skills/persona-calibrate/SKILL.md` → "What it needs" and "Models".

## Phase 1 — Questions

Default: a 15-question market-research interview (background, shopping, tech adoption, brands, media, a big
purchase, pain points, money, products, plans, values, three fun personality questions, and an open close).
If the user has their own — the questions they actually plan to ask the persona — use those instead: write
them to a text file, one per line, or a JSON list of `{"category", "question"}`.

## Phase 2 — Run

```bash
uv run skills/persona-calibrate/scripts/calibrate.py validate --persona <slug> [--questions <file>] \
  [--persona-model haiku|luna] [--judge-model opus|sol]
```

About a minute and well under $1 at the defaults for 15 questions. It writes, to a new
`./.personas/assets/<slug>/calibration/<timestamp>-validate/` folder:

- `survey.csv` — `question_number, category, question, response` (the winning answer per question).
- `report.json` — both candidates, which one the judge picked, and why.

The persona doc isn't changed.

## Phase 3 — Review

Read every winning answer against the persona doc and the real answers in the assets. Flag, with the question
number:

- **Invented facts** — specific claims (places, brands, people, numbers, events) the doc and assets don't
  support. Some extrapolation is the point; confident new biography is a problem.
- **Contradictions** — with the doc, the real answers, or another answer in the same survey.
- **Voice drift** — answers that sound like a generic assistant or a summary of the doc, not the person.
- **Over-reciting** — the same few doc details crammed into every answer (the judge's reasoning often names
  this).

Also skim the losing candidates in `report.json`: if both candidates are often weak, the persona needs more
data, not a better pick.

## Phase 4 — Report

A short verdict (holds up / mostly / not yet), then the flagged answers as a list with one-line reasons, and
the fix for each pattern: missing substance → `persona-observe` or `persona-distill` to add data; a wrong
answer → `persona-correct`; voice → `persona-calibrate` again. Give the path to `survey.csv`.
