# District Graph Rendering Standard

STATUS: REQUIRED FOR DISTRICT TOOLS THAT GENERATE MATHEMATICAL GRAPHS
VERSION: district-graph-rendering-standard/1.0
DATE: 2026-09-18

This standard keeps mathematical graphs consistent across district tools and prevents each request builder from inventing its own graph renderer or print darkness.

## 1. Canonical graph authority - HARD

At request-build time, resolve the current registered graph tool from:

`Tools/MANIFEST.json -> tools.graph_tool`

Package the resolved entrypoint and every required behavior-base dependency into the request ZIP when the response builder needs local access to the graph tool.

For the current tool chain, the authoritative entrypoint is `Tools/~graph_tool_v14.py`, with its declared v13/v12 dependencies staged beside it.

Do not hard-code an older graph-tool version in a new district tool when `Tools/MANIFEST.json` points to a newer registered entrypoint.

## 2. Use the registered tool - HARD

When the registered graph tool supports the required mathematical graph type, use it directly.

Do not replace a supported graph with:

- hand-built coordinate SVG;
- CSS axes;
- approximate line art;
- generative imagery;
- an improvised plotting style copied from an old artifact.

A deterministic custom SVG/HTML representation is appropriate only when it is not owned by the graph tool, such as a ratio table, double number line, simple shape array, scale drawing, or exact non-Cartesian instructional diagram.

## 3. Teacher-approved Cartesian print weights - HARD

For full-size Cartesian graphs, preserve the teacher-approved 2026-09-18 printed line-weight standard:

- grid: **0.6 pt**, `#aaaaaa`
- axes and axis arrows: **1.8 pt**, `#222222`
- plotted relation: **2.0 pt**
- major ticks: **1.2 pt**
- relation exit arrows: **1.5 pt** when used

These weights are the approved printed darkness. Do not thicken or thin them through tool-specific CSS or ad hoc SVG overrides.

Compact multi-panel graph types may retain the registered graph tool's proportional compact styling.

## 4. Resize geometry, not stroke weights - HARD

When a teacher changes graph size, scale the completed graph's layout geometry/width. Do not change grid, axis, relation, or tick stroke widths to simulate resizing.

Graph size controls must be independent from workspace size unless a tool-specific contract explicitly says otherwise.

## 5. Accuracy / answer-neutrality - HARD

Every graph must be checked for the actual mathematical job:

- axis ranges and scale;
- tick values;
- labels and units;
- plotted points/curves;
- intercepts/asymptotes/endpoints when relevant;
- readable placement;
- answer-neutrality when students are supposed to construct the graph themselves.

If graph construction is the assessed skill, provide only the needed blank axes/grid/data/scaffold rather than the completed answer graph.

## 6. Assets and QA - HARD

- Prefer crisp SVG when practical; PNG is acceptable when appropriate.
- Store generated graph assets under the tool's graph asset folder, normally `assets/graphs/`.
- Record the graph tool/entrypoint used and an accuracy check in `data/qa.json`.
- PASS is not allowed when a required supported graph bypasses the registered graph tool, is mathematically inaccurate, or uses the wrong full-size Cartesian print weights.
