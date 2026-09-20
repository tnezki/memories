# GRAPH TOOL CAPABILITY INVENTORY — Algebra 1 Framework

**READ THIS BEFORE INVENTING A NEW FIGURE OR ASSUMING THE GRAPH TOOL CANNOT DO IT.**

Canonical registry: `Tools/MANIFEST.json`  
Authoritative tool: `Tools/graph_tool.py`

Production rule: resolve the canonical tool through the registry, copy the one self-contained runtime into a generated build when local execution is needed, then append only the unit/artifact-specific generation calls. Do not maintain a separate Algebra graph engine.

## Quick capability inventory

| Type | Function | Best uses / notable options |
|---|---|---|
| Standard coordinate plane | `make_standard_graph` | Algebra graphs on the standard -10 to 10 plane; parent functions, transformations, intersections, multiple functions, legends, exit arrows. |
| Custom / blank Cartesian window | `make_window_graph` | Canonical custom two-sided Cartesian window. Pass an empty function list for a blank student construction grid using the Worksheet Builder / Quick Check bounded-grid geometry and approved print weights. |
| Context / modeling graph | `make_context_graph` | Real-world/modeling graphs with custom axis ranges and axis labels; useful when quantities/units matter. |
| Number line | `make_number_line` / `make_number_line_blank` | Inequalities, absolute-value solutions, domain/range; open/closed endpoints, intervals/rays, and blank student number lines. |
| 2x2 graph grid | `make_2x2_grid` | Compare four graphs/examples in a compact grid. |
| 2x1 graph grid | `make_2x1_grid` | Before/after, compare/contrast, function/transformation pairs. |
| 3x1 graph grid | `make_3x1_grid` | Transformation series or three related graphs. |
| 4x1 graph grid | `make_4x1_grid` | Four transformations/parent functions in a row. |
| Rectangle / area model | `make_rectangle_model` | Polynomial multiplication, factoring, generic area/box models. |
| Diamond problem | `make_diamond` | Sum/product Diamonds for factoring and number relationships. Any of the four cells may be blank. |
| Piecewise function | `make_piecewise_graph` | Multiple pieces with domain endpoints, open/closed dots, and arrows. |
| Unit circle | `make_unit_circle_blank` / `make_unit_circle_angles` | Blank unit circle or angle/coordinate variants. |
| 2D inequality/system | `make_inequality_graph` | Linear/nonlinear inequalities and systems with boundary/shading behavior. |
| Trig graph | `make_trig_graph` | Sine/cosine with amplitude, frequency, phase shift, vertical shift, and pi-based axis labels. |
| Bar chart | `make_bar_chart` | Categorical comparisons, surveys, grouped data. |
| Histogram | `make_histogram` | Frequency distributions and data spread. |
| Scatter plot | `make_scatter_plot` | Data analysis, sequences/series, optional linear line of best fit. |
| Hundred grid | `make_hundred_grid` | Percents, decimals, fractions, shaded-part models. |
| Fraction bar / tape diagram | `make_fraction_bar` | Fractions, ratios, part-part-whole relationships. |
| Algebra tiles | `make_algebra_tiles` | Visual algebraic expressions/models using tile representations. |

## Diamond problems: supported variants

The Diamond generator is **not one fixed question type**. Its four cells are:

- **top** = product
- **bottom** = sum
- **left** and **right** = the two factors/numbers

`make_diamond(top, left, right, bottom, ...)` allows **any cell to be `''` (blank)**. This means the Bank can intentionally rotate among useful Diamond forms instead of always asking the same missing-values pattern.

Common supported uses include:

1. Find both side numbers from product + sum.
2. Find product and sum from the two side numbers.
3. Find one missing side number when the other side and product/sum information are shown.
4. Find a missing product from known side numbers.
5. Find a missing sum from known side numbers.
6. Multiple blanks when the given information still determines the intended relationship.
7. Integer/sign variants.
8. Symbolic/algebraic variants such as `x`, `y`, `xy`, or `x+y`.
9. Completed/reference Diamonds for worked-example or structure-reading purposes.

### Algebra authoring rule for Diamonds

Do not assume every Warm-Up Diamond must be the same classic "product and sum given; find the factors" form. Choose the Diamond variant that serves the actual prerequisite/review skill, and map the item to that real skill. Rotation is encouraged when it improves retrieval; forced variety is not required.

## How to use this inventory

Before drawing a figure manually or deciding that a representation is unavailable:

1. Check this inventory.
2. Inspect the corresponding function comments/signature in `Tools/graph_tool.py` when exact parameters are needed.
3. Use the canonical tool whenever a supported type can cleanly represent the intended mathematics.
4. Only build a new figure method when the existing inventory genuinely cannot express the needed representation.

This inventory describes **capabilities**, not quotas. The I-can and instructional purpose determine whether a particular figure type belongs in a question.
