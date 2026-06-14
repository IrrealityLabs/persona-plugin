# Email source

Turn an email archive into the same thread records the Slack source produces, so the
distillation fan-out extracts `{context, question, answer}` turns from email exactly as it does
from Slack. No API key — you point at a file the user already has.

## What it accepts

- **`.eml`** — a single message (or a saved thread exported as one `.eml`).
- **`.mbox`** — a mailbox export (many messages). Gmail/Apple Mail/Thunderbird all export `.mbox`.
- **`.txt`** — a pasted or saved plain-text email thread.

Most useful: an export of the target person's **sent mail** (so their replies are the "answers"),
or full threads they participated in.

## How to get the file

- **Gmail** — Google Takeout → Mail → exports `.mbox`. Or, for one thread, "Show original" → save as `.eml`.
- **Apple Mail** — select messages → File → Save As → Raw Message Source (`.eml`), or export a mailbox (`.mbox`).
- **Outlook / Thunderbird** — export the folder to `.mbox` (Thunderbird ImportExportTools), or save a message as `.eml`.
- Or just paste a thread into a `.txt` file.

## Run

```
node skills/persona-distill/scripts/parse-email.mjs --slug=<slug> --file=<path> --target="<name or email>"
```

`--target` identifies the persona — whose messages are the "answers" the distiller learns from
(match a display name or an email address). The script:

- splits `.mbox` into messages (a `.eml` is one message),
- decodes quoted-printable / base64 bodies and strips HTML to text,
- **strips quoted reply text** (`> …` lines and "On … wrote:" trailers) so each message is what
  that person actually wrote, not the history,
- groups messages into threads by normalized subject (ignoring `Re:` / `Fwd:`), ordered by date,
- writes `email-messages.jsonl` (thread records, same shape as `slack-messages.jsonl`) and
  `email-metadata.json` (with the target) to `./.personas/assets/<slug>/`.

If it warns that no messages matched `--target`, it prints the senders it saw — re-run with the
right name/email.

## Then

Distillation reads `email-messages.jsonl` like any other source: the target's replies become
`answer`s, the message they replied to becomes the `question`, and earlier thread messages become
`context`. Add `email` to the doc's `sources` frontmatter.

## Privacy

Email is private correspondence. Keep `./.personas/assets/` gitignored, paraphrase in the doc
body (verbatim only in `## Examples`), and apply the same consent standard as any persona of a
real, identifiable person.
