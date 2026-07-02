# The HTML report — shared spec for every study

Every study in the persona-research family ends by writing **one self-contained
`report.html`** and telling the user the path. The chat synthesis is the summary; the
report is the full, shareable artifact.

## The three rules

1. **Self-contained.** Inline CSS and JS only, all run data embedded in the file. No
   `fetch()`, no CDN, no external fonts or images, no local server. It must open with a
   double-click from the filesystem and still work when emailed to someone.
2. **One file, standard place.** `./.persona-research-runs/<method>-<YYYY-MM-DD>-<slug>/report.html`
   (create the folder; `<slug>` = 2–4 words from the question/asset). Skills that already
   keep their own run folder (market, town, grounded-theory, user-test, presentation,
   multiverse) write `report.html` into *that* folder instead.
3. **Auditable.** Every persona's public answer appears verbatim with its confidence tag;
   grounding references sit in a collapsed `<details>` per persona. A reader can always
   get from a headline number back to who said what and why.

## Contents, in order

- **Header** — the question (or asset tested), method name, date, personas used:
  `N=<n> personas · <method> · <date>`, with the sample-size caveat right there
  (sweet spot vs. actual N; directional vs. robust).
- **Headline** — the one-sentence answer, big. If the study produced a tally, the
  winner/number leads.
- **Tally / results** — the method's aggregate view: distributions, rankings, price
  curves, theme counts. Charts are styled `<div>` bars (or an inline `<svg>`) — never a
  charting library. Show raw counts alongside percentages.
- **Per-persona responses** — one card per persona: slug, confidence tag, their public
  answer (Talking) verbatim, and a `<details>Grounding</details>` with the persona-doc
  references. For multi-round studies, group by round or thread the exchanges.
- **Insights** — the 2–5 takeaways, each tied to the evidence above (theme counts,
  dissenters, outliers). What the user should *do* next, if the study supports it.
- **Footer** — method sweet-spot note, personas list, plugin version, and "simulated
  personas — directional, not a substitute for real research."

Adapt the middle sections to the method (a Van Westendorp shows the four price curves;
a focus group shows rounds; a roast shows the burns) — the header, per-persona cards,
and footer are invariant.

## Skeleton

```html
<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">
<title><Method>: <short question></title>
<style>
  body{margin:0;font:15px/1.5 system-ui;color:#1a1a1a;background:#fafafa}
  main{max-width:860px;margin:0 auto;padding:32px 20px}
  .meta{color:#666;font-size:13px} .headline{font-size:22px;font-weight:700;margin:16px 0}
  .bar{height:14px;background:#4a7dff;border-radius:3px;display:inline-block;vertical-align:middle}
  .card{background:#fff;border:1px solid #e2e2e2;border-radius:8px;padding:14px 16px;margin:10px 0}
  .conf{font-size:11px;padding:1px 7px;border-radius:9px;background:#eef;color:#336}
  details{margin-top:8px;font-size:13px;color:#555} footer{color:#888;font-size:12px;margin-top:32px}
</style></head><body><main>
  <div class="meta">Survey · 2026-07-02 · N=6 personas (sweet spot ~10 — directional)</div>
  <h1><the question></h1>
  <div class="headline"><the one-sentence answer></div>
  <section><!-- tally: rows of label + <span class="bar" style="width:NNpx"></span> count --></section>
  <section><!-- one .card per persona: <b>slug</b> <span class="conf">high</span>
    <p>verbatim Talking</p> <details><summary>Grounding</summary>…</details> --></section>
  <section><h2>Insights</h2><ol>…</ol></section>
  <footer>Simulated personas — directional, not a substitute for real research. persona-plugin v0.6</footer>
</main></body></html>
```

Write the HTML directly (you are the renderer — no build step, no template engine).
Keep it under ~200KB; for very long transcripts, put full text in `<details>` and keep
cards scannable.
