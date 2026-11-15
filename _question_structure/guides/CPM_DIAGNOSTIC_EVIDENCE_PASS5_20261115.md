# CPM Question Structures - Diagnostic Evidence Research (Pass 5)

**Status:** Research only - not a grading, bank, or Portfolio update.

## Why this pass is different

Passes 1-4 catalogued source ideas, meaningful variations, and quality gates. Pass 5 addresses what an incorrect response actually allows us to conclude. **An incorrect answer is not a reliable diagnosis on its own.** It is a reason to inspect work or give a contrasting prompt.

The JSON adds **28 diagnostic profiles** to Pass 4 (four profiles per course). They extend the same 28 canonical-family-aligned variation recipes; **no new canonical family IDs** are created.

## Research method and evidence limit

- Visually reviewed saved DeltaMath grade 6, 7, and 8 pages and earlier grade 4 examples; read selected text from Kuta, Exeter and Carnegie Algebra II sources.
- Cross-referenced their task *architectures* with the canonical 390-family Question Structures registry (165 base + 95 Algebra 1 + 25 Geometry + 62 advanced + 43 Calculus).
- Authored original contrasting probes, worked answer keys, targeted feedback and renderer checks; these are **proposed diagnostic hypotheses, not validated psychometric items**.
- Mappings to exact CPM lesson/I-can goals are still pending. Do not insert these as original CPM Review & Preview items or use them in an assessment until aligned and checked.

## Eight rules for evidence-aware banks

1. Start with the target, evidence job and student action, not with a “good distractor.”
2. Keep separate: family / difficulty / teacher bank-review status / student evidence judgment / grade.
3. A wrong numerical answer can reflect reasoning, arithmetic, reading, transcription, or representation; **do not classify a misconception from one error**.
4. When suspected reasoning matters, follow with a short **independently answerable contrast item** that isolates the suspected error.
5. Selected response can check recognition; it does not prove that a student can construct an equation, model, diagram, or graph.
6. Answer-neutral student visuals are mandatory, including accurate generic rectangles, number lines, geometry and registered Graph Tool graphs.
7. A confirmed error should generate specific teacher-facing feedback and one focused practice step, followed by new independent evidence.
8. No automatic Portfolio grade/movement from question-bank research or from a single multiple-choice distractor.

## Diagnostic workflow for future Assessment Builder / Portfolio

```text
Verified CPM learning target -> canonical family -> task & answer rule
   -> independent student response (may have visible work)
   -> observed evidence (Convincing / Limited / Incorrect / Not observed)
   -> tentative error signature when supported
   -> short contrasting probe at comparable demand
   -> supported / contradicted / unresolved hypothesis
   -> focused feedback + practice + independent reassessment
```

The existing **Good / Needs Work / Bad** bank-review buttons are a *different* rating and must not be repurposed as student evidence labels.

## Course-by-course inventory

| Course | Profiles |
|---|---:|
| CC1 | 4 |
| CC2 | 4 |
| CC3 | 4 |
| Algebra 1 | 4 |
| Geometry | 4 |
| Algebra 2 | 4 |
| Precalculus | 4 |

## Four high-value examples

### Algebra 1 - multiplying powers (P5-013)
Use two different exponential structures: `x^2 * x^5 -> x^7` uses **product of powers** whereas `(a^3)^4 -> a^12` uses **power of a power**. Getting the two rules reversed on two tasks is more informative than a single wrong answer. Students should still simplify before any property multiple choice.

### Algebra 1 - write an equation (P5-014)
For the newly written club example, joining costs `$7`, classes cost `$4` each and total cost is `$31`. Students must produce `7+4c=31`, then `c=6`. Do **not** give that equation in the question. If they divide 31 by 4, probe a different context with a fixed charge to see whether the fee is being omitted.

### CC3 - a plateau is not a zero value (P5-009)
Tank contains `4 L`, gains `2 L/h` for `3 h`, then holds steady for `2 h`: `V(3)=V(5)=10 L`. A graph incorrectly falling to zero when the rate becomes zero needs a second context to distinguish confusion about *rate* from confusion about *amount*. The student must draw the graph on an answer-neutral registered grid.

### Precalculus - rational hole versus asymptote (P5-026)
`(x-1)/((x-1)(x+1))` has a **hole at `(1, 1/2)`** and a vertical asymptote at `x=-1`; cancellation does not restore the excluded input. A second function with a different removable factor checks whether this is a reproducible reasoning issue.

## Alignment to prior research (do not duplicate sources)

Pass 1 gives initial topic ideas; Pass 2 gives deeper evidence tasks; Pass 4 gives 28 variation recipes and renderer checks. This pass attaches one diagnostic profile to each Pass 4 recipe using the same `P4-###` pointer. Exact source coverage is inherited from Pass 4 and supplemented with a source ledger in the JSON.

## What is not yet done

- No items have been installed into active CPM banks or approved for student assessments.
- Source collections were sampled, not exhaustively read; diagnostic mechanisms and feedback are teacher-review hypotheses.
- No statistical analysis of student distractor choices or validated misconception taxonomy has occurred.
- No student information or Portfolio state is carried in the transfer.
- All example question/answer pairs should undergo subject and renderer QA when promoted into a lesson-aligned bank.

## Recommended next implementation checkpoint

Use Algebra 1 Chapter 3 as a pilot. For each confirmed lesson goal, choose a family, keep its student action invariant, test one meaningful wrong-response signature, and verify an answer-neutral follow-up before expanding its variations. Teacher review remains in charge.

### P5-001 | CC1 | `DEC_OPEN_NL`
- Suspected error: A student adds decimal amounts correctly but subtracts by moving right on the number line.
- Confirm: Calculate 4.6 - 1.8; show the direction and total size of your jumps.
- Correct: 2.8; net movement left 1.8 from 4.6 to 2.8
- Independent check: Calculate 3.2 - 0.7; show the jumps.
- Correct: 2.5; left 0.7
- If supported: For subtraction, the signed net jump must match the change from the starting value to the result.

### P5-002 | CC1 | `RATIO_DOUBLE_NUMBER_LINE`
- Suspected error: Student scales one row of a double number line additively, not multiplicatively.
- Confirm: Three notebooks cost $12. Complete the double number line at 6 and 9 notebooks.
- Correct: $24 and $36
- Independent check: Five pens cost $15. What does 10 pens cost? Show matching points.
- Correct: $30
- If supported: Each corresponding pair must keep the same dollars-per-item ratio.

### P5-003 | CC1 | `EQ_BALANCE_MODEL`
- Suspected error: Student removes a quantity from only one side of a balance equation.
- Confirm: A balanced model has two identical bags and three blocks on the left and eleven blocks on the right. How many blocks are in one bag?
- Correct: 4 blocks
- Independent check: Three identical bags and two blocks balance fourteen blocks. Find one bag.
- Correct: 4 blocks
- If supported: Keeping a balance means doing the same operation to both sides.

### P5-004 | CC1 | `PATTERN_INPUT_OUTPUT`
- Suspected error: Student recognizes a shared difference but assumes two growing patterns have different rates.
- Confirm: Pattern A is 2, 6, 10, 14. Pattern B is 5, 9, 13, 17. How do the rates and same-position values compare?
- Correct: Both increase by 4; B is 3 greater at every position.
- Independent check: Given A(n)=4n-2 and B(n)=4n+1, find B(n)-A(n).
- Correct: 3 for every n
- If supported: A constant vertical offset changes values but not the common difference.

### P5-005 | CC2 | `SCALE_FACTOR_FIGURES`
- Suspected error: Student reports the reciprocal scale factor even when the source and image are labeled.
- Confirm: A side of length 6 on Figure A corresponds to length 9 on Figure B. Find the factor from A to B.
- Correct: 3/2
- Independent check: A side of length 4 on Shape P corresponds to 10 on Shape Q. Find the factor from Q to P.
- Correct: 2/5
- If supported: Scale factor is image length divided by original length, in the named direction.

### P5-006 | CC2 | `DILATION_GRID`
- Suspected error: Student translates a figure when asked to dilate from the origin.
- Confirm: Dilate A(2,1) by scale factor 2 about the origin. Give A'.
- Correct: (4,2)
- Independent check: Dilate B(-3,2) by scale factor 1/2 about the origin. Give B'.
- Correct: (-3/2,1)
- If supported: For an origin dilation, multiply both coordinate components by the scale factor.

### P5-007 | CC2 | `RATIO_TABLE_COMPLETE`
- Suspected error: Student extends a ratio table by adding a constant rather than multiplying both quantities.
- Confirm: For the relationship 2 cups concentrate to 5 cups water, which row is invalid: (4,10), (6,15), or (8,18)?
- Correct: (8,18) is invalid; at 8 cups concentrate water should be 20.
- Independent check: Complete a row proportional to (3,7) if the first quantity is 12.
- Correct: Second quantity 28
- If supported: Equivalent ratios scale both quantities by the same multiplicative factor.

### P5-008 | CC2 | `SCALE_DRAWING_DISTANCE_AREA`
- Suspected error: Student multiplies area by the length scale factor, not its square.
- Confirm: A rectangle is enlarged by factor 3 in each direction. Its original area is 6 square units. Find its new area.
- Correct: 54 square units
- Independent check: A square's side doubles from 4 to 8. Compare its old and new areas.
- Correct: 16 to 64 square units; factor 4
- If supported: Length changes by k; area changes by k squared.

### P5-009 | CC3 | `FUNC_PIECEWISE_CONTEXT_GRAPH`
- Suspected error: Student treats a constant interval in a change-of-rate story as a drop to zero.
- Confirm: A tank starts with 4 L, gains 2 L/hour for 3 hours, then stays unchanged for 2 hours. Give its volume at t=3 and t=5.
- Correct: 10 L at both t=3 and t=5
- Independent check: A cart begins 7 m from a sensor, moves away at 1 m/s for 2 s, then stops for 3 s. Give distance at t=5.
- Correct: 9 m
- If supported: Zero rate means horizontal graph, not necessarily zero quantity.

### P5-010 | CC3 | `LINE_EQ_FROM_REP`
- Suspected error: Student uses change in y as slope but omits a nonzero intercept.
- Confirm: For x=0,1,2 the table gives y=2,5,8. Write y as a function of x.
- Correct: y=3x+2
- Independent check: A table has (x,y)=(1,5),(2,7),(3,9). Write its rule.
- Correct: y=2x+3
- If supported: A table defines both the repeated change and the value at x=0.

### P5-011 | CC3 | `SLOPE_FROM_GRAPH`
- Suspected error: Student computes y/x from one point instead of rise/run between two points.
- Confirm: A line passes through (1,3) and (4,9). Find its slope.
- Correct: (9-3)/(4-1)=2
- Independent check: A line passes through (2,1) and (6,9). Find its slope.
- Correct: (9-1)/(6-2)=2
- If supported: Slope compares changes between two points, not the y/x ratio at an arbitrary point.

### P5-012 | CC3 | `LINE_CONTEXT_INTERPRET`
- Suspected error: Student swaps initial value and rate when interpreting a contextual linear function.
- Confirm: A tank has h(t)=18-3t liters after t hours. State the initial amount and rate of change.
- Correct: Initial 18 L; change -3 L/hour
- Independent check: A supply is modeled by s(t)=120-5t. Interpret the 120 and -5 with units.
- Correct: 120 items initially; decreases by 5 items per unit t
- If supported: The constant term describes the starting quantity; coefficient is the signed change per input unit.

### P5-013 | Algebra 1 | `EXP_RULES`
- Suspected error: Student multiplies exponents for a product of like bases.
- Confirm: Simplify x^2 * x^5 and select the property used.
- Correct: x^7, product of powers
- Independent check: Simplify (a^3)^4 and select the property used.
- Correct: a^12, power of a power
- If supported: For the same base multiplied, add exponents; for a power raised to a power, multiply them.

### P5-014 | Algebra 1 | `EQ_CONTEXT_WRITE_SOLVE`
- Suspected error: Student divides total cost by the per-item price without removing the fixed fee.
- Confirm: A club charges $7 to join plus $4 per class. A member spent $31. Write an equation and find how many classes the member attended.
- Correct: 7+4c=31; c=6 classes
- Independent check: A gym charges $10 registration plus $5 per visit. Total paid is $25. Write and solve an equation for visits.
- Correct: 10+5v=25; v=3 visits
- If supported: Remove the one-time charge before dividing by the per-visit rate.

### P5-015 | Algebra 1 | `POLY_MULT`
- Suspected error: Student multiplies only the first and last terms of a binomial product.
- Confirm: Use a blank area model to multiply (x+2)(x+5). Write the four partial products and the total.
- Correct: x^2,5x,2x,10; total x^2+7x+10
- Independent check: Multiply (x+3)(x+4) using a generic rectangle.
- Correct: x^2+7x+12
- If supported: Every row factor multiplies every column factor before combining like terms.

### P5-016 | Algebra 1 | `FUNC_EVALUATE_FORMULA`
- Suspected error: Student evaluates an expression but drops function notation or substitutes only in one occurrence.
- Confirm: For f(x)=2x+3, find f(-2).
- Correct: -1
- Independent check: For g(x)=x^2-4x, find g(-1).
- Correct: 5
- If supported: f(-2) means substitute -2 for every x in the rule for f.

### P5-017 | Geometry | `GEO_SIMILARITY`
- Suspected error: Student decides triangles are not similar because one is rotated.
- Confirm: Triangles have corresponding side lengths (3,4,5) and (6,8,10) in rotated diagrams. Are they similar? State the factor.
- Correct: Yes, SSS similarity; factor 2 from first to second.
- Independent check: Sides (4,6,8) correspond to (6,9,12). Are the triangles similar?
- Correct: Yes; factor 3/2
- If supported: Similarity depends on corresponding angle/side relationships, not how the figure is oriented.

### P5-018 | Geometry | `GEO_TRANSFORM_CONSTRUCT`
- Suspected error: Student recognizes a reflection but cannot construct transformed vertices.
- Confirm: Reflect triangle vertices A(1,1), B(3,1), C(1,2) across the y-axis. Give the image coordinates.
- Correct: A'(-1,1), B'(-3,1), C'(-1,2)
- Independent check: Reflect P(-2,3) across the x-axis.
- Correct: P'(-2,-3)
- If supported: Across the y-axis negate x; across the x-axis negate y.

### P5-019 | Geometry | `GEO_PROOF_TRIANGLE`
- Suspected error: Student assumes any three positive side lengths form a triangle.
- Confirm: Can three segments of lengths 3, 4, and 8 form a triangle? State a specific reason.
- Correct: No; 3+4=7<8
- Independent check: Can 5, 7, and 11 form a triangle? What about 5, 7, and 13?
- Correct: First yes (12>11); second no (12<13)
- If supported: The two shorter lengths must have a sum strictly greater than the longest.

### P5-020 | Geometry | `GEO_SIMILAR_PROPORTIONS`
- Suspected error: Student scales side length and area by the same factor.
- Confirm: Two similar figures have length scale factor 2. If original area is 9 square units, what is new area?
- Correct: 36 square units
- Independent check: A shape has area 4 square units and is enlarged by length factor 3. What is new area?
- Correct: 36 square units
- If supported: Areas scale by the square of the length factor.

### P5-021 | Algebra 2 | `ADV_FUNC_EXTREMA_CONCAVITY`
- Suspected error: Student maximizes the cut size rather than the resulting box volume.
- Confirm: From a 6-by-6 sheet, equal corner squares of side x are removed to fold an open box. Write V(x) and compare V(1) and V(2).
- Correct: V=x(6-2x)^2; V(1)=16, V(2)=8 cubic units
- Independent check: For the same box, determine the feasible interval for x and where the maximum volume occurs.
- Correct: 0<x<3; maximum V=16 at x=1
- If supported: Volume is height times remaining base area; consider the valid dimensions before maximizing.

### P5-022 | Algebra 2 | `RATIONAL_GRAPH_FEATURES_ADV`
- Suspected error: Student thinks sharing asymptotes means two rational functions must be identical.
- Confirm: Give two distinct rational functions with vertical asymptote x=2 and horizontal asymptote y=0.
- Correct: Example: 1/(x-2) and 3/(x-2)
- Independent check: Can 5/(x-2) and -2/(x-2) have the same asymptotes?
- Correct: Yes; both VA x=2 and HA y=0
- If supported: Several functions can share asymptotes without having the same values.

### P5-023 | Algebra 2 | `SEQ_EXPLICIT_ADV`
- Suspected error: Student uses a_n=a_1*r^n and shifts every geometric term by one position.
- Confirm: A geometric sequence starts with a_1=3 and common ratio 2. Write a_n and find a_4.
- Correct: a_n=3*2^(n-1); a_4=24
- Independent check: A sequence has a_1=5 and ratio 3. Find a_3.
- Correct: 45
- If supported: The first term occurs at n=1, so the ratio has been applied zero times then.

### P5-024 | Algebra 2 | `POLY_REMAINDER_FACTOR_ADV`
- Suspected error: Student mixes up the sign in a linear factor and its corresponding root.
- Confirm: Given f(x)=x^2-5x+6 and that x-2 is a factor, give another factor and all zeros.
- Correct: (x-3); zeros 2 and 3
- Independent check: For x^2-7x+12, use the given factor x-3 to determine the other factor.
- Correct: x-4
- If supported: A factor x-a corresponds to root a, and substitution f(a)=0 checks it.

### P5-025 | Precalculus | `ADV_FUNC_TRANSFORM_DOMAIN_RANGE`
- Suspected error: Student reverses the direction of a horizontal shift of a square-root function.
- Confirm: Find domain and range of f(x)=sqrt(x-4)+2.
- Correct: Domain [4,infinity); range [2,infinity)
- Independent check: Find domain and range of g(x)=sqrt(x+3)-1.
- Correct: Domain [-3,infinity); range [-1,infinity)
- If supported: Set the radicand >=0 before writing the domain; read the vertical translation from the outer constant.

### P5-026 | Precalculus | `RATIONAL_GRAPH_FEATURES_ADV`
- Suspected error: Student treats every denominator zero as a vertical asymptote, ignoring removable factors.
- Confirm: For f(x)=(x-1)/((x-1)(x+1)), classify the behavior at x=1 and x=-1.
- Correct: Hole at x=1 with y=1/2; vertical asymptote at x=-1
- Independent check: For g(x)=(x+2)/((x+2)(x-3)), locate hole and vertical asymptote.
- Correct: Hole at x=-2 (y=-1/5); VA x=3
- If supported: Cancel common factors for the simplified rule, but preserve their excluded input values.

### P5-027 | Precalculus | `TRIG_UNIT_CIRCLE_EXACT_ADV`
- Suspected error: Student uses a reference-angle value but assigns the wrong sign by quadrant.
- Confirm: Find sin(5*pi/6) and cos(5*pi/6) exactly.
- Correct: sin=1/2, cos=-sqrt(3)/2
- Independent check: Find sin(7*pi/6) and cos(7*pi/6) exactly.
- Correct: sin=-1/2, cos=-sqrt(3)/2
- If supported: Use reference angles for magnitude and quadrant coordinates for signs.

### P5-028 | Precalculus | `LOG_EXPAND_CONDENSE_ADV`
- Suspected error: Student incorrectly expands log(a+b) as log(a)+log(b).
- Confirm: For positive x,y, expand ln(xy) and say whether ln(x+y)=ln(x)+ln(y).
- Correct: ln(x)+ln(y); the second identity is not generally true.
- Independent check: For x>0, condense ln(x)+ln(5) and expand ln(3x).
- Correct: ln(5x); ln(3)+ln(x)
- If supported: The log product rule applies to multiplication, not to a sum of arguments.
