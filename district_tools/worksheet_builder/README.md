# Math Worksheet Builder — Pilot

District teacher tool for building self-contained worksheet requests from reusable canonical math question families.

## Current catalog coverage
- Lower Elementary Math
- Grade 4 Math
- Grade 5 Math
- Grade 6 Math
- Grade 7 Math
- Grade 8 Math
- **Algebra 1**
- Geometry, Algebra 2, Precalculus, and Calculus are next as their reference sets are incorporated.

## Algebra 1 coverage
Algebra 1 adds 91 course-specific canonical families and reuses shared base families where the evidence architecture is genuinely the same. The teacher catalog exposes 12 topic cards: Foundations & Expressions; Equations & Modeling; Inequalities; Functions & Relations; Linear Functions; Systems; Exponents & Exponential Functions; Polynomials & Factoring; Quadratics; Radicals & Rational Expressions; Statistics & Regression; Coordinate Geometry & Right-Triangle Tools.

The Algebra 1 set was inferred from the teacher-supplied parallel DeltaMath forms and cross-checked against Kuta Software's free Algebra 1 catalog for coverage/property options. Source questions are not stored or copied.

## Quality rule
A family name/summary is metadata, not student wording. Every generated item must be a concrete, independently solved instance of its exact canonical family. Curated previews show complete representative problems with the correct graph/model/table/diagram. If no reviewed specimen exists, Preview fails closed.

## Worksheet display standards
Finished adjustable worksheets now use **true page view** on desktop: each visible white sheet is a real US Letter print page, with the same 0.55 in margins and page boundaries that browser Print will use. Refreshing a problem or changing its workspace/graph size must repaginate the version so the screen page breaks stay aligned with print.

For symbolic math, division defaults to a **stacked fraction bar**. The division sign `÷` is reserved for families where that symbol itself is intentional (for example, elementary division notation). Algebraic expressions, exponent rules, rational expressions, and similar work should use MathJax fractions instead of `÷` or an operation slash.

## Workflow
1. Choose one or more grade/course filters.
2. Choose 1–4 parallel versions, difficulty, one/two columns, and optional answer key.
3. Browse/search family cards and inspect previews.
4. Select exact families and quantities.
5. Create the request ZIP; upload it to ChatGPT; open the returned `CLICK_ME.html`.
6. In the adjustable worksheet, use per-problem workspace/visual controls and **↻ New Question** to cycle same-family alternatives before printing.
7. The page frames in the worksheet view are the actual page breaks used for print.

The request ZIP receives a compatibility generator bank merged at runtime from the canonical base library plus Algebra 1 extension, so selected Algebra 1 families travel with their complete generator contracts.
