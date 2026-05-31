---
name: persona-goal
description: Closed-loop optimization of a creative or asset against one or more personas, driven by the native goal feature in Claude Code and Codex (both supported). Each round runs the persona panel, scores how the asset lands, applies the highest-leverage changes, keeps the best version, and re-scores — stopping when the panel score stops improving for several rounds in a row, when no persona has a blocker left, or when a user-set round budget is hit. Use when the user says "/persona-goal", "optimize this against my personas", "iterate this copy until the personas stop finding problems", "use the goal feature to improve this asset for <persona>", or "keep improving this until it stops getting better". Borrows the convergence-vs-hardening logic of a deliberation panel so it knows the difference between done and stuck.
---

# Persona Goal

Iteratively optimize an asset (copy, headline, landing page, ad, pricing page, email, pitch) against a persona panel until it stops getting better. Each round is a `persona-review` + an edit: the panel reacts, you score how it landed, you apply the highest-leverage changes, you keep the best version, and you re-score. The skill runs that loop inside the platform's **goal feature** so it proceeds hands-off across turns, with a principled stopping place rather than an arbitrary number of edits.

The hard part of any optimization loop is *knowing when to quit*. This skill borrows the convergence logic of a deliberation panel (see `ask-team` / `persona-council`): it distinguishes **converged** (the panel has no blockers left — done) from **stuck/hardened** (the same objection keeps coming back no matter what you change — a structural problem edits won't fix) from **plateaued** (recent changes aren't moving the score — diminishing returns). All three are stop conditions; only the first is a "win."

## Using the goal feature (both platforms)

The loop is the same on both; only the wrapper differs. The goal feature lets the agent keep running rounds across turns and decide for itself when the stopping condition is met.

### Claude Code (v2.1.139+)
`/goal <condition>` sets a completion condition; after each turn a fast evaluator checks it *from the transcript* (it does not run tools itself), and Claude keeps going until it holds. `/goal` shows status, `/goal clear` cancels. Because the evaluator reads the transcript, the loop must **print the round ledger each round** (below) so the condition is checkable. Paste-ready:

```
/goal Optimize <asset> against personas <slugs> per the persona-goal skill. Each round: run the panel, print the round ledger (round k/N, panel score, best-so-far, blocker count, no-improvement streak), apply the top changes, keep the best version. Stop when the ledger shows no improvement for 2 rounds running, OR zero blockers with panel score >= 6/7, OR round = <N>. Then output the best version, the score trajectory, and why it stopped. Do not change <constraints>.
```

### Codex (0.128.0+)
Enable once: add `goals = true` under `[features]` in `~/.codex/config.toml`, or launch with `codex --enable goals`. Then `/goal <outcome>` (with `/goal pause`, `/goal resume`, `/goal clear`). Codex requires **evidence-based** completion, so the round ledger *is* the evidence. Phrase the goal in its four parts:

```
/goal
Objective: optimize <asset> so the persona panel (<slugs>) scores it >= 6/7 with zero blockers.
Do not change: <constraints — brand voice, claims, layout, whatever is fixed>.
Validate: after each round, re-run the panel and record the round ledger (panel score, best-so-far, blocker count, no-improvement streak).
Stop when: no improvement for 2 rounds running, OR zero blockers and score >= 6/7, OR <N> rounds reached. Output the best version, the score trajectory, and the stop reason.
```

### If the goal feature isn't available
Older version, or goals disabled — no problem. Run the same loop **manually**: execute rounds yourself up to the cap, applying the identical stopping rules below. The goal feature only automates the across-turn looping and the stop check; the skill's logic stands on its own.

## When to use vs. alternatives

- Use `persona-goal` to **improve** an asset through repeated panel-and-edit rounds with an automatic stopping place.
- Use `persona-review` for a **single** round of feedback (no editing, no loop). `persona-goal` calls it repeatedly.
- Use `persona-ab-test` to **compare fixed variants** you already wrote — not to generate and refine new ones.
- Use `autoresearch` for general non-persona optimization loops against a numeric benchmark.

## Inputs

- **The asset** — the thing to optimize, captured verbatim. If it's a file, edit the file in place each round (keep versions). If pasted, track versions in a run dir.
- **The persona(s)** — one or a panel. Resolve via `persona-review` Phase 1 (named / all / `persona-sample` for a relevant subset). The same panel is used every round — switching panels mid-run makes the score incomparable.
- **The objective** — what "better" means: more would-convert, clearer value prop, fewer bounces, a specific persona's approval. This defines the score (below).
- **Round budget (cap)** — how many rounds, max. **Ask if unspecified**; default 5. This is the user's explicit control over how long it runs.
- **Patience** — how many no-improvement rounds to tolerate before stopping. Default 2.
- **Constraints (what not to change)** — fixed claims, brand voice, legal lines, layout. Passed into every round so edits don't drift off-brief. (Critical for the Codex four-part goal.)
- **Success target** (optional) — e.g. "zero blockers and panel mean >= 6/7." Default is that target.

## The optimization loop

### Each round
1. **Score** — run the panel on the *current* version (one subagent per persona, the `persona-review` reviewer contract: first-person, references + confidence, `[BLOCKER]/[IMPORTANT]/[NIT]` severity). Each persona also gives a **would-act score 1–7** ("how well does this land / how likely would you act") per `persona-ask` Likert handling. Aggregate to a **panel score** (confidence-weighted mean of would-act) plus a **blocker count**.
2. **Diagnose** — synthesize the panel's curated change list (as `persona-review` Phase 5): the highest-leverage, most cross-persona-supported blockers first.
3. **Change** — apply the **top 1–3 changes only**, minimal and targeted. Small, attributable edits beat a rewrite — a rewrite makes it impossible to tell what helped and invites thrash.
4. **Keep-best** — record the version and its score. If this round's score beat the best-so-far (by more than the noise threshold), this is the new best. If it regressed, **revert the working copy to the best version** before the next round — never build on a step backwards.
5. **Log the round ledger** — print one line so the loop (and the goal evaluator) can see where things stand:
   ```
   Round k/N · panel 5.4/7 (best 5.4) · blockers 2 · no-improve 0/2 · decision: continue
   ```

### What counts as "improvement" (don't chase noise)
Persona simulations are noisy and variance-compressed — a 0.1 wiggle is not signal. Count a round as an improvement only if the panel score rises by **≥ ~0.3 / 7** *or* the blocker count drops. Otherwise it's a no-improvement round and the streak increments. Say this threshold out loud in the ledger reasoning so the user can audit it.

## Stopping rules — done vs. stuck

After each round, stop when **any** of these holds (state which one, and the round count, before the final output):

- **Converged (win).** Zero blockers and panel score ≥ the success target. The panel accepts it. This is the goal. (Analogous to `ask-team` stopping when positions are stable and no answerable question remains.)
- **Plateaued (diminishing returns).** No improvement for `patience` rounds running (default 2) — "several changes in a row haven't moved it." Stop and return the best version. The score has found its ceiling for edit-level changes.
- **Hardened (stuck — structural).** The *same* blocker recurs across rounds despite targeted attempts to fix it, or every new variant gets rejected for the same reason. This is the panel "hardening" against the asset: the problem isn't the wording, it's the offer / positioning / audience fit. Stop early and report it as a **structural finding**, not a copy bug — burning more rounds won't help. (This is the key borrow from `ask-team`'s `hardened` stance: recurrence is a signal to stop, not to push harder.)
- **Budget hit.** Round count reached the cap `N`. Stop and return the best version, noting it may not have converged.

Always run at least one full round before declaring anything. Keep and return the **best** version seen — not necessarily the last one (the last round may have been a reverted regression).

## Output

```
# Persona-goal: <asset> · stopped after <k> rounds (<reason>)

## Best version
The winning version, verbatim (or the file path if edited in place).

## Why it stopped
Converged | Plateaued (no improvement for <patience> rounds) | Hardened (structural — <the recurring objection>) | Budget hit. One or two lines.

## Score trajectory
Round-by-round: panel score, blocker count, and the change applied that round. A compact table or the ledger lines, so the user can see what moved the needle and what didn't.

## What changed and why
The 2–4 edits that actually improved the score, each tied to the persona(s) and finding that drove it.

## If hardened: the structural issue
The objection edits couldn't fix, and what it implies (reposition? different audience? different offer?). This is often the most valuable output.

## Open questions for real customers
What the simulation can't settle — and a warning if the asset has been tuned hard to the panel (see below).
```

Close with the simulation disclaimer.

## Honesty: the overfitting risk (read this)

Iteratively optimizing against a simulated panel is **Goodhart-prone** — you can tune an asset until the personas love it without making it better for real humans, especially since persona simulations under-disperse and can be gamed by language that pattern-matches their docs. Guard against it:

- Prefer **fewer, higher-leverage** changes over many micro-tweaks; stop at the first stop condition rather than squeezing the score.
- A rising panel score across rounds is **directional evidence the edits address stated concerns**, not proof the asset is now good. Say so.
- Recommend a **held-out check**: validate the best version with a real customer (or at least a fresh persona not used in the loop) before shipping. A score optimized against the same N personas that produced it is the most overfit number in the run.

## Cost

Each round ≈ N persona subagents + one synthesis/edit. A 5-persona panel × 5 rounds ≈ 25+ subagent runs. The round cap and the patience/convergence checks exist to bound this — that's the whole point of the stopping logic. Estimate with `persona-research/references/cost-estimator.md` and confirm before a large run. Under the goal feature the loop can run unattended, so the cap matters more, not less — never set the loop running without a round budget.

## Notes

- **Same panel every round.** Changing personas mid-run breaks score comparability. If the user wants a different audience, that's a new run.
- **Edit in place, keep versions.** For file assets, edit the file and snapshot each round into the run dir so "keep-best / revert" is real, not notional.
- **The goal evaluator reads the transcript** (Claude) / **requires evidence** (Codex) — so the round ledger is mandatory, not decorative. No ledger, no checkable stop condition.
- This skill *uses* `persona-review` and `persona-ask`; don't reimplement the panel or the scoring — call into their contracts so grounding (references + confidence) is preserved every round.
