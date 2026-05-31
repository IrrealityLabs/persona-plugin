# X (Twitter) source

How to obtain X API credentials, store them, and run the dump script that pulls posts into `./.personas/assets/<slug>/x-posts.jsonl`.

## A note on X API access (as of 2026)

X's free API tier does **not** include read access to user timelines. To pull tweets you need at least **Basic** ($200/month) or higher. If the user doesn't have a paid X API tier:

- Offer to switch to the web-search source instead (`references/web-search-source.md`) — it can scrape public X posts via search engines and is usually adequate for persona distillation, just lower fidelity than direct API access.
- Or, if the user has the `xurl` skill installed, that may already be configured with their X credentials — flag it and prefer that path over our standalone script.

Don't force the user into a paid plan they don't have. Surface options.

## Token acquisition (if they have API access)

X API v2 uses a **Bearer Token** for read-only requests, which is sufficient for the dump.

Walk the user through this:

1. Go to <https://developer.x.com/en/portal/dashboard> (formerly developer.twitter.com).
2. Select their project and app (or create one).
3. Under **Keys and tokens**, find the **Bearer Token** section and copy it (or regenerate if they don't have it saved).
4. Confirm the project has at least the Basic tier and `tweet.read`, `users.read` permissions.

## Storing the token

Same two options as Slack:

- **Paste in chat → we save it.** Write to `./.env` as `X_BEARER_TOKEN=…`. Append, don't overwrite.
- **They put it in `.env` themselves.** Confirm the variable name (`X_BEARER_TOKEN`).

Add `.env` to `.gitignore` if it isn't already.

## Running the dump

```bash
node ${CLAUDE_PLUGIN_ROOT}/skills/persona-distill/scripts/dump-x.mjs \
  --slug <persona-slug> \
  --user <x-handle-without-@> \
  [--max=1000] [--include-replies]
```

For multi-account aggregation (e.g. "the typical bootstrapped founder, distilled from these 5 accounts"), pass `--user` multiple times:

```bash
node ${CLAUDE_PLUGIN_ROOT}/skills/persona-distill/scripts/dump-x.mjs \
  --slug bootstrapped-founder \
  --user paulg --user patio11 --user nathanbarry \
  --max=500
```

Flags:
- `--max=N` — cap total posts per user (default 1000). The X API paginates; the script stops once it has N or hits a rate limit.
- `--include-replies` — include the user's replies as well as standalone posts. Off by default; replies are higher-volume but lower-signal for persona work.

## What gets written

```
./.personas/assets/<slug>/
├── x-posts.jsonl         # one JSON record per line
└── x-metadata.json       # users, date range, post counts, whether rate-limited
```

JSONL record shape:

```jsonc
{
  "id": "...",
  "author_handle": "...",
  "author_name": "...",
  "created_at": "2026-…",
  "text": "...",
  "kind": "post" | "reply" | "quote",
  "in_reply_to": "..." | null,
  "metrics": {"retweets": N, "likes": N, "replies": N},
  "url": "https://x.com/..."
}
```

## Limits and failure modes

- Basic tier rate limits are tight (~15-min windows). Long pulls will sleep between pages — be patient or reduce `--max`.
- Protected accounts can't be read. The script will report and skip.
- Reposts (RTs) without comment aren't included — they aren't the persona's own writing. Quote-tweets are included with `kind: "quote"`.
