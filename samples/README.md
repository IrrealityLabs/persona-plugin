# Sample personas

Ready-made personas, so you can try the plugin before building your own. Each was built from a **real
person's video-survey interview**, anonymized: everyone's name is a pseudonym, and towns, business names
and other identifying specifics were generalized. The respondents agreed to their answers being used.
Each persona ships with its **raw interview** (anonymized), so you can rebuild or clone it yourself.

| Persona | Who | Built with | Interview |
|---|---|---|---|
| `wearable-art-microfarmer` | US small-business owner building a goat-and-chicken microfarm; clothes are "wearable art" | `persona-create` | 15 questions |
| `wearable-art-microfarmer-calibrated` | **The calibrated example:** the same persona, then optimized with `persona-calibrate` | `persona-create` → `persona-calibrate` | same 15 |
| `early-retired-wine-collector` | Early-retired ex-radio and marketing man in New Zealand; frugal, rations a 40-year wine cellar | `persona-create` | 15 questions |
| `plainspoken-ex-trucker` | Former truck driver in the US South, now working online from home on a tight budget | `persona-create` | 15 questions |
| `british-american-ai-engineer` | British-American AI engineer and dad of two in an English village, about to move to New York | `persona-create` | 10 questions (life, then cars) |

The 15-question interview covers: about yourself, a typical weekday, time off, friends, life history,
a perfect day, travel, media, politics, food, apparel, personal care, cars, finances, and anything else.
Each row holds the full question exactly as it was asked, with the person's answer. Answers are
automatic speech-to-text, so expect garbled words; that's how real interview data looks.

## Plain vs calibrated

`wearable-art-microfarmer` and `wearable-art-microfarmer-calibrated` are the same persona doc, built from
the same interview with the normal `persona-create` flow. The calibrated one then went through
`persona-calibrate`. Its doc is identical except for the `## Calibration` section at the end, which holds
two things: its Turing score and, under "How to answer as this person", the roleplay instruction that
calibration found. Anything that answers as her reads that instruction. Its trained judge, the
round-by-round score history and the validation survey are in
`assets/wearable-art-microfarmer-calibrated/calibration/`.

Ask both the same question, or run a study with just the two of them, to see what calibration changes.

**What calibration did here** (3 rounds × 10 candidates, Claude Haiku persona, Claude Opus judge):
- **Judge:** it still spots her on all 6 held-out answers. Believability went from 0.09 to 0.07, so no gain on
  that measure.
- **Voice:** the instruction calibration found leans heavily on her verbatim answers, and her answers to new
  questions sound much more like her. Before: "Oh, that's a good one. I'd say the Indian spiced popcorn." After:
  "okay so um the popcorn the Indian spiced popcorn that i tried recently. i didnt really expect much…".
  Compare the validation answers in `calibration/*-validate/survey.csv`.
- **Why it's hard:** real answers that are raw speech-to-text are hard to pass for, because the noise itself is
  a tell.

## Layout

```
samples/personas/
├── <slug>.md                       # the persona doc
└── assets/<slug>/
    ├── survey.jsonl                # the anonymized raw interview: one {context, question, answer, source} row per answer
    └── calibration/<run>/          # calibrated example only: trained judge, report.json, validation survey.csv
```

## Load them

Copy them into the project's persona store, `./.personas/` (or `$PERSONA_HOME` if set). Only copy what
isn't already there, so existing personas are never overwritten:

```bash
mkdir -p .personas && cp -Rn <plugin>/samples/personas/. .personas/
```

Then they work with every skill: `persona-ask wearable-art-microfarmer "…"`, or name them in any study
(`persona-focus-group`, `persona-survey`, …), or leave names out to use them all. (Leaving names out
includes both versions of the microfarmer; name them when you want a panel of distinct people.)

## What you can do with them

- **Use them as they are.** They're normal personas.
- **Look at calibration.** Read `assets/wearable-art-microfarmer-calibrated/calibration/*/report.json`
  for the score after every judge and persona turn, and the judge's reasons case by case. Run
  `persona-test wearable-art-microfarmer-calibrated` to re-score it, or `persona-validate` to put it
  through an interview it has never seen. (These need a model API key, OpenRouter recommended; see `persona-calibrate`.)
- **Calibrate the others.** Run `persona-calibrate <slug>` on any of the plain ones to test whether the
  persona prompt actually works.
- **Clone one yourself from the raw data.** The interviews in `assets/<slug>/survey.jsonl` are the real
  input. Run `persona-clone` on one (it builds the persona from the interview, then calibrates and
  validates it) and compare your persona with the shipped one. This is the quickest way to learn the
  full clone → calibrate → validate path before running it on your own people.
- **Use them as a template.** To build personas of your own customers, run the same interview with them
  (video, call or written), save each answer with the exact question you asked, then `persona-clone`.

Personas are stand-ins, not the people themselves. Treat what they say as hypotheses to check with real
customers.
