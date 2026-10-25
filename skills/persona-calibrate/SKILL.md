---
name: persona-calibrate
description: Calibrate a persona against the real person's answers — a modified Turing test where a judge model has to pick the real answer from the persona's, run as an adversarial loop. Each round GEPA (DSPy) improves the judge (10 candidates), then improves the persona's roleplay instruction against that judge (10 candidates); one round by default, more with --rounds. Proves the persona prompt actually works, saves the trained judge, and writes the Turing score and calibrated instruction into the persona doc. Use when the user says "/persona-calibrate", "calibrate <persona>", "make <persona> more accurate", "optimize this persona", "does this persona prompt actually work", or right after persona-create / persona-distill built a persona from real data.
---

# Persona Calibrate

`persona-create` and `persona-distill` write a persona prompt; calibration **tests that the prompt
works** and makes it better. The persona answers questions the real person already answered, and a
judge model sees both answers side by side and has to pick the real one.

**Turing score** = share of held-out questions where the judge picked the persona's answer as the real
one. 50% means indistinguishable; 0% means always caught. **Believability** is the finer-grained
version: the judge also says how sure it is, so each answer gets the judge's probability that it's the
real person's (0 = obviously AI, 0.5 = can't tell). A persona that loses every pick can still become
more believable, and that's the signal the optimizer climbs.

It runs as an adversarial loop. Each **round**:

1. **Judge turn** — GEPA proposes up to 10 rewrites of the judge's instruction and keeps the best at
   telling this person from the persona.
2. **Persona turn** — GEPA proposes up to 10 rewrites of the persona's roleplay instruction, each scored
   by that judge; the judge's reasoning and the real answer are fed back, so each rewrite targets what
   gave the last one away.

One round by default, because each round takes a while; add rounds (`--rounds 3`) and a better judge trains a
better persona, which trains a better judge. After
every turn the persona is re-tested on held-out answers it never sees, so the report shows the arms race
round by round. Each turn picks its winner on training questions whose real answers the optimizer never
saw in feedback, so a rewrite only wins if it helps beyond the examples it learned from. Rewrites may quote
the person verbatim; that's a fair way to capture how they sound.

Only the *instruction* is optimized — never the persona's facts. If the judge keeps catching it on
substance (wrong habits, missing context), the fix is more data (`persona-observe`, `persona-distill`),
not more rounds. Often nothing beats the default instruction; that's a valid result, and the score still
tells you where the persona stands.

## What it needs

- **A persona with real answers in its assets** — at least 6 rows in `./.personas/assets/<slug>/*.jsonl`
  (`survey.jsonl`, `interview.jsonl`, `slack.jsonl`…); the `answer` field is the person's own words. A
  persona built from a description has no real answers, so there's nothing to test against — say so. With
  under ~20 answers, call the result **directional**. To build and calibrate in one go, use `persona-clone`.
  Each row's `question` should be **the exact question the person was asked**, not a short topic label: the
  persona answers that question, and the judge compares the answer with what the person actually said to it.
  If the data only has labels but the user has the original wording (an interview script, a survey export),
  put it in first.
- **A model API key.** Calibration needs many model calls, so it runs a script, not subagents. It uses
  whichever key it finds in a `.env` in the working directory (or the environment), checking OpenRouter
  first:
  - `OPENROUTER_API_KEY` (recommended: one key reaches every model below)
  - `ANTHROPIC_API_KEY`
  - `OPENAI_API_KEY`
  - `GEMINI_API_KEY`
  - `XAI_API_KEY` (Grok)

  `PERSONA_PROVIDER=<openrouter|anthropic|openai|gemini|xai>` forces one. For a **local model** with no key
  (Ollama, LM Studio or a llama.cpp server), set `PERSONA_PROVIDER=ollama`, `lmstudio` or `llamacpp` and name the
  models (`--persona-model llama3.2`); `PERSONA_BASE_URL` changes the server address. Be honest about the
  trade-off: local runs go one request at a time, so they're slow. And a small local judge can't tell people
  apart, so its score drifts to a meaningless ~50%. Keep the judge on a strong model if you can. If the user has none, walk them
  through OpenRouter: sign in at https://openrouter.ai, create a key at https://openrouter.ai/keys, add a few
  dollars of credit, and save `OPENROUTER_API_KEY=sk-or-…` in `.env` (check `.env` is gitignored). The `.env`
  wins over a key already in the shell.
- **`uv`**, which installs DSPy on the fly (`uv --version`; install from https://docs.astral.sh/uv/). Without
  it: `pip install dspy` and run the script with `python3`.

## Models

Two choices, each a short alias or any model id the provider offers:

- **Persona:** cheap and fast, since it answers many times. `haiku` (Claude Haiku, the default), `luna`
  (GPT Luna), `flash` (Gemini Flash), or a Grok model.
- **Judge:** the stronger the judge, the more a passing score means. `opus` (Claude Opus, the default), `sol`
  (GPT Sol), `pro` (Gemini Pro), or `grok`. GEPA's rewrites are proposed by the judge model too
  (`--reflection-model` to change).

Through OpenRouter every alias works. With a single provider's own key, the defaults switch to that
provider's pair: Haiku / Opus (Anthropic), Luna / Sol (OpenAI), Flash / Pro (Gemini), or Grok 4.3 / Grok (xAI).
Set per run with `--persona-model` / `--judge-model`, or as defaults in `.env` (`PERSONA_MODEL=luna`,
`JUDGE_MODEL=sol`). Ask the user only if they bring it up; otherwise use the defaults.

## Phase 1 — Announce

Resolve the persona in `./.personas/` (or `$PERSONA_HOME`) and count its real answers. Then: "I'll hold out
40% of <name>'s N real answers, then run a round of judge-vs-persona optimization on the rest and re-test on
the held-out ones. About 20–25 minutes and roughly $5–10 at the default models (an Opus judge) for ~15
answers, more with more answers. More rounds (`--rounds 3`) push further and cost about that much again
per round; `--judge-model sonnet` or `sol` is several times cheaper."

## Phase 2 — Run

```bash
uv run skills/persona-calibrate/scripts/calibrate.py calibrate --persona <slug> \
  [--rounds 1] [--candidates 10] [--persona-model haiku|luna] [--judge-model opus|sol] [--seed 0]
```

Run it in the background for long runs; it prints a score after every turn and the report path at the end.
If the persona already has a judge from an earlier run, it continues from that judge and keeps the same
held-out questions, so the judge never trains on them.

Each run is saved append-only to `./.personas/assets/<slug>/calibration/<timestamp>-calibrate/`:
`report.json` (score history per turn, both instructions, every held-out case with the judge's reasoning),
`judge.json` (the trained judge — the latest one is the persona's *current judge*) and `instruction.txt`.

The script also writes the result into the persona doc — it replaces (or adds) the `## Calibration` section
at the end of `./.personas/<slug>.md` and touches nothing else:

```markdown
## Calibration

- Turing score 42% on 6 held-out answers against this persona's judge (…). 50% = indistinguishable.

### How to answer as this person

<the calibrated instruction — only present if it beat the default>
```

Anything that answers as this persona reads the doc, so that instruction is how calibration takes effect.

## Phase 3 — Report

Read `report.json`. Give the score history as a short table (start → each judge turn → each persona turn),
whether the instruction changed (quote its key guidance in a line or two), and the judge's most common reason
for catching the persona on the cases that still fail — that's the actionable part. Be honest about sample
size: one case swings a small held-out set a lot, so before trusting a small win suggest re-checking with
`persona-test` on the other judge model (e.g. `--judge-model sol`), or adding data.

## Notes

- `persona-test` re-scores the current persona against the current judge with no training — use it after
  editing the doc, adding data, or switching models.
- `persona-validate` is the next step: the calibrated persona answers an interview it has never seen (best of
  2, picked by this judge) and you review the answers.
- `persona-refresh` and `persona-distill` regenerate the doc and drop `## Calibration`; the judge stays in
  the assets, so run `persona-test` (score only) or `persona-calibrate` (re-tune) afterwards.
- A garbled source (speech-to-text, chat logs) next to clean persona prose is an easy tell for the judge.
  That's a real gap, and worth saying so.
