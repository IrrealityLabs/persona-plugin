# Slack source

How to obtain a Slack API token, store it, and run the dump script that pulls messages into `./.personas/assets/<slug>/slack-messages.jsonl`.

## Token acquisition (one-time)

The dump uses Slack's `search.messages` and `conversations.history` APIs, which require a **user token** (`xoxp-…`), not a bot token (`xoxb-…`). User tokens act with the authenticating user's permissions — the dump will only see what that user can already see in Slack.

Walk the user through this:

1. Go to <https://api.slack.com/apps> and click **Create New App** → **From scratch**. Name it something like "Persona Distill" and pick the workspace.
2. In the left sidebar, go to **OAuth & Permissions**.
3. Under **User Token Scopes** (not Bot Token Scopes), add:
   - `search:read` — required for the message search.
   - `users:read` — to resolve usernames to user IDs.
   - `channels:read`, `channels:history` — for public channels.
   - `groups:read`, `groups:history` — for private channels the user is in.
4. Scroll up and click **Install to Workspace**. Approve the scopes.
5. Back on **OAuth & Permissions**, copy the **User OAuth Token** (starts with `xoxp-`).

If the workspace requires admin approval to install apps, the user will need to coordinate with their workspace admin.

## Storing the token

Two options — let the user pick:

- **Paste in chat → we save it.** User pastes the `xoxp-…` token; you write it to `./.env` as `SLACK_USER_TOKEN=xoxp-…`. Append, don't overwrite, if `.env` already has other keys.
- **They put it in `.env` themselves.** Tell them the variable name (`SLACK_USER_TOKEN`) and confirm by reading `.env` (don't print the value back).

Either way, **add `.env` to `.gitignore`** if it isn't already. Check and update if needed — don't assume.

The dump script auto-loads `.env` from the current directory.

## Running the dump

Two modes — the user picks based on what represents their target persona:

### Mode A: dump a specific user's messages

For when the persona is grounded in a real person (a customer, a public Slack member, a colleague who represents a customer type).

```bash
node ${CLAUDE_PLUGIN_ROOT}/skills/persona-distill/scripts/dump-slack.mjs \
  --slug <persona-slug> \
  --user <slack-username-or-display-name> \
  [--months=12]
```

The script resolves the user, runs `search.messages` with `from:@<user>` across the time window, expands every thread the user touched (so context is preserved), and writes the result.

### Mode B: dump a channel's messages

For when the persona aggregates many voices — e.g. `#customer-feedback`, a community Slack channel, a beta-tester channel. The persona becomes "the typical participant in this channel."

```bash
node ${CLAUDE_PLUGIN_ROOT}/skills/persona-distill/scripts/dump-slack.mjs \
  --slug <persona-slug> \
  --channel <channel-name-without-#> \
  [--months=12]
```

The script pulls `conversations.history` for the channel across the time window and expands threads.

### What gets written

```
./.personas/assets/<slug>/
├── slack-messages.jsonl     # one JSON record per line; see schema below
└── slack-metadata.json      # source info: mode, target, date range, counts
```

JSONL record shapes:

```jsonc
// Standalone message
{"kind": "standalone", "channel_id": "...", "channel_name": "...", "ts": "...", "user": "...", "user_name": "...", "text": "...", "permalink": "..."}

// Thread (root + replies)
{"kind": "thread", "channel_id": "...", "channel_name": "...", "thread_ts": "...", "permalink": "...", "messages": [{"ts": "...", "user": "...", "user_name": "...", "text": "..."}, ...]}
```

DMs and multi-person DMs are excluded by design — personas are grounded in public/channel conversation only.

## Limits and failure modes

- `search.messages` is capped at ~10,000 results per query. The script reports `search_capped: true` in metadata if hit; the user can narrow the window (`--months=3`) and re-run.
- Only public channels and conversations the token's user belongs to are searchable.
- If the script returns zero messages, the most common causes are: wrong username/channel spelling, token missing required scopes, or the user truly has no messages in scope. Don't proceed to distillation — fix the dump first.
