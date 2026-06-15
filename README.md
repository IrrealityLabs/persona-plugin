# persona-plugin

A plugin for running **market research with simulated persona panels** — locally, without recruiting respondents. Build personas once; then review assets, ask focused questions, or run any of 20+ research methodologies against them.

## A note before you use it

**Persona simulations are not a substitute for talking to real customers.** They are best where real research isn't feasible — early-stage exploration, fast directional checks, methods you'd never run on real users because of cost or time, or as a pre-filter before investing in real interviews. They are simulations grounded in *what you've put into the persona docs* (interviews you ran, data you distilled, ICPs you've written) — they cannot surface what your personas don't know, can't replace lived experience, and will sound confident about things they're extrapolating.

Treat every result as a structured prompt for your own judgment, and as a list of hypotheses to validate with real customers before betting on them. Be customer-focused: the personas are stand-ins, not the customers themselves.

If you build a persona of a **real, identifiable person** (e.g. distilling someone's Slack, posts, or public writing), that's processing personal data and may be regulated where you and they are based — see [Legal & compliance](#legal--compliance) below. Complying with the law that applies to you is your responsibility.

## The four main skills

These are the entry points you'll use most. Everything else either consumes these or is dispatched by `persona-research`.

### `persona-create` — build a persona

The best-practice walkthrough for creating a persona doc. Three modes:

- **Interview** — answer ~6 questions about your target customer; auto-research the segment; draft and save.
- **Bulk import** — point at a CSV (one row per persona, one column per question); spawns subagents to turn each row into a persona doc.
- **Pre-supplied research** — paste an ICP doc, customer-research summary, or prior persona work; we structure it into our format.
- **Batch from a description** — give one description and a count ("10 potential Jaguar buyers aged 40–60 who value British heritage"); it pins down the must-hold criteria, plans a deliberate diversity frame, and generates that many *unique, non-duplicated* personas that all strictly fit.

Every persona doc captures the four dimensions plus verbatim language: **demographics**, **psychographics**, **behavioral**, **contextual**, and **how they actually talk**.

> Invoke: `create a persona`, `add a persona`, `/persona-create`, `build personas from this CSV`, `create 10 personas who are…`

### `persona-distill` — build a persona from real data

Turn real source data into a persona via fan-out distillation. Supports:

- **Slack** — dump messages from a user or channel (with a token walkthrough).
- **X (Twitter)** — dump posts from one or more accounts.
- **Web research** — aggregate public writing, interviews, podcast transcripts.
- **Multi-source** — combine the above into one persona corpus.

Distillation runs a two-stage worker/reducer fan-out and produces a doc in the same format as `persona-create`.

> Invoke: `distill a persona from <source>`, `/persona-distill`, `build a persona from this person's tweets`

### `persona-ask` — one persona, one question

Resolve a single persona by name and get their grounded, referenced response to a question. Every answer comes back with:

- A first-person quoted reaction.
- **References** to the persona doc sections that back it.
- A **confidence** tag (`high` / `medium` / `low` / `off-pattern`).

Quoted questions get asked verbatim; unquoted questions are reframed for better signal. Tally logic kicks in automatically for vote/rate/scale questions.

> Invoke: `ask <name>`, `what would <name> think of <X>`, `/persona-ask <name> "<question>"`

### `persona-research` — run a study

The parent / dispatcher for the full library of research methodologies. Helps you pick the right method based on your stage in the product lifecycle (WHY / WHAT / HOW) and dispatches to the matching child skill. Always estimates cost before launching expensive studies (uses live model pricing via LiteLLM / `ccusage`).

> Invoke: `run a study`, `do market research with the personas`, `/persona-research`, or describe a research question without naming a methodology

## Plus

- **`persona-review`** — review an asset (copy, landing page, ad, pricing page) past the panel with code-review-style feedback (severity tags, references, suggested changes). Originally the namesake of this plugin; now one method among many.
- **`persona-goal`** — *optimize* an asset against the panel in a loop: review → edit → re-score, driven by the native goal feature in Claude Code and Codex. Stops on a principled signal — the score stops improving, the panel runs out of blockers, or your round budget is hit — and tells done apart from stuck.
- **`persona-roleplay`** — rehearse a high-stakes conversation against a persona who plays the counterpart: a journalist interviewing you, a prospect you're pitching, your boss in a 1:1. Inverts the usual setup — *you* are the one being tested, and you get coached at the end.
- **`persona-presentation`** — slide-by-slide audience feedback on a deck or talk. Feed it a deck, a run-of-show, and/or a transcript/video; the personas sit through the whole talk and the panel feedback becomes a curated change list.
- **`persona-of-thought`** — each persona answers a question independently, then the answers are fused into a single anonymous joint response. Use when you want *one* better answer informed by many perspectives, not a panel breakdown.
- **`persona-observe` / `persona-correct` / `persona-refresh`** — keep a persona current: add real data you already have (`persona-observe`, freeform or CSV), fix a wrong answer so it sticks (`persona-correct`), or rebuild the persona from its source assets (`persona-refresh`).

## Studies available under `persona-research`

| Method | Skill | What it answers | Sample-size sweet spot |
|---|---|---|---|
| 1:1 interview | `persona-interview` | Depth on one viewpoint | 1 persona |
| JTBD switch interview | `persona-jtbd-interview` | Why did/didn't they switch? | 1–3 personas |
| Survey | `persona-survey` | Same Q's across many personas | 5–10 personas |
| Focus group | `persona-focus-group` | Group reactions with cross-talk | 3–6, 2–4 rounds |
| Council | `persona-council` | Adversarial debate / pressure-test | 4–7, 3–4 rounds |
| User test | `persona-user-test` | UX reactions to a URL or video | 3–5 personas |
| Presentation feedback | `persona-presentation` | Slide-by-slide audience read on a deck / talk | 3–6 personas |
| Tree test | `persona-tree-test` | Does the navigation / IA work? | 5–10 personas |
| A/B test | `persona-ab-test` | Which variant wins? | All available |
| Concept test | `persona-concept-test` | Validate an unbuilt concept | 5–8 personas |
| TURF analysis | `persona-turf` | Smallest set with widest reach | 8+ personas |
| Conjoint | `persona-conjoint` | Trade-offs between attributes | 8+ personas |
| MaxDiff | `persona-max-diff` | Rank a long list by importance | 5+ personas |
| Van Westendorp | `persona-van-westendorp` | Optimal price range | 8+ personas |
| Brand tracking | `persona-brand-tracking` | Awareness / associations / NPS | All available |
| Social listening | `persona-social-listening` | Organic brand mention rate | 8+ personas |
| Hacker News simulation | `persona-hacker-news` | Technical/contrarian thread reaction | 5–10 personas |
| X (Twitter) simulation | `persona-x-post` | Replies / quote-tweets / ratio risk | 6–12 personas |
| LinkedIn simulation | `persona-linkedin-post` | Comments / reposts / professional voice | 6–12 personas |
| Slack simulation | `persona-slack-message` | Channel reactions + invisible DM iceberg | 5–10 personas |
| Email simulation | `persona-email` | Reply rate / latency / tone | 4–10 personas |
| Roast | `persona-roast` | Brutally honest unfiltered critique | 3–6 personas |
| Collaborative brainstorm | `persona-brainstorm` | Generate & build on ideas as a group (yes-and) | 3–7, 2–3 rounds |
| Ethnographic | `persona-ethnographic` | "Walk me through your day" | 1–3 personas |
| Diary study | `persona-diary-study` | Behavior over time (7+ days) | 1–3 personas |

All methods know their sweet spot for sample size and **always run with whatever you have**, marking the output as `directional` when running below the methodology's preferred N.

## What it looks like

```
> ask skeptical-cto what they'd think of switching to our new auth system

skeptical-cto (Series A CTO, security-burned):

  "Switch what? You're asking me to migrate a working auth layer
  during the most fragile point in our scale curve. The post says
  it's 'simple' — that word triggers every alarm bell I have.
  Show me your customer references at our scale before I read past
  the headline."

References (persona doc):
  - § What makes them bounce: "vendors who use 'simple' to describe
    infra changes have always cost me at least a weekend"
  - § How they decide: "demands customer refs at comparable scale"

Confidence: high — direct match on bounce list + decision pattern.

— Simulated skeptical-cto, distilled from interview + web research,
  last refreshed 2026-05-30. Verify load-bearing claims with a real CTO.
```

## Installation

This repo is a plugin for both Claude Code and Codex.

### Claude Code

```
/plugin marketplace add <github-org>/persona-plugin
/plugin install persona-plugin@persona-plugin
```

Or from a local clone:

```
/plugin marketplace add /absolute/path/to/persona-plugin
/plugin install persona-plugin@persona-plugin
```

### Codex

Register the marketplace from the terminal:

```
codex plugin marketplace add IrrealityLabs/persona-plugin
# or: codex plugin marketplace add /absolute/path/to/persona-plugin
```

Then install the plugin:

```
codex plugin add persona-plugin@persona-plugin
```

Start a new Codex thread after installing so the new skills are loaded.

### Cursor

Cursor reads skills directly from a `skills/` directory in your workspace (or globally from `~/.cursor/skills/`). To use this plugin's skills in Cursor:

1. Clone the repo (or copy its `skills/` directory) into your workspace, or:
2. Symlink the plugin's `skills/` into `~/.cursor/skills/`:
   ```
   ln -s /absolute/path/to/persona-plugin/skills ~/.cursor/skills/persona-plugin
   ```
3. Restart Cursor. The skills will be available in Composer / Chat the same way the rest of your Cursor skills work.

The `.personas/` data directory lives in whatever workspace you're working in — no global setup required.

## How personas are stored

Personas and their source assets live in `.personas/` relative to your current working directory:

```
./.personas/
├── <slug>.md                         # the persona: synthesized body + a ## Examples section
└── assets/
    └── <slug>/                       # immutable, append-only source of truth
        ├── slack-messages.jsonl      # raw pulls the persona is distilled from
        ├── x-posts.jsonl
        ├── web-research.md
        ├── corrections.jsonl         # answers you fixed via persona-correct
        ├── observations.jsonl        # data you added via persona-observe
        └── ...
```

The `<slug>.md` is a disposable **projection** of the assets — `persona-distill` / `persona-refresh` regenerate it. The assets are append-only and never overwritten, so regenerating loses nothing. Add `.personas/assets/` to `.gitignore` if your raw source data shouldn't be committed (it usually shouldn't).

### A global persona store (`PERSONA_HOME`)

By default the store is **project-local** — `./.personas/` in whatever directory you're working in — so each project carries its own audience. If you'd rather keep **one shared set of personas across projects**, set the `PERSONA_HOME` environment variable to a directory of your choice and every skill (and the dump scripts) reads and writes there instead:

```bash
export PERSONA_HOME="$HOME/.personas"   # a global store, reused from any project
```

When `PERSONA_HOME` is set it fully replaces `./.personas/` — personas live at `$PERSONA_HOME/<slug>.md` and assets at `$PERSONA_HOME/assets/<slug>/`, with the same layout shown above. Leave it unset for the default per-project behavior.

## Repo layout

```
persona-plugin/
├── .agents/
│   └── plugins/
│       └── marketplace.json          # Codex marketplace manifest
├── .claude-plugin/
│   └── plugin.json                   # Claude Code manifest
├── .codex-plugin/
│   └── plugin.json                   # Codex manifest
├── plugins/
│   └── persona-plugin -> ..          # Codex marketplace entry points back to this plugin root
├── README.md                         # this file
└── skills/
    ├── persona-create/               # build a persona (interview / CSV / paste)
    ├── persona-distill/              # build a persona from real data (Slack/X/web)
    │   ├── references/               # per-source walkthroughs + distillation spec
    │   └── scripts/                  # zero-dep Node dump scripts
    ├── persona-ask/                  # one persona, one grounded answer
    ├── persona-observe/              # add real data to a persona (CSV / freeform)
    ├── persona-correct/              # fix a wrong answer so it sticks
    ├── persona-refresh/              # rebuild a persona's doc from its assets
    ├── persona-review/               # asset review with line-level critique
    ├── persona-goal/                 # optimize an asset against the panel in a stopping-aware loop (goal feature)
    ├── persona-roleplay/             # rehearse a live conversation; the persona plays the counterpart
    ├── persona-presentation/         # slide-by-slide audience feedback on a deck / talk
    ├── persona-of-thought/           # independent answers fused into one anonymous joint answer
    ├── persona-research/             # parent: catalog + dispatcher
    │   └── references/
    │       └── cost-estimator.md     # live model-pricing-aware cost rules
    └── persona-<study-type>/         # 20+ child skills, one per methodology
```

## Limits and honest caveats

- **Personas are not customers.** They reflect what you've encoded in their docs (interview, distillation, ICP). They will sound confident about things they're extrapolating; the references-and-confidence tagging exists to make that visible. Use it.
- **Sample sizes are small.** Real market research often needs hundreds or thousands of respondents. A persona panel of 5–15 produces *directional* results for most methods — useful for narrowing options, generating hypotheses, killing weak ideas cheaply. Not useful for statistical claims.
- **Quant methods especially.** Van Westendorp, conjoint, MaxDiff, TURF — all designed for large N. Persona-scale runs give you the shape of the answer, not a defensible number. Validate with real research before pricing decisions, feature commitments, or anything else that bets the budget.
- **Quality of personas determines quality of research.** A thin persona doc produces thin research outputs no matter which method you pick. Invest in `persona-create` / `persona-distill` before you invest in studies.
- **Cost can add up fast** for multi-round methods (council, focus group, video user testing). Always confirm the cost estimate before launching expensive runs.

## Legal & compliance

Most personas are **synthetic or aggregate** — an ICP, a segment, a batch generated from a description, a population sampled from survey data. Those raise no special legal issue.

But the plugin can also build a persona of a **real, identifiable person** — `persona-distill` pulls someone's Slack, X/Twitter, email, or public web writing into a profile of how they think and decide. That is *processing personal data about a real person*, and depending on where you and they are based it may be regulated by data-protection, privacy, and employment law (e.g. the EU/EEA [GDPR](https://gdpr-info.eu/), workplace/co-determination rules such as Germany's [BetrVG](https://www.gesetze-im-internet.de/englisch_betrvg/), the [EU AI Act](https://artificialintelligenceact.eu/), and comparable laws elsewhere).

**Understanding and complying with the law that applies to you is your responsibility** — this project can't do that for you, and the above is general awareness, not legal advice. Before profiling a named individual:

- **Have a lawful basis and, where appropriate, permission.** Being *able* to read someone's messages doesn't mean you may profile them — for colleagues and other non-public people especially, consider consent and whether they'd be comfortable with the persona existing. Profiling a public figure from their on-the-record public statements is a safer posture than profiling a private individual from internal communications, but "public" is not a blanket exemption everywhere.
- **Keep raw source data local.** Raw dumps live under `.personas/assets/` and are gitignored by default — keep it that way. The persona body is paraphrased (verbatim source belongs only in `## Examples`); treat the whole persona as private notes about a real person.
- **A persona is a simulation, not the person.** It can be wrong or out of date — never treat its output as the real person's actual position; verify anything load-bearing with them.

## Credits

Created by the team behind [AskRally](https://askrally.com).

## License

MIT.
