---
name: persona-avatar
description: Give a persona a face and a voice — a photorealistic video-call-style profile photo and a ~6-second talking-head intro video where they introduce themselves, generated through OpenRouter. Works from a description in the persona doc, or from a real photo / video of the person when they consented to it. Use when the user says "/persona-avatar", "make an avatar for <persona>", "give <persona> a face", "generate a profile picture / intro video for <persona>", or wants personas to feel real in a demo or presentation.
---

# Persona Avatar

A face and a voice make a persona easier to work with — for demos, decks, or just keeping a panel
memorable. This skill makes two files in the persona's assets folder:

- `./.personas/assets/<slug>/avatar.png` — a 16:9 webcam-style profile photo.
- `./.personas/assets/<slug>/intro.mp4` — a 6-second clip of that person saying a one-line intro, with audio.

Everything but the two generation calls is done by you, the agent: reading the doc, looking at any photo,
writing the description and the line.

## What it needs

- **An OpenRouter key** (`OPENROUTER_API_KEY` in env or `.env`). Avatars are OpenRouter-only, because the
  image and video models are reached through its API; other providers' keys don't work here. If missing, walk the user through
  `skills/persona-calibrate/SKILL.md` → "What it needs". Cost: the photo is a few cents; the video is about
  $0.30 for 6 seconds at the default model.
- **`ffmpeg`**, only if starting from a video of the person (`ffmpeg -version`; `brew install ffmpeg`).
- **Consent, if it's a real person.** Using a real person's photo or video to make a synthetic likeness of
  them is only OK when they agreed to it (e.g. survey respondents who opted in). Without that, build the
  avatar from the description alone — it's a stand-in, not their likeness. Never make an avatar meant to
  pass as a real, identifiable person to others.

## Phase 1 — Describe the person

- **From a video of them** (e.g. their survey intro): grab a frame —
  `ffmpeg -ss 3 -i <video> -frames:v 1 -q:v 2 -y frame.jpg` — then look at it and write an objective
  description: approximate age and gender, build, hair, facial features, skin tone, clothing, setting,
  demeanor. Pass the frame as `--reference`.
- **From a photo:** same, using the photo directly.
- **From the doc only:** compose the description from `## Demographics`, `## Contextual` and anything
  visual the doc grounds (job, hobbies → clothing and background props). Don't invent striking features the
  doc doesn't support; keep it plausible and ordinary.

## Phase 2 — Photo

```bash
python3 skills/persona-avatar/scripts/avatar.py image --prompt "<description>" \
  [--reference frame.jpg] --out ./.personas/assets/<slug>/avatar.png
```

Look at the result. If it doesn't fit the persona, adjust the description and run again (new filename —
assets are append-only, never overwrite).

## Phase 3 — Intro line

Write what they say: a greeting, a first name, and one interesting thing about them, ~10–15 words (about 5
seconds spoken), in their voice from `## How they actually talk` / `## Examples`. E.g. "Hey! I'm Sam, I
teach high-school chemistry and spend weekends restoring old sailboats." Never mention children or anything
about minors, and use the persona's display name or a pseudonym rather than a real person's name.

## Phase 4 — Video

```bash
python3 skills/persona-avatar/scripts/avatar.py video --image ./.personas/assets/<slug>/avatar.png \
  --speaker "A <age>-year-old <gender> from <location>" --line "<intro line>" \
  --out ./.personas/assets/<slug>/intro.mp4
```

The job takes a minute or two; the script polls and downloads. `--model` takes any OpenRouter video model
with first-frame support (`curl https://openrouter.ai/api/v1/videos/models` lists them).

## Phase 5 — Report

Show the photo, give both paths and the cost the script printed. The files live with the persona's other
assets; nothing in the persona doc needs to change.
