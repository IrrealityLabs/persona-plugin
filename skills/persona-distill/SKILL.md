---
name: persona-distill
description: Build a persona by distilling real data — Slack messages, X/Twitter posts, web research, or any combination — into the same persona doc format that persona-review consumes. Use when the user says "distill a persona from <source>", "/persona-distill", "build a persona from this person's tweets", "make a persona from our #feedback channel", "distill <name> from web research", or wants a data-grounded persona instead of the interview-based persona-create. Walks the user through API key setup if needed, pulls raw data into ./.personas/assets/<slug>/, then runs a fan-out distillation into ./.personas/<slug>.md.
---

# Persona Distill

Turn real data — Slack history, X/Twitter posts, web research, or a multi-source combination — into a persona doc the `persona-review` panel can consume. The difference from `persona-create` is the *source of truth*: persona-create asks the user; persona-distill reads the data and infers.

Output is the same persona doc shape (At a glance / Context / JTBD / What they've tried / What makes them bounce / How they talk about this problem / What would actually convince them / Known gaps) so the same panel skill consumes either one indifferently.

**One persona per run.** Pulls can be slow and corpora can be large — focusing on a single persona keeps the synthesis honest.

## Phase 0 — Identify target, source(s), and name

Three things, in order, before any data moves:

1. **Who is the persona?** A real named person (e.g. "Sarah Chen, CMO at Acme"), a public figure who represents a customer type ("paulg as a proxy for the bootstrapped-founder ICP"), or an abstract type to be aggregated from many sources ("the typical solo consultant"). Get this crisp — it determines what to search for.

2. **Which source(s)?** Currently supported:
   - **Slack** — messages from a specific user or a specific channel in a Slack workspace the user can access. See `references/slack-source.md`.
   - **X (Twitter)** — posts from one or more X accounts. See `references/x-source.md`.
   - **Web search** — public writing, interviews, podcast transcripts, forum posts, etc. See `references/web-search-source.md`.
   - **Email** — an `.eml` / `.mbox` / `.txt` export of the person's mail (no API key). See `references/email-source.md`.
   - **Files the user already has** — a PDF, Word/Excel doc, screenshot, pasted transcript, or exported chat JSON. See `references/file-import.md`.

   Multi-source is supported and often better — e.g. pull someone's X posts *and* their public blog posts *and* their Slack messages, then distill from the combined corpus. Ask the user which sources to use; default to whatever they mentioned, otherwise ask.

3. **What slug?** Same naming rules as `persona-create`:
   - If the user gave a name, use it (kebab-cased).
   - Otherwise pick one based on who the persona is — `sarah-chen.md`, `paulg.md`, `bootstrapped-consultant.md`. Never `persona-1.md`.
   - Tell the user the slug before you start writing files so they can override.

## Phase 1 — Walk through API setup (if needed)

For Slack and X, the user needs an API token. Before running any dump script:

- Check whether the token is already in env (`SLACK_USER_TOKEN`, `X_BEARER_TOKEN`) or in a `.env` file in the current directory.
- If not, load the matching source reference and walk the user through obtaining and storing the token. Each reference doc has a token-acquisition walkthrough with the minimum required permissions/scopes.
- Offer the user two storage options: (a) save to `./.env` (we'll write it; remind them to `.gitignore` it), or (b) they paste the token in chat and we write it to `./.env` for them. Don't ask them to set a shell env var manually — too easy to lose between sessions.
- Never log or echo the token back to the user. Confirm "saved" without printing the value.

For web search, no API key is needed — the built-in WebSearch / WebFetch tools cover it.

## Phase 2 — Pull data into the assets folder

The persona store is `$PERSONA_HOME` if that env var is set, else `./.personas/` (the dump scripts honor it automatically). Paths below show the default; substitute `$PERSONA_HOME` for `./.personas` when it's set.

**Every source writes the same universal asset row** — one JSONL line per thing the person said:

```jsonl
{"context": "what was happening", "question": "what prompted it (empty if unprompted)", "answer": "their words, verbatim", "source": "permalink / URL / file — resolves back to the origin"}
```

`answer` is always the person's own verbatim words — that's the whole invariant. Adding a new source to the plugin means nothing more than emitting this file.

Assets layout:

```
./.personas/
├── <slug>.md                       # the persona doc (written in Phase 4)
└── assets/
    └── <slug>/
        ├── slack.jsonl             # if Slack source used
        ├── x.jsonl                 # if X source used
        ├── web.jsonl               # if web search source used
        ├── email.jsonl             # if email source used
        └── metadata.json           # which sources, when pulled, counts
```

Per-source mechanics:

- **Slack** — run `scripts/dump-slack.mjs` per the slack-source reference. Writes `slack.jsonl` + metadata.
- **X** — run `scripts/dump-x.mjs` per the x-source reference. Writes `x.jsonl` + metadata.
- **Web search** — fan out a small set of research subagents per the web-search-source reference. Writes `web.jsonl` — **only things the person themselves said** (interview answers, podcast quotes, their own posts); third-party commentary is not collected.
- **Email** — run `scripts/parse-email.mjs` per the email-source reference. Writes `email.jsonl` + `email-metadata.json`.
- **Files the user has** — read/convert per the file-import reference (PDF and images via the Read tool; convert docx/xlsx first). Extract the rows into `assets/<slug>/<name>.jsonl`, keeping the original alongside (no script).

If a source pull fails or returns nothing meaningful, surface it clearly and ask the user how to proceed. Don't silently distill from a thin or missing source — flag it.

After Phase 2, write/update `assets/<slug>/metadata.json` with `{sources: [...], pulled_at, counts, target_description}`.

## Phase 3 — Fan-out distillation

Now turn the corpus into a persona doc. Use the spec in `references/distillation.md` — it defines the two-stage fan-out (workers extract evidence per facet, reducers synthesize per section) tuned to the persona doc shape persona-review consumes.

The corpus may be much larger than a single agent's context (a year of someone's Slack can be >5MB of JSONL; an active X account is similar). The fan-out exists for exactly this reason — chunk the input, parallelize workers, reduce per section.

If the corpus is small enough to fit comfortably in one agent's context (rough heuristic: combined source size under ~50KB), skip the fan-out and synthesize directly in a single pass. Don't fan out for the sake of it.

## Phase 4 — Write the persona doc and confirm

The persona doc is two parts: a **synthesized body** (paraphrased, no verbatim — the generalist model) plus a **`## Examples`** section (verbatim few-shot turns). Build them in order:

1. **Write the body** to `./.personas/<slug>.md` using the persona doc template (reproduced in `references/distillation.md`). Frontmatter must include `name`, `description`, `last_distilled_at`, `sources` (an array — `[slack]`, `[x]`, `[web]`, or any combination), and a `distilled_from` block with per-source pull dates and corpus sizes.
2. **Append `## Examples`** — select up to ~30 of the best asset rows and render them verbatim as the final section (format in `references/distillation.md`). Prioritize rows from `corrections.jsonl` (known-good ground truth), then choose for coverage and variety over redundancy. This is the distiller's judgment call while reading the assets — there's no separate script, and it's intentionally not deterministic. A *refresh* re-runs exactly this selection against the current assets.

Then show the user the finished doc and ask if anything reads as wrong, overstated, or putting words in the persona's mouth that the source data doesn't actually back. Persona docs distilled from real data almost always need a correction pass — spot-check at least one strong claim per section against the underlying assets before declaring it done.

Close with: "Persona saved to `./.personas/<slug>.md` (with N examples). Run `persona-review` to use it, `persona-correct` when it answers something wrong, `persona-observe` to add data you already have, or `persona-refresh` to rebuild it from the assets."

## Privacy

- Raw asset dumps in `./.personas/assets/` should be gitignored. Remind the user if `.gitignore` doesn't already cover it.
- Slack and X data may include things people said in semi-private contexts. The persona doc is a *paraphrased* synthesis — never copy verbatim message or post text into the persona doc itself. The fan-out spec enforces this; check the doc before saving.
- If distilling a persona of a real, identifiable person, consider whether they'd be comfortable knowing this exists — same standard as keeping private notes about someone.

## Notes

- **One persona per run.** Multiple personas need multiple runs.
- **Refreshing an existing persona:** the `.md` is a disposable projection of the assets, so regenerating it loses nothing the user can't rebuild. Use `persona-refresh` to rebuild from the assets *without* re-pulling sources; rerun `persona-distill` only when you want to pull fresh source data. Corrections (`corrections.jsonl`) and manually-added observations are append-only and survive every rebuild. (Raw source re-pulls currently *replace* the prior dump for that source — making pulls themselves append-only/versioned is a follow-up.)
- **If the user has already pulled their own data** (e.g. a CSV export of customer interviews) and just wants you to distill it, drop them into Phase 3 directly — point the distillation at the file they provide instead of running the source-specific scripts.
