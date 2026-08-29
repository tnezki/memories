# Algebra Notes HTML Structure Reference — Framework v6.16

This is the approved structural reference from the Unit 1 Section 1.1 Notes pilot. It is a course-specific layer on top of Base Notes PM v4.3. Production HTML continues to link only `../../css/base.css` and `../../css/notes.css`. The companion CSS file is a merge/reference artifact, not a third stylesheet.

## Opening sequence

1. Title card.
2. Learning Target + exact I-can list.
3. `Vocabulary / Key Notation Preview` wrapped as `.vocab-preview-section`:
   - term list only (no definitions yet)
   - **Sort the vocabulary.** direction
   - 3 equal columns: **Know for sure | Recognize | Don't know yet**
4. `What's to Come` wrapped as `.notes-wtc`:
   - strong left-rule heading
   - separate `.wtc-instructions` callout beginning **DO NOT SOLVE IT YET.**
   - canonical Bank WTC unchanged
   - configured workspace
5. `Let's Get Started` wrapped as `.skim-section-task`:
   - **Skim the section.** Record what catches your attention before you read closely.
   - three-row table: **What I noticed | What I predict | What I wonder**
6. Before I Can 1, use `.close-reading-instructions` inside the same `.notes-ican-start` wrapper as the I-can heading and opening reading.

## I-can cluster

Use the exact I-can statement as the visible cluster heading. A typical cluster may contain:

- developed reading/representation (usually 3–4 paragraphs in Algebra)
- immediate `.notes-discuss-task` after each substantial reading
- one or more substantive `.math-notes` reference blocks when useful
- canonical Examples/YTIs in instructionally natural order
- optional later one-question discussion checkpoint

Do not force one identical cycle per Bank pair.

## Stop and Discuss

Main post-reading discussion: 2–3 questions. Usually 1–2 are direct/text/vocabulary/representation checks and the remaining question(s) require conceptual inference or connection. Later checkpoints within the same I-can are normally one focused question. Prompt + workspace remain together when they fit.

## Math Notes

Prefer concrete reference artifacts. For multiple-representation ideas, a 2×2 `rep-grid` can show **Graph / Equation / Table / Context** around one coherent relationship. More useful Math Notes are allowed; teacher can skip.

## Example / YTI wrapper

Wrap title + canonical problem/representation + 2.0in workspace as `.notes-task`. Visible numbering follows rendered teaching order; canonical Bank identity stays in metadata such as `data-source-id`.

## Current sizing

- default workspace: 2.0in
- graph max: 2.52in × 2.52in
- I-can heading: 13pt
- compact 2-column tables: intrinsic/minimum useful width, centered, 50/50 columns
- final miscellaneous blank workspace after Common Mistakes: 9.0in and starts on a new page
- Summary: no dedicated workspace in current Algebra layout

## Approved typography baseline

- normal prose, lists, tables, and captions: 9pt
- Learning Target / Vocabulary / Summary / Common Mistakes headings: 18pt
- Example / You Try It headings: 13pt
- I-can heading: 13pt
- title card: 7.5pt kicker, 21pt main title, 10.5pt subtitle, 9pt quote
- Math Notes: 8.5pt label, 10.5pt title
- Stop and Discuss: 9pt body, 9.5pt label
- What's to Come and Let's Get Started remain 20pt to preserve strong section hierarchy

These are the approved Unit 1 pilot values. Do not mix them with older +2pt pilot values.

## Keep-together rule

Use `break-inside: avoid-page` / `page-break-inside: avoid` on meaningful wrappers so a heading is not stranded from its table/graph/question/workspace when the whole block can fit on the next page. Do not try to force an actually-too-tall block onto one page.


## Canonical graph markup — required

A canonical Bank graph may keep its Bank image bytes, but the Notes HTML must apply the Notes figure class so the approved sizing actually takes effect:

```html
<figure class="notes-graph">
  <img src="figures/example.png" alt="descriptive accessibility text">
</figure>
```

Do **not** add a visible `<figcaption>` merely to name or describe the graph. Do not add a decorative graph title. Preserve labels that are mathematical data: axis names, units, tick values, legends, or point/function labels needed by the task. New Notes-specific graph-tool calls should normally use `title=''`.

A bare `<figure><img ...></figure>` is a layout failure for an Algebra Notes graph because the 2.52in sizing rule will not fire.

## Compact two-column task-table markup — required when eligible

For simple x/y or other two-column data tables whose contents do not need page width:

```html
<table class="compact-table">
  <colgroup>
    <col class="half-col">
    <col class="half-col">
  </colgroup>
  ...
</table>
```

The table stays 50/50 internally but uses only the minimum useful overall width and remains centered. Do not use this compact form for genuinely wide/multiline tables that need more room.
