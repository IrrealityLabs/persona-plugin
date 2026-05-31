---
name: persona-audience
description: Define and manage named audiences — saved groups of persona slugs you can refer to by name. Once "stay-at-home-moms" is defined as an audience, "ask stay-at-home-moms about X" or "/persona-review with stay-at-home-moms" resolves to the underlying personas automatically. Use when the user says "create an audience", "save this group as an audience", "name this segment", "ask <audience name>" (and the name doesn't match a single persona), "/persona-audience", or after persona-sample filters down to a useful subset worth keeping.
---

# Persona Audience

A persona is a single simulated person. An **audience** is a named, saved group of personas — a reusable segment.

Audiences solve two problems:
- **Naming.** "Ask stay-at-home-moms about this" is easier than "ask busy-mom-of-three and working-from-home-parent and empty-nester about this." The audience IS the segment.
- **Reuse.** When `persona-sample` filters to a useful subset for one study, saving it as an audience means the next study can reach the same group without re-sampling.

Audiences live in `./.personas/audiences/<audience-slug>.md`. Every skill in this family checks audiences during slug resolution: if "stay-at-home-moms" matches an audience name, it expands to that audience's persona list before the study runs.

## When to use vs. alternatives

- Use `persona-audience` to create or update a named group of personas.
- Use `persona-sample` to dynamically filter personas for one study without saving the result. Optionally save the sample's output as an audience for next time.
- Use `persona-create` to make new personas (audiences group existing personas; they don't make new ones).

## Three modes

### Mode 1 — Define a new audience by description
The user names an audience and describes who's in it. You pick the matching personas from `./.personas/`, confirm with the user, save the audience.

### Mode 2 — Save a sample result as an audience
After running `persona-sample` (or after a successful study), the user wants to remember the persona subset that was used. You take the slug list and save it under a name they pick.

### Mode 3 — List / inspect / update existing audiences
The user wants to see what audiences exist, check who's in one, add or remove members, or delete an audience.

## Mode 1 workflow — Define by description

### Phase 1 — Get the audience name and description

The user says something like "create an audience called stay-at-home-moms — US parents managing households of 2+ kids."

You need:
- **Audience name (slug)** — kebab-case, e.g. `stay-at-home-moms`. Lowercase the user's name input.
- **Description** — one to three sentences describing who's in the audience. This isn't just a label; downstream skills use this description to confirm relevance.

### Phase 2 — Pick the personas

Two paths:

**A. User listed the slugs explicitly:** use that list. Validate each slug exists in `./.personas/`; flag missing ones and ask the user how to handle them (drop / pick alternatives / cancel).

**B. User described the audience without listing slugs:** call `persona-sample` with the description as the topic and request all matching personas (no N cap — audiences can be any size). Show the user the sampled list with the `why` per persona, and ask them to confirm or edit before saving.

If no personas match the description meaningfully (the sample comes back empty or low-confidence), tell the user — don't fabricate an empty audience. Offer: "No existing personas clearly match this audience. Want to create one via persona-create first, or relax the audience definition?"

### Phase 3 — Confirm and save

Show the user the assembled audience: name, description, the persona slugs included (with each persona's one-line description for context). Confirm before writing.

Save to `./.personas/audiences/<audience-slug>.md`:

```markdown
---
name: <audience-slug>
description: <one to three sentences>
created: <YYYY-MM-DD>
personas:
  - <persona-slug-1>
  - <persona-slug-2>
  - ...
---

# <Display name>

<Optional longer description of the audience: who's in it, why it's defined this way, anything important about how downstream skills should treat it. Leave the body empty if there's nothing useful to add beyond the description.>
```

## Mode 2 workflow — Save a sample as an audience

After `persona-sample` returned a useful subset (or a study just ran on a deliberately-picked group), the user says "save those as an audience called <name>."

You already have the slug list. Just:
1. Confirm the audience name with the user.
2. Confirm or solicit a one-line description (default to the topic that drove the original sample).
3. Save per the format above.

This mode is fast — no re-sampling, no re-confirming. Useful right after a study.

## Mode 3 workflow — List / inspect / update

**List audiences:** `ls ./.personas/audiences/` — for each, read frontmatter and show name + description + N personas.

**Inspect one audience:** read the file, show the description + persona list with each persona's one-line description.

**Add / remove personas:**
- Read the audience file.
- Update the `personas:` list in frontmatter.
- Confirm with the user before writing.

**Delete an audience:** confirm with the user before `rm`. Audiences are cheap to recreate but the slug-list memory of "who was in our beta-tester audience last quarter" is lost on delete — make sure the user means it.

## How downstream skills use audiences (for reference)

The other skills in this family check audiences during slug resolution:

- `persona-ask <name>` → look in `./.personas/` first for a matching persona file. If none, look in `./.personas/audiences/` for an audience. If found, expand to the audience's persona list and ask each one (subject to the persona-ask 5-persona default, with the audience size as override).
- `persona-review` with a slug list → audience names are valid in the slug list; they expand inline.
- `persona-research` child skills → same. Audiences can substitute for explicit slug lists in any sample input.

Audience expansion is recursive **only one level deep** — audiences contain persona slugs, not other audience slugs. If the user wants nested groupings, define them as flat audiences with overlapping members.

## Notes

- Audiences are *references*, not copies. If a persona doc is updated, every audience that includes it reflects the new content immediately.
- If a persona is deleted (`rm ./.personas/<slug>.md`), audiences that referenced it will have a broken pointer. The skills using audiences should flag missing personas at resolution time, not crash. Periodically (or after deletions) run a quick audit: for each audience, check every persona slug exists.
- A persona can be in any number of audiences. Audiences can overlap freely.
- Avoid audiences that are just "all personas" — that's the default. Audiences earn their keep by being narrower than the full roster.
