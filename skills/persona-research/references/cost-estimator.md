# Cost estimator

Quick token-and-dollar estimates for `persona-research` methods, used to warn the user before launching anything expensive.

Pricing changes constantly and varies by model. **Pull live pricing where possible** rather than hardcoding it — the rates inline below are reasonable rough numbers for May 2026 but should be treated as approximations.

## Where to get fresh pricing

The simplest live source is the `ccusage` package (npm). It tracks Claude Code usage and resolves prices against model-pricing data sources (LiteLLM's `model_prices_and_context_window.json` and similar registries) that are kept current with Anthropic, OpenAI, and OpenRouter releases.

To get current per-model pricing from inside this skill:

```bash
# Latest model-pricing JSON (LiteLLM is the de facto source ccusage uses)
curl -sL https://raw.githubusercontent.com/BerriAI/litellm/main/model_prices_and_context_window.json \
  | jq '.["claude-opus-4-7"], .["claude-sonnet-4-6"], .["claude-haiku-4-5"]'
```

Fields you want: `input_cost_per_token`, `output_cost_per_token`, and (where present) `cache_read_input_token_cost`, `cache_creation_input_token_cost`.

If `ccusage` is available on the user's system (`command -v ccusage`), you can also shell out for live pricing — it caches the data and resolves with the right model aliases.

If neither curl nor ccusage is available, fall back to the rough numbers below and **say so in the warning** ("using May 2026 estimates, may be slightly stale").

## Rough rates (May 2026, approximate)

Per million tokens, USD. Use these as a fallback only.

| Model | Input | Output |
|---|---|---|
| Claude Opus 4.7 | $15 | $75 |
| Claude Sonnet 4.6 | $3 | $15 |
| Claude Haiku 4.5 | $1 | $5 |

Most persona-research subagents are `general-purpose` (Sonnet default in Claude Code unless overridden), so most estimates assume Sonnet rates.

## Per-method rough sizes

These are order-of-magnitude only — actual usage varies with persona-doc length, asset length, and follow-up questions. Use as a *triage* signal, not a quote.

| Method | Typical subagent runs | ~Tokens per run | Approx total tokens | When to warn user |
|---|---|---|---|---|
| persona-ask (1 question) | 1 | 5–15K | 10K | Never |
| persona-interview (5 Q's, 1 persona) | 5 | 5–15K | 50K | Never |
| persona-survey (10 Q, 5 personas) | 5 | 20–40K | 150K | If >20 personas |
| persona-focus-group (5 personas, 3 rounds) | 15 | 10–20K | 250K | Always |
| persona-council (6 personas, 4 rounds) | 24 | 10–20K | 400K | Always |
| persona-ab-test (5 personas, 4 variants) | 5 | 15–30K | 100K | If >10 personas or >5 variants |
| persona-user-test (URL, 5 screens, 5 personas) | 25 | 15–25K + images | 500K + image tokens | Always |
| **persona-user-test (video)** | **see formula below** | **frames × persona** | **multi-million** | **Always — show estimate** |
| persona-turf (10 personas, 12 options) | 10 | 10–20K | 150K | If >15 personas |
| persona-conjoint (8 personas, 15 profiles) | 8 (or 8×15=120 if pairwise) | 10–30K | 150K–3M | Always for pairwise |
| persona-max-diff (8 personas, 6 sets) | 8 | 10–20K | 120K | Rarely |
| persona-van-westendorp (8 personas, 4 Q's) | 8 | 5–10K | 60K | Never |
| persona-brand-tracking (8 personas, 5 brands) | 8 | 10–20K | 100K | If >15 personas |
| persona-ethnographic (1 persona narrative) | 1 | 30–60K | 50K | Never |
| persona-diary-study (1 persona, 7 entries) | 7 | 20–40K | 200K | If >14 entries |
| persona-concept-test (5 personas) | 5 | 20–40K | 150K | Never |
| persona-tree-test (5 personas, 10 tasks) | 5 | 15–25K | 100K | Rarely |

## Video-specific estimate (persona-user-test)

Video reactions are the most expensive thing in the catalog by 1–2 orders of magnitude. Always estimate before launching.

Variables:
- `D` = video duration in minutes
- `C` = chunk size in minutes (default 2)
- `F` = frames extracted per chunk (default 12 — one every 10s for a 2-min chunk)
- `P` = number of personas reacting
- `I` = tokens per image (Claude vision: ~1500–2000 tokens per image at standard resolution)
- `T_text` = text tokens per persona reaction (~10K including persona doc loaded once per chunk per persona)

Total chunks: `chunks = ceil(D / C)`
Total subagent runs: `runs = chunks × P`
Total tokens: `tokens ≈ runs × (F × I + T_text)`
Estimated cost: `tokens / 1_000_000 × ($3 input + $15 output) ≈ tokens / 1_000_000 × ~$18` (rough blend, mostly input)

**Worked example** — 30-minute video, 5 personas, defaults:
- chunks = 15
- runs = 75
- per-run tokens ≈ 12 × 1800 + 10000 ≈ 32K
- total ≈ 2.4M tokens ≈ **~$40–60**

A 1-hour video with 8 personas would cost roughly $200–300. **Always warn at this scale.**

Hard cap suggested in `persona-user-test`: 1 hour of video, 8 personas, or any combination that the estimator says will exceed ~$50 — surface for explicit user confirmation.

## How to warn the user

Format the warning consistently so the user can compare across methods. Before launching anything in the "always warn" tier or anything the user might find surprising:

```
This study will spawn ~<N> subagent runs and use roughly <T>K–<T>K tokens.
Estimated cost: $<low>–$<high> (using <model> at <date> pricing).
Run time: ~<minutes> minutes (parallelized in batches of <batch>).
Proceed?
```

Use a blocking question (AskUserQuestion in Claude Code, equivalent in Codex). Only skip the confirmation if the user explicitly said something like "just run it, don't ask me about cost" or has set a project-level instruction to that effect.

For cheap methods (under ~$1 estimated), don't ask — just launch. Asking for trivial confirmations is its own kind of friction.
