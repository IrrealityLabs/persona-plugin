# Importing files the user already has

For data that isn't a live Slack/X/web pull or an email archive — a PDF, a Word/Excel doc, a
screenshot, pasted text, or an exported chat log. The goal is the same: get the material into
`./.personas/assets/<slug>/` so distillation can read it and pull `{context, question, answer}`
turns out of it. This path is shared by `persona-distill` (build a new persona) and
`persona-observe` (add to an existing one).

There's deliberately **no parser script** for these — you read them with the tools you already
have, then write a cleaned artifact into assets.

## By format

- **PDF** — read it directly with the Read tool (it extracts text and pages). Save the relevant
  extracted text/transcript to `assets/<slug>/<name>.md`.
- **Screenshots / images** (a chat screenshot, a photographed note) — read with the Read tool
  (vision). Transcribe the exchange into text and save it.
- **Pasted text** — the user pastes a transcript, interview, or note. Save it verbatim to
  `assets/<slug>/<name>.md`.
- **Exported chat JSON** (WhatsApp/Discord/Messenger/etc. exports) — read the JSON directly;
  structure varies by platform, so identify the sender/text/timestamp fields, then either save a
  cleaned transcript or, if it's large, treat it like the Slack JSONL (thread records:
  `{kind:"thread", messages:[{user_name, text, ts}]}`) so the fan-out can chunk it.
- **Word (`.docx`)** — the Read tool doesn't read `.docx`. Convert first: `pandoc file.docx -t
  markdown` (or, on macOS, `textutil -convert txt file.docx`), then read the result. If neither
  is available, ask the user to paste the text or export to PDF.
- **Excel / Sheets (`.xlsx`)** — convert to CSV (`xlsx2csv file.xlsx > file.csv`) and use the CSV
  path. A spreadsheet of question→answer rows maps straight to `{context, question, answer}` turns
  (this is exactly `persona-observe`'s CSV mode).

## Turning it into turns

The artifact you save is raw material, like a Slack dump. When distilling (or in
`persona-observe`'s light refresh), pull verbatim `{context, question, answer}` turns from it
wherever the person is *responding* to something — an interview question and their answer, a
prompt and their reply. Material with no exchange (a bare bio, a list of facts) informs the
synthesized body, not `## Examples`.

## Privacy

Same as every source: keep `./.personas/assets/` gitignored, paraphrase in the body (verbatim only
in `## Examples`), and apply a real-person consent standard.
