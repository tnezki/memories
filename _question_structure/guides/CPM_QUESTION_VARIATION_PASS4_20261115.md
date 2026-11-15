# CPM Question Sources — Fourth Pass: Variation and Quality (2026-11-15)

**Status:** RESEARCH ONLY. This package adds supplemental research; it does not change CPM Tools banks, assessments, teacher ratings, or review comments.

## Why this pass is different

The earlier research files hold **42 initial ideas and 111 deeper task candidates**. This fourth pass does **not** claim 28 new question families. It documents **28 worked-out variation recipes** for existing canonical families (four for each of seven courses), with source provenance, same-family invariants, legal changes, three difficulty steps, a concrete verification condition and a failure to catch. It also introduces **16 reusable acceptance gates** and **eight Chapter 3 pilot QA cases**.

## A significant finding in your Kuta archives

Four bundles have many printed parallel forms: 25 items × 50 versions (slope); 53 items × 30 versions (evaluate/solve/graph); 42 items × 50 versions (systems); 50 items × 40 versions (quadratics). The individual numerical versions are helpful for procedural fluency, **but the version number is not a count of genuinely different mathematical question structures**. In the quadratics bundle, multiplying, factoring, solving by factoring and using the quadratic formula are genuinely different student jobs. In the graphing bundle, graph→equation and equation→graph must remain honestly distinguished.

## Sources actually inspected in this pass

- **DeltaMath:** visual pages from prior 4th-, 6th-, 7th- and 8th-grade uploads. Particularly revealing are answer-neutral double number lines, scaled figures even when rotated, graph interpretation, tables to rules, and piecewise graphs. These are structural references, never templates to copy verbatim.
- **Kuta:** direct text inspection of the four large version bundles and targeted exponent, word-problem, inequalities, polynomial, piecewise, graphing, trigonometry and logarithm worksheets.
- **Exeter:** selected problems from Mathematics 1, 2, and 3 showing generalization, counterexamples and dependent reasoning.
- **Carnegie Algebra II:** Skills Practice Chapters 3, 7, 10, illustrating volume functions, rational features and geometric sequence/exponential models.
- **CPM Algebra 1 Chapter 3:** the current review observations are recorded only as future QA test cases; the bank remains untouched.

Not every page has been checked. The JSON source records distinguish **visual page inspection**, **text inspection** and **accessible local originals**.

## Canonical rules reinforced

1. **An evidence job comes before the wording.** Math family ID, student action, response mode, representation, allowed values, and answer rule must agree.
2. **Three difficulty levels do not imply three families or 12 variants.** Different levels change mathematical structure and load; the New Question control at one level must keep the same evidence job and comparable challenge.
3. **Semantic variety has a measurable profile.** Count distinct unknowns, evidence/givens sets, task directions, representations and misconception targets. A long numeric roster alone does not establish it.
4. **No accidental answer exposure.** For construction/graphing/matching/writing tasks, student sees givens and a usable blank surface. Completed graphs, equations or cell products belong in the answer view.
5. **Representations are mathematics.** Draw source-correct corresponding figures, open and closed endpoints, double-number-line anchors, algebraic area cells and registered Cartesian graphs.
6. **Explanations must assess actual reasoning.** Do not turn a duplicate question into a new family by appending “explain/justify.”
7. **Review & Preview is textbook-original.** Keep CPM originals, diagrams, worked examples and multipart structure; number swaps must retain the original student job and have newly checked solutions.
8. **Extensions should transfer.** Add new constraints, create/counterexample challenges or cross-representation reasoning—not longer arithmetic.

## Practical sequence for future bank changes

Use `target → evidence job → canonical family → allowed morphologies → difficulty → legal parameters → independent math/diagram check → final student view → teacher review`.

**Before generating questions:** choose the family and draw a small coverage matrix (which student actions and modes the lesson actually needs). **During generation:** create legal instances with varied primary axes; do not fill an arbitrary quota. **Before release:** run the 16 checks in the JSON; fail closed on hard failures, and show pending status when verified art/solutions cannot be produced. Use the eight Chapter 3 cases as regression tests after the teacher finishes reviewing that chapter.

## Source rights and portability

Reference DeltaMath, Kuta, Exeter and Carnegie question *structures* and mathematical moves only. Do not import third-party wording, complete problems, exact values, diagrams or answer choices into CPM banks. Create original student questions and independently verified solutions. CPM Review & Preview originals are separately sourced and must remain identified as original textbook material.

## Installation / isolation

This package uses the current schema-3 Curriculum Transfer wrapper and creates two files under the approved `memories` root. It does not depend on any earlier package being applied but conceptually supplements the earlier two research catalogs. It contains no private student data and requires no Git action.
