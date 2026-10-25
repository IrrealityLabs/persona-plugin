---
name: persona-anonymize
description: Strip real names (and optionally emails / phone numbers) out of interview transcripts, survey exports or other source files before they become persona assets — replacing each with a consistent, culturally similar pseudonym so the data reads the same but no longer identifies anyone. Use when the user says "/persona-anonymize", "anonymize this transcript", "remove the names before building the persona", "pseudonymize this data", or is about to build or calibrate personas from data about real people that will be shared.
---

# Persona Anonymize

Source data about real people — interviews, survey videos, chat logs — is full of names: theirs, their
partner's, their boss's. If the personas will be shared, scrub them **before** import. Assets are
append-only, so the clean version has to be what goes in.

You (the agent) find the names; a small script applies the replacements exactly, so the same name
always becomes the same pseudonym across every file.

## Phase 1 — Read and build the map

Read the source files. List every span that identifies someone:

- **PERSON** names first — the subject and everyone they mention, including speech-to-text misspellings
  of the same name (map each variant to the same pseudonym).
- **EMAIL** / **PHONE** if present.

For each, pick a replacement that keeps the meaning: culturally similar, same number of name parts,
ideally the same first letter and a similar length and syllable feel — without being identifying. Don't
replace place names, employers or brands unless the user asks; they're usually the useful context.
Don't rewrite anything else.

Save the map as JSON next to the sources (keep it out of git — it's the key to undo the anonymization):

```json
[{"type": "PERSON", "text": "Jane Smith", "replacement": "Joan Sutton", "reason": "respondent"}]
```

Show the user the map and ask them to confirm or edit it before applying.

## Phase 2 — Apply

```bash
python3 skills/persona-anonymize/scripts/anonymize.py --map pii-map.json <file> [<file> ...]
```

Writes `<name>.anon<ext>` beside each file (originals untouched), replacing whole-word matches longest
first; a full name's first and last parts are mapped on their own too. Then grep the output for each
original name to confirm none survived, and skim for anything the map missed.

## Phase 3 — Hand off

Build the persona from the `.anon` files: `persona-create` (Mode 2 for a spreadsheet, Mode 3 for
transcripts) or `persona-distill` (file import). Remind the user that the map and the originals still
identify people — keep them private or delete them.

## Notes

- This removes direct identifiers, not everything: a distinctive job plus a small town can still point at
  someone. Say so when the data is sensitive.
- For an existing persona built from un-anonymized data, anonymize the original source files and build a
  new persona from the output; don't edit assets in place.
