# District Graph Rendering Standard

STATUS: REQUIRED FOR DISTRICT TOOLS THAT GENERATE MATHEMATICAL GRAPHS  
VERSION: district-graph-rendering-standard/1.1  
DATE: 2026-09-20

This standard keeps mathematical graphs consistent across district tools and prevents each request builder, course, or artifact from inventing its own graph renderer or print darkness.

## 1. One canonical graph authority - HARD

At request/build time, resolve the current registered graph tool from:

`Tools/MANIFEST.json -> tools.graph_tool`

The current canonical entrypoint is:

`Tools/graph_tool.py`

`Tools/graph_tool.py` is intentionally **self-contained**. It consolidates the formerly layered v12/v13/v14 behavior into one runtime. New builds must not require a versioned graph-tool dependency chain.

Do not hard-code a versioned graph-tool filename in a new district tool, course framework, request package, PM, or artifact. Resolve the current tool through `Tools/MANIFEST.json`.

## 2. Request-package rule - HARD

When a response builder needs local graph generation capability, package exactly:

- the current `Tools/MANIFEST.json` registry snapshot; and
- the single file resolved by `tools.graph_tool`.

Do not package retired versioned graph-tool source files merely because they remain in Git history or temporarily remain in the repository during migration.

The request ZIP should therefore expose one graph runtime, not several apparent graph-tool versions.

## 3. Use the registered tool - HARD

When the registered graph tool supports the required mathematical graph type, use it directly.

Do not replace a supported graph with:

- hand-built coordinate SVG;
- CSS axes;
- approximate line art;
- generative imagery;
- an improvised plotting style copied from an old artifact.

A deterministic custom SVG/HTML representation is appropriate only when it is not owned by the graph tool, such as a ratio table, double number line, simple shape array, scale drawing, or exact non-Cartesian instructional diagram.

## 4. Blank Cartesian construction surfaces are graph-tool output - HARD

A blank coordinate plane is still a mathematical graph and is owned by the registered graph tool.

For student tasks such as **graph an equation**, **graph an inequality**, **plot a relation**, **draw a transformed image**, or any other construction-on-axes task, generate the student surface with the registered tool rather than drawing a second browser/SVG grid.

Canonical blank-window pattern:

```python
fig, ax = plt.subplots(...)
graph_tool.make_window_graph(
    ax,
    [],          # no plotted relation in the student view
    xmin, xmax,
    ymin, ymax,
    title="",
    xlabel="x",
    ylabel="y",
)
fig.savefig(..., format="svg", bbox_inches="tight")
```

Passing an empty `functions` list intentionally produces the same canonical grid, axes, arrows, tick treatment, labels, typography, spacing, and approved print weights without revealing the relation the student is supposed to construct.

For the answer key, use the same bounds/scale and the graph tool again with the completed mathematical relation or construction overlay.

A browser may resize the completed SVG asset geometrically. It may not redraw the axes/grid in a different style.

## 5. Teacher-approved Cartesian print weights - HARD

For full-size Cartesian graphs, preserve the teacher-approved 2026-09-18 printed line-weight standard:

- grid: **0.6 pt**, `#aaaaaa`
- axes and axis arrows: **1.8 pt**, `#222222`
- plotted relation: **2.0 pt**
- major ticks: **1.2 pt**
- relation exit arrows: **1.5 pt** when used

Compact multi-panel graph types retain the canonical graph tool's proportional lighter styling.

Do not thicken or thin these through tool-specific CSS or ad hoc SVG overrides.

## 6. Resize geometry, not stroke weights - HARD

When a teacher changes graph size, scale the completed graph's layout geometry/width. Do not change grid, axis, relation, or tick stroke widths to simulate resizing.

Graph size controls must be independent from workspace size unless a tool-specific contract explicitly says otherwise.

## 7. Accuracy / answer-neutrality - HARD

Every graph must be checked for the actual mathematical job:

- axis ranges and scale;
- tick values;
- labels and units;
- plotted points/curves;
- intercepts/asymptotes/endpoints when relevant;
- readable placement;
- answer-neutrality when students are supposed to construct the graph themselves.

If graph construction is the assessed skill, provide only the needed blank axes/grid/data/scaffold rather than the completed answer graph.

## 8. Assets and QA - HARD

- Prefer crisp SVG when practical; PNG is acceptable when appropriate.
- Store generated graph assets under the tool's graph asset folder, normally `assets/graphs/`.
- Record the canonical graph tool path/entrypoint used and an accuracy check in `data/qa.json`.
- For every Cartesian graph asset, record its renderer as the registered graph tool.
- For a student construction surface, also record that the asset was generated as an answer-neutral blank window with an empty relation list.
- PASS is not allowed when a required supported graph bypasses the registered graph tool, is mathematically inaccurate, uses the wrong full-size Cartesian print weights, or uses an improvised SVG/CSS/canvas coordinate plane.

## 9. Course-framework rule

Course frameworks may document graph capabilities and course-specific usage, but they do not own a separate graph engine. Their graph-tool manifests should point back to `Tools/MANIFEST.json` / `Tools/graph_tool.py` rather than maintaining competing course copies as current authority.
