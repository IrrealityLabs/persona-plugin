---
name: persona-tree-test
description: Test information architecture / navigation with the personas — given a hierarchical sitemap or menu structure and a list of tasks, see where each persona would click to complete each task. Outputs per-task success rate, average path depth, and the wrong-path patterns that indicate IA problems. Use when the user says "/persona-tree-test", "tree test", "test my navigation", "would my personas find X in this menu", "validate my sitemap", or has an IA/navigation question.
---

# Persona Tree Test

Tree testing evaluates information architecture independent of visual design. Personas are given a text-only hierarchy (menu, sitemap, doc TOC) and a task ("where would you click to <goal>?"), and they navigate the tree by following labels. Output: where they went, whether they got there, and what wrong turns reveal about labels that don't match user mental models.

## When to use vs. alternatives

- Use `persona-tree-test` to validate that a hierarchy *labels* its sections in ways users would predict — pre-build for new IA, post-launch when search/navigation feedback suggests problems.
- Use `persona-user-test` when you want full-UI reactions (visuals, layout, friction in actual flow).
- Use `persona-survey` for opinion-based feedback on IA labels.
- Use `persona-max-diff` for ranking labels by clarity or appeal.

## Sample size

- **Sweet spot:** 5–10 personas. Below 5, the per-task success rates aren't meaningful; above 10, returns diminish for IA detection.
- Default: all personas if ≤8; else `persona-sample` for 6 with the product domain as topic.

## Inputs

- **Tree** — the hierarchy to test. Represented as nested text:
  ```
  Home
  ├── Products
  │   ├── Hardware
  │   ├── Software
  │   └── Services
  ├── Pricing
  ├── Resources
  │   ├── Documentation
  │   ├── Tutorials
  │   └── Community
  └── About
  ```
  Or as a structured JSON / YAML if the user prefers. Trees with 8–80 nodes are testable; smaller is trivial, larger is fatiguing.

- **Tasks** — 3–10 specific tasks framed as user goals. *Not* navigation-instruction phrasing — say "you want to find pricing for the enterprise plan," not "find the Enterprise Pricing page."

- **Task answers** — for each task, which node(s) in the tree are the "correct" answer(s). Multiple correct nodes is fine (e.g. "you could find this under either /pricing or /products/software").

## Workflow

### Phase 1 — Validate the tree and tasks

- The tree should be the *actual* labels users would see (sidebar labels, menu items) — not internal nicknames.
- Tasks should be goal-oriented, not navigation-instruction-shaped. "Find out how much the team plan costs" is good; "Click on Pricing" is testing nothing.
- Each task should have at least one correct answer node identified by the user. If the user can't say where the answer lives, the tree-test isn't ready — first decide what's where.

### Phase 2 — Per-persona task fan-out

Spawn one subagent per persona, in parallel. Each prompt:
- Persona doc path.
- The full tree.
- All tasks (in randomized order per persona).
- For each task: instruction to navigate the tree by picking labels at each level, recording the path. They can backtrack at most once per task ("I'd click X, but if I didn't find it I'd go back and try Y").
- `persona-ask` reviewer contract.
- Tree-test response format below.

Tree-test response format:
```
## Task 1: <task statement>
**Path I'd take:** Home > <child> > <grandchild> > ...
**End node:** <where I'd stop and expect to find the answer>
**Confidence I picked right:** [high|medium|low]
**Reasoning:** one sentence on why this label looked like the right turn at each fork.
**Backtrack** (if any): "If <node> wasn't it, I'd back up and try <alternative>."

## Task 2: ...
...
```

### Phase 3 — Score paths

For each (persona, task) pair, compare the chosen end-node to the correct-answer set:

- **Direct success** = ended on a correct node, no backtrack.
- **Success with backtrack** = ended on a correct node, but used the backtrack.
- **Wrong** = ended on an incorrect node, no backtrack reached a correct one.
- **Lost** = backtracked but still ended on an incorrect node.

Per task, compute:
- **Success rate** = (direct + with-backtrack) / total personas
- **Direct success rate** = direct / total personas (the stricter measure)
- **Top wrong destination** = the incorrect node most personas landed on

Per persona:
- Tasks they succeeded on, struggled with, failed.
- Whether they used backtrack a lot (signals the tree's first-level labels are misleading them).

### Phase 4 — Synthesize

```
# Tree test: <tree, short>

## Overall success
- N tasks tested, M personas each.
- Average direct success: X%
- Average success (with backtrack): Y%

## Per-task results
| Task | Direct success | With backtrack | Top wrong destination |
|---|---|---|---|
| Find pricing for team plan | 6/6 (100%) | 6/6 | — |
| Find API documentation | 2/6 (33%) | 4/6 (67%) | /Resources/Tutorials |
| ...

## Where the tree breaks
For each task with direct success < 60%: the wrong-destination pattern. e.g. "4 of 6 personas went to /Resources/Tutorials looking for API docs. The 'Documentation' label is being read as user-guide content, not API reference. Consider renaming or splitting."

## Confusing labels (cross-task patterns)
Labels that lost personas across multiple tasks. These are the highest-leverage rename candidates.

## First-click correctness (where the test went sideways first)
For each task with low success: where did personas branch wrong on the first click? First-click errors propagate — fixing the top-level label often fixes downstream task failures cascade-style.

## Recommendations
3–5 concrete IA changes — renames, moves, splits, merges — prioritized by how many task-failures each would resolve.

## Sample-size caveat
"N=<N> personas; tree-test results are reliable for first-click direction even at small N (signal is strong), but per-task success rates are *directional* below ~10 personas."
```

## Notes

- **First-click accuracy is the gold-standard tree-test metric** — research consistently shows it predicts real-user task success better than full-path success. Surface first-click error patterns specifically.
- The tree-test format is text-only by design. If a persona says "I'd want to see a search bar at the top," they're right but they're also off-method — note it as a finding, don't re-run with search included.
- A task with 100% success on a deep path probably doesn't need testing — pull it from the next round and replace with a task users actually have trouble with based on real-world signal.
- Re-running after IA changes is a primary use case. Save the tree and task set so before/after success rates are directly comparable.
- Tree tests with personas are *useful for label-clarity* even where real-user tree tests would also detect visual-design issues. Use this method for label and structure decisions, not for visual/interaction decisions.
