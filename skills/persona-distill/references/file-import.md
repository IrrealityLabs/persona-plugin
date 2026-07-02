# Importing files the user already has

For data that isn't a live Slack/X/web pull or an email archive — a PDF, a Word/Excel doc, a
screenshot, pasted text, or an exported chat log. The goal is the same as every source: end up
with universal asset rows — `{context, question, answer, source}`, `answer` always the person's
own verbatim words, `source` pointing back to the file — in `./.personas/assets/<slug>/`.
This path is shared by `persona-distill` (build a new persona) and `persona-observe` (add to an
existing one).

There's deliberately **no parser script** for these — you read them with the tools you already
have, extract the rows yourself, and write them to `assets/<slug>/<name>.jsonl`. Keep the
original file (or the cleaned transcript) alongside in the same folder — assets are append-only
and the raw artifact is the row's `source`.

## By format

- **PDF** — read it directly with the Read tool (it extracts text and pages), then extract rows.
- **Screenshots / images** (a chat screenshot, a photographed note) — read with the Read tool
  (vision). Transcribe the exchange, then extract rows.
- **Pasted text** — the user pastes a transcript, interview, or note. Save the paste verbatim to
  `assets/<slug>/<name>.md` (it's the `source`), then extract rows from it.
- **Exported chat JSON** (WhatsApp/Discord/Messenger/etc. exports) — read the JSON directly;
  structure varies by platform, so identify the sender/text/timestamp fields, then emit one row
  per message by the target person (question = the preceding message by someone else).
- **Word (`.docx`)** — the Read tool doesn't read `.docx`. Convert first: `pandoc file.docx -t
  markdown` (or, on macOS, `textutil -convert txt file.docx`), then read the result. If neither
  is available, ask the user to paste the text or export to PDF.
- **Excel / Sheets (`.xlsx`)** — convert to CSV (`xlsx2csv file.xlsx > file.csv`) and use the CSV
  path. A spreadsheet of question→answer rows maps straight onto the universal rows
  (this is exactly `persona-observe`'s CSV mode).

## Extracting the rows

Emit a row wherever the person is *speaking* — an interview question and their answer, a prompt
and their reply, an unprompted remark (question empty). `answer` is their words verbatim;
`context` says what was happening ("customer interview 2026-03, discussing onboarding");
`source` names the file (plus a page/position hint for long ones). Only their own words become
rows — a bare bio or a list of facts about them isn't an asset row; if it matters, it belongs in
the user's own description when creating the persona, not in the quotes corpus.

## Privacy

Same as every source: keep `./.personas/assets/` gitignored, paraphrase in the body (verbatim only
in `## Examples`), and apply a real-person consent standard.
