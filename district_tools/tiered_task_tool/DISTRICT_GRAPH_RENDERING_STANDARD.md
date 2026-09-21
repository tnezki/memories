# District Graph Rendering Standard

STATUS: REQUIRED FOR DISTRICT TOOLS THAT GENERATE MATHEMATICAL GRAPHS
VERSION: district-graph-rendering-standard/1.2
DATE: 2026-09-20

## 1. One canonical graph authority - HARD

At request/build time, resolve the current registered graph tool from `Tools/MANIFEST.json -> tools.graph_tool`. The current canonical entrypoint is `Tools/graph_tool.py`, and it is self-contained.

Do not hard-code or package retired versioned graph-tool chains.

## 2. Request-package rule - HARD

Package exactly the current `Tools/MANIFEST.json` snapshot and the single file resolved by `tools.graph_tool`.

## 3. Use the registered tool - HARD

When the registered tool supports the required Cartesian graph, use it directly. Do not replace it with hand-built coordinate SVG, CSS axes, approximate line art, generative imagery, or a copied legacy style.

Deterministic custom SVG/HTML is appropriate only for representations not owned by the graph tool, such as ratio tables, double number lines, simple arrays, exact non-Cartesian instructional diagrams, or similar structures.

## 4. Blank Cartesian construction surfaces are graph-tool output - HARD

Student construction-on-axes tasks use the registered graph tool with an empty relation list so the grid/axes geometry and print weights remain canonical without revealing the answer.

For answer keys, use the same bounds/scale and the graph tool again with the completed relation.

## 5. Teacher-approved Cartesian print weights - HARD

For full-size Cartesian graphs preserve:

- grid: 0.6 pt, `#aaaaaa`
- axes: 1.8 pt, `#222222`
- plotted relation: 2.0 pt
- major ticks: 1.2 pt
- relation exit arrows: 1.5 pt when used

Do not alter these through tool-specific CSS.

## 6. Worksheet / Quick-Check visual geometry - HARD

Use a clean bounded grid, dark straight axes through zero when in range, numeric labels adjacent to axes, no duplicate origin zero, and no oversized decorative axis-end arrows. Omit x/y labels when they add clutter. Preserve mathematically faithful bounds/scale.

## 7. Resize geometry, not stroke weights - HARD

When graph size changes, scale the completed graph geometry. Do not change stroke weights to simulate resizing.

## 8. Accuracy / answer-neutrality - HARD

Check axis ranges, scale, labels/units, points/curves, intercepts/asymptotes/endpoints where relevant, readable placement, and answer-neutrality for student construction tasks.

## 9. Assets and QA - HARD

Prefer SVG when practical. Store graph assets under `assets/graphs/`. Record the registered renderer and an accuracy check in `data/qa.json`. PASS is not allowed when a required supported graph bypasses the registered tool or is mathematically inaccurate.
