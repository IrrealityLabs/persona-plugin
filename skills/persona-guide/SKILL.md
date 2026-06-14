---
name: persona-guide
description: Start-here orientation for this plugin and for personas in general — what a persona is, how the plugin is structured and where personas are stored, what you can use personas for, and what makes a persona good. Use whenever the user asks a question about this plugin or how it works ("how does this plugin work", "where are personas stored", "what skills are there", "what's the difference between persona-create and persona-distill"), about personas in general ("what are personas good for", "what can I use personas for", "use cases for personas", "I'm new to this, where do I start"), or about persona quality ("how do I make a good persona", "what makes a persona accurate"). Load this before answering plugin/persona questions so the answer reflects how the plugin actually works.
---

# Persona Guide — start here

This plugin builds **AI personas** and runs research against them, all locally — no account, no
API key, no server. This skill is the map: what a persona is, where things live, what the other
skills do, what people use personas for, and how to make a good one. Read it before answering a
"how does this work / what can I do with this" question, then point the user at the specific
skill they need.

## What a persona is, and where it lives

**A persona is one markdown file.** Everything for the user's project lives under `.personas/` in
the current working directory (or `$PERSONA_HOME` if that env var is set). Show the *shape* with an
example rather than reciting a full file inventory — the exact files depend on what the persona was
built from. For instance, a persona distilled from Slack with a few hand-added fixes might look
like:

```
./.personas/
├── <slug>.md                  # THE PERSONA — one file per person
└── assets/
    └── <slug>/                # immutable, append-only source data
        ├── slack-messages.jsonl   # whatever the persona was built from
        ├── corrections.jsonl      # answers the user fixed (persona-correct)
        └── observations.jsonl     # data the user added (persona-observe)
```

- **The `.md` has two parts.** A synthesized **body** (paraphrased prose — the general model of
  the person) and a **`## Examples`** section of up to ~30 verbatim `{context, question, answer}`
  turns showing how the person actually responds. The examples are the strongest grounding and
  win over the body when they disagree.
- **The assets are the real history; the `.md` is disposable.** `assets/<slug>/` is append-only —
  data only gets added, never rewritten. The `.md` is a *projection* of the assets, so it can be
  rebuilt at any time (`persona-refresh`) without losing anything. Corrections and hand-added
  observations survive every rebuild because they live in the assets.

## The skills, by what you're trying to do

There's a skill for each step. Point the user at a couple of relevant ones as examples rather than
reciting the whole list — the full set is available as the plugin's skills, and `persona-research`
is the menu for studies:

- **Build a persona** — e.g. `persona-create` (from scratch) or `persona-distill` (from real data
  like Slack / X / web).
- **Keep it current** — e.g. `persona-correct` (fix a wrong answer so it sticks) or
  `persona-observe` (add data you already have).
- **Use one persona** — `persona-ask` (one grounded, referenced answer with a confidence tag).
- **Use a panel** — `persona-research` picks the right study method; or go direct, e.g.
  `persona-review` to critique an asset.

Selection is simple everywhere: **name the personas you want, or get all of them.** There's no
search or sampling.

## What people use personas for

A persona panel is fast, cheap, and available when real research isn't — early exploration,
directional checks, or a pre-filter before you spend time on real interviews. Common uses:

- **Review something before you ship it** — landing-page copy, an ad, a pricing page, an email
  (`persona-review`, channel sims like `persona-x-post` / `persona-linkedin-post` /
  `persona-email`).
- **Compare variants** — which headline / page / concept wins (`persona-ab-test`,
  `persona-concept-test`).
- **Pressure-test a decision or plan** — surface objections and pushback before a real meeting or
  launch (`persona-council`, `persona-roast`).
- **Understand people cheaply** — focus groups, surveys, interviews, JTBD switch interviews,
  ethnographic / diary studies (`persona-focus-group`, `persona-survey`, `persona-interview`,
  `persona-jtbd-interview`, `persona-ethnographic`, `persona-diary-study`).
- **Price something** — find the acceptable range or the trade-offs that drive choice
  (`persona-van-westendorp`, `persona-conjoint`, `persona-max-diff`).
- **See how an idea travels** — how a message lands on a channel, or spreads through a population
  or market (`persona-social-listening`, `persona-town`, `persona-market`).
- **Brainstorm from many angles** — lateral ideas, or one better answer fused from many
  perspectives (`persona-high`, `persona-of-thought`).
- **Rehearse a high-stakes conversation** — a journalist interview, a sales pitch, a 1:1 with your
  boss, where the persona plays the counterpart and *you* are the one being tested
  (`persona-roleplay`).
- **Get a specific person's likely take** — consult a persona distilled from a real colleague,
  expert, or thinker without involving them (`persona-ask`).
- **Run it as an automated eval in a loop** — a persona review is a check an agent can call on
  every iteration of a build/optimize loop, not just once by a human (`persona-goal`,
  `persona-review`).
- **Generate synthetic respondents or test inputs** — a stand-in audience for testing a system, or
  a survey-grounded synthetic population (`persona-copula`).

Personas are stand-ins, not customers. Treat every result as a hypothesis to check with real
people before you bet on it.

## What makes a persona good

The full evidence base for persona quality lives in **`persona-create`** — read it before
investing in a persona. The headlines:

- **One persona = one real, specific person.** A persona can stand in for many people, but the
  faithful model of a single human is the thing worth building. Accuracy of the individual is
  what matters.
- **Concrete behavior and context beat adjectives.** What they've actually done, in what
  situation, with real verbatim quotes (that's what `## Examples` is for) — not a pile of
  personality labels.
- **Negative experiences matter.** What makes them bounce, distrust, or churn is some of the most
  predictive signal you can capture.
- **A persona gets better as you use it.** Every time you `persona-correct` a wrong answer or
  `persona-observe` real data, the persona improves and that improvement is permanent (it lives in
  the assets). Personas are meant to be maintained, not built once and frozen.

## New here? The shortest path

1. Build one persona — `persona-create` (from scratch) or `persona-distill` (from real data).
2. Ask it something — `persona-ask`.
3. When you want a study, `persona-research` helps you pick the method.

Then keep it sharp with `persona-correct` and `persona-observe` as you learn where it's wrong.
