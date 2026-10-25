---
name: persona-clone
description: Clone a real person into a calibrated persona — the alternative to persona-create when you have the person's own words (interview or survey answers, transcripts, Slack, X, web). Builds the persona from that data (persona-distill / persona-create), then calibrates it against the real answers with a judge-vs-persona Turing test (persona-calibrate), so you end with a persona prompt that's been shown to work, plus a score. Optionally scrubs names first (persona-anonymize) and adds a face and intro video (persona-avatar). Use when the user says "/persona-clone", "clone <person>", "make a calibrated persona of <person>", "turn this interview into an accurate persona", or has a real respondent's answers and wants the most faithful persona possible.
---

# Persona Clone

`persona-create` writes a persona from what you know; `persona-clone` makes one from what a **real person
actually said** and then **proves it**. It's a sequence of existing skills, each of which can also be run on
its own:

```
(persona-anonymize) → persona-distill / persona-create → persona-calibrate → persona-validate → (persona-avatar)
```

## Phase 1 — What do they have?

Ask what data there is about the person, and route the build step:

- **Interview or survey answers** (a spreadsheet or JSON of questions and answers, one person or many) →
  `persona-create` Mode 2 (spreadsheet) or Mode 3 (transcripts). One persona per respondent. All you need
  is each question and the person's answer. Make sure each question is the full wording they were asked,
  not a column label like "Q7 Travel". If the export only has labels, ask for the interview script and
  swap the wording in.
- **Slack, X, web, email, files** → `persona-distill` with that source.
- **Rows already in the asset format** (`{context, question, answer, source}` JSONL — e.g. a sample
  persona's `samples/personas/assets/<slug>/survey.jsonl`) → copy the file into
  `./.personas/assets/<new-slug>/survey.jsonl` and build with `persona-create` Mode 2 Phase 3 onwards.
  Use a new slug, so you don't overwrite a persona that's already loaded.

Calibration needs at least 6 real answers to a prompt or question; aim for 15+. If they have less, build the
persona anyway and say calibration will have to wait for more data (`persona-observe` adds it later).

If the data names real people and the personas will be shared, run `persona-anonymize` on the source files
first and build from the `.anon` copies.

## Phase 2 — Build

Run the chosen build skill as it's written. Both save the person's own words as asset rows in
`./.personas/assets/<slug>/` — that's what the next step tests against.

## Phase 3 — Calibrate

Run `persona-calibrate` on the new persona (`skills/persona-calibrate/SKILL.md`): a model API key (OpenRouter recommended), then the
default single round of judge-then-persona optimization (more with `--rounds`). For many respondents, run them one after another (each is
its own script call) and mention the per-persona cost up front.

## Phase 4 — Validate

Run `persona-validate`: the calibrated persona takes an interview it has never seen (best of 2 per question,
picked by its judge), and you review the answers for invented facts, contradictions and voice drift. If the
user has the questions they actually plan to ask, use those.

## Phase 5 — Optional face and voice

Offer `persona-avatar` — a profile photo and a 6-second intro video. If the source includes a video of the
person and they consented to it, use a frame from it as the reference.

## Phase 6 — Report

One line per persona: name, how many real answers, Turing score, whether the instruction changed, and the
validation verdict. Then point to
`persona-ask` to use them and `persona-test` to re-check after any change.
