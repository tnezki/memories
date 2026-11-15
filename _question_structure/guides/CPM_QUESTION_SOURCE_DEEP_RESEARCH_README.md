# CPM Question Source Research - Deeper Pass (2026-11-15)

**Status:** Source research and question-structure design candidates only. This does **not** update any CPM question bank or change any review data.

## How this fits the original catalog

- Earlier catalog: `catalogs/cpm_reference_question_ideas_20261115.json` (42 first-pass ideas).
- This supplement: `catalogs/cpm_question_structure_deep_research_20261115.json` (111 deeper evidence-task ideas).
- The canonical 390-family library remains authoritative. Many of these proposals **enrich existing families** rather than create any new family. Do not make a question slot for each entry.

## Passes completed

1. **Read sources:** visually inspected saved DeltaMath example pages, inspected Kuta procedural worksheet types, sampled Exeter problem-centered texts, and read DeltaMath topic inventories. The source registry records confidence and exact limitations.
2. **Extract structures:** recorded student action, representation, primary variation axes, three mathematical difficulty stages, misleading shortcuts, and source reference for each candidate.
3. **Reconcile:** candidate IDs checked against existing base, Algebra 1, Geometry, and advanced mathematical family contracts. All candidates still need exact CPM lesson and Assessment Plan alignment.

## By course

| Course | Deeper candidates | High priority | Existing family matches | Needs canonical crosswalk |
|---|---:|---:|---:|---:|
| CC1 | 16 | 6 | 15 | 1 |
| CC2 | 14 | 4 | 14 | 0 |
| CC3 | 14 | 6 | 14 | 0 |
| Algebra 1 | 15 | 9 | 15 | 0 |
| Geometry | 13 | 4 | 13 | 0 |
| Algebra 2 | 20 | 4 | 20 | 0 |
| Precalculus | 19 | 3 | 19 | 0 |

## The strongest cross-course lessons

- **Same skill, different evidence:** reverse unknowns, choose representation, find a mismatched entry, analyze a specific incorrect solution, and explain a physical meaning where appropriate.
- **CPM first:** lesson targets decide bank placement; sources are design references. Actual textbook Review & Preview remains authentic.
- **Three levels remain useful** when they reflect distinct mathematical demands, but number of families/variants is not capped.
- **Variation must be meaningful:** numerical swaps can support fluency, but higher-value refreshes vary givens, unknown quantity, representation, misconception and dependency path.
- **Proof of quality:** independent answer verification, target-specific diagrams, clean symbolic notation, no answer leaking through graphs, and teacher approval.

## High-priority changes for the next Chapter 3 review

- Algebra 1: exponent law recognition *after* simplification, reverse exponent products, actual distributive expressions, equation construction without supplying it, full function notation in every refresh.
- Lower courses: missing information from ratio tables and double number lines, reversing a scale relationship, meaningful story-to-graph tasks.
- Higher courses: graph/table/rule connections with correct endpoint, domain, and excluded-value restrictions.

## Source confidence is not universal

`visually_inspected` means selected pages were checked; it is not a full scan. `pdf_text_checked` means an excerpt was inspected, but figures may still need visual QA. `topic_inventory_text_checked` indicates topic names only. `folder_inventory_only` indicates no question-level evidence; do not cite as though pages were read. The Glencoe Course 3 PDF gave cover-only text.

## Steps before turning a candidate into a question bank family

1. Choose a course and exact lesson; read original lesson and Assessment Plan learning focus.
2. Match candidate with **existing** canonical family and current bank IDs; avoid duplicates.
3. Author representative Level 1 / 2 / 3 tasks with correct mathematical structure.
4. Generate additional variations only where they preserve evidence and maintain valid answers.
5. Independently verify solutions, notation, diagrams, selected-response distractors, and rendering.
6. Review with the teacher Good / Needs Work / Bad UI before allowing assessment use.

## Transfer details

Files in this transfer are **new supplemental research files** under `memories/_question_structure/`, created via the Local Only Curriculum Transfer schema 3. It does not replace the earlier research JSON; this makes installation safe whether or not the first-pass catalog was previously installed.

### CC1: priority candidates

- **DEEP-001 Separate part-to-part from part-to-whole ratios:** Choose numerator/denominator according to named sets and use total only when required. (DM6R, DM7; RATIO_VISUAL_COUNTS).
- **DEEP-003 Recover an original batch from a changed serving count:** Solve recipe scaling backwards rather than only multiplying to a larger serving count. (DM6R, DM7; FRAC_RECIPE_SCALE).
- **DEEP-004 Locate the missing anchor on a double number line:** Determine original unit or scale where neither axis has consecutive marked multiples. (DM7; RATIO_DOUBLE_NUMBER_LINE).
- **DEEP-005 Detect a broken proportional table:** Identify one inconsistent entry and replace it to preserve a fixed multiplicative rule. (DM7; RATIO_TABLE_COMPLETE, RATIO_ERROR_ANALYSIS).
- **DEEP-007 Distinguish a balance model from its equation:** Read group/constant counts, write equation, then solve without the equation being supplied. (DM6V; EQ_BALANCE_MODEL).
- **DEEP-010 Trace distributive area-model factors:** Complete factor, cell and total representations without writing the completed products in the empty work cells. (KDISTR; EXPR_EQUIVALENT_DISTRIB).

### CC2: priority candidates

- **DEEP-017 Scale factor despite rotation or reflection:** Match correct corresponding sides and recover transformation scale. (DM7; SCALE_FACTOR_FIGURES, CORRESPONDING_PARTS).
- **DEEP-018 Recover a preimage dimension:** Given enlarged output and factor, determine original side or perimeter. (DM7; SCALE_CORRESPONDING_SIDE).
- **DEEP-019 Distinguish length factor from area factor:** Find area ratio of similar rectangles/triangles after linear scale is known. (DM7, EX2; SCALE_DRAWING_DISTANCE_AREA).
- **DEEP-020 Complete a partly plotted dilation:** Complete image from one or two anchored vertices, with accurate gridded construction space. (DM7; DILATION_GRID).

### CC3: priority candidates

- **DEEP-031 Derive a linear rule from nonconsecutive table points:** Determine both change and initial value without x=0 being listed. (DM8; LINE_EQ_FROM_REP, FUNC_LINEAR_TABLE).
- **DEEP-032 Explain meaning of a graph point using axes:** Match a point to a full context statement including both quantities and units. (DM8; FUNC_GRAPH_STORY).
- **DEEP-033 Compare rates across graph and table:** Select smallest/largest signed change using consistent units across representations. (DM8; SLOPE_FROM_GRAPH, SLOPE_FROM_TWO_POINTS).
- **DEEP-034 Build a changing-rate graph from timed stages:** Plot cumulative totals from initial amount and sequential rates; do not restart at zero after each interval. (DM8; FUNC_PIECEWISE_CONTEXT_GRAPH).
- **DEEP-036 Decide proportionality by intercept versus ratio:** Distinguish y=kx from y=mx+b with nonzero b across multiple displays. (DM8; FUNC_PROP_GRAPH_K, LINE_DIRECT_VARIATION).
- **DEEP-038 Work in both directions with graph and equation:** Given graph find rule, then given rule identify a graph feature not already marked. (KGRAPH, DM8; LINE_EQ_FROM_REP).

### Algebra 1: priority candidates

- **DEEP-045 Classify exponent law only after actual simplification:** Simplify expression, then select property used; property list includes upcoming laws as distractors without using them in computation. (KEXP; EXP_RULES).
- **DEEP-046 Reverse an exponent product:** Given simplified monomial, construct two nontrivial factors whose product matches it. (KEXP; EXP_RULES).
- **DEEP-047 Differentiate product, quotient and power of power:** Choose/perform only the law matching given expression, including parentheses placement. (KEXP; EXP_RULES).
- **DEEP-049 Complete a genuine generic rectangle product:** Connect factor labels, blank cells, and total; make workspace sized for handwritten answers. (KPOLY, KDISTR; POLY_MULT).
- **DEEP-050 Undo signed distribution with like terms:** Solve equations that actually display unexpanded factors and require meaningful collecting. (KLIN, KDISTR; EQ_MULTI_STEP).
- **DEEP-051 Model and solve a two-cost story:** Construct fixed+variable equation from context, identify unknown from wording, solve then interpret unit. (DM8, KWORD; EQ_CONTEXT_WRITE_SOLVE).
- **DEEP-053 Compare numerical value and input from function notation:** Evaluate f(a) and determine x from f(x)=b as different evidence jobs, retaining notation. (DM8; FUNC_EVALUATE_FORMULA, FUNC_FIND_INPUT_FOR_OUTPUT).
- **DEEP-054 Diagnose a distributive solution step:** Show a specific mathematical error, identify first incorrect step, and correct it. (KDISTR; EXPR_EQUIVALENT_DISTRIB).
- **DEEP-058 Select proper equation morphology at fixed complexity:** Rotate equivalent evidence tasks across ax+b=c, b-ax=c, rational coefficient, variable-both-sides without fake difficulty. (KLIN; EQ_TWO_STEP, EQ_VARIABLE_BOTH_SIDES).

### Geometry: priority candidates

- **DEEP-060 Map corresponding parts under rotation:** Identify correspondence before computing missing sides; do not assume similar placement means same index. (DM7, EX2; GEO_SIMILAR_PROPORTIONS).
- **DEEP-061 Reject invalid congruence marking claims:** Decide whether marked diagram justifies congruence and name exactly missing condition. (EX2; GEO_CONGRUENCE_CRITERIA, GEO_DIAGRAM_MARKINGS).
- **DEEP-064 Prove a coordinate quadrilateral type:** Use distances and slopes to justify rectangle/parallelogram rather than label by sight. (EX2; GEO_COORD_PROOF).
- **DEEP-065 Compute length and area change under similarity:** Distinguish linear ratio and squared area ratio in a diagram including reverse inference. (DM7; GEO_SIMILARITY).

### Algebra 2: priority candidates

- **DEEP-077 Distinguish removable hole and asymptote:** Factor and cancel expressions while maintaining original domain restrictions. (KPCRAT; RATIONAL_ASYMPTOTES_ADV, RATIONAL_RESTRICT_VALUES).
- **DEEP-088 Model rational asymptotes and holes jointly:** Choose domain, zero, vertical asymptote, and horizontal/slant behavior from one rational function. (KPCGRAPH, KPCRAT; RATIONAL_GRAPH_FEATURES_ADV).
- **DEEP-089 Use polynomial end behavior to vet a context model:** Identify mathematical graph behavior and decide which portion of an applied model is physically credible. (CAR4; POLY_END_BEHAVIOR_ADV).
- **DEEP-091 Construct two rational functions from shared features:** Find two distinct formulas meeting the same hole, asymptote, intercept or range constraints. (CAR7; RATIONAL_GRAPH_FEATURES_ADV).

### Precalculus: priority candidates

- **DEEP-093 Draw endpoint-sensitive piecewise functions:** Graph each piece with exact open/closed endpoint and isolated value conventions. (KPCPIECE; ADV_FUNC_TRANSFORM_DOMAIN_RANGE).
- **DEEP-099 Translate exact unit-circle ratios among angle types:** Use signed coterminal degrees and radians with quadrant reasoning; no calculator. (KPCTRIG; TRIG_UNIT_CIRCLE_EXACT_ADV).
- **DEEP-103 Find rational holes and asymptotes from factorization:** Separate canceled denominator factor from remaining pole and distinguish hole coordinate from x value. (KPCRAT, KPCGRAPH; RATIONAL_GRAPH_FEATURES_ADV).
