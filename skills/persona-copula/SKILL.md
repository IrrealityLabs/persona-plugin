---
name: persona-copula
description: Generate a synthetic *population* of personas that statistically matches real survey data, using a Gaussian copula (the SYNC / SynC method). Feed it survey microdata (one row per respondent, columns = variables) and it fits the marginal distribution of every variable plus the dependence/correlation between them, samples N synthetic respondents from that joint distribution, validates fidelity, and turns each sampled respondent into a persona doc. Use when the user says "/persona-copula", "make personas from this survey", "generate a representative population of personas", "sample personas from these distributions", "synthetic respondents from survey data", or has tabular survey/panel data and wants many statistically-grounded personas rather than a few hand-built ones.
---

# Persona Copula

Most persona creation builds a handful of archetypes one at a time. `persona-copula` does the opposite: it learns the **joint statistical distribution** of a real survey and samples a whole synthetic population from it, so the personas collectively reproduce the real audience's marginals *and* the correlations between variables (older respondents skew higher-income, higher-income skews luxury-preferring, and so on). Each synthetic respondent becomes one persona.

The method is a **Gaussian copula**, from SYNC / SynC (Li, Zhao & Fu, 2020):
- Paper: https://arxiv.org/abs/2009.09471 (ICDMW 2020) · https://arxiv.org/abs/1904.07998 (journal)
- Reference implementation (R): https://github.com/winstonll/SynC

The skill ships a self-contained Python port of the core copula fit-and-sample in `scripts/sync_copula.py` (the paper's extra neural-net step for fusing multiple *aggregated* census sources is out of scope — see Aggregate mode below).

## Why a copula (and why it matters for personas)

`persona-create`'s own research notes that the dominant failure mode of LLM personas is **variance compression** — hand-built personas cluster near the mean and miss the extremes and the awkward combinations. A copula directly counters that: it samples across the *real* joint distribution, so the population includes the high-income-but-price-sensitive respondent, the young luxury buyer, the tails — in the proportions the survey actually observed. The personas are grounded in measured statistics, not an author's intuition about who the segments are.

## When to use vs. alternatives

- Use `persona-copula` when you have **tabular survey/panel data** and want **many** personas whose distribution matches the population — for large panels, quant-style studies (`persona-survey`, `persona-van-westendorp`, `persona-turf`), or any time representativeness across a population matters.
- Use `persona-create` **Mode 2** when you want **one persona per real respondent row** — no synthesis, just transcribe the actual respondents you have. (`persona-copula` *feeds* Mode 2; see Phase 4.)
- Use `persona-create` **Mode 1/3** to build a few rich, qualitatively-deep personas from interviews or your own knowledge.
- Use `persona-distill` to build a persona from a real person's footprint (Slack / X / web).

Rule of thumb: **real rows → `persona-create` Mode 2. Real distribution, synthetic rows → `persona-copula`.**

## Inputs

- **Survey microdata (primary)** — a CSV, one row per real respondent, one column per variable (demographics, attitudes, behaviors, purchase data, Likert items…). The richer the columns, the richer the personas. This is what the copula is fit to.
- **Target N** — how many synthetic personas to generate. The copula can sample any N (more or fewer than the survey had); pick what the downstream study needs (e.g. 10–50).
- **Variable types** — the script auto-detects continuous vs. categorical, but confirm: which columns are **ordinal** (ordered: Likert, education, income bracket) vs. **nominal** (unordered: region, brand). Pass them with `--ordinal` / `--categorical`. Getting this right improves dependence fidelity.
- **Optional filter / conditioning** — e.g. "only potential buyers, not current customers" (like the Jaguar example). Filter the input CSV *before* fitting so the population is sampled from the right subgroup.

If the user has no data file, this isn't the right skill — route to `persona-create`. The whole point is grounding in real distributions.

## Workflow

### Phase 0 — Announce

"I'll fit a Gaussian copula to your survey (preserving each variable's distribution *and* the correlations between them), sample <N> synthetic respondents, check the fit, then turn each into a persona. These are statistically-plausible synthetic people drawn from your data's distribution — not real individuals."

### Phase 1 — Inspect the data and confirm the model

Read the first few rows of the CSV. Confirm with the user:
- **Which columns to include** (`--include`). Drop free-text and ID columns from the copula fit — they don't have a meaningful distribution to model (you can still carry an ID separately). Note: open-text columns are exactly where rich speech samples live, so flag that personas built from purely structured data will be thin on the speech dimension (→ Known gaps).
- **Ordinal vs. nominal** for each categorical column.
- **Any filter** to apply first (the target subgroup).
- **Target N.**

Check `python3 -c "import numpy, scipy, pandas"`. If it fails, tell the user to `pip install numpy scipy pandas` (a venv is fine) and stop until ready.

### Phase 2 — Fit and sample

```bash
mkdir -p ./.persona-research-runs/<timestamp>
python3 scripts/sync_copula.py \
  --input <survey.csv> \
  --n <N> \
  --out ./.persona-research-runs/<timestamp>/synthetic.csv \
  --report ./.persona-research-runs/<timestamp>/fidelity.json \
  --include <col1,col2,...> \
  --ordinal <likert1,education,...> \
  --categorical <region,brand,...> \
  --seed <int>      # set a seed so the run is reproducible
```

The script fits empirical marginals per column, builds the latent Gaussian correlation (positive-definite–corrected), draws N samples, inverts each back through its marginal, and writes the synthetic CSV plus a fidelity report.

### Phase 3 — Check fidelity before building personas

Read the printed report / `fidelity.json`. It gives:
- **Marginal fidelity** — KS distance (continuous) / total-variation distance (categorical) per column. Low = the synthetic column matches the real one. Flag any column that drifted (rare categories can get under-sampled at small N).
- **Dependence fidelity** — mean / max absolute difference between the real and synthetic Spearman correlation matrices. Low = the cross-variable structure survived.

Surface this to the user in a sentence or two. If fidelity is poor (tiny survey, heavy missingness, a mis-typed column), say so and offer to fix types / raise N / get more data before proceeding. **Don't build personas on a bad fit silently.**

### Phase 4 — Turn synthetic respondents into personas

Hand the synthetic CSV to **`persona-create` Mode 2 (bulk spreadsheet import)** — one persona per synthetic row. Don't reinvent persona writing; `persona-create` owns the doc template and the quality bar. Pass along:
- The synthetic CSV path and the column→dimension mapping (which columns are behavioral / contextual / demographic / Big Five, per `persona-create`).
- **Provenance:** set `sources: [copula-synthetic]` in frontmatter, and have each doc's *Known gaps* note that it's a copula-sampled synthetic respondent from `<survey>` (run `<timestamp>`, seed `<seed>`), **not** a measured individual — so nothing downstream mistakes it for a real interview. If Big Five / personality columns aren't in the survey, Mode 2 leaves them "not measured" rather than inventing them.
- **Naming:** derive evocative slugs from each row's defining variables (`bmw-driving-sf-tech-exec`, `price-sensitive-luxury-curious`), never `synthetic-1`.

For large N, `persona-create` Mode 2 fans out in parallel batches and recommends spot-checking — do that here too.

### Phase 5 — Honesty and hand-off

Tell the user: N personas saved to `./.personas/`, the fidelity summary, and the honest caveats (below). Offer next steps — a `persona-survey` / `persona-research` study now that the population exists, or `persona-audience` to group them.

## Aggregate mode (marginals only — no microdata)

The original SYNC use case is *downscaling*: you have only aggregated marginals (e.g. census: 52% female, age-bracket counts, income-bracket counts) and no row-level data. A Gaussian copula still works **if you can supply or assume the dependence structure**, because marginals alone don't pin down the correlations — that's the hard part SYNC solves by fusing multiple overlapping aggregated sources with a neural net (not implemented here).

Practical fallback when you only have marginals:
- Synthesize a microdata table by sampling each variable from its marginal, then **assume independence** (or apply a user-supplied correlation matrix / a few known pairwise correlations), and feed that to the sampler.
- **Be loud about the assumption.** Independence-sampled personas reproduce the marginals but *not* real-world correlations — say so explicitly; it's a materially weaker grounding than fitting to microdata. Prefer getting microdata if at all possible.

## Caveats (state these honestly)

- **Synthetic, not real.** Each persona is a plausible draw from the survey's distribution, not a measured person. Great for building representative panels; never cite a synthetic respondent as evidence of a real one.
- **Gaussian copula captures monotonic dependence**, not arbitrary nonlinear or tail dependence. It reproduces correlations and marginals well; it can miss complex interaction effects and exact joint tails. Fidelity for nominal (unordered) variables is approximate — their dependence is encoded via a frequency-based ordering.
- **Garbage in, garbage out.** Fidelity is bounded by the survey's quality, size, and representativeness. A biased or tiny survey yields a biased or unstable population — the fidelity report will hint at this but can't fix it.
- **Don't re-derive stats from synthetic data.** It's for populating persona panels and simulations, not for statistical inference (you'd just be reading back your own input distribution with sampling noise).
- The usual plugin disclaimer applies downstream: persona simulations are directional, validate load-bearing findings with real people.

## Notes

- Set `--seed` and keep the run directory so a population is reproducible and auditable.
- Continuous columns that are really integers (age, counts) are re-rounded to integers automatically.
- Rows with missing values in the modelled columns are dropped before fitting; the report counts how many. Heavy missingness → consider imputing first or narrowing `--include`.
- For a production-grade alternative with more marginal families and constraints, the `copulas` / `sdv` Python libraries (sdv-dev) implement the same Gaussian-copula idea; this script is the zero-config, dependency-light version that ships with the plugin.
