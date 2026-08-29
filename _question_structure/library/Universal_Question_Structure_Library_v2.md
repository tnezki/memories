# Universal Question Structure Library — v2

## Purpose

This library stores **reusable question/task structures**, not canned questions. Each
entry defines the *shape of the reasoning* a task must require — not specific
numbers, contexts, or wording. Any AI instantiating a question from this
library must write new content that satisfies the architecture's constraints;
it must never copy, closely paraphrase, or reuse a source problem's context,
numbers, or phrasing.

No text, numbers, scenarios, or images from any copyrighted source were
reproduced in building this library. Entries were built by identifying
recurring *structural patterns* across sources and writing original
demonstration examples. See each entry's `provenance` field for what informed
it — provenance names a source's general style or documented practice, never
a specific problem.

## Schema

Each architecture entry has these fields:

- **structure_id** — `CATEGORY-DESCRIPTOR-##`
- **applicability** — course/subject tags (Alg1, Alg2, Geo, PreCalc, APCalc, Physics, Chem, Bio, cross-curricular)
- **destinations** — where this is appropriate: Notes, Practice, Warm-Up, Exit Ticket, Blooket, Summative, Formative, PT (Performance Task), Quick Check
- **content types** — the kinds of concepts it fits (e.g., linear models, limits, circuits)
- **response type** — selected-response, short constructed-response, extended constructed-response, graph/diagram production, numeric entry
- **required representation** — equation, graph, table, diagram, prose/verbal, data set, multiple/mixed
- **reasoning architecture** — the actual cognitive task, stated as a rule
- **misconception/distractor strategy** — what a wrong answer would reveal, and how to design distractors (for selected-response) or anticipate errors (for constructed-response)
- **variation axes** — what can be changed across instantiations without changing the architecture
- **DOK range** — Webb levels this architecture can support, and what changes the level
- **Bloom process descriptors** — from Revised Bloom's (Remember/Understand/Apply/Analyze/Evaluate/Create)
- **evidence produced** — what a grader/teacher actually learns about student thinking from a response
- **works well when** — conditions that make this architecture the right choice
- **avoid when** — conditions that make it the wrong choice or a lazy default
- **security suitability** — Practice/Formative-only, or Summative-safe (i.e., resistant to answer-sharing/memorization), and why
- **demonstration example** — one newly-written, non-source-derived instantiation
- **provenance** — general source style that informed the architecture (never a specific copied problem)

---

## 1. Procedural / Fluency

### PROC-SELECT-STRATEGY-01
- **applicability:** Alg1, Alg2, PreCalc, APCalc
- **destinations:** Warm-Up, Practice, Quick Check
- **content types:** any topic with 2+ valid solution strategies (factoring, limits, integration technique)
- **response type:** short constructed-response
- **required representation:** equation/expression
- **reasoning architecture:** Student is given an expression/problem and must first *classify* which strategy applies before executing it — the strategy choice is graded, not just the final answer.
- **misconception/distractor strategy:** distractors represent applying a plausible-but-wrong strategy (e.g., trying to factor when the discriminant is negative, applying the power rule to a composite function instead of chain rule)
- **variation axes:** which strategy family is being discriminated; number of candidate strategies (2 vs. 3+); whether student names the strategy or just uses it
- **DOK range:** 2 (apply known procedure after correct classification) — does not reach 3 unless multiple structurally different problems are bundled and compared
- **Bloom process descriptors:** Apply, and Analyze (classification step)
- **evidence produced:** whether the student has procedure *recognition*, not just execution
- **works well when:** a unit has multiple procedures students conflate (e.g., u-substitution vs. direct integration)
- **avoid when:** there's only one plausible strategy — the classification step becomes fake
- **security suitability:** Formative/Practice only — trivially memorized once strategy-cues are known
- **demonstration example:** "For each expression below, state which method you'd use to find the limit (direct substitution, factoring, or L'Hôpital's Rule) and explain your choice in one sentence. You do not need to evaluate the limit." [3 expressions given, each requiring a different method]
- **provenance:** AP Calculus CED Skill 1.C ("Identify an appropriate mathematical rule or procedure based on the classification of a given expression")

### PROC-MULTISTEP-CHAIN-01
- **applicability:** all math/science courses
- **destinations:** Notes, Practice, Exit Ticket, Quick Check, Summative
- **content types:** any task where an intermediate result is required to obtain the final requested result
- **response type:** short or extended constructed-response; usually one final requested answer
- **required representation:** equation/expression/data/diagram as appropriate, with intermediate work visible when useful
- **reasoning architecture:** the student must determine, calculate, infer, or look up an intermediate quantity/result and then use that result in a later operation, relationship, or formula to answer the final question. Two dependent stages are enough to make a task genuinely multi-step. Multi-step does NOT require two formulas, two labeled parts, or multiple final answers.
- **misconception/distractor strategy:** for selected-response variants, distractors should represent a plausible error in the intermediate result, failure to carry the intermediate result forward, or use of the final relationship before the needed quantity is known
- **variation axes:** number of dependent stages; whether the intermediate result is computed, inferred from a graph/table, measured, or looked up; symbolic vs. contextual setting; whether unit conversion is part of the dependency
- **DOK range:** 2–3. More steps alone do not raise DOK. DOK rises only when the student must decide what intermediate quantity is needed, choose among relationships, or interpret the intermediate result before continuing.
- **Bloom process descriptors:** Apply, Analyze when the student must determine the needed intermediate quantity/relationship
- **evidence produced:** whether the student can connect dependent ideas and carry a meaningful intermediate result into a final solution rather than treating procedures as isolated facts
- **works well when:** the learning target genuinely requires a chain, such as finding volume before density, inferring a constant speed from one trip before predicting another trip, or determining a temperature change before converting that change to another scale
- **avoid when:** a second calculation is appended only to make the problem longer, or when two unrelated answers are requested with no dependency between them
- **security suitability:** Summative-safe with new values/context when the chain itself must be reasoned through
- **demonstration example:** "A cyclist travels 8 miles to school in 30 minutes at a constant speed. At the same speed, how long will a trip of 11 miles take?" The student must first determine or reason from the cyclist's rate, then use that rate to obtain one final time.
- **provenance:** user-defined curriculum rule for meaningful dependent multi-step work; aligned with general chained-procedure structures but intentionally revised so multi-step means dependency, not merely multiple formulas or multiple answers

---

## 2. Representation Transfer

### REPTRANS-TRANSLATE-VERBAL-SYMBOLIC-01
- **applicability:** Alg1, Alg2, cross-curricular
- **destinations:** Notes, Warm-Up, Practice
- **content types:** equation-writing, expression-building
- **response type:** matching or short constructed-response
- **required representation:** prose → equation (or reverse)
- **reasoning architecture:** student must parse a verbal description into correct symbolic structure — the point is correctly identifying operations/order/relationships implied by ordinary language, not solving
- **misconception/distractor strategy:** distractors reverse operation order, misplace which quantity is the unknown, or conflate "more than" language with the wrong operation direction
- **variation axes:** whether student writes the equation from scratch or matches given equations to given descriptions; complexity of the verbal structure (single clause vs. layered clauses)
- **DOK range:** 1–2 (translation is DOK 2 when the sentence structure is non-trivial, e.g. layered comparisons)
- **Bloom process descriptors:** Understand
- **evidence produced:** whether a student can separate mathematical structure from surface wording
- **works well when:** introducing equation-writing, or diagnosing whether errors are conceptual (setup) vs. computational (execution) — pair with PROC problems to isolate which
- **avoid when:** context is too thin to actually require translation (single-step "x plus 3 is 10" type items add no value at DOK 2)
- **security suitability:** Formative
- **demonstration example:** "Match each situation to its equation: (1) A number decreased by 7 is 2 more than half the number. (2) Twice a number, decreased by 7, is 2 more than the number." [give 2 equations, 2 situations, deliberately close in surface wording]
- **provenance:** CPM's "match mathematical sentence to translation" lesson-opener pattern (matching multiple close variants, not a single translate-and-solve item)

### REPTRANS-GRAPH-TABLE-EQUATION-01
- **applicability:** Alg1, Alg2, PreCalc, APCalc, Physics
- **destinations:** Notes, Practice, Summative
- **content types:** functions, relations, motion, any covariational relationship
- **response type:** graph/diagram production, table completion, or short constructed-response
- **required representation:** student produces one representation given a different one (any pairing of graph/table/equation/verbal)
- **reasoning architecture:** requires the student to identify what structural features (slope, intercept, rate, asymptote, concavity) carry across representations and reconstruct them in the new form
- **misconception/distractor strategy:** distractor graphs/tables preserve surface features (e.g., right y-intercept) but get the rate of change wrong, or vice versa
- **variation axes:** which two representations are paired; direction of the transfer; whether the relationship is linear, exponential, quadratic, trigonometric, etc.
- **DOK range:** 2, reaching 3 if the representation given is incomplete/noisy (e.g., a table with unevenly spaced x-values) and the student must first determine structure before transferring
- **Bloom process descriptors:** Understand, Apply
- **evidence produced:** whether a student's understanding of a concept (e.g., "rate of change") is representation-independent or tied to one format
- **works well when:** you want to know if a student has a genuine concept of a feature (slope, limit, period) vs. a procedural trick for one representation only
- **avoid when:** used as pure busywork transfer with no new structural feature to identify (transferring a trivial y = x + 1 gains nothing)
- **security suitability:** Summative-safe with parameter variation
- **demonstration example:** "The table shows the height of a drone over time, but the time values are not evenly spaced. Determine whether the relationship is linear or exponential, and write an equation for it."
- **provenance:** AP Calculus CED Skill 2.C ("Identify a re-expression of mathematical information presented in a given representation"); pattern also present throughout CPM's routine pairing of table/equation/graph for the same model

### REPTRANS-MULTIPLE-SIMULTANEOUS-01
- **applicability:** Alg1, Alg2, PreCalc, APCalc
- **destinations:** PT, Summative
- **content types:** function modeling
- **response type:** extended constructed-response, three-part
- **required representation:** all three of table, equation, graph, produced by the student from the same verbal prompt, with solution required in all three
- **reasoning architecture:** student builds and reconciles three representations of the same model simultaneously and must explain how the solution appears identically (but differently) in each
- **misconception/distractor strategy:** N/A (constructed response); watch for students solving in only one representation and back-filling the others cosmetically without genuine cross-checking
- **variation axes:** context; whether the model is single-variable or a comparison of two models (see MODEL-COMPARE below)
- **DOK range:** 3 (requires students to explain *why* the solution appears consistently across representations, not just produce three separate answers)
- **Bloom process descriptors:** Apply, Analyze
- **evidence produced:** whether a student sees representations as equivalent views of one relationship rather than three disconnected procedures
- **works well when:** capstone/PT tasks where representation fluency itself is the target, not just the underlying algebra
- **avoid when:** the underlying algebra is itself the target skill being newly introduced — layering three representations on a brand-new skill overloads working memory
- **security suitability:** Summative-safe, ideal for PT
- **demonstration example:** see MODEL-COMPARE-TWO-LINEAR-01 demonstration — same task, explicitly requiring table + equation + graph + written reconciliation
- **provenance:** CPM's "represent this problem with tables, equations, and one graph; use each representation to find the solution" task framing (a documented, recurring CPM instruction pattern, not a specific problem)

---

## 3. Model Construction & Comparison

### MODEL-COMPARE-TWO-LINEAR-01
- **applicability:** Alg1, Alg2
- **destinations:** Practice, PT, Summative
- **content types:** linear/exponential growth comparison, break-even, intersection-in-context
- **response type:** extended constructed-response
- **required representation:** equation and graph minimum; table optional
- **reasoning architecture:** two independent real-world processes are each modeled, then compared to answer a question about when/whether they become equal — requires building *two* models before the comparison step, not just solving a given system
- **misconception/distractor strategy:** watch for students solving each model in isolation without ever setting them equal, or answering "which is bigger" using only the starting values instead of the rates
- **variation axes:** linear-vs-linear, linear-vs-exponential (no solution algebraically — requires graphical/numerical estimate), context domain
- **DOK range:** 3 (student must decide how to compare, not just execute a given comparison)
- **Bloom process descriptors:** Apply, Analyze
- **evidence produced:** whether a student understands intersection as "equal outputs," not just "solve the system because that's the unit"
- **works well when:** introducing systems of equations in context, or connecting linear models to exponential ones for growth-rate reasoning
- **avoid when:** the "compare two things" framing is bolted onto a routine system-solving problem without a genuine decision point (e.g., if it's obvious from the setup which grows faster, there's no real comparison happening)
- **security suitability:** Summative-safe with new contexts/rates each version
- **demonstration example:** "A tree is planted at 3 ft tall, growing 1.2 ft/year. A second tree is planted the same day at 2 ft tall, growing 1.6 ft/year. Represent both trees' growth with equations, a table, and a graph. Will the trees ever be the same height? If so, when? Explain how your answer appears in all three representations."
- **provenance:** CPM's recurring two-growth-rate comparison task type (documented pattern across multiple CC Algebra lessons, not a specific problem)

### MODEL-SELECT-BEST-FIT-01
- **applicability:** Alg1, Alg2, PreCalc, Physics, Bio
- **destinations:** Practice, Summative
- **content types:** data modeling — linear vs. quadratic vs. exponential
- **response type:** short constructed-response with justification
- **required representation:** data set (table or scatterplot) → model type + equation
- **reasoning architecture:** student is given data that does not announce its model type and must justify the choice of model family before fitting it
- **misconception/distractor strategy:** distractor models fit the data reasonably well numerically but violate a structural feature (e.g., a linear fit to data with clearly increasing rate of change)
- **variation axes:** which two model families are being discriminated; how "close" the data is to ambiguous (build both easy and hard versions)
- **DOK range:** 3
- **Bloom process descriptors:** Analyze, Evaluate
- **evidence produced:** whether a student can reason about model *appropriateness*, not just curve-fitting mechanics
- **works well when:** you want to prevent the common failure mode of students defaulting to "linear" for every data set
- **avoid when:** the data set has an obvious visual signature that removes the reasoning (a extremely curved scatterplot makes the justification trivial)
- **security suitability:** Summative-safe with new data sets
- **demonstration example:** "A biologist records bacteria population every hour: [table with clearly multiplicative growth]. A student claims a linear model fits well because the differences look 'close to constant.' Determine whether a linear or exponential model is more appropriate, and explain what evidence in the table supports your choice."
- **provenance:** general model-selection framing informed by CPM's "models are usually not perfect representations" framing around line-of-best-fit lessons

---

## 4. Inverse / Reverse Reasoning

### INVERSE-GIVEN-OUTPUT-FIND-INPUT-01
- **applicability:** all math courses, Physics
- **destinations:** Practice, Warm-Up, Summative
- **content types:** any invertible process (functions, equations, physics formulas)
- **response type:** short constructed-response
- **required representation:** equation
- **reasoning architecture:** student is given the result of a process and must work backward to determine the input(s) that produced it, rather than being given the input and asked to compute forward
- **misconception/distractor strategy:** distractors result from applying the forward procedure to the given output instead of correctly inverting
- **variation axes:** whether the inverse is unique or multi-valued (e.g., ±√); which formula/function family
- **DOK range:** 2, reaching 3 when the inverse is non-unique and student must reason about which solutions are valid in context (domain restrictions)
- **Bloom process descriptors:** Apply, Analyze (when domain-restriction reasoning is required)
- **evidence produced:** whether a student's procedural fluency is direction-independent, i.e. a genuine grasp of the relationship rather than a memorized forward algorithm
- **works well when:** following a unit that has only practiced forward computation — this is the natural check for whether understanding is bidirectional
- **avoid when:** the inverse operation is trivial/identical to the forward one (little new reasoning gained)
- **security suitability:** Summative-safe
- **demonstration example:** "An object's height is modeled by h(t) = -16t² + 40t + 5. At what time(s) does the object reach a height of 25 feet? Explain why there may be more than one valid answer, or why one of the two algebraic solutions should be rejected."
- **provenance:** general algebra/physics pattern; domain-rejection reasoning drawn from standard projectile-motion task structure

### INVERSE-WORK-BACKWARD-FROM-GRAPH-01
- **applicability:** APCalc, PreCalc, Physics
- **destinations:** Practice, Summative
- **content types:** derivative/rate graphs, velocity-position relationships
- **response type:** graph/diagram production
- **required representation:** graph → graph (student sketches the "opposite" function)
- **reasoning architecture:** given the graph of a derivative/rate function, student must sketch the graph of the original function (or vice versa) using structural reasoning (sign → increasing/decreasing, zero-crossings → extrema), not by finding a formula
- **misconception/distractor strategy:** common error is copying the shape of the given graph rather than translating its features (e.g., sketching f like f′ instead of using f′'s sign to determine f's behavior)
- **variation axes:** derivative→original or original→derivative direction; simple sign changes vs. concavity reasoning (f′→f″ layer)
- **DOK range:** 3
- **Bloom process descriptors:** Analyze
- **evidence produced:** whether a student has a graphical/conceptual understanding of the derivative relationship independent of algebraic differentiation
- **works well when:** reinforcing that the derivative is a *rate of change relationship*, not just a symbol-pushing operation
- **avoid when:** students haven't yet built the sign-to-shape reasoning explicitly in notes — this architecture assumes that connection has been taught, not discovered cold
- **security suitability:** Summative-safe (graph can vary each version)
- **demonstration example:** "The graph shows f′(x). Sketch a possible graph of f(x), assuming f(0) = 2. Label where f has local extrema and explain how you determined them from the given graph."
- **provenance:** standard AP Calculus "work backward" framing; explicitly named as a sample instructional activity type in the AP Calculus CED (Unit 1, "Work Backward" activity)

---

## 5. Error Diagnosis / Misconception

### ERROR-DIAGNOSE-WORKED-SOLUTION-01
- **applicability:** all math/science courses
- **destinations:** Practice, Formative, Exit Ticket
- **content types:** any procedure prone to a specific, well-documented student error
- **response type:** short constructed-response
- **required representation:** worked solution (given) + prose explanation (produced)
- **reasoning architecture:** student is shown a worked solution containing exactly one error and must locate it, name what went wrong conceptually (not just "it's wrong here"), and produce the correct result
- **misconception/distractor strategy:** the embedded error must be a real, common misconception (sign error in distributing a negative, dropping a constant of integration, treating a rate as a total) — not an arbitrary typo, since typo-hunting doesn't diagnose understanding
- **variation axes:** which misconception is embedded; whether the error is early (cascades) or late (isolated) in the solution
- **DOK range:** 3 (requires evaluating someone else's reasoning, not just executing your own)
- **Bloom process descriptors:** Analyze, Evaluate
- **evidence produced:** direct evidence of whether the student holds the specific misconception themselves, since correctly diagnosing it usually requires not making the same error
- **works well when:** you have identified a specific, recurring class error (e.g., from a prior bank audit) worth targeting directly
- **avoid when:** used generically without a real, documented misconception behind it — becomes an empty "find the mistake" exercise with no diagnostic value
- **security suitability:** Formative-preferred; fine for Summative if the specific worked solution varies
- **demonstration example:** "A student solves 3(x − 4) = 2x + 5 and gets x = 17 by writing: 3x − 4 = 2x + 5, x = 9... [shown work skips distributing the 3 across both terms]. Identify the specific error, explain what misconception likely caused it, and give the correct solution."
- **provenance:** general error-analysis architecture; matches the "diagnose flawed reasoning" pattern flagged as needed in the Physics bank audit (see [[physics-curriculum]] pass_bad_questions system)

### ERROR-CRITIQUE-CLAIM-01
- **applicability:** all math/science courses
- **destinations:** Practice, Formative, Discourse/Reflection
- **content types:** any topic with a common surface-plausible but wrong claim
- **response type:** short constructed-response
- **required representation:** prose claim (given) + prose/quantitative rebuttal or support (produced)
- **reasoning architecture:** student is given a claim made by a hypothetical student/scientist and must evaluate whether it's true, false, or true-with-conditions, using evidence — this differs from ERROR-DIAGNOSE because the claim is a *conclusion*, not a worked procedure, so there's no single located "step" to find
- **misconception/distractor strategy:** claim should be genuinely debatable on the surface (partially true, or true under unstated conditions) rather than obviously false
- **variation axes:** true/false/conditionally-true claims; whether evidence must be quantitative or purely conceptual
- **DOK range:** 3, can reach 4 if evaluating the claim requires the student to design or reference an investigation (pairs well with EXPDESIGN architectures)
- **Bloom process descriptors:** Evaluate
- **evidence produced:** whether the student can construct an argument using evidence, not just recall the correct fact
- **works well when:** targeting scientific-argumentation or mathematical-justification skills explicitly (CER-adjacent tasks)
- **avoid when:** the claim is unambiguously true or false with no reasoning required to see it — becomes a disguised recall question
- **security suitability:** Formative-preferred (open response is easy to game via memorized "correct" essay if reused)
- **demonstration example:** "A classmate claims: 'Doubling the mass of an object doubles its potential energy, so it must also double its kinetic energy when dropped from the same height.' Evaluate this claim. Is it correct? Use the relevant equations to support your answer."
- **provenance:** general CER-style claim-evidence-reasoning structure, informed by the AP CED's "Think Aloud" sample activity type

---

## 6. Estimation & Approximation

### ESTIMATE-BEFORE-COMPUTE-01
- **applicability:** all math/science courses
- **destinations:** Warm-Up, Notes
- **content types:** any computation with an intuitive magnitude check available
- **response type:** short constructed-response (two-part: estimate, then compute)
- **required representation:** numeric/prose estimate + full computation
- **reasoning architecture:** student must commit to a reasoned estimate *before* seeing/doing the full computation, then compare — the estimate must be justified (not a guess), and the comparison step is graded
- **misconception/distractor strategy:** N/A; watch for students estimating after computing (defeats the purpose) — sequencing in delivery matters for this architecture
- **variation axes:** context; whether estimation uses rounding, bounding, or a known reference value
- **DOK range:** 2
- **Bloom process descriptors:** Understand, Apply
- **evidence produced:** number sense and whether a student can self-check for reasonableness — catches "calculator answers that don't make sense" errors
- **works well when:** building the habit of sanity-checking answers, especially before a unit involving calculator/technology use
- **avoid when:** the quantity has no intuitive magnitude reference for estimation (some abstract algebra contexts)
- **security suitability:** Practice/Formative only
- **demonstration example:** "Before calculating, estimate: what is 47% of 812? Explain your estimation strategy in one sentence. Then compute the exact value and compare it to your estimate."
- **provenance:** general numeracy practice; also reflects Finney calc textbook's recurring "Now try Exercise" pattern of pairing conceptual estimate with algebraic confirmation (e.g., graphical estimate before algebraic solve)

### ESTIMATE-BOUND-CONFIDENCE-01
- **applicability:** APCalc, Physics, Bio, Chem
- **destinations:** Practice, Summative
- **content types:** Riemann sums, measurement uncertainty, error propagation
- **response type:** short constructed-response
- **required representation:** numeric with justified bound (over/under-estimate)
- **reasoning architecture:** student must determine not just an approximate value but whether it is an over- or under-estimate of the true value, using structural reasoning (concavity, monotonicity) rather than computing the true value to check
- **variation axes:** left/right/midpoint/trapezoid Riemann sums; increasing/decreasing and concave up/down combinations
- **misconception/distractor strategy:** distractors swap over/under reasoning (a common error: assuming right sums always overestimate regardless of whether the function is increasing or decreasing)
- **DOK range:** 3
- **Bloom process descriptors:** Analyze
- **evidence produced:** whether students understand *why* an approximation method over/underestimates, not just how to compute it
- **works well when:** reinforcing the conceptual link between Riemann sum type and function behavior
- **avoid when:** the function's monotonicity/concavity isn't given or determinable — the reasoning step has nothing to stand on
- **security suitability:** Summative-safe
- **demonstration example:** "A function f is decreasing and concave up on [0,4]. Without computing the actual sums, determine whether a left Riemann sum, right Riemann sum, and trapezoidal approximation each over- or under-estimate the true area under the curve. Justify each answer."
- **provenance:** standard AP Calculus reasoning pattern tied to CED Unit 6 (Integration and Accumulation of Change)

---

## 7. Comparison & Justification of Methods

### COMPARE-COMPETING-METHODS-01
- **applicability:** all math/science courses
- **destinations:** Notes, Practice, Discourse/Reflection
- **content types:** any topic with two genuinely valid solution strategies
- **response type:** short constructed-response
- **required representation:** two given worked solutions (correct, different methods) + prose comparison
- **reasoning architecture:** two different, both-valid strategies are shown; student must explain *why* both work and identify what each method reveals or obscures, or under what conditions one is more efficient — not identify which is "right" (both are)
- **misconception/distractor strategy:** N/A — this is the architecture flagged as previously overused/misapplied in the Physics banks when reduced to "who is correct" framing. Only use when both approaches are genuinely valid.
- **variation axes:** which two methods; whether the comparison is about efficiency, insight, or generalizability
- **DOK range:** 3
- **Bloom process descriptors:** Analyze, Evaluate
- **evidence produced:** depth of conceptual understanding — whether a student sees a topic as one rigid procedure or a flexible set of equivalent approaches
- **works well when:** two genuinely viable strategies illuminate an important distinction (e.g., completing the square vs. quadratic formula — one reveals vertex form, the other doesn't)
- **avoid when:** one "method" is actually wrong (that's ERROR-DIAGNOSE, not this) or the two methods are trivially identical with cosmetic differences — do not use as a generic wrapper for routine computation
- **security suitability:** Formative-preferred (open comparative reasoning is easy to templatize if reused verbatim)
- **demonstration example:** "Two students solve x² − 6x + 5 = 0. Student A factors it. Student B completes the square. Both reach correct, equivalent answers. Explain one thing Student B's method reveals about the parabola that Student A's method does not."
- **provenance:** direct response to the documented Student A/Student B overuse failure in the Physics banks — this entry exists specifically to constrain that pattern to its valid use case

### COMPARE-EFFICIENCY-CONTEXT-01
- **applicability:** Alg1, Alg2, PreCalc
- **destinations:** Practice, Summative
- **content types:** any topic where method choice depends on the specific numbers/structure given
- **response type:** short constructed-response
- **required representation:** problem (given) + method choice with justification (produced)
- **reasoning architecture:** student is given a problem instance and must select and justify the most efficient method *for this specific instance*, demonstrating that method choice is structure-dependent, not fixed
- **misconception/distractor strategy:** distractor "efficient" choices apply a method that works but is needlessly long for the given structure (e.g., quadratic formula on an obviously factorable trinomial)
- **variation axes:** which structural features make one method clearly better
- **DOK range:** 3
- **Bloom process descriptors:** Analyze, Evaluate
- **evidence produced:** flexible strategic thinking vs. rote default-method application
- **works well when:** students have a tendency to default to one memorized method regardless of structure (a very common failure mode worth targeting directly)
- **avoid when:** all valid methods are genuinely equally efficient for the given instance
- **security suitability:** Summative-safe with new instances
- **demonstration example:** "Solve x² − 9 = 0. Then explain why factoring was more efficient here than using the quadratic formula, referencing a specific structural feature of the equation."
- **provenance:** general strategic-flexibility framing, informed by CPM's frequent framing of "which representation/method is most useful here" discussion prompts

---

## 8. Prediction & Extrapolation

### PREDICT-EXTRAPOLATE-MODEL-01
- **applicability:** Alg1, Alg2, PreCalc, Bio, Physics
- **destinations:** Practice, PT, Summative
- **content types:** any fitted model (linear, exponential, quadratic)
- **response type:** short constructed-response
- **required representation:** data/model (given) → predicted value + reliability judgment (produced)
- **reasoning architecture:** student uses a model to predict a value *outside* the given data range (extrapolation) or between data points (interpolation), and must explicitly judge how reliable that prediction is given the model type and distance from known data
- **misconception/distractor strategy:** distractors apply the model mechanically without ever addressing reliability — this reliability judgment is the differentiator from a plain "plug into the model" item
- **variation axes:** interpolation vs. extrapolation; how far outside the data range; model type
- **DOK range:** 3
- **Bloom process descriptors:** Apply, Evaluate
- **evidence produced:** whether a student understands models as approximations with a validity range, not universal truth-generators
- **works well when:** following any line/curve-of-best-fit unit, to counter the common failure of blind extrapolation
- **avoid when:** the prediction point is close enough to the data that reliability isn't a genuine question
- **security suitability:** Summative-safe
- **demonstration example:** "Using a line of best fit built from data collected between 2015-2020, a student predicts a value for the year 2050. Calculate the predicted value, then evaluate whether this prediction is likely to be reliable. Explain your reasoning."
- **provenance:** CPM's recurring line-of-best-fit / prediction lesson structure (documented recurring pattern, not a specific problem)

---

## 9. Theorem-Condition / Hypothesis Verification

### CONDITION-VERIFY-THEOREM-01
- **applicability:** APCalc, Geo, PreCalc
- **destinations:** Notes, Practice, Summative
- **content types:** any theorem with explicit hypotheses (IVT, MVT, Continuity, Squeeze Theorem, triangle congruence theorems)
- **response type:** short constructed-response
- **required representation:** given function/figure + prose verification
- **reasoning architecture:** before applying a theorem's conclusion, student must explicitly check and state whether each hypothesis is satisfied — including cases where a hypothesis fails and the theorem therefore cannot be applied
- **misconception/distractor strategy:** include at least one instance across a set where a hypothesis visibly fails (discontinuity, non-differentiable point) so the correct answer is "the theorem does not apply here," not just successful application every time
- **variation axes:** which theorem; how many hypotheses (2 vs. 3+); whether hypotheses are satisfied, violated, or ambiguous from the given information
- **DOK range:** 2–3 (3 when a hypothesis fails and student must explain *why* the theorem breaks down, not just say "no")
- **Bloom process descriptors:** Understand, Analyze
- **evidence produced:** whether students verify hypotheses out of habit or skip straight to applying conclusions (a well-documented AP scoring-loss pattern)
- **works well when:** used consistently across a unit so hypothesis-checking becomes automatic, not a one-off gotcha
- **avoid when:** the hypotheses are trivially satisfied every time in your item set — the verification step becomes rote and stops being checked for real
- **security suitability:** Summative-safe
- **demonstration example:** "A function f is given by a graph with a removable discontinuity at x = 2 on the interval [0,4]. A student wants to apply the Intermediate Value Theorem on [0,4]. Determine whether IVT can be applied as stated. If not, explain which hypothesis fails and what would need to be true for it to apply."
- **provenance:** AP Calculus CED Skill 3.C ("Confirm whether hypotheses or conditions of a selected definition, theorem, or test have been satisfied") — the CED explicitly instructs "students should establish the practice of explicitly verifying hypotheses before applying theorems"

### CONDITION-CLASSIFY-CASE-01
- **applicability:** Geo, Alg2, PreCalc
- **destinations:** Practice, Notes
- **content types:** classification tasks (triangle congruence criteria, conic sections, function families)
- **response type:** short constructed-response or selected-response
- **required representation:** given information (diagram/equation) → classification + justification
- **reasoning architecture:** student must determine which of several defined categories a given object belongs to, using the formal defining conditions, not surface appearance
- **misconception/distractor strategy:** distractor classifications correspond to surface-feature matching (e.g., classifying by "looks like it might be similar" rather than checking the actual criteria)
- **variation axes:** number of candidate categories; whether the classification is determinate or requires additional information (see MISSING-INFO)
- **DOK range:** 2–3
- **Bloom process descriptors:** Understand, Analyze
- **evidence produced:** whether students apply formal definitions or rely on visual/surface pattern-matching
- **works well when:** a unit introduces several categories that share surface similarities
- **avoid when:** categories are visually unambiguous — no real classification reasoning occurs
- **security suitability:** Summative-safe
- **demonstration example:** "Given two triangles with two pairs of congruent sides and one pair of congruent angles (not the included angle), determine whether the triangles can be proven congruent, and if so, by which criterion. Explain why SSA is not generally a valid congruence criterion using this example."
- **provenance:** standard geometry classification-task structure; framing informed by Glencoe's counterexample-generation pattern for testing whether a general rule holds

---

## 10. Data Interpretation

### DATA-BESTFIT-PREDICT-01
- **applicability:** Alg1, Alg2, Bio, Physics
- **destinations:** Practice, PT, Summative
- **content types:** scatterplot analysis, correlation, line/curve of best fit
- **response type:** extended constructed-response
- **required representation:** data set/scatterplot (given) → equation + prediction + reliability statement (produced)
- **reasoning architecture:** student constructs a model from data, uses it to predict, and evaluates the strength/appropriateness of the correlation itself (not just mechanically fitting a line to any data)
- **misconception/distractor strategy:** N/A (constructed response); watch for students fitting a line to data with no real linear correlation without ever questioning whether a linear model is appropriate
- **variation axes:** strong vs. weak vs. no correlation in the data; outliers present or absent
- **DOK range:** 3
- **Bloom process descriptors:** Apply, Evaluate
- **evidence produced:** whether a student critically evaluates a model's fit, not just mechanically executes regression
- **works well when:** paired with MODEL-SELECT-BEST-FIT for full data-modeling fluency
- **avoid when:** the data is too clean — every real modeling task should include at least mild scatter/noise
- **security suitability:** Summative-safe with new data sets
- **demonstration example:** "A dataset relates hours of sleep to reaction time for 12 students, with one clear outlier (an athlete with unusually fast reaction time despite low sleep). Determine the line of best fit with and without the outlier included. Discuss which is more appropriate to report and why."
- **provenance:** CPM's line-of-best-fit lesson structure combined with AP-style outlier/reliability reasoning

### TABLE-RECONSTRUCT-MISSING-CELLS-01
- **applicability:** Alg1, Alg2, Chem (stoichiometry tables), Physics (kinematics tables)
- **destinations:** Practice, Warm-Up
- **content types:** any relationship expressible in a table with a consistent rule
- **response type:** table completion
- **required representation:** partial table (given) → completed table + stated rule (produced)
- **reasoning architecture:** table has select cells filled and others blank, including at least one blank that cannot be filled by simple pattern-continuation and requires inferring/applying the underlying rule (formula) instead
- **misconception/distractor strategy:** design so that naive "add the same difference each time" pattern-continuation fails for at least one blank (e.g., nonlinear relationship, or non-adjacent blank cells) — this forces rule-based reasoning over surface pattern-matching
- **variation axes:** linear vs. nonlinear relationship; which cells are blank (adjacent vs. scattered)
- **DOK range:** 2, reaching 3 if the table's spacing is irregular enough that pattern-continuation is actively unreliable
- **Bloom process descriptors:** Apply, Analyze
- **evidence produced:** whether a student has the actual functional rule vs. just a local pattern-completion trick
- **works well when:** you specifically want to break students of iterative "add 3 each time" pattern habits for a relationship that isn't actually linear
- **avoid when:** the relationship is genuinely linear with even spacing — pattern-continuation is a valid strategy there and shouldn't be treated as wrong
- **security suitability:** Formative
- **demonstration example:** "Complete the table for y = 2^x, where the given x-values are 0, 1, 3, and 5 (not consecutive). Determine the missing y-values for x = 2 and x = 4, and state the rule you used."
- **provenance:** general function-table structure; scattered-blank design specifically informed by CPM's non-adjacent data table style

---

## 11. Missing-Information / Underdetermined

### MISSING-INFO-IDENTIFY-NEEDED-01
- **applicability:** all math/science courses
- **destinations:** Practice, Discourse/Reflection
- **content types:** any multi-variable relationship or formula
- **response type:** short constructed-response
- **required representation:** underdetermined problem (given) → identification of missing quantity (produced), no numeric solution required
- **reasoning architecture:** student is given a problem that cannot be solved as stated and must identify specifically what information is missing and why it's needed — the task is explicitly not solvable, and recognizing that is the point
- **misconception/distractor strategy:** N/A; watch for students inventing a plausible-sounding "solution" rather than recognizing insufficiency — this is exactly the failure mode the architecture targets
- **variation axes:** which piece of information is missing; whether multiple pieces are missing
- **DOK range:** 3
- **Bloom process descriptors:** Analyze, Evaluate
- **evidence produced:** whether a student understands the *structure* of a formula/relationship well enough to know what it depends on, rather than pattern-matching to "plug numbers into formula"
- **works well when:** countering the common failure of students attempting to solve anything presented as a "solve for X" problem regardless of whether it's actually solvable
- **avoid when:** used too frequently — if every problem in a set is unsolvable, students learn to distrust all problems rather than developing real judgment
- **security suitability:** Formative-preferred
- **demonstration example:** "A student is asked to find the exact area of a triangle, and is only given the lengths of two sides. Explain what additional information is needed to find the area, and why the two given side lengths alone are not sufficient."
- **provenance:** general critical-reasoning architecture; explicitly designed as a countermeasure to the "always solvable" assumption baked into most textbook problem sets

---

## 12. Argument, Justification & Counterexample

### ARGUE-COUNTEREXAMPLE-01
- **applicability:** Alg1, Alg2, Geo, PreCalc
- **destinations:** Practice, Notes, Discourse/Reflection
- **content types:** any general claim/conditional statement that is sometimes but not always true
- **response type:** short constructed-response
- **required representation:** general claim (given) → specific counterexample or valid-conclusion judgment (produced)
- **reasoning architecture:** student is given a conditional statement and must either produce a specific counterexample that disproves it, or determine that no counterexample exists and explain why the statement holds generally
- **misconception/distractor strategy:** N/A; the key design constraint is that the claim must be genuinely false-but-plausible (true for many/most cases, false for a specific edge case) — an obviously false claim doesn't require real search
- **variation axes:** true-for-all vs. false-with-counterexample claims mixed in a set; domain (numbers, geometric figures, functions)
- **DOK range:** 3
- **Bloom process descriptors:** Analyze, Evaluate
- **evidence produced:** whether a student can search for edge cases rather than accepting general claims after checking one or two confirming examples
- **works well when:** targeting the common student habit of over-generalizing from limited examples
- **avoid when:** the claim's truth value is obvious without any search (defeats the purpose)
- **security suitability:** Summative-safe if the claim set rotates
- **demonstration example:** "A student claims: 'If a quadrilateral has two pairs of congruent sides, it must be a parallelogram.' Determine whether this claim is true. If false, provide a specific counterexample (a description or sketch is sufficient)."
- **provenance:** Glencoe's deductive reasoning / counterexample lesson structure (Study Guide and Intervention: "you need to find only one counterexample for the statement to be false")

### ARGUE-JUSTIFY-GENERAL-CASE-01
- **applicability:** Alg1, Alg2, Geo, PreCalc, APCalc
- **destinations:** Notes, PT, Summative
- **content types:** any pattern/rule that holds for a general case (algebraic identities, geometric theorems, number patterns)
- **response type:** extended constructed-response
- **required representation:** prose/symbolic proof or general argument
- **reasoning architecture:** student must justify why a pattern holds *in general* (for all valid inputs), not just verify it for specific instances — requires moving from example-checking to general argument
- **misconception/distractor strategy:** N/A; watch for students submitting "I checked it for x=2 and x=5 and it worked" as if that constitutes a general proof — this is the exact gap the architecture targets
- **variation axes:** algebraic identity vs. geometric theorem vs. numeric pattern; level of formality expected (informal argument vs. formal proof)
- **DOK range:** 3–4 (4 when full formal proof/generalization to arbitrary n or arbitrary case is required)
- **Bloom process descriptors:** Analyze, Create (when the student must construct the argument structure themselves)
- **evidence produced:** whether a student distinguishes empirical confirmation from genuine proof
- **works well when:** a unit's culminating task should assess conceptual depth beyond procedural fluency
- **avoid when:** students haven't yet been taught what a general argument looks like in this domain — introduce via modeling before assessing
- **security suitability:** Summative-safe, strong PT candidate
- **demonstration example:** "Show that the sum of two consecutive odd integers is always divisible by 4. Do not just check examples — construct a general argument using algebraic expressions for consecutive odd integers."
- **provenance:** general proof/generalization architecture, standard across Common-Core-aligned algebra materials (Pearson's "Essential Understanding" framing routinely sets up general-case claims before specific practice)

---

## 13. Graphical Inference

### GRAPH-INFER-BEHAVIOR-01
- **applicability:** Alg1, Alg2, PreCalc, APCalc, Physics
- **destinations:** Practice, Summative
- **content types:** any function/relationship where qualitative features (increasing/decreasing, sign, extrema, asymptotes, concavity) can be read from a graph without an equation
- **response type:** short constructed-response
- **required representation:** graph only (no equation given) → qualitative feature identification (produced)
- **reasoning architecture:** student must extract structural/behavioral information purely from graphical features, with no algebraic formula available — this isolates graph-reading from computation
- **misconception/distractor strategy:** distractors confuse related-but-distinct features (e.g., confusing where a function is zero with where its derivative is zero; confusing steepness with sign)
- **variation axes:** which feature(s) are being read; whether the graph includes a function, its derivative, or both simultaneously
- **DOK range:** 2, reaching 3 when features must be inferred by combining multiple graphical cues (e.g., determining concavity from a velocity-vs-time graph)
- **Bloom process descriptors:** Understand, Analyze
- **evidence produced:** whether a student's understanding of a feature is graph-native or dependent on having an equation to fall back on
- **works well when:** you want to confirm conceptual (not just computational) fluency
- **avoid when:** the graph is too simple/idealized to distinguish related features from each other
- **security suitability:** Summative-safe
- **demonstration example:** "The graph shows a car's velocity over time (not position). Determine the time interval(s) during which the car's speed is increasing, and explain how you can tell this from a velocity-time graph rather than a position-time graph."
- **provenance:** standard physics/calculus graph-reading architecture; the velocity-vs-position framing specifically targets a commonly documented misconception (confusing position and velocity graphs)

### GRAPH-CONSTRUCT-FROM-CONSTRAINTS-01
- **applicability:** Alg1, Alg2, PreCalc, APCalc
- **destinations:** Practice, PT
- **content types:** any function family
- **response type:** graph/diagram production
- **required representation:** verbal constraints (given) → original graph satisfying all constraints (produced) — deliberately open-ended, many correct answers exist
- **reasoning architecture:** student is given a list of qualitative constraints (e.g., "increasing on (-∞,2), decreasing on (2,∞), passes through (0,3), concave down everywhere") and must construct a graph satisfying all of them simultaneously — no single correct graph exists, which shifts the task from "find the answer" to "verify your own construction meets every constraint"
- **misconception/distractor strategy:** N/A (open construction); design constraint sets so that satisfying them all simultaneously requires genuine reconciliation, not just satisfying them one at a time in isolation
- **variation axes:** number of constraints (3 vs. 5+); whether constraints are ever contradictory (advanced version, tests whether students notice impossibility)
- **DOK range:** 3–4
- **Bloom process descriptors:** Create, Evaluate (self-verification against constraints)
- **evidence produced:** whether a student holds an integrated mental model of multiple graphical features simultaneously, rather than being able to identify each feature only in isolation
- **works well when:** as a culminating/PT task after multiple individual GRAPH-INFER items have been used to build each feature separately
- **avoid when:** used before students can reliably read individual features — this architecture assumes GRAPH-INFER-level skills are already solid
- **security suitability:** Summative-safe (infinite valid answers make answer-sharing largely useless)
- **demonstration example:** "Sketch a graph of a function f that is: increasing on (−∞, −1), decreasing on (−1, 3), increasing on (3, ∞), has a local max at x = −1, and is continuous everywhere. Verify your graph satisfies all four conditions."
- **provenance:** standard AP Calculus "construct a function from qualitative behavior" task type, widely used to assess conceptual (not computational) understanding of derivative behavior

---

## 14. Experimental Design / CER (Physics, Chem, Bio)

### CER-CLAIM-EVIDENCE-REASONING-01
- **applicability:** Physics, Chem, Bio
- **destinations:** Practice, PT, Summative
- **content types:** any phenomenon explainable by a scientific principle
- **response type:** extended constructed-response
- **required representation:** data/observation (given) → claim + evidence + reasoning (produced), explicitly labeled
- **reasoning architecture:** student is given data or an observed phenomenon and must produce a three-part response: a claim (what happened/is true), evidence (specific data supporting it), and reasoning (the scientific principle connecting evidence to claim) — each part graded separately
- **misconception/distractor strategy:** N/A; common failure is restating the claim as the reasoning, or citing evidence without connecting it explicitly to the underlying principle — structure the rubric to catch this
- **variation axes:** which principle; whether data is provided or must be read from a diagram/graph first
- **DOK range:** 3
- **Bloom process descriptors:** Analyze, Evaluate
- **evidence produced:** whether a student can construct scientific argument structure, not just recall the correct principle
- **works well when:** it's the target skill itself (AP Science Practices explicitly include this structure)
- **avoid when:** used for a phenomenon whose principle hasn't been taught yet — CER requires a reasoning resource to draw on
- **security suitability:** Formative-preferred; Summative-safe if phenomenon/data varies
- **demonstration example:** "Two identical balls are dropped from the same height, one solid and one hollow (same size, different mass). Data show both hit the ground at the same time. State a claim about how mass affects free-fall time, cite the specific evidence, and explain your reasoning using the relevant physics principle."
- **provenance:** standard CER framework used broadly in NGSS-aligned science instruction; matches the learning-ladder Science Practices already built into [[physics-curriculum]]

### EXPDESIGN-CONTROL-VARIABLE-01
- **applicability:** Physics, Chem, Bio
- **destinations:** Practice, PT
- **content types:** any investigable relationship between two or more variables
- **response type:** extended constructed-response
- **required representation:** research question (given) → experimental design (produced): independent/dependent/controlled variables, procedure outline
- **reasoning architecture:** student designs an investigation to test a specific question, explicitly identifying which variable is manipulated, which is measured, and which must be held constant — and must justify why each controlled variable matters (what confound it prevents)
- **misconception/distractor strategy:** N/A; watch for students listing controlled variables without justification (a list isn't evidence of understanding why control matters)
- **variation axes:** which phenomenon; number of variables to control; whether multiple confounds must be addressed simultaneously
- **DOK range:** 4 (genuine experimental design, non-routine, requires synthesis)
- **Bloom process descriptors:** Create, Evaluate
- **evidence produced:** whether a student understands controlled-variable logic as reasoning about confounds, not just a checklist habit
- **works well when:** used as a PT or unit-culminating task tied to an actual or simulated investigation
- **avoid when:** used as a routine practice item — DOK 4 tasks are appropriately rare, not a daily architecture
- **security suitability:** Summative-safe (open design space resists memorization)
- **demonstration example:** "Design an experiment to test whether the length of a pendulum affects its period. Identify the independent, dependent, and controlled variables, and explain what confound each controlled variable prevents."
- **provenance:** standard experimental-design task type; aligned to AP Science Practices and the Science Practices structure already used in the [[physics-curriculum]] learning ladders

### CER-MECHANISM-EXPLAIN-01
- **applicability:** Physics, Chem, Bio
- **destinations:** Notes, Practice, Summative
- **content types:** any phenomenon with an underlying causal mechanism (why, not just what)
- **response type:** short constructed-response
- **required representation:** phenomenon/observation (given) → mechanistic explanation (produced)
- **reasoning architecture:** student explains *why* a phenomenon occurs at the mechanism level (what's physically/chemically/biologically happening), not just labels or describes what is observed
- **misconception/distractor strategy:** watch for description-as-explanation (restating what happens instead of why) — the rubric must explicitly require causal language
- **variation axes:** phenomenon; depth of mechanism required (surface-level vs. multi-step causal chain)
- **DOK range:** 2–3 (3 when the mechanism involves multiple interacting causes)
- **Bloom process descriptors:** Understand, Analyze
- **evidence produced:** whether a student has moved from descriptive to explanatory/mechanistic understanding
- **works well when:** routinely, as the standard "why" companion to a "what" observation task
- **avoid when:** the mechanism hasn't been taught — don't use to introduce new content cold
- **security suitability:** Formative-preferred
- **demonstration example:** "A metal spoon left in a hot cup of tea becomes warm to the touch even though it isn't touching the tea directly at the handle. Explain the mechanism by which heat travels through the spoon."
- **provenance:** general mechanism-explanation architecture, standard in Hewitt-style conceptual physics instruction (used across [[physics-curriculum]])

---

## 15. Multi-Step Synthesis

### MULTISTEP-SYNTHESIS-CROSS-UNIT-01
- **applicability:** all courses, as capstone tasks
- **destinations:** PT, Summative (final review)
- **content types:** any two skills from different units that combine naturally
- **response type:** extended constructed-response
- **required representation:** mixed, as needed by the combined skills
- **reasoning architecture:** task requires genuine sequential application of skills from two different units/chapters, where the second skill cannot be applied until the first is correctly completed — tests retention and integration, not just the most recent unit
- **misconception/distractor strategy:** N/A; design so the "bridge" between the two skills is the actual point of assessment (e.g., using a factored form from Unit 3 as input to a Unit 7 rational-expression simplification)
- **variation axes:** which two units are bridged; how far apart in the course sequence
- **DOK range:** 3
- **Bloom process descriptors:** Apply, Analyze
- **evidence produced:** retention of earlier material and ability to recognize when it's needed without being told
- **works well when:** built for cumulative review, midterms, or finals
- **avoid when:** used routinely within a single unit — defeats the "cross-unit" purpose and just becomes a longer version of PROC-MULTISTEP
- **security suitability:** Summative-safe
- **demonstration example:** "Simplify (x² − 9)/(x² − x − 12), then use the simplified form to determine any values of x for which the original expression is undefined." [bridges factoring from an earlier unit into a rational-expressions unit]
- **provenance:** general cumulative-assessment design principle, standard practice for final/midterm construction

### MULTISTEP-REAL-CONTEXT-DECOMPOSE-01
- **applicability:** Alg1, Alg2, Physics, Chem
- **destinations:** PT, Summative
- **content types:** any applied context requiring the student to identify which sub-problems are embedded
- **response type:** extended constructed-response
- **required representation:** rich context (given, more information than strictly needed) → decomposition into sub-questions + solution (produced)
- **reasoning architecture:** unlike PROC-MULTISTEP (where steps are explicitly sequenced for the student), here the student must *identify* what the sub-problems even are from a realistic, somewhat messy context before solving any of them
- **misconception/distractor strategy:** N/A; include some information in the context that is not needed, so students must also practice filtering relevant from irrelevant information
- **variation axes:** context; number of embedded sub-problems; amount of irrelevant information included
- **DOK range:** 3–4
- **Bloom process descriptors:** Analyze, Apply
- **evidence produced:** whether a student can structure an ill-defined real problem into solvable pieces, the actual transferable skill behind "word problems"
- **works well when:** used sparingly, as a genuine capstone/PT task
- **avoid when:** used as routine practice — decomposition-from-scratch is cognitively demanding and shouldn't be the daily default
- **security suitability:** Summative-safe
- **demonstration example:** "A family is planning a road trip and wants to know if they'll arrive before a scheduled event. [Realistic paragraph gives distance, speed limits on different road segments, a planned rest stop duration, and the event start time — more numbers than strictly needed, including irrelevant details like gas mileage.] Determine whether they will arrive on time, and show how you decided which information was necessary."
- **provenance:** general applied-modeling task structure; matches CPM's habit of embedding real-context word problems with more narrative detail than strictly required for the computation

---

## 16. Pattern Recognition & Generalization

### PATTERN-EXTEND-NUMERIC-01
- **applicability:** Alg1, Alg2, cross-curricular (any grade band)
- **destinations:** Warm-Up, Practice
- **content types:** sequences, numeric/visual patterns
- **response type:** short constructed-response
- **required representation:** sequence of terms/figures (given) → next term(s) + stated rule (produced)
- **reasoning architecture:** student identifies the generating rule behind a sequence (not just the next number) and uses it to predict a term, including at least one non-adjacent or far-out term that punishes counting-by-hand instead of using the rule
- **misconception/distractor strategy:** distractor predictions come from continuing a surface pattern one step too literally (e.g., assuming constant difference when the pattern is actually quadratic)
- **variation axes:** arithmetic, geometric, quadratic, or figural (visual/growing-pattern) sequences; how far the "punishing" term is
- **DOK range:** 2, reaching 3 when the far term requires the closed-form rule rather than iteration
- **Bloom process descriptors:** Understand, Analyze
- **evidence produced:** whether a student has the generating rule or is just iterating one step at a time
- **works well when:** introducing sequences/functions as rules rather than lists
- **avoid when:** the "far term" is close enough that iteration is just as fast as the rule — defeats the purpose
- **security suitability:** Formative
- **demonstration example:** "A figure pattern grows by adding a ring of dots around the previous figure: Figure 1 has 1 dot, Figure 2 has 5 dots, Figure 3 has 13 dots. Without drawing Figure 10, determine how many dots it will have, and explain the rule you used."
- **provenance:** Cuoco/Goldenberg/Mark "pattern sniffers" habit of mind — general framing that instruction should require rule-finding, not just pattern-continuation

### PATTERN-GENERALIZE-CLOSED-FORM-01
- **applicability:** Alg2, PreCalc, APCalc (sequences/series units)
- **destinations:** Notes, Practice, Summative
- **content types:** arithmetic/geometric sequences, series, recursive-to-explicit conversion
- **response type:** short constructed-response
- **required representation:** several specific cases (given) → general/closed-form expression (produced)
- **reasoning architecture:** student moves from several worked specific instances to a symbolic general rule that would produce all of them — the specific instances are scaffolding, not the answer
- **misconception/distractor strategy:** distractors correctly reproduce the given specific cases but fail on an untested case (overfit to the shown examples rather than true generalization) — a good check item asks the student to verify their rule on a new case
- **variation axes:** recursive vs. explicit form target; verification requirement included or not
- **DOK range:** 3
- **Bloom process descriptors:** Analyze, Create
- **evidence produced:** whether a student generalizes or merely pattern-matches to the presented cases
- **works well when:** paired with a verification step against an untested case
- **avoid when:** used without ever asking the student to check their generalization — an unchecked "guess a formula" task doesn't confirm real generalization occurred
- **security suitability:** Summative-safe
- **demonstration example:** "For the sequence 3, 7, 11, 15, ..., write a closed-form expression for the nth term. Then use your expression to verify the 20th term, and explain why simply continuing to add 4 repeatedly would not be practical for finding term 200."
- **provenance:** general algebra sequence-generalization structure; explicitly informed by Hess Cognitive Rigor Matrix's DOK 3 descriptor "generalize a pattern"

---

## 17. Parameter Exploration & Experimentation

### PARAM-VARY-CONJECTURE-01
- **applicability:** Alg1, Alg2, PreCalc, APCalc, Physics
- **destinations:** Notes, PT
- **content types:** any family of functions/relationships with a controllable parameter (slope, coefficient, amplitude, spring constant)
- **response type:** extended constructed-response
- **required representation:** graph or table across multiple parameter values (produced by student) → written conjecture (produced)
- **reasoning architecture:** student holds all but one parameter fixed, systematically varies it across several trials, records what changes, and states a general conjecture about that parameter's effect — mirrors an actual controlled-variable experiment but within a purely mathematical family
- **misconception/distractor strategy:** N/A; watch for students testing only one value of the parameter and generalizing from a single trial — the architecture requires multiple trials before conjecturing
- **variation axes:** which parameter is varied; how many trials are required before conjecturing (2 is too few for genuine confidence; 3+ recommended)
- **DOK range:** 3
- **Bloom process descriptors:** Analyze, Create (conjecture formation)
- **evidence produced:** whether a student can isolate a variable's effect through controlled comparison, a directly transferable skill to experimental science
- **works well when:** introducing how a parameter affects a graph/behavior (transformations of functions, effect of amplitude/period in trig, effect of a rate constant)
- **avoid when:** the parameter's effect is already explicitly stated in notes — this architecture is for discovery, not review of known facts
- **security suitability:** Formative-preferred (discovery-oriented, not ideal to re-use verbatim)
- **demonstration example:** "Graph y = a·x² for a = 1, a = 3, and a = 0.5, keeping all else the same. Based on these three graphs, write a conjecture about how the value of a affects the parabola's shape. Test your conjecture with one more value of a of your choosing."
- **provenance:** Cuoco/Goldenberg/Mark habits-of-mind "experimenters" and "tinkerers" framing (fix all but one variable, vary parameters in regular ways); also matches AP Calculus CED's "Create Representations" sample activity type

### PARAM-EXTREME-CASE-01
- **applicability:** PreCalc, APCalc, Physics
- **destinations:** Notes, Practice, Summative
- **content types:** limits, asymptotic behavior, boundary conditions in physics formulas
- **response type:** short constructed-response
- **required representation:** general expression/relationship (given) → behavior at an extreme/limiting case (produced)
- **reasoning architecture:** student examines what happens to a relationship as a variable approaches an extreme (zero, infinity, a boundary value) to understand the general behavior — using the extreme case as a reasoning tool, not as an isolated computation
- **misconception/distractor strategy:** distractors treat the extreme case as a special exception disconnected from the general rule, rather than as a lens on it
- **variation axes:** which extreme (zero, infinity, a physical boundary like "no friction" or "massless string"); algebraic vs. physical context
- **DOK range:** 3
- **Bloom process descriptors:** Analyze
- **evidence produced:** whether a student uses extreme/limiting cases as a genuine reasoning strategy (a hallmark of expert problem-solving) rather than only computing within given bounds
- **works well when:** introducing limits, asymptotes, or "what if this term is negligible" physics reasoning
- **avoid when:** the extreme case is degenerate/undefined with no instructive value
- **security suitability:** Summative-safe
- **demonstration example:** "In the formula for gravitational force between two objects, F = Gm₁m₂/r², explain what happens to F as r approaches 0, and as r approaches infinity. What does each extreme case tell you about the general shape of the relationship between F and r?"
- **provenance:** Cuoco/Goldenberg/Mark "extreme cases and passing to the limit" — an explicitly named geometric/mathematical habit of mind

---

## 18. Invariant & Transformation Reasoning

### INVARIANT-IDENTIFY-UNDER-TRANSFORM-01
- **applicability:** Geo, Alg2, PreCalc
- **destinations:** Notes, Practice
- **content types:** rigid transformations, function transformations, algebraic manipulations
- **response type:** short constructed-response
- **required representation:** object before/after a transformation (given, as diagram or expression) → identification of what stayed the same vs. what changed (produced)
- **reasoning architecture:** student explicitly separates the properties of an object that are preserved under a given transformation from those that change — the "what stays the same" question is the graded target, not just performing the transformation
- **misconception/distractor strategy:** distractors claim a non-invariant property is preserved (e.g., claiming orientation is preserved under a reflection) or an invariant property is not preserved
- **variation axes:** rigid transformation (reflection, rotation, translation) vs. non-rigid (dilation); geometric vs. algebraic/functional context
- **DOK range:** 2–3
- **Bloom process descriptors:** Analyze
- **evidence produced:** whether a student understands transformations structurally (what property defines the transformation) rather than just being able to execute one
- **works well when:** consolidating a transformations unit, specifically to prevent surface-level "it just looks moved" understanding
- **avoid when:** used before students can perform the transformation itself — invariant-reasoning assumes procedural fluency already exists
- **security suitability:** Summative-safe
- **demonstration example:** "A triangle is dilated by a scale factor of 2 centered at the origin. Identify two properties of the triangle that stay the same after the dilation, and two properties that change. Explain why each invariant property is preserved."
- **provenance:** Cuoco/Goldenberg/Mark "seeking geometric invariants" — a named geometric habit of mind; also reflects Big Ideas Math's "Structure" (MP7) exercise framing

### CONTINUOUS-DEFORM-GENERALIZE-01
- **applicability:** Geo, PreCalc
- **destinations:** PT, Notes (with dynamic geometry tool)
- **content types:** circle theorems, geometric relationships that hold across a continuous family of configurations
- **response type:** extended constructed-response
- **required representation:** diagram with a movable element (given, ideally via dynamic geometry software) → general relationship that holds across all positions (produced)
- **reasoning architecture:** student mentally or physically moves one element of a figure continuously through a family of positions (including degenerate/limiting positions) and identifies what relationship remains true throughout — connects specific configurations into one general theorem
- **misconception/distractor strategy:** N/A; watch for students treating each position as an unrelated separate case rather than recognizing continuity across the family
- **variation axes:** which geometric relationship; whether degenerate positions (vertex on the circle, vertex at infinity) are included as reasoning checkpoints
- **DOK range:** 4
- **Bloom process descriptors:** Analyze, Create
- **evidence produced:** deep structural understanding of why a theorem is true across all cases, not just verification in one static diagram
- **works well when:** used as a rare, high-value discovery task introducing a major theorem (inscribed angle theorem and its special cases are a classic example)
- **avoid when:** used routinely — this is a DOK 4 discovery architecture, appropriately infrequent
- **security suitability:** Formative/discovery-only, not summative
- **demonstration example:** "Using a dynamic geometry tool, place a point on a circle and form an inscribed angle from two chords. Drag the point to several different positions on the circle, including near the endpoints of the chords. What stays true about the angle's measure across all positions? What happens in the limiting case as the point approaches one of the chord's endpoints?"
- **provenance:** Cuoco/Goldenberg/Mark "reasoning by continuity" habit of mind, explicitly illustrated in their own writing using the inscribed-angle-theorem example as the canonical case

---

## 19. Problem Posing

### PROBLEM-POSE-FROM-CONSTRAINTS-01
- **applicability:** all math/science courses
- **destinations:** PT, Notes (peer-exchange activities)
- **content types:** any topic where a class of valid problems shares a target structure
- **response type:** extended constructed-response (student writes a new problem, then solves it)
- **required representation:** constraints (given: e.g., "must require factoring a trinomial with a negative leading coefficient") → original problem + solution (produced)
- **reasoning architecture:** student constructs their own problem satisfying stated constraints, rather than solving a given one — requires understanding a problem type well enough to generate a valid instance of it, which is a deeper test than solving
- **misconception/distractor strategy:** N/A; watch for students writing a problem that's solvable but doesn't actually satisfy the stated constraint — grading must explicitly check the constraint was met, not just that a valid problem was produced
- **variation axes:** how tightly specified the constraints are; whether students swap and solve each other's problems (adds a peer-check layer)
- **DOK range:** 4
- **Bloom process descriptors:** Create
- **evidence produced:** genuine mastery of a problem type's structure — a classic sign a student "gets it" is being able to construct new correct instances of it
- **works well when:** as a unit-culminating or review task, especially good for peer-exchange activities (CPM's collaborative structure fits naturally here)
- **avoid when:** used with a skill that's still shaky — problem-writing requires more fluency than problem-solving, not less
- **security suitability:** Summative-unsuitable as a graded item bank source (every instance is unique by design) but excellent for PT/review
- **demonstration example:** "Write your own word problem that requires solving a system of linear equations, where the solution must include a negative x-value. Solve your problem and show that it satisfies this constraint."
- **provenance:** Hess Cognitive Rigor Matrix DOK 4 Create descriptor, "formulate an original problem given a situation"

### PROBLEM-POSE-MATCH-TARGET-01
- **applicability:** Alg1, Alg2, PreCalc
- **destinations:** Practice, Notes
- **content types:** any topic where a specific target answer/equation is given
- **response type:** short constructed-response
- **required representation:** target equation or answer (given) → original context/scenario that would produce it (produced)
- **reasoning architecture:** this is the reverse of typical word-problem solving — student is given the mathematical object (equation, answer, graph) and must invent a plausible real-world scenario it could represent, testing whether they understand what the mathematical structure *means*, not just how to manipulate it
- **misconception/distractor strategy:** N/A; watch for scenarios that are only superficially plausible without actually matching the given structure (e.g., writing a scenario implying a different rate than the one given)
- **variation axes:** equation type (linear, quadratic, exponential); whether a specific numeric answer must also be matched, not just the equation form
- **DOK range:** 3–4
- **Bloom process descriptors:** Create, Evaluate (self-checking that the scenario matches)
- **evidence produced:** whether symbolic fluency is connected to real-world meaning, or purely mechanical
- **works well when:** used after REPTRANS-TRANSLATE-VERBAL-SYMBOLIC has been taught in the forward direction — this is the natural reverse-direction follow-up
- **avoid when:** introducing equation-writing for the first time — this reverse task assumes forward translation is already comfortable
- **security suitability:** Formative-preferred
- **demonstration example:** "Write a real-world scenario that could be modeled by the equation y = 15x + 40. Explain what the 15 and the 40 represent in your scenario."
- **provenance:** general reverse-translation architecture, a natural complement to CPM's forward-direction "match sentence to translation" pattern

---

## 20. Unit Conversion & Dimensional Reasoning

### UNITCONV-DIMENSIONAL-CHAIN-01
- **applicability:** Physics, Chem, Alg1 (rates/ratios units)
- **destinations:** Warm-Up, Practice
- **content types:** any multi-unit conversion (metric/customary, compound units like m/s to km/h)
- **response type:** short constructed-response
- **required representation:** given quantity with units → converted quantity via explicit factor-label/dimensional-analysis chain (produced, showing units canceling)
- **reasoning architecture:** student must show units canceling algebraically through the conversion chain, not just produce the correct final number — the unit-tracking itself is the graded skill
- **misconception/distractor strategy:** distractors result from inverting a conversion factor (multiplying instead of dividing) — a common, specific, well-documented error
- **variation axes:** single-step vs. multi-step conversion chain; compound units (rates, densities) vs. simple units
- **DOK range:** 2
- **Bloom process descriptors:** Apply
- **evidence produced:** whether a student tracks units as a self-checking mechanism, a foundational science skill
- **works well when:** early in any science course, and as a recurring low-stakes check throughout
- **avoid when:** the conversion is trivial (single familiar factor) — save the architecture for genuinely multi-step chains where unit-tracking prevents errors
- **security suitability:** Summative-safe (numbers/units vary easily)
- **demonstration example:** "Convert 72 km/h to m/s, showing your unit cancellation explicitly at each step of the conversion chain."
- **provenance:** standard factor-label method used across Glencoe and Pearson science-adjacent materials; Hess CRM DOK 1–2 descriptor "make conversions among representations or numbers, within and between customary and metric measures"

### UNITCONV-VERIFY-PLAUSIBILITY-01
- **applicability:** Physics, Chem
- **destinations:** Practice, Formative
- **content types:** any formula combining multiple physical quantities
- **response type:** short constructed-response
- **required representation:** a claimed formula or equation (given, possibly incorrect) → dimensional check (produced)
- **reasoning architecture:** student checks whether a given equation *could* be dimensionally correct by analyzing the units on both sides, without solving the equation numerically — this catches a specific class of errors (mismatched units) using pure structural reasoning
- **misconception/distractor strategy:** N/A; the equation itself should sometimes be dimensionally wrong so "this equation cannot be correct" is a valid, expected answer in some instances
- **variation axes:** which physical quantities/formula; correct vs. dimensionally-inconsistent given equation
- **DOK range:** 3
- **Bloom process descriptors:** Analyze, Evaluate
- **evidence produced:** whether a student can use dimensional analysis as an error-checking tool, a genuine practicing-scientist habit
- **works well when:** paired with VERIFY-REASONABLENESS as part of a broader "sanity check your work" instructional emphasis
- **avoid when:** students haven't yet learned to track units through formulas — this assumes UNITCONV-DIMENSIONAL-CHAIN fluency already exists
- **security suitability:** Formative-preferred
- **demonstration example:** "A student claims that force can be calculated as F = mv (mass times velocity). Using dimensional analysis, determine whether this equation could possibly be correct for force, and explain what F = mv actually represents dimensionally."
- **provenance:** standard physics dimensional-analysis-as-error-check technique, widely used across conceptual physics instruction (Hewitt-style courses, informing [[physics-curriculum]])

---

## 21. Vector & Diagram Construction (Physics)

### VECTOR-DECOMPOSE-COMPONENTS-01
- **applicability:** Physics
- **destinations:** Notes, Practice, Summative
- **content types:** projectile motion, inclined planes, force analysis
- **response type:** short constructed-response + diagram
- **required representation:** vector at an angle (given) → x/y component decomposition (produced), with diagram
- **reasoning architecture:** student decomposes a single vector into perpendicular components and must justify the trigonometric choice (why sine vs. cosine for each component) based on the angle's definition in the diagram, not by memorized formula alone
- **misconception/distractor strategy:** distractors swap sine and cosine (a very common, specific error when the angle is measured from a non-standard reference)
- **variation axes:** angle measured from horizontal vs. vertical vs. an incline; which quadrant
- **DOK range:** 2–3 (3 when the angle reference is non-standard and requires geometric reasoning to set up correctly, not just formula recall)
- **Bloom process descriptors:** Apply, Analyze
- **evidence produced:** whether a student understands vector decomposition geometrically or has just memorized "x is cosine"
- **works well when:** varying the angle reference deliberately across a problem set to prevent the sine/cosine memorization shortcut
- **avoid when:** always using the same angle reference (horizontal from the right) — this is exactly what allows the memorization shortcut to go undetected
- **security suitability:** Summative-safe
- **demonstration example:** "A ball is launched up a 25° incline with an initial speed of 12 m/s, where the incline itself is angled 25° from the horizontal ground. Decompose the initial velocity into components parallel and perpendicular to the incline surface, and explain your choice of sine or cosine for each component."
- **provenance:** standard physics vector-decomposition task type; angle-reference-variation strategy included specifically as a countermeasure to a well-documented sine/cosine memorization shortcut

### FREEBODY-DIAGRAM-CONSTRUCT-01
- **applicability:** Physics
- **destinations:** Notes, Practice, Summative
- **content types:** forces, Newton's laws
- **response type:** diagram production + short constructed-response
- **required representation:** described physical situation (given, prose or picture) → free-body diagram with labeled forces (produced)
- **reasoning architecture:** student identifies every force acting on a specified object (and only that object — a common error is including forces on other objects in the system) and represents them as vectors with appropriate relative magnitude and direction
- **misconception/distractor strategy:** watch for (a) omitted forces (commonly normal force or friction), (b) forces belonging to a different object in the system included by mistake, (c) a "motion force" drawn in the direction of travel that doesn't correspond to any real force
- **variation axes:** number of forces involved; static equilibrium vs. accelerating system; single object vs. multi-object system (requiring the student to correctly isolate just one)
- **DOK range:** 3
- **Bloom process descriptors:** Analyze, Apply
- **evidence produced:** whether a student can correctly identify which forces act on which object — the single most diagnostic skill for early mechanics understanding
- **works well when:** used consistently as a required first step before any force-based numeric problem, not just as a standalone task
- **avoid when:** never — this should be a default companion step attached to nearly every force-related problem, not a rare special architecture
- **security suitability:** Summative-safe
- **demonstration example:** "A book rests on a table. Draw a free-body diagram showing all forces acting on the book only (not the table). Label each force and explain why there is no net force on the book."
- **provenance:** standard, near-universal physics instructional architecture; explicitly a Science Practice skill embedded in the [[physics-curriculum]] learning ladders

---

## 22. Information Screening

### INFO-SCREEN-RELEVANT-IRRELEVANT-01
- **applicability:** all math/science courses
- **destinations:** Practice, Summative
- **content types:** any context-rich problem, data table, or graphic with more information than needed
- **response type:** short constructed-response
- **required representation:** data-rich context/table/graphic (given, with excess information) → identification of which pieces are needed vs. not, plus the solution (produced)
- **reasoning architecture:** student is explicitly asked to identify which given information is necessary for the specific question before/while solving — trains filtering as its own skill rather than assuming students will naturally ignore irrelevant data
- **misconception/distractor strategy:** distractor solutions incorporate an irrelevant piece of information into the calculation where it doesn't belong
- **variation axes:** how much excess information; whether irrelevant info is numeric (easy to spot) or contextual/narrative (harder to spot)
- **DOK range:** 2–3
- **Bloom process descriptors:** Analyze
- **evidence produced:** whether a student solves by understanding the problem's actual structure or by reflexively using every number given
- **works well when:** real-world, realistically messy contexts are used (paired well with MULTISTEP-REAL-CONTEXT-DECOMPOSE)
- **avoid when:** the excess information is so obviously irrelevant that no real filtering judgment occurs
- **security suitability:** Summative-safe
- **demonstration example:** "A recipe table lists ingredient amounts, prep time, and calories per serving for a dish that serves 4. A student wants to make enough for 10 people. Determine how much of each ingredient is needed, and identify which information in the table you did not need to use."
- **provenance:** Hess Cognitive Rigor Matrix DOK 2 descriptor "identify whether specific information is contained in graphic representations," extended to a full relevance-screening task

---

## 23. Verify Reasonableness / Self-Check

### VERIFY-REASONABLENESS-01
- **applicability:** all math/science courses
- **destinations:** Practice, Exit Ticket
- **content types:** any computed numeric result with a real-world interpretation
- **response type:** short constructed-response
- **required representation:** a computed answer (given, sometimes wrong by an order of magnitude or a sign error) → reasonableness judgment + explanation (produced)
- **reasoning architecture:** student evaluates whether a given numeric result makes sense in context (right order of magnitude, right sign, right units) without necessarily re-deriving it from scratch — a distinct skill from computing correctly in the first place
- **misconception/distractor strategy:** N/A; include both reasonable and unreasonable given answers across a set so "yes, this is reasonable" is sometimes correct too
- **variation axes:** type of error in the unreasonable case (order of magnitude, sign, wrong units, physically impossible result)
- **DOK range:** 3
- **Bloom process descriptors:** Evaluate
- **evidence produced:** whether a student has real-world number sense as a check on procedural work, catching the common "I got a negative answer for a length and didn't notice" failure mode
- **works well when:** used as a recurring, low-stakes exit-ticket habit rather than a rare special task
- **avoid when:** the context has no clear real-world sense to check against (purely abstract symbolic problems)
- **security suitability:** Formative
- **demonstration example:** "A student calculates the height a ball reaches after being thrown and gets an answer of -12 meters. Is this answer reasonable? Explain what the negative sign likely indicates about an error in the student's work."
- **provenance:** Hess Cognitive Rigor Matrix DOK 3 Evaluate descriptor, "verify reasonableness of results"; also directly reflects ESTIMATE-BEFORE-COMPUTE-01's complementary skill (checking after, rather than predicting before)

---

## 24. Transfer to Novel Context

### TRANSFER-NOVEL-CONTEXT-01
- **applicability:** all courses, especially strong for Summative/final review
- **destinations:** Summative, PT
- **content types:** any concept that's been taught in one recurring context and needs testing in a genuinely new one
- **response type:** extended constructed-response
- **required representation:** matches whatever the novel context requires
- **reasoning architecture:** the underlying concept/procedure is applied in a context structurally different from any example seen in instruction — not just new numbers in the same scenario type, but a different scenario type entirely that requires the same underlying mathematics
- **misconception/distractor strategy:** N/A; the core design constraint is that the surface context must genuinely differ from instructional examples, or this collapses into ordinary PROC-MULTISTEP practice
- **variation axes:** how far the transfer context is from instructional examples; whether the connection to the underlying concept is signaled or must be discovered
- **DOK range:** 3–4 (4 when the student must also recognize *that* the concept applies before applying it, with no signal)
- **Bloom process descriptors:** Apply, Analyze (recognition step)
- **evidence produced:** genuine understanding vs. context-bound pattern matching — the single best test of whether a skill has actually transferred
- **works well when:** used sparingly on summative assessments/finals specifically to distinguish deep from surface learners
- **avoid when:** used in routine practice, where predictable, signaled contexts are more appropriate for skill-building
- **security suitability:** Summative-safe, ideal use case
- **demonstration example:** "Exponential decay has been taught using radioactive half-life examples all unit. On the exam: 'A rumor spreads through a school such that the number of people who have NOT yet heard it decreases by 20% every hour. If 800 students haven't heard it at 8 AM, model the situation and determine when fewer than 50 students remain unaware.'" [same underlying exponential decay structure, unsignaled new context]
- **provenance:** Hess Cognitive Rigor Matrix DOK 3 Evaluate/Apply descriptor "apply understanding in a novel way"; general transfer-assessment principle standard in assessment design literature

---

## 25. Synthesis Across Multiple Sources

### SYNTHESIZE-MULTISOURCE-01
- **applicability:** APCalc, Physics, Chem, Bio, PT tasks generally
- **destinations:** PT, Summative (capstone)
- **content types:** any question answerable only by combining two distinct given sources/data sets
- **response type:** extended constructed-response
- **required representation:** two or more independent data sets/graphs/texts (given) → single integrated answer requiring both (produced)
- **reasoning architecture:** neither given source alone is sufficient to answer the question — student must identify what each source contributes and combine them, which is a distinct skill from using one source at a time
- **misconception/distractor strategy:** N/A; watch for students answering using only one of the given sources, missing that integration was required
- **variation axes:** number of sources (2 vs. 3+); whether sources agree, conflict, or are complementary
- **DOK range:** 4
- **Bloom process descriptors:** Analyze, Evaluate, Create
- **evidence produced:** whether a student can integrate multiple pieces of evidence into one coherent conclusion, a capstone-level skill
- **works well when:** used as a rare, high-value PT or final-review task
- **avoid when:** used routinely — DOK 4 multi-source synthesis is appropriately infrequent and cognitively demanding
- **security suitability:** Summative-safe
- **demonstration example:** "Source 1 is a table of a car's position over time. Source 2 is a separate graph of the same car's fuel consumption rate over time. Using both sources, determine during which time interval the car was both accelerating and consuming fuel most efficiently, and justify your answer using evidence from each source."
- **provenance:** Hess Cognitive Rigor Matrix DOK 4 Create descriptor, "synthesize information across multiple sources or texts"

---

## 26. Discrimination / Odd-One-Out

### DISCRIMINATE-ODD-ONE-OUT-01
- **applicability:** all math/science courses
- **destinations:** Warm-Up, Notes, Discourse/Reflection
- **content types:** any set of 3-4 items sharing multiple possible groupings
- **response type:** short constructed-response, open-ended
- **required representation:** 3–4 items (equations, graphs, figures, values) → identification of which doesn't belong + justification (produced) — deliberately designed so more than one defensible answer exists
- **reasoning architecture:** student selects one item from a small set as the outlier and justifies the choice using a specific mathematical property — because the set is designed so multiple items could be defensibly excluded, the value is entirely in the justification, not in matching a single "correct" answer
- **misconception/distractor strategy:** N/A (open-ended by design); the design skill is ensuring each of the items in the set actually could be defensibly excluded for a different, real reason
- **variation axes:** domain (numbers, graphs, equations, geometric figures); how many valid justification pathways exist
- **DOK range:** 3
- **Bloom process descriptors:** Analyze, Evaluate
- **evidence produced:** breadth of a student's property recognition — a student who can only find one valid grouping reveals narrower conceptual coverage than one who can articulate multiple
- **works well when:** used as a discussion-opener (small groups can disagree productively) rather than a single-answer graded item
- **avoid when:** grading strictly for one "correct" outlier — this defeats the architecture's entire purpose and punishes valid alternative reasoning
- **security suitability:** Formative/discussion-only; not appropriate as a single-answer summative item
- **demonstration example:** "Which one doesn't belong? (a) y = 3x + 2  (b) y = 3x² + 2  (c) y = -3x + 2  (d) y = 3x - 2. There is more than one reasonable answer — choose one and justify your reasoning using a specific mathematical property."
- **provenance:** Big Ideas Math's "Which One Doesn't Belong?" named recurring feature, explicitly documented as encouraging "debate and sense making" tied to Mathematical Practice 3 (construct viable arguments and critique the reasoning of others)

---

## 27. Geometry: Transformation, Similarity & Coordinate Proof

### GEOM-TRANSFORM-DESCRIBE-COMPOSITION-01
- **applicability:** Geo, Alg2
- **destinations:** Practice, Summative
- **content types:** sequences of rigid transformations mapping one figure to a congruent/similar one
- **response type:** short constructed-response
- **required representation:** two figures (given, before/after) → sequence of transformations that maps one to the other (produced)
- **reasoning architecture:** student must determine and describe a composition of two or more transformations (not just one) that accomplishes the mapping, since a single transformation is often insufficient — requires planning a sequence, not just recognizing one operation
- **misconception/distractor strategy:** distractors describe a transformation sequence that gets the position right but not the orientation, or vice versa
- **variation axes:** number of transformations needed in the composition; whether a dilation is included (similar vs. congruent)
- **DOK range:** 3
- **Bloom process descriptors:** Analyze, Apply
- **evidence produced:** whether a student can plan a multi-step transformation sequence, not just execute single named transformations
- **works well when:** the two figures cannot be mapped by any single transformation, forcing genuine composition reasoning
- **avoid when:** a single transformation suffices — reduces to simple identification, not composition planning
- **security suitability:** Summative-safe
- **demonstration example:** "Figure A and Figure B are congruent triangles, but Figure B is both rotated and in a different location relative to Figure A. Describe a sequence of transformations that would map Figure A onto Figure B exactly."
- **provenance:** standard geometry transformation-composition task type, common across Common-Core-aligned geometry sequences

### GEOM-COORDINATE-PROVE-PROPERTY-01
- **applicability:** Geo, Alg2
- **destinations:** Practice, PT, Summative
- **content types:** coordinate proof (parallelogram properties, right triangles, distance/midpoint-based classification)
- **response type:** extended constructed-response
- **required representation:** figure with coordinate vertices (given) → proof using distance/slope/midpoint formulas (produced)
- **reasoning architecture:** student proves a general geometric property using algebraic tools (slope for parallel/perpendicular, distance formula for congruent sides) applied to specific coordinates, connecting algebraic computation to geometric meaning explicitly
- **misconception/distractor strategy:** N/A; watch for students computing correct algebraic values (slopes, distances) without ever connecting them back to the geometric claim being proven (e.g., computing two equal slopes but never stating that this proves the sides are parallel)
- **variation axes:** which property is being proven (parallelogram, rectangle, isosceles triangle, right triangle); whether general or specific coordinates are used
- **DOK range:** 3
- **Bloom process descriptors:** Apply, Analyze
- **evidence produced:** whether a student connects algebraic computation to geometric conclusion, not just correct arithmetic
- **works well when:** bridging algebra and geometry units explicitly
- **avoid when:** the connecting statement (what the algebra proves geometrically) isn't required in the rubric — without it, this collapses into plain slope/distance practice
- **security suitability:** Summative-safe
- **demonstration example:** "A quadrilateral has vertices A(0,0), B(4,2), C(6,6), D(2,4). Use the slope formula to determine whether this quadrilateral is a parallelogram, and explain how your slope calculations support your conclusion."
- **provenance:** standard coordinate-geometry proof architecture, common across Common-Core-aligned geometry sequences (Pearson/Prentice Hall style Essential Understanding framing)

### GEOM-SIMILARITY-INDIRECT-MEASURE-01
- **applicability:** Geo
- **destinations:** Practice, PT
- **content types:** similar triangles, indirect measurement
- **response type:** short constructed-response
- **required representation:** real-world scenario with a measurable and an immeasurable quantity (given) → similar-triangle setup + solution (produced)
- **reasoning architecture:** student recognizes that a real-world situation (shadow length, mirror reflection, scale model) sets up similar triangles, and must justify the similarity (AA, SAS, etc.) before using the proportion to solve — the similarity justification is graded, not just the proportion arithmetic
- **misconception/distractor strategy:** distractor solutions set up the proportion with corresponding sides mismatched (a very common specific error in indirect measurement problems)
- **variation axes:** context (shadows, mirrors, scale drawings, map distances)
- **DOK range:** 3
- **Bloom process descriptors:** Apply, Analyze
- **evidence produced:** whether a student recognizes similarity structure in a real context and can correctly justify it, not just execute a memorized "shadow problem" template
- **works well when:** context varies enough that students can't pattern-match to one memorized shadow-problem setup
- **avoid when:** the same shadow-problem context is reused repeatedly — becomes memorized rather than reasoned
- **security suitability:** Summative-safe with context variation
- **demonstration example:** "A 6-foot-tall person standing near a streetlight casts a 4-foot shadow. At the same time, a nearby flagpole casts an 18-foot shadow. Explain why the person and the flagpole form similar triangles with their shadows, then find the height of the flagpole."
- **provenance:** standard indirect-measurement/similar-triangles application, common across geometry curricula (CPM's Similarity Toolkit eTool references this task family directly)

---

## 28. PreCalc: Trigonometric Reasoning

### TRIG-IDENTITY-VERIFY-STRATEGIC-01
- **applicability:** PreCalc, APCalc
- **destinations:** Practice, Summative
- **content types:** trig identity verification
- **response type:** extended constructed-response
- **required representation:** identity to verify (given) → strategic manipulation path (produced), working from one side to match the other
- **reasoning architecture:** student must choose a strategic starting point and manipulation path (which side to work from, which identity substitutions to try) rather than following a single memorized algorithm — genuinely different identities require different strategic entry points
- **misconception/distractor strategy:** N/A (constructed response); watch for students manipulating both sides simultaneously (not a valid proof technique) rather than working one side to match the other
- **variation axes:** which identities are needed (Pythagorean, sum/difference, double angle); how many valid strategic paths exist for this particular identity
- **DOK range:** 3
- **Bloom process descriptors:** Apply, Analyze
- **evidence produced:** strategic flexibility with identities, not just memorized substitution chains
- **works well when:** identity has multiple valid solution paths, so the strategic choice itself is meaningful
- **avoid when:** the identity has only one obvious path — reduces to PROC-MULTISTEP with no real strategic decision
- **security suitability:** Summative-safe
- **demonstration example:** "Verify the identity: (1 - cos²θ)/sinθ = sinθ. Show your work starting from the left side, and explain which identity you used to simplify the numerator."
- **provenance:** standard PreCalc trig-identity task structure, present across Finney-style and CPM-style precalculus sequences

### TRIG-CONNECT-UNITCIRCLE-GRAPH-EQUATION-01
- **applicability:** PreCalc
- **destinations:** Notes, Practice, Summative
- **content types:** unit circle, trig function graphs, trig equations
- **response type:** short constructed-response
- **required representation:** one of unit circle / graph / equation (given) → another representation (produced), specifically for periodic/trig relationships
- **reasoning architecture:** a specialization of REPTRANS-GRAPH-TABLE-EQUATION for the trig domain — student must connect angle position on the unit circle to the corresponding point on a sinusoidal graph, or vice versa, using period/amplitude/phase-shift structural features
- **misconception/distractor strategy:** distractors confuse period with amplitude, or get phase-shift direction backward
- **variation axes:** which representation pair; whether transformations (amplitude/period/phase shift) are involved
- **DOK range:** 2–3
- **Bloom process descriptors:** Understand, Apply
- **evidence produced:** whether trig understanding is unit-circle-native or graph-native or both, versus memorized in only one representation
- **works well when:** early in a trig-graphing unit, to prevent students from treating the unit circle and the graph as unconnected topics
- **avoid when:** the specific angle/point chosen is a "nice" special angle every time — vary to include non-special angles to prevent memorized lookup-table answers
- **security suitability:** Summative-safe
- **demonstration example:** "A point on the unit circle is at angle 5π/6. Without a calculator, determine the corresponding point on the graph of y = sin(x) at this x-value, and explain how the unit circle position determines the sign and approximate value."
- **provenance:** general PreCalc representation-transfer pattern, specialized from REPTRANS-GRAPH-TABLE-EQUATION-01 for periodic functions

---

## 29. Chemistry: Stoichiometry & Equilibrium

### CHEM-STOICH-FACTOR-LABEL-CHAIN-01
- **applicability:** Chem
- **destinations:** Practice, Summative
- **content types:** mole-mass-particle conversions, stoichiometric ratios
- **response type:** short constructed-response
- **required representation:** given quantity of one substance → quantity of another substance via a balanced equation (produced), showing the full factor-label chain
- **reasoning architecture:** a chemistry-specialized instance of PROC-MULTISTEP-CHAIN, where each conversion factor (molar mass, mole ratio from balanced equation, Avogadro's number) must be correctly selected and chained, with units canceling at each step
- **misconception/distractor strategy:** distractors use the wrong mole ratio (not accounting for balanced equation coefficients) or invert a conversion factor
- **variation axes:** starting/ending unit (mass, moles, particles, volume at STP); number of steps in the chain
- **DOK range:** 2
- **Bloom process descriptors:** Apply
- **evidence produced:** procedural fluency with the factor-label method specific to stoichiometry
- **works well when:** early in a stoichiometry unit, building the chain step by step before combining into longer multi-step conversions
- **avoid when:** used exclusively — pair with CHEM-EQUILIBRIUM-SHIFT-PREDICT or CER tasks so the unit isn't purely procedural
- **security suitability:** Summative-safe
- **demonstration example:** "Given the balanced equation 2H₂ + O₂ → 2H₂O, determine how many grams of water are produced from 5.0 grams of hydrogen gas, showing your full factor-label conversion chain."
- **provenance:** standard chemistry stoichiometry task structure, a domain-specialized instance of the PROC-MULTISTEP-CHAIN-01 architecture

### CHEM-EQUILIBRIUM-SHIFT-PREDICT-01
- **applicability:** Chem
- **destinations:** Practice, Summative
- **content types:** Le Chatelier's principle, equilibrium systems
- **response type:** short constructed-response
- **required representation:** equilibrium system + a described perturbation (given) → predicted shift direction + justification (produced)
- **reasoning architecture:** student predicts which direction an equilibrium will shift in response to a specific stress (concentration change, pressure change, temperature change) and must justify the prediction using the underlying principle, not just state a memorized rule
- **misconception/distractor strategy:** distractors misapply the principle to volume/pressure changes for reactions where moles of gas are equal on both sides (a specific common error), or confuse the direction of a temperature-based shift for endo- vs. exothermic reactions
- **variation axes:** type of stress (concentration, pressure/volume, temperature); whether moles of gas differ across the reaction (relevant for pressure changes)
- **DOK range:** 3
- **Bloom process descriptors:** Apply, Analyze
- **evidence produced:** whether a student applies Le Chatelier's principle through genuine reasoning about the system, or through memorized shift-direction rules that break down on edge cases (like equal-mole reactions under pressure change)
- **works well when:** the item set deliberately includes at least one edge case (equal moles of gas, so pressure changes don't shift equilibrium) to test genuine understanding vs. rule memorization
- **avoid when:** every instance is a "textbook standard" case — edge cases are what actually differentiate real understanding here
- **security suitability:** Summative-safe
- **demonstration example:** "For the reaction N₂(g) + 3H₂(g) ⇌ 2NH₃(g), predict the direction of shift if the volume of the container is decreased. Then, for a different reaction where moles of gas are equal on both sides, explain why decreasing volume would NOT cause a shift."
- **provenance:** standard chemistry equilibrium task structure; edge-case design specifically informed by the general error-diagnosis principle established in ERROR-DIAGNOSE-WORKED-SOLUTION-01

---

## 30. Selected-Response, Low-Stakes Optimized

### SELRESP-SINGLE-MISCONCEPTION-CHECK-01
- **applicability:** all courses
- **destinations:** Blooket, Quick Check, Warm-Up
- **content types:** any topic with one well-documented, specific misconception worth a fast check
- **response type:** selected-response (single best answer, 4 options)
- **required representation:** minimal — short prompt, no extended context needed
- **reasoning architecture:** designed for speed — one correct answer, and exactly one distractor engineered to catch one specific, named misconception; the other two distractors are plausible but not diagnostically targeted (they exist to prevent guessing, not to diagnose)
- **misconception/distractor strategy:** this IS the architecture — one distractor = the target misconception's answer, precisely. If you can't name the specific misconception a distractor represents, it's a filler distractor, not a diagnostic one — every item needs at least one real diagnostic distractor to justify using this architecture over a coin-flip check
- **variation axes:** which misconception; whether used as a pre-check (before instruction) or post-check (after)
- **DOK range:** 1–2 (this format is intentionally low-DOK — it's built for speed and diagnostic precision, not depth)
- **Bloom process descriptors:** Remember, Understand
- **evidence produced:** rapid, low-stakes signal of whether a specific misconception is present class-wide (aggregate response data is more valuable than any single response)
- **works well when:** used for fast formative checks (Blooket, warm-up polls) where speed and aggregate diagnostic signal matter more than depth
- **avoid when:** used as a Summative item, or when depth of understanding (not just presence/absence of one misconception) is the actual assessment target — this architecture is deliberately shallow by design
- **security suitability:** Formative/low-stakes only — not summative-safe, since selected-response with one obvious diagnostic distractor is easy to memorize
- **demonstration example:** "Simplify: -3² + 1. (A) 10  (B) -8  (C) 8  (D) -10" — where (A) results from the specific, common error of applying the negative sign before exponentiation instead of after (i.e., computing (-3)² instead of -(3²)).
- **provenance:** general fast-formative-check design principle, distinct from the constructed-response ERROR-DIAGNOSE architecture by being optimized for speed/aggregation rather than depth

---

## 31. AP Calculus: FRQ-Style Multi-Part Architectures

### FRQ-MULTIPART-SHARED-CONTEXT-01
- **applicability:** APCalc (meta-architecture; also generalizes to Physics extended problems)
- **destinations:** Summative, PT
- **content types:** any unit with 3+ skills that can share one setup
- **response type:** extended constructed-response, multi-part (typically 3–4 parts, labeled a/b/c/d)
- **required representation:** one shared context/setup (given) → multiple independently-scored sub-answers (produced), each testing a different skill against the same underlying object
- **reasoning architecture:** a single rich setup (a function, a table, a graph, a physical scenario) is probed from several different angles across sub-parts — each part is graded independently (partial credit for later parts even if an earlier part was wrong, using "follow-through" scoring), and later parts often depend conceptually (not numerically) on earlier ones
- **misconception/distractor strategy:** N/A; the design principle is "consistency, not correctness, is required for later parts" — a rubric should allow a student who made an early error to still earn later points if they used their own (incorrect) result correctly and consistently
- **variation axes:** number of parts; how tightly parts depend on each other conceptually; which skills are combined (this is the architecture that MULTISTEP-SYNTHESIS-CROSS-UNIT and REPTRANS-MULTIPLE-SIMULTANEOUS are both specific cases of)
- **DOK range:** 3, with individual parts ranging 1–3
- **Bloom process descriptors:** varies per part; the overall task typically spans Apply through Analyze
- **evidence produced:** a fuller picture of a student's understanding of one object from multiple angles, plus resilience — whether an early error cascades into total failure or the student can recover with follow-through work
- **works well when:** used as the default structure for Summative items testing an entire unit's connected skills around one rich object
- **avoid when:** the parts don't actually share meaningful structure — bolting unrelated questions together under one label isn't this architecture, it's just a numbered list
- **security suitability:** Summative-safe; this is the standard architecture for high-stakes assessment
- **demonstration example:** "A tank's water level is modeled by a differentiable function W(t). (a) Estimate W'(3) using given table data. (b) Is the water level increasing or decreasing at t=3? Justify using your answer to (a). (c) Using your value from (a), estimate W(3.5)." — part (c) uses the student's own (possibly imperfect) answer from (a) consistently, and should be scored on that consistency, not on independently re-deriving the right numeric value.
- **provenance:** structural pattern observed across AP Classroom Topic Questions scoring guides (format and point-allocation structure only — no specific problem content reproduced); this is also the canonical structure of released AP FRQs generally

### TABLE-ESTIMATE-RATE-FROM-DATA-01
- **applicability:** APCalc
- **destinations:** Practice, Summative
- **content types:** derivative/rate estimation from discrete data
- **response type:** short constructed-response
- **required representation:** data table with unevenly-spaced values (given) → difference-quotient estimate with units (produced)
- **reasoning architecture:** student selects the appropriate pair of table values surrounding the target point and computes a symmetric (or one-sided, if the target is at an endpoint) difference quotient as an estimate of the derivative — correct selection of which two table values to use is graded, not just the arithmetic
- **misconception/distractor strategy:** distractors use a one-sided difference when a symmetric one is available and more appropriate, or use non-adjacent table values
- **variation axes:** target point at interior vs. endpoint of the table; unevenly spaced table intervals (forces genuine selection reasoning rather than a fixed formula)
- **DOK range:** 2
- **Bloom process descriptors:** Apply
- **evidence produced:** whether a student understands the derivative as a rate estimated from local data, not only as a symbolic differentiation output
- **works well when:** paired with a units-justification requirement (units of the rate must be stated correctly, e.g., meters/second²)
- **avoid when:** the table is evenly spaced with only one obviously correct pair to use — a slightly irregular table produces better reasoning evidence
- **security suitability:** Summative-safe with new data sets
- **demonstration example:** "A particle's velocity is given at times t = 2, 5, 9, and 14 seconds in a table. Estimate the particle's acceleration at t = 9 seconds using the given data, showing your computation and including correct units."
- **provenance:** standard AP Calculus table-based rate-estimation task structure, observed consistently across AP Classroom Topic Questions covering derivative estimation from data (structure only)

### BOUND-JUSTIFY-VIA-SIGN-CONDITION-01
- **applicability:** APCalc
- **destinations:** Practice, Summative
- **content types:** accumulation/FTC reasoning, monotonicity arguments
- **response type:** short constructed-response
- **required representation:** a sign condition on a rate function (given) → an inequality bound on a related quantity's value (produced), without ever computing the quantity exactly
- **reasoning architecture:** student must justify that a quantity is greater than (or less than) some threshold using only a sign/monotonicity condition and the Fundamental Theorem of Calculus — the point is producing a rigorous bound argument, not a numeric answer, since the numeric answer is often not calculable from the given information
- **misconception/distractor strategy:** N/A; watch for students attempting to compute an exact value when only a bound is possible/required — recognizing that exact computation isn't available (and isn't needed) is itself part of the graded reasoning
- **variation axes:** which theorem/condition underlies the bound (positive derivative → increasing, positive integrand → positive net change); direction of the inequality
- **DOK range:** 3
- **Bloom process descriptors:** Analyze, Evaluate
- **evidence produced:** whether a student can reason rigorously about a quantity's value without needing to compute it exactly — a hallmark of genuine calculus understanding vs. purely computational fluency
- **works well when:** paired with an accumulation-function or velocity/position context in Unit 4 or 6
- **avoid when:** the exact value actually is computable from given information — using a bound-argument when a precise answer exists undersells what should be asked
- **security suitability:** Summative-safe
- **demonstration example:** "A particle starts at position 5 meters. Its velocity is positive for all 0 < t < 10. Explain why the particle's position at t = 10 must be greater than 5 meters, without calculating its exact position."
- **provenance:** observed structural pattern across AP Classroom Topic Questions covering contextual applications of differentiation/integration (structure only — this is a well-known, widely-taught AP Calculus reasoning pattern, not unique content)

### ACCUMULATION-FUNCTION-MULTIPART-01
- **applicability:** APCalc
- **destinations:** Practice, Summative
- **content types:** Fundamental Theorem of Calculus, accumulation functions defined as g(x) = [constant] + ∫f(t)dt
- **response type:** extended constructed-response, multi-part
- **required representation:** a graphically-defined integrand f (given, typically as a piecewise-linear graph) → evaluation, differentiation, and concavity analysis of the accumulation function g (produced across several parts)
- **reasoning architecture:** student must move fluently between the accumulation function g and its integrand f using FTC (g'(x) = f(x)), then use g' to reason about g's second derivative and concavity — all without ever having an explicit formula for f, working entirely from its graph
- **misconception/distractor strategy:** distractors confuse g and f's roles (e.g., reading concavity of g directly off the graph of f without applying FTC correctly), or fail to recognize when g''(x) doesn't exist because f isn't differentiable at that point (a graph with a corner)
- **variation axes:** how many derivative levels are probed (g, g', g''); whether a non-differentiable point in f is deliberately included to test DNE recognition
- **DOK range:** 3
- **Bloom process descriptors:** Apply, Analyze
- **evidence produced:** whether a student has an integrated, FTC-fluent understanding connecting a function's graph to multiple derivative levels of a related accumulation function
- **works well when:** used as a Unit 6 capstone item — this architecture efficiently tests several connected FTC skills in one task
- **avoid when:** used before FTC itself has been solidly taught — this is a synthesis architecture, not an introductory one
- **security suitability:** Summative-safe with a new graph each version
- **demonstration example:** "The graph of a piecewise-linear function f is given on [-4, 6], with a corner at x=2. Let g(x) = 3x + ∫₀ˣ f(t)dt. Find g(2). Find g'(x) in terms of f(x). Determine whether g''(2) exists, and explain why or why not."
- **provenance:** structural pattern observed consistently across AP Classroom Topic Questions covering Unit 6 (Integration and Accumulation of Change); also directly reflected in the AP Calculus CED's emphasis on FTC as a connecting theorem across units

### COMPOSE-ABSTRACT-FUNCTION-DERIVATIVE-01
- **applicability:** APCalc
- **destinations:** Practice, Summative
- **content types:** chain rule, product rule, quotient rule applied to functions defined only by graph or table (not explicit formula)
- **response type:** short constructed-response
- **required representation:** two or more functions defined abstractly (given, via graph/table, with only specific values/derivative-values known) → a derivative of their composition/product/quotient evaluated at a specific point (produced)
- **reasoning architecture:** student applies a differentiation rule symbolically first (writing the general rule in terms of the abstract functions), then substitutes only the specific known values — this differs fundamentally from PROC-SELECT-STRATEGY because there's no explicit formula to differentiate directly; the rule must be applied at the structural/notational level before any arithmetic happens
- **misconception/distractor strategy:** distractors substitute values before applying the rule correctly (e.g., trying to "compute" f(g(x)) numerically first, which isn't well-defined without a formula), or misidentify which given value corresponds to which piece of the rule
- **variation axes:** which rule (chain, product, quotient); how many functions are abstractly defined vs. explicit
- **DOK range:** 3
- **Bloom process descriptors:** Apply, Analyze
- **evidence produced:** whether a student understands differentiation rules as general symbolic relationships (transferable to any function, known or not) rather than formula-manipulation tied to explicit algebraic expressions
- **works well when:** reinforcing that derivative rules are structural, not tied to having an explicit formula — a common AP-level gap
- **avoid when:** introducing a new differentiation rule for the first time — abstract-function application should follow, not precede, formula-based practice
- **security suitability:** Summative-safe
- **demonstration example:** "Given that h(x) = f(g(x)), where f(3) = 5, f'(3) = 2, g(1) = 3, and g'(1) = 4, find h'(1)."
- **provenance:** structural pattern observed consistently across AP Classroom Topic Questions covering Unit 3 (Composite, Implicit, and Inverse Functions); a well-established, widely-taught AP Calculus task structure

### NONEXISTENCE-VALID-ANSWER-01
- **applicability:** APCalc, PreCalc
- **destinations:** Practice, Summative
- **content types:** derivatives at non-differentiable points, limits at discontinuities, any concept with a legitimate "does not exist" outcome
- **response type:** short constructed-response
- **required representation:** a function/graph with at least one point where a requested quantity doesn't exist (given) → correct identification of non-existence with justification (produced), mixed among other sub-questions that DO have computable answers
- **reasoning architecture:** at least one item in a set is deliberately constructed so that "does not exist" (or "cannot be determined from the given information") is the correct, fully-creditable answer — this breaks the default assumption that every question has a computable numeric answer, which is otherwise reinforced by nearly every other architecture in this library
- **misconception/distractor strategy:** N/A; the entire point is testing whether a student will force an answer where none exists rather than recognizing and justifying the non-existence
- **variation axes:** why the quantity doesn't exist (a corner/cusp, a jump discontinuity, insufficient given information, an undefined operation); whether it's mixed among items with real answers (recommended) or isolated
- **DOK range:** 3
- **Bloom process descriptors:** Analyze, Evaluate
- **evidence produced:** whether a student has genuine conceptual understanding of existence conditions, or is trained to always produce a number
- **works well when:** deliberately mixed into a set alongside normally-answerable items — the contrast is what makes it diagnostic
- **avoid when:** used in isolation as an obvious "gotcha" flagged by context — the diagnostic value comes from it being indistinguishable in framing from a normal item until the student actually reasons through it
- **security suitability:** Summative-safe
- **demonstration example:** "The graph of f has a corner at x = 2. State whether f'(2) exists. If it does, find its value. If it does not, explain why, referencing the specific graphical feature that causes it."
- **provenance:** structural pattern observed repeatedly across AP Classroom Topic Questions (the "find the value, or state that it does not exist" phrasing recurs across multiple units) — this framing pattern itself, not any specific instance, is the architecture

### DIFFERENTIATE-WITH-SYMBOLIC-PARAMETER-01
- **applicability:** APCalc, PreCalc, Alg2
- **destinations:** Practice, Summative
- **content types:** any procedure (differentiation, solving, simplification) where a letter constant is carried through instead of a specific number
- **response type:** short constructed-response
- **required representation:** an expression containing a symbolic parameter (given, e.g., k, a, or b as an arbitrary constant) → the procedure's result, left in terms of that parameter (produced)
- **reasoning architecture:** student carries a literal constant through an entire procedure without ever needing (or being able) to substitute a numeric value for it — this tests whether procedural fluency is tied to specific numbers or genuinely general
- **misconception/distractor strategy:** distractors treat the parameter inconsistently partway through (e.g., correctly carrying it through the first differentiation step but then dropping or mishandling it in a subsequent step, such as an incorrect power-rule application to the parameter itself)
- **variation axes:** which procedure; how many times the parameter must be correctly carried through multiple steps
- **DOK range:** 2–3 (3 when multiple dependent steps must each correctly retain the parameter)
- **Bloom process descriptors:** Apply, Analyze
- **evidence produced:** whether procedural understanding is general (works for any value) or dependent on having concrete numbers to compute with
- **works well when:** following any procedure that's been practiced extensively with numeric values — this is a natural fluency check that the procedure is understood symbolically
- **avoid when:** introducing the procedure for the first time — symbolic-parameter versions should come after numeric fluency is established, not before
- **security suitability:** Summative-safe
- **demonstration example:** "Let f(x) = k·x³ − 2x, where k is a positive constant. Find f'(x) and f''(x) in terms of k."
- **provenance:** structural pattern observed across AP Classroom Topic Questions in multiple units (differentiation rules applied to functions with an arbitrary positive constant) — a standard AP-level technique for testing generalized procedural understanding

### INVARIANT-PROVE-PARAMETER-INDEPENDENT-01
- **applicability:** APCalc, Alg2, PreCalc
- **destinations:** Summative, PT
- **content types:** optimization, extrema, any result that turns out to be independent of a parameter defining a family of functions/objects
- **response type:** extended constructed-response
- **required representation:** a family of functions/objects defined by a parameter (given) → algebraic proof that a specific computed result (an extremum's value, an intersection point, etc.) is the same for every value of that parameter (produced)
- **reasoning architecture:** an extension of PARAM-VARY-CONJECTURE and INVARIANT-IDENTIFY into a formal proof requirement — rather than conjecturing an invariant from a few numeric trials, the student must algebraically show the result holds for the arbitrary/general parameter value, which is a strictly higher bar than pattern-noticing
- **misconception/distractor strategy:** N/A (constructed response); the most common failure is checking the claim for a few specific parameter values and treating that as sufficient proof — this is exactly the gap between ARGUE-JUSTIFY-GENERAL-CASE's DOK 3 empirical-checking failure mode and genuine DOK 4 general proof
- **variation axes:** what kind of family (linear family, exponential family, geometric family); what result is shown to be invariant (an extremum value, a limit, a rate)
- **DOK range:** 4
- **Bloom process descriptors:** Analyze, Create
- **evidence produced:** the clearest possible distinction between empirical pattern-noticing and rigorous general proof — a capstone-level skill
- **works well when:** used as a rare, high-value final part of a larger multi-part item (this pairs naturally as the culminating part of FRQ-MULTIPART-SHARED-CONTEXT)
- **avoid when:** used routinely — genuinely proving parameter-independence is appropriately rare and demanding
- **security suitability:** Summative-safe
- **demonstration example:** "For the family of functions y = a·xe^(ax), where a is a nonzero constant, show algebraically that the absolute minimum value of the function is the same for every nonzero value of a."
- **provenance:** structural pattern observed directly in an AP Classroom Topic Question (Unit 1) — the "show that the result is the same for all nonzero values of b" framing; the general architecture (not the specific function or context) is what's extracted here

---

## 32. Metacognitive Reflection & Self-Assessment

### SELFASSESS-CONFIDENCE-RESPOND-01
- **applicability:** all courses, especially as a unit-closing routine
- **destinations:** Notes, Discourse/Reflection (unit closure)
- **content types:** any set of problems spanning a unit's range of skills
- **response type:** short constructed-response, self-directed
- **required representation:** a completed set of practice problems (given, already attempted) → confidence rating per problem + a differentiated follow-up task depending on that rating (produced)
- **reasoning architecture:** after attempting a representative problem set, student rates their own confidence/comfort on each problem, then completes a different follow-up task depending on the rating — low-confidence items prompt the student to articulate specific questions or list what they *do* know (partial-knowledge surfacing); high-confidence items prompt the student to either explain the problem to a hypothetical struggling peer or write a harder variant — the follow-up task itself is the graded evidence of genuine self-assessment, not just the rating number
- **misconception/distractor strategy:** N/A; the design risk is students rating everything as high-confidence to avoid the harder follow-up work — pairing the follow-up tasks so the "high confidence" branch is also nontrivial (write a harder problem, not just "nothing to do") counteracts this
- **variation axes:** which follow-up tasks are offered at each confidence level; whether ratings are private/self-only or shared with the teacher for grouping
- **DOK range:** varies by follow-up task chosen (the rating itself is DOK 1; the low-confidence question-generation or high-confidence harder-problem-writing follow-ups are DOK 2–3)
- **Bloom process descriptors:** Evaluate (self-assessment), Create (follow-up task, either direction)
- **evidence produced:** metacognitive accuracy — whether a student's self-rated confidence actually predicts their performance — plus specific, actionable information about exactly where a low-confidence student is stuck
- **works well when:** used consistently as a unit-closing routine so students build the habit of honest self-assessment over time
- **avoid when:** used as a graded/scored task on correctness — this architecture's value is in honest self-report, which is undermined the moment it's graded like a content question
- **security suitability:** Formative only
- **demonstration example:** "For each of the 6 problems you just completed, shade a bar from 0 (not confident at all) to 10 (very confident) showing your comfort level. For any problem rated below 5, write two specific questions you'd want answered about that problem type. For any problem rated 8 or above, write a new problem of the same type that would be more challenging, and solve it."
- **provenance:** CPM's chapter closure "What Have I Learned?" self-assessment structure (documented recurring closure-section pattern across CPM courses, not a specific problem)

---

## 33. Reverse Narrative / Context Invention from Data

### GRAPH-TO-NARRATIVE-01
- **applicability:** Alg1, Alg2, Physics
- **destinations:** Notes, Discourse/Reflection, Practice
- **content types:** any graph with distinct qualitative features (increasing/decreasing/flat segments, sharp changes)
- **response type:** short constructed-response
- **required representation:** an abstract graph with no context (given, axes may even be unlabeled or generically labeled) → an invented real-world story consistent with every feature of the graph (produced)
- **reasoning architecture:** the reverse of GRAPH-INFER-BEHAVIOR-01 — instead of extracting behavior from a graph, the student invents a plausible context whose story matches every qualitative feature of the given graph (every flat section, increase, decrease, and sharp change must correspond to something explicit in the story) — this tests whether graphical features carry real meaning for the student, not just names
- **misconception/distractor strategy:** N/A; common failure is a story that gets the overall shape right but ignores a specific feature (e.g., explaining the increasing/decreasing parts but never addressing why there's a flat section)
- **variation axes:** how many distinct features the graph has (more features = harder to account for all of them); whether axes are labeled with units or left abstract
- **DOK range:** 3
- **Bloom process descriptors:** Understand, Create
- **evidence produced:** whether a student's graph-reading is genuinely meaningful (can generate context) rather than only receptive (can answer questions about a given context)
- **works well when:** used after GRAPH-INFER-BEHAVIOR has been practiced in the forward direction
- **avoid when:** the graph is too simple (a single straight line) to require accounting for multiple distinct features
- **security suitability:** Formative-preferred (open-ended, hard to standardize grading for summative use)
- **demonstration example:** "The graph shows distance from home over time: distance increases steadily, then stays flat for a while, then increases more steeply, then drops sharply back to zero. Write a short story about someone's trip that matches every feature of this graph, and explain which part of your story corresponds to each section."
- **provenance:** CPM chapter closure task type — "interpret the graph to tell a story about what could have happened" (documented recurring closure pattern, general framing only, not a specific problem's context)

---

## 34. Numeric Puzzle / Factor-Pair Fluency

### FACTORPAIR-SUM-PRODUCT-PUZZLE-01
- **applicability:** Alg1 (pre-factoring fluency), cross-curricular warm-up
- **destinations:** Warm-Up, Notes
- **content types:** factoring trinomials (as a fluency precursor), integer operations
- **response type:** short constructed-response, puzzle format
- **required representation:** a given sum and product (or two of three related quantities in a small fixed structure) → the two numbers satisfying both conditions (produced)
- **reasoning architecture:** student finds two numbers that simultaneously satisfy a given sum and a given product — a compact, fast-cycling fluency task that directly builds the number-sense prerequisite for factoring trinomials (where the same sum/product reasoning is applied to the linear and constant coefficients), without yet requiring the full factoring procedure
- **misconception/distractor strategy:** distractors satisfy one condition (sum or product) but not both — a common shortcut error is stopping after finding a pair that satisfies just the more obvious of the two conditions
- **variation axes:** positive/negative combinations (four sign cases: both positive, both negative, mixed with larger positive, mixed with larger negative — each requires slightly different number-sense reasoning); whether the puzzle is presented visually (e.g., in a simple two-cell structure) or as a plain sum/product statement
- **DOK range:** 1–2
- **Bloom process descriptors:** Apply
- **evidence produced:** rapid diagnostic signal of the specific sum-product number sense that later supports factoring fluency — a well-isolated prerequisite skill check
- **works well when:** used as a warm-up routine in the weeks immediately before formally introducing trinomial factoring
- **avoid when:** used in isolation without ever being connected explicitly to the factoring procedure it supports — the payoff is in making that connection explicit
- **security suitability:** Formative/Practice
- **demonstration example:** "Find two numbers whose sum is -3 and whose product is -40."
- **provenance:** CPM's recurring "Diamond Problem" warm-up puzzle format, a widely-used sum/product fluency device (the underlying sum-product task structure is described generically here; the specific graphic device is CPM's own recurring feature)

---

## 35. Notice & Wonder / Three-Act Structure

### NOTICE-WONDER-ESTIMATE-REVEAL-01
- **applicability:** all math/science courses (strongest for Alg1/Alg2/Physics contextual problems)
- **destinations:** Notes, PT (lesson-opening activity)
- **content types:** any real-world scenario with a genuinely surprising or curiosity-provoking quantity
- **response type:** extended, multi-stage constructed-response (not a single question — a full lesson-arc activity)
- **required representation:** a real-world image, video, or brief scenario (given, with deliberately withheld numeric information) → student-generated question, three estimates (too-low, too-high, best-guess), a stated information request, and finally a compare-to-reveal reflection (produced, across stages)
- **reasoning architecture:** unlike every other architecture in this library, the mathematical question itself is not given — students first generate their own question from an intentionally sparse, curiosity-provoking prompt, commit to a range of estimates (forcing an early number-sense judgment before any computation), explicitly request the specific information they believe they need (testing whether they can identify what's relevant), solve, and then compare their answer to a revealed real value — this full arc is the architecture, not any single step within it
- **misconception/distractor strategy:** N/A; this is fundamentally a formative, discussion-driving structure rather than a graded-response format
- **variation axes:** how sparse Act 1 is; whether the "reveal" is a real measured value or a computed one; how much the requested-information step is scaffolded vs. fully open
- **DOK range:** 3–4 (problem formulation and information-need identification are themselves DOK 3+ tasks, before any computation begins)
- **Bloom process descriptors:** Analyze (question formulation), Apply (solving), Evaluate (comparing to the reveal)
- **evidence produced:** whether students can formulate their own mathematical questions and identify necessary information from an unstructured real situation — the single hardest and most authentic modeling skill, and one that every other architecture in this library assumes has already been done for the student
- **works well when:** used to open a unit or introduce a new modeling context, where curiosity and question-generation are the actual instructional goal
- **avoid when:** used as a routine daily structure — it's intentionally time-intensive and loses its curiosity-driven power if overused; also avoid when the "reveal" doesn't actually resolve cleanly (a weak Act 3 undermines the whole arc)
- **security suitability:** Formative only; not a gradable summative item in the traditional sense
- **demonstration example:** "Show students a photo of a large stack of identical boxes with no visible count or measurements. Ask: what do you notice? What do you wonder? After the class settles on 'how many boxes are in the stack,' have students commit to a too-low estimate, a too-high estimate, and a best guess. Ask what information they'd need to figure it out (they should request box dimensions and stack dimensions). Provide that information, have them solve, then reveal the actual count and discuss the gap between the estimate and the reveal."
- **provenance:** Dan Meyer's "Three-Act Math" task structure (Act 1: notice/wonder with withheld information; Act 2: information request and solving; Act 3: reveal and compare to estimates) — a well-documented, widely-adopted instructional framework, described generically here without reproducing any specific published three-act task

---

## 36. Constrained Optimization (Open Middle Style)

### OPTIMIZE-CONSTRAINED-ARRANGEMENT-01
- **applicability:** Alg1, Alg2, cross-curricular (adaptable to any grade band)
- **destinations:** Warm-Up, Practice, Notes
- **content types:** any task where a fixed set of digits/values must be arranged to satisfy an expression, then optimized
- **response type:** short constructed-response, open-ended within a closed answer space
- **required representation:** a fixed set of values/digits and an expression template with blanks (given) → an optimal (maximum or minimum) arrangement (produced)
- **reasoning architecture:** the task has a closed beginning (same starting materials for everyone) and a closed end (everyone is working toward the same type of optimal answer — maximum or minimum), but the middle is genuinely open: there are multiple valid strategies to reach the optimum, and reaching it requires reasoning about how each value's placement affects the result, not just guess-and-check — the richness comes from students being able to compare and justify *why* their arrangement is optimal, not just report a final value
- **misconception/distractor strategy:** N/A; the design principle is ensuring the optimization genuinely requires structural reasoning about place value/operation order rather than being solvable by exhaustive guess-and-check in a trivial amount of time
- **variation axes:** which digits/values are provided; which expression template; maximize vs. minimize; how many blanks (more blanks = larger search space, richer strategic reasoning required)
- **DOK range:** 3
- **Bloom process descriptors:** Analyze, Evaluate
- **evidence produced:** whether a student reasons structurally about how placement affects outcome (e.g., understanding that the largest digit should go in the highest place value for maximizing a sum of products) versus solving by trial and error alone
- **works well when:** used as a fast-cycling warm-up that still requires genuine strategic thinking — this architecture is unusually good at producing DOK 3 reasoning in a short, low-prep format
- **avoid when:** the search space is small enough that trial-and-error is just as fast as genuine reasoning (defeats the purpose) — the value comes from a search space large enough to reward structural insight
- **security suitability:** Summative-safe if numbers/template vary; Formative-ideal for daily warm-ups
- **demonstration example:** "Using each of the digits 1, 2, 3, 4 exactly once, fill in the blanks to create the equation ▢▢ + ▢▢ that has the greatest possible sum. Then find the arrangement with the least possible sum. Explain the placement strategy you used for each."
- **provenance:** Robert Kaplinsky's "Open Middle" task format (closed beginning, closed end, open middle) — a well-documented, widely-used instructional framework; described generically here as a task structure, not any specific published Open Middle problem

---

## 37. Guided Inquiry Model Cycle

### MODEL-GUIDED-INQUIRY-CYCLE-01
- **applicability:** Chem, Bio, Physics, Alg1/Alg2 (concept-introduction contexts)
- **destinations:** Notes, PT (concept-introduction activities)
- **content types:** any concept that can be discovered from a well-chosen model/data set rather than told directly
- **response type:** extended constructed-response, sequenced question set (typically team-based)
- **required representation:** a model (given: data table, diagram, or simulation output) → a sequence of three question types answered in order (produced): directed questions (surface-level, ensure the model is read correctly), convergent questions (synthesize a pattern/relationship from the model into a stated concept), and application questions (apply the newly-formed concept to a new, unseen situation)
- **reasoning architecture:** the three-phase sequence is the architecture itself — directed questions must be answered correctly before convergent questions are attempted (they ensure the model has been read correctly, preventing concept-invention from a misread model), convergent questions require the team to articulate the concept in their own words (not just recognize it), and application questions test genuine transfer to unseen situations — skipping the directed phase or the application phase breaks the cycle's diagnostic value
- **misconception/distractor strategy:** N/A; the failure mode this guards against is students reaching a "concept invention" question without having correctly processed the underlying model — hence directed questions must be sequenced first, not skipped
- **variation axes:** what the model is (data table, diagram, simulation, graph); how many directed/convergent/application questions in the sequence; team vs. individual completion
- **DOK range:** spans 1 (directed) through 3 (application) within a single activity — the sequence itself is the point, not any single question's level
- **Bloom process descriptors:** Remember/Understand (directed), Analyze (convergent), Apply (application)
- **evidence produced:** a full diagnostic trace of where a team's understanding broke down — whether at model-reading, concept-formation, or transfer — rather than a single pass/fail signal
- **works well when:** introducing a new concept that has a clean underlying model or pattern (e.g., gas laws from pressure/volume/temperature data, or the effect of a coefficient on a function's graph) — this architecture is specifically for concept *discovery*, not review
- **avoid when:** used for review of an already-taught concept — the guided-discovery structure is wasted effort if the concept is already known; also avoid when no clean underlying model/pattern exists to discover
- **security suitability:** Formative only — this is fundamentally a team discovery activity, not a gradable individual assessment item
- **demonstration example:** "[Model: a data table showing pressure and volume measurements for a gas at constant temperature.] Directed: What happens to volume as pressure increases in the table? Convergent: Write a general statement (in your own words) describing the relationship between pressure and volume shown in the data. Application: Using your statement, predict what would happen to the volume of a different gas sample if its pressure were tripled."
- **provenance:** POGIL (Process Oriented Guided Inquiry Learning) — a well-established, widely-used instructional framework originating in chemistry education (three-phase learning cycle: exploration/directed questions, concept invention/convergent questions, application/divergent questions), described generically here as a task-sequencing architecture

---

## 38. Peer Construction & Precision Communication

### CONSTRUCT-REPLICATE-CONJECTURE-01
- **applicability:** Geo, Alg1 (early function/pattern discovery contexts)
- **destinations:** Notes, PT (discovery activities)
- **content types:** any geometric or numeric property that holds invariantly across independently-constructed instances (angle sums, always-true relationships)
- **response type:** extended constructed-response, team-based, hands-on
- **required representation:** a set of construction conditions (given, e.g., specific angle/side measurements) → independently-built physical or digital constructions (produced by each team member separately) → compared results → a stated conjecture about what's invariant across all of them
- **reasoning architecture:** each team member independently constructs a figure/object satisfying the same given conditions without seeing others' work first, then the team compares results to check whether everyone's construction matches and to measure/identify what stayed constant across all independent constructions — the independence-then-compare structure is what makes the resulting conjecture trustworthy (it isn't just one example, it's convergent evidence from several independent attempts), and a technology-based verification step (dynamic geometry tool) typically follows to test the conjecture against additional cases beyond what was hand-constructed
- **misconception/distractor strategy:** N/A; watch for teams comparing results before each member has finished their own independent construction — the independence is what gives the comparison its evidentiary value, so sequencing matters
- **variation axes:** what property is being discovered (angle sum, a numeric pattern, a scaling relationship); whether a follow-up technology-verification step is included
- **DOK range:** 3–4 (4 if the technology-verification step extends testing to cases beyond what was physically constructed, approaching genuine generalization)
- **Bloom process descriptors:** Analyze, Create (conjecture formation)
- **evidence produced:** whether a student trusts a pattern because of convergent independent evidence (a genuine scientific-reasoning habit) rather than accepting a single example or being told the result directly
- **works well when:** introducing a new geometric theorem or numeric relationship that's genuinely discoverable through hands-on construction, rather than told directly first
- **avoid when:** the property isn't actually discoverable this way (too abstract for physical/independent construction) or when time constraints don't allow for genuine independent work before comparison
- **security suitability:** Formative only — this is a discovery activity, not a gradable item
- **demonstration example:** "Without looking at your teammates' work, each person should independently draw a quadrilateral with one angle measuring 100° and two sides of length 4 cm. Compare your constructions with your team — are they all the same shape? Measure all four angles in your quadrilateral and find their sum. Compare sums across the team. What do you notice? Then use a dynamic geometry tool to test your conjecture with two more quadrilaterals that don't share these same starting conditions."
- **provenance:** CPM's independent-construction-then-compare lesson structure (documented recurring pattern across CPM geometry-strand lessons, general framing only, not a specific problem's numbers/context)

### DESCRIBE-TO-REPRODUCE-01
- **applicability:** Geo, Alg1, Alg2 (any topic where an object can be fully specified by a set of conditions/properties)
- **destinations:** Notes, Practice (paired/team activities)
- **content types:** geometric figures, functions, data sets — anything specifiable by a list of defining conditions
- **response type:** short constructed-response, paired activity (two distinct roles: describer and reproducer)
- **required representation:** a target object known only to the describer (given/chosen by student A) → a written set of conditions precise enough for a partner to reproduce it without seeing it (produced by student A) → the partner's reproduction attempt based solely on the description (produced by student B) → comparison and correction
- **reasoning architecture:** student A must identify which properties of an object are *sufficient* to uniquely specify it (not too few — ambiguous, not too many — redundant) and communicate them with mathematical precision; student B must correctly interpret and execute purely from the written description with no visual access to the original — this is fundamentally a precision-of-mathematical-language task, testing whether a student's understanding is precise enough to transmit without the crutch of a shared visual reference
- **misconception/distractor strategy:** N/A; the natural failure modes are diagnostic themselves — an under-specified description (partner produces a valid but different object) reveals the describer didn't identify a sufficient condition set; if the reproduction is correct, the describer's understanding of what defines the object is confirmed precise
- **variation axes:** what kind of object (triangle by side/angle conditions, a function by a list of properties, a data set by summary statistics); whether roles are swapped so both students practice both sides
- **DOK range:** 3
- **Bloom process descriptors:** Understand, Create (precise specification), Apply (reproduction from specification)
- **evidence produced:** precision of mathematical communication and understanding of which properties are defining vs. incidental for a given object — a skill distinct from being able to construct or identify an object when given a visual
- **works well when:** following CONSTRUCT-REPLICATE-CONJECTURE or any lesson establishing what properties define a category of object
- **avoid when:** the object has only one or two defining properties (too simple to require genuine precision) — richer objects (quadrilaterals, functions with several stated behaviors) produce better evidence
- **security suitability:** Formative only (paired activity, not independently gradable)
- **demonstration example:** "Without showing your partner, write down three specific conditions that define a unique triangle (for example, side lengths and/or angle measures). Trade descriptions with your partner and have them draw the triangle from your description alone — they may not ask clarifying questions. Compare the resulting triangle to what you intended. If it doesn't match, discuss what was missing or ambiguous in your description."
- **provenance:** CPM's reciprocal partner-construction task structure ("write down conditions, trade papers, verify without drawing it for them") — documented recurring lesson pattern; conceptually parallel to the widely-used Desmos "Polygraph" describe-to-identify activity format, though extracted here directly from the CPM source material

---

## 39. Part-Whole Decomposition

### PARTWHOLE-PERCENT-DECOMPOSITION-01
- **applicability:** Alg1, cross-curricular (proportional reasoning)
- **destinations:** Practice, Warm-Up
- **content types:** percent-of-a-whole problems where several known parts must reconcile with a total
- **response type:** short constructed-response or table completion
- **required representation:** several parts of a whole, given as a mix of percentages and absolute amounts, with exactly one part unknown (given) → the missing part, found using the constraint that all parts must sum to the whole (produced)
- **reasoning architecture:** student must recognize that the parts collectively constrain the unknown (they must sum to 100% / the total amount) rather than solving each part in isolation — this differs from a simple "find X% of Y" task because the missing-part value can only be found by using the whole-sum constraint across all given parts simultaneously
- **misconception/distractor strategy:** distractors compute the missing part using an assumed or incorrect total instead of correctly deriving the total from the given parts first, or fail to convert consistently between percentage and absolute-amount parts before combining them
- **variation axes:** whether parts are given as a mix of percents and amounts (harder, requires unit reconciliation) or all one type; how many known vs. unknown parts
- **DOK range:** 2–3 (3 when parts are given in mixed units requiring reconciliation before the sum-constraint can be applied)
- **Bloom process descriptors:** Apply, Analyze
- **evidence produced:** whether a student reasons about parts-of-a-whole as a constrained system rather than a set of independent percent calculations
- **works well when:** following direct percent-of-a-whole instruction, as a step up in reasoning complexity
- **avoid when:** all parts are given in the same unit and the missing part is simply "100% minus the others" with no real reconciliation needed — vary the units to keep the reasoning genuine
- **security suitability:** Summative-safe with new values
- **demonstration example:** "A charity's annual budget is spent on four categories. Category A is 35% of the budget. Category B is $18,000. Category C is 20% of the budget. Category D is the remainder. If the total budget is $120,000, find the amount and percentage spent on Category D."
- **provenance:** CPM's recurring part-whole percent decomposition task type (documented recurring pattern in CC Course 1 percent-unit lessons, general framing only, not a specific problem's context or numbers)

---

## Coverage Notes (Tranche 5 update)

Tranches 1–5 combined: **72 architectures across 39 categories.**

This tranche returned to the CPM download specifically to sample courses not yet
examined in depth (CC Course 1 / grade 6, and CC Course 2 / grade 7 non-closure
lessons). The richest find was CPM's independent-construction-then-compare lesson
structure, which produced two genuinely new architectures around precision of
mathematical communication and convergent-evidence conjecture formation — neither
derivable from ordinary practice-problem sampling, since their value is in the
paired/team process around the task rather than in a single question.

Remaining known gaps for a future tranche:
- Biology-specific architectures (genetics/Punnett-square reasoning, homeostasis/feedback-loop reasoning, phylogenetic-tree interpretation)
- Statistics-specific architectures
- Geometry proof architectures beyond coordinate proof (two-column/flow proof construction, indirect/contradiction proof)
- AP Calculus Units 7–8 from the aptopics source (differential equations, applications of integration — zip files available but not yet sampled)
- Desmos Classroom activity structures (Polygraph, card sorts) — DESCRIBE-TO-REPRODUCE-01 covers similar territory now, but Desmos's specific card-sort/matching format may still add something distinct
- A dedicated "peer-critique exchange" architecture using real, unscripted peer work rather than a pre-written flawed solution

## Provenance Sources Consulted (structure-only, no content reproduced)

**Tranche 1:**
- CPM Educational Program eBooks (CC Course 1–3, CC Algebra) — collaborative multi-representation task style, model-comparison framing, line-of-best-fit structure
- Glencoe/McGraw-Hill Algebra 1 (Study Guide and Intervention, Homework Practice, Study Notebook) — worked-example + skill-drill structure, deductive reasoning/counterexample lesson type
- Pearson Algebra 1 (Common Core edition) — Essential Understanding framing, Mathematical Practices tagging
- Finney/Demana/Waits/Kennedy, *Calculus: Graphical, Numerical, Algebraic* — Model→Solve→Interpret process framing, Exploration/discovery structure
- College Board AP Calculus AB/BC Course and Exam Description — explicit Skills taxonomy (1.C, 2.B, 2.C, 3.C, 3.D, etc.), Sample Instructional Activities (Work Backward, Think Aloud, Create Representations)

**Tranche 2 (additional publisher/framework sources, web-sourced, structure-only):**
- Karin Hess, *Cognitive Rigor Matrix & Curricular Examples: Applying Webb's DOK to Bloom's Cognitive Process Dimensions — Math/Science* (2009, updated 2014; author permits reproduction with citation) — DOK×Bloom cell descriptors directly informed ~12 entries, especially DOK 3–4 architectures (synthesis, transfer, problem-posing, reasonableness-verification)
- Big Ideas Math (Larson/Boswell, Cengage/National Geographic Learning) — named recurring task-type features documented in publisher materials: Error Analysis, Which One Doesn't Belong, You Be the Teacher, How Do You See It?, Number Sense, Structure, Precision
- Cuoco, Goldenberg & Mark, "Habits of Mind: An Organizing Principle for Mathematics Curriculum" (*Journal of Mathematical Behavior*, 1996) — named mathematical habits of mind (pattern-sniffing, extreme cases, reasoning by continuity, seeking invariants, experimenting/tinkering) directly informed the Pattern Recognition, Parameter Exploration, and Invariant/Transformation categories
- General, widely-used chemistry/physics instructional conventions (factor-label/dimensional analysis, free-body diagrams, Le Chatelier's principle framing) — not attributed to a single publisher; these are standard cross-textbook conventions, not proprietary to one source

**Tranche 3 (AP Classroom Topic Questions — secure/restricted source, extraction held to a stricter standard):**
- College Board AP Classroom, AP Calculus AB Topic Questions scoring guides (Units 1, 3, 4, 6 sampled) — this is restricted/access-controlled formative content (distinct from the publicly released FRQs used in Tranche 1) available only to authorized AP teachers. Only the recurring *structural and scoring-point patterns* were extracted (multi-part shared-context design, follow-through partial-credit logic, table-based rate estimation, bound-justification-without-computation, accumulation-function multi-part probing, abstract-function differentiation, "does not exist" as a valid answer, symbolic-parameter procedures, parameter-independence proofs). No topic numbers, specific functions, specific numeric values, or scoring-guide language appear anywhere in the library.

**Tranche 4 (deeper CPM closure-lesson mining + web-sourced instructional frameworks):**
- CPM Educational Program eBooks, chapter *closure* lessons specifically (CC Course 3 sampled) — a lesson type not examined in Tranche 1, containing self-assessment/confidence-rating structure and graph-to-narrative tasks distinct from ordinary practice problems
- Dan Meyer, "The Three Acts of a Mathematical Story" (2011) and the broader Three-Act Math instructional framework — publicly documented, widely-adopted pedagogy; described generically as a task-sequencing structure
- Robert Kaplinsky, *Open Middle Math: Problems That Unlock Student Thinking* and the Open Middle task format (closed beginning, closed end, open middle) — publicly documented instructional framework
- POGIL (Process Oriented Guided Inquiry Learning) — a well-established instructional framework (three-phase learning cycle: exploration/directed questions, concept invention/convergent questions, application/divergent questions), widely used in chemistry and other sciences

**Tranche 5 (deeper CPM cc1/cc2 mining):**
- CPM Educational Program eBooks, CC Course 1 (grade 6) and CC Course 2 (grade 7) lessons not previously sampled — surfaced the independent-construction-then-compare lesson structure (angle-sum/property discovery via convergent independent evidence) and the reciprocal describe-then-reproduce partner activity, plus a recurring part-whole percent decomposition task type from CC Course 1's percent unit

---

## Tranche 6 — Curriculum Reliability Additions
These additions close specific gaps identified during curriculum-philosophy work: direct fluency without fake rigor, bidirectional vocabulary structures, evaluate-vs-solve, Physics FRQ language, AP Calculus Units 7–8, short evidence-set structures, and a dedicated WTC opener. They are structure-only and use original examples.

### PROC-DIRECT-EXECUTE-01
- **applicability:** Alg1, Alg2, PreCalc, APCalc, Physics, Chem, cross-curricular
- **destinations:** Warm-Up, Notes, Practice, Exit Ticket, Quick Check, Blooket
- **content types:** solve, evaluate, simplify, differentiate, substitute, calculate, identify a directly taught relationship
- **response type:** numeric entry, short constructed-response, or selected-response
- **required representation:** equation/expression/data/diagram as appropriate
- **reasoning architecture:** Student directly executes one known skill with no artificial reasoning wrapper. The cognitive target is accurate retrieval and execution of the skill itself.
- **misconception/distractor strategy:** Use wrong-operation, sign, substitution, unit, notation, or structural errors that are actually common for the target skill; do not invent random distractors.
- **variation axes:** values; algebraic form; sign/fraction complexity; representation; whether units are present; whether the direct skill appears in pure or light context
- **DOK range:** 1–2 depending on the skill and representation; direct execution is not raised by adding the word explain
- **Bloom process descriptors:** Remember, Apply
- **evidence produced:** whether the student can accurately perform the exact target skill without unnecessary scaffolding
- **works well when:** fluency matters and repeated legitimate execution is instructionally useful
- **avoid when:** wrapping a simple skill in fake dialogue/context solely to appear more rigorous
- **security suitability:** Practice/Formative by default; Summative-safe when parameters vary and the target legitimately belongs on the assessment
- **demonstration example:** "Find f'(x) for f(x)=3x^4-5x+2."
- **provenance:** user curriculum philosophy: direct solve/evaluate/simplify/differentiate questions are legitimate and should not be disguised merely to create surface variety

### PROC-DIRECT-VARIATION-SET-01
- **applicability:** Alg1, Alg2, PreCalc, APCalc, Physics, Chem
- **destinations:** Practice, Warm-Up, CYU
- **content types:** a single skill that benefits from several repetitions with meaningful variation
- **response type:** set of short constructed-response or numeric-entry items
- **required representation:** same core representation with controlled structural variation
- **reasoning architecture:** A short set asks students to perform the same target skill several times while changing mathematically/scientifically meaningful features so fluency and discrimination improve. Repetition is the point; the variants must change something students actually need to notice.
- **misconception/distractor strategy:** Choose variations that expose predictable errors such as sign, coefficient, orientation, denominator, initial condition, units, or structure; do not merely change names in a story.
- **variation axes:** parameter size; sign; coefficient placement; representation; boundary case; common misconception trigger
- **DOK range:** 1–2
- **Bloom process descriptors:** Apply
- **evidence produced:** whether execution is stable across nearby but meaningfully different cases
- **works well when:** students need repeated practice to make a foundational process reliable
- **avoid when:** creating cosmetic clones that add no discrimination or fluency value; legitimate procedural numeric parallels may repeat whenever repetition itself builds fluency
- **security suitability:** Practice/Formative only as a set
- **demonstration example:** "Solve four equations chosen so one has variables on both sides, one includes fractions, one has a negative coefficient, and one simplifies before solving."
- **provenance:** user curriculum philosophy distinguishing useful repetition from mechanical filler

### VOCAB-TERM-TO-DEFINITION-01
- **applicability:** all courses
- **destinations:** Warm-Up, Practice, Exit Ticket, Blooket, Tarsia, Quick Check
- **content types:** discipline vocabulary, symbols, named theorems/principles
- **response type:** short constructed-response, matching, or selected-response
- **required representation:** term/name -> verbal meaning
- **reasoning architecture:** Given the term, student identifies or states the accurate definition/meaning.
- **misconception/distractor strategy:** Distractors should be nearby terms that students genuinely confuse, not unrelated definitions.
- **variation axes:** term family; selected vs constructed response; formal vs student-friendly wording
- **DOK range:** 1
- **Bloom process descriptors:** Remember, Understand
- **evidence produced:** whether the student recognizes what an important term means
- **works well when:** terminology itself is necessary for later reasoning
- **avoid when:** using vocabulary recall as a substitute for conceptual/application evidence
- **security suitability:** Formative; low-security unless embedded in a richer assessment
- **demonstration example:** "What does equilibrium mean in a force system?"
- **provenance:** user-specified term-to-definition structure; common cross-curricular vocabulary check

### VOCAB-DEFINITION-TO-TERM-01
- **applicability:** all courses
- **destinations:** Warm-Up, Practice, Exit Ticket, Blooket, Tarsia, Quick Check
- **content types:** discipline vocabulary, symbols, named theorems/principles
- **response type:** short constructed-response, matching, or selected-response
- **required representation:** verbal definition -> term/name
- **reasoning architecture:** Given an accurate definition, student identifies the corresponding term.
- **misconception/distractor strategy:** Use confusable neighboring terms as distractors.
- **variation axes:** definition wording; examples vs formal definitions; one-to-one matching vs single prompt
- **DOK range:** 1
- **Bloom process descriptors:** Remember
- **evidence produced:** whether the student can retrieve the correct disciplinary term from meaning
- **works well when:** vocabulary retrieval is part of the target
- **avoid when:** when the assessment needs application rather than label recall
- **security suitability:** Formative; low-security
- **demonstration example:** "Name the term for the tendency of an object to resist a change in its motion."
- **provenance:** user-specified definition-to-term structure

### VOCAB-CONCEPT-TO-TERM-01
- **applicability:** all courses
- **destinations:** Warm-Up, Practice, Exit Ticket, Blooket, Tarsia, Quick Check
- **content types:** concept examples/situations that instantiate a named idea
- **response type:** short constructed-response or selected-response
- **required representation:** example/situation -> term/name
- **reasoning architecture:** Student recognizes which named concept is exemplified by a short situation rather than merely matching a formal definition.
- **misconception/distractor strategy:** Distractors should represent concepts that could plausibly fit if the student focuses on the wrong feature.
- **variation axes:** context; representation; how explicit the defining feature is
- **DOK range:** 1–2
- **Bloom process descriptors:** Understand
- **evidence produced:** whether vocabulary is connected to an actual concept/example rather than memorized wording only
- **works well when:** students must connect language to situations
- **avoid when:** when the context adds no interpretive demand beyond copying a definition phrase
- **security suitability:** Formative; Summative-safe only when context varies and the target is legitimately low-DOK
- **demonstration example:** "A car moves in a straight line at constant speed while the forces on it balance. Which term describes the force state?"
- **provenance:** user-specified concept-to-term structure

### VOCAB-TERM-TO-CONCEPT-01
- **applicability:** all courses
- **destinations:** Warm-Up, Notes, Practice, Exit Ticket, Quick Check
- **content types:** discipline vocabulary tied to conceptual examples
- **response type:** short constructed-response
- **required representation:** term/name -> example/explanation
- **reasoning architecture:** Given a term, student supplies an example, situation, feature, or short explanation that correctly instantiates the concept.
- **misconception/distractor strategy:** Anticipate examples that match a neighboring term or omit the defining condition.
- **variation axes:** student-generated example vs choose-best-example; real-world vs symbolic example
- **DOK range:** 1–2
- **Bloom process descriptors:** Understand, Apply
- **evidence produced:** whether the student can move from a label to an actual conceptual instance
- **works well when:** you want stronger evidence than definition recall but still a compact prompt
- **avoid when:** requiring a long explanation when a brief valid example would suffice
- **security suitability:** Formative; can be Summative-safe if open response and target fits
- **demonstration example:** "Give one example of dynamic equilibrium and state the feature that makes it equilibrium."
- **provenance:** user-specified term-to-concept structure

### FEATURE-IDENTIFY-FROM-REPRESENTATION-01
- **applicability:** Alg1, Alg2, PreCalc, APCalc, Physics
- **destinations:** Warm-Up, Notes, Practice, Exit Ticket, Quick Check, Blooket
- **content types:** graph/table/diagram features such as intercept, maximum, increasing interval, slope, velocity sign, force direction, wave feature
- **response type:** short constructed-response, numeric entry, or selected-response
- **required representation:** graph/table/diagram -> named or numeric feature
- **reasoning architecture:** Student reads one explicit representation and identifies a target feature without being asked to convert the entire representation.
- **misconception/distractor strategy:** Distractors should correspond to common feature confusions such as x-vs-y value, local-vs-absolute, slope-vs-height, velocity-vs-speed, force-vs-net-force.
- **variation axes:** feature; representation; labeled vs unlabeled axes; exact vs approximate reading
- **DOK range:** 1–2
- **Bloom process descriptors:** Understand, Apply
- **evidence produced:** whether the student can correctly read the representation needed for later reasoning
- **works well when:** the representation itself is part of the I-can
- **avoid when:** describing a graph in prose when an actual graph should be supplied
- **security suitability:** Formative; Summative-safe with new representations
- **demonstration example:** "From the graph, identify the interval on which f is decreasing."
- **provenance:** user visual-notes philosophy plus representation-authenticity rules in the existing library

### FEATURE-EVALUATE-VS-SOLVE-01
- **applicability:** Alg1, Alg2, PreCalc, APCalc
- **destinations:** Notes, Warm-Up, Practice, Exit Ticket, Quick Check
- **content types:** function notation; graph/table/equation evaluation vs solving
- **response type:** short constructed-response or paired numeric responses
- **required representation:** graph/table/equation
- **reasoning architecture:** Student must distinguish finding an output for a given input from finding input value(s) that produce a specified output, using the same function/representation.
- **misconception/distractor strategy:** Target swapping x/y, answering f(a) when asked f(x)=a, or reporting a y-value when an x-value is required.
- **variation axes:** representation; exact/approximate values; one vs multiple solutions; domain restrictions
- **DOK range:** 2
- **Bloom process descriptors:** Understand, Apply
- **evidence produced:** whether the student distinguishes evaluation from inverse/solve thinking instead of treating both as substitution
- **works well when:** the course needs the evaluate-vs-solve distinction made explicit
- **avoid when:** using two unrelated functions, which weakens the conceptual contrast
- **security suitability:** Formative; Summative-safe with new functions
- **demonstration example:** "Using the same graph, determine f(2), then solve f(x)=2. State why the two answers represent different questions."
- **provenance:** user-identified high-value Algebra discussion/visual distinction

### PHYS-PREDICT-JUSTIFY-01
- **applicability:** Physics, AP Physics, physical science
- **destinations:** WTC, Notes, Quick Check, Exit Ticket, Summative, PT
- **content types:** motion, forces, energy, momentum, waves, electricity, magnetism, thermal phenomena
- **response type:** short or extended constructed-response
- **required representation:** scenario/diagram/data as appropriate
- **reasoning architecture:** Before any result is supplied, student predicts what will happen and justifies the prediction using a named physical principle, model, or evidence feature.
- **misconception/distractor strategy:** Anticipate intuitive-but-incorrect everyday explanations; scoring should distinguish correct prediction with weak reasoning from principle-based reasoning.
- **variation axes:** phenomenon; qualitative vs quantitative prediction; whether a diagram/data set is supplied
- **DOK range:** 2–3
- **Bloom process descriptors:** Apply, Analyze
- **evidence produced:** whether the student can use physics to predict rather than merely explain after seeing an outcome
- **works well when:** prediction can expose conceptual models before or after instruction
- **avoid when:** asking for a guess with no required physical basis
- **security suitability:** Formative; Summative-safe with novel scenario
- **demonstration example:** "A cart moving right enters a region where the net force points left. Predict how its velocity will change during the next few seconds and justify using the relationship between net force and acceleration."
- **provenance:** user-requested Physics FRQ language; structure-only synthesis of common physics free-response reasoning

### PHYS-PREDICT-OBSERVE-RECONCILE-01
- **applicability:** Physics, AP Physics, physical science
- **destinations:** WTC, Demonstration support, Investigation support, Quick Check, PT
- **content types:** observable phenomena and demonstrations
- **response type:** multi-part constructed-response
- **required representation:** prediction -> observed result/data -> revised explanation
- **reasoning architecture:** Student records a prediction, compares it with an observed or supplied result, then reconciles any difference by revising the physical model or explanation.
- **misconception/distractor strategy:** Look for post-hoc description that never addresses the original prediction or the evidence that forced revision.
- **variation axes:** live demo vs supplied data; surprising vs confirming result; qualitative vs quantitative observation
- **DOK range:** 3
- **Bloom process descriptors:** Analyze, Evaluate
- **evidence produced:** whether the student can revise a model in response to evidence rather than protect an initial intuition
- **works well when:** demonstrations/investigations are used to create conceptual conflict or model refinement
- **avoid when:** when students see the result before making a prediction
- **security suitability:** Formative / PT; not a routine secure summative structure
- **demonstration example:** "Predict which of two objects reaches the bottom first, observe the result, then identify what assumption in your original reasoning was supported or contradicted."
- **provenance:** user demonstration/investigation philosophy plus general scientific model-revision practice

### PHYS-RANK-COMPARE-QUANTITIES-01
- **applicability:** Physics, AP Physics
- **destinations:** Practice, Quick Check, Exit Ticket, Summative
- **content types:** force, acceleration, energy, momentum, power, field, wave quantities, circuit quantities
- **response type:** ranking + short justification
- **required representation:** 2–5 diagrams/scenarios/data cases
- **reasoning architecture:** Student ranks the same physical quantity across several cases and justifies the ranking using the controlling relationship rather than computing every case unless computation is the target.
- **misconception/distractor strategy:** Common errors include ranking by a visually salient but irrelevant quantity or assuming more of one variable always means more of the target without holding other variables in view.
- **variation axes:** number of cases; ties allowed; qualitative vs values; one principle vs competing effects
- **DOK range:** 2–3
- **Bloom process descriptors:** Analyze
- **evidence produced:** whether the student understands qualitative dependence and controlling variables
- **works well when:** you want conceptual comparison more than arithmetic
- **avoid when:** when each case requires a completely unrelated calculation
- **security suitability:** Summative-safe with novel cases
- **demonstration example:** "Rank the magnitude of acceleration for four carts with different masses and net forces. Explain which relationship controls your ranking."
- **provenance:** structure-only synthesis of common physics ranking-task / free-response conventions

### PHYS-REPRESENTATION-CONSISTENCY-01
- **applicability:** Physics, AP Physics
- **destinations:** Notes, Practice, Quick Check, Exit Ticket, Summative
- **content types:** force diagrams, motion diagrams, graphs, circuit diagrams, ray diagrams, wave representations
- **response type:** constructed-response / critique
- **required representation:** two or more representations of the same physical situation
- **reasoning architecture:** Student determines whether the supplied representations are mutually consistent; if not, identifies the conflict and repairs one representation.
- **misconception/distractor strategy:** Target confusion between force and motion, slope and value, current and voltage, object motion and wave motion, or diagram conventions.
- **variation axes:** representation pair/triple; one flawed vs several plausible; repair requested or not
- **DOK range:** 3
- **Bloom process descriptors:** Analyze, Evaluate
- **evidence produced:** whether understanding transfers across representations and whether the student can diagnose a mismatch
- **works well when:** the I-can explicitly connects models/representations
- **avoid when:** when representations are decorative duplicates with no consistency question
- **security suitability:** Summative-safe with new representations
- **demonstration example:** "A velocity-time graph, motion description, and force diagram are shown for the same cart. Determine whether all three can describe the same motion; identify and correct any mismatch."
- **provenance:** user Physics framework style and existing multi-representation architecture, specialized for physics model consistency

### PHYS-DESIGN-MEASUREMENT-PROCEDURE-01
- **applicability:** Physics, AP Physics
- **destinations:** Quick Check, PT, Summative, Investigation support
- **content types:** experimental measurement of physical relationships
- **response type:** extended constructed-response
- **required representation:** apparatus/phenomenon -> procedure + measurements + analysis plan
- **reasoning architecture:** Student designs a feasible procedure to test a physical claim, explicitly states what will be measured, what will be controlled, and how the measurements will be used to evaluate the claim.
- **misconception/distractor strategy:** Common weaknesses: measuring the wrong quantity, changing multiple variables at once, no repeat/trial plan, or collecting data without stating how it answers the question.
- **variation axes:** available equipment; target relationship; direct vs indirect measurement; graphing/linearization analysis
- **DOK range:** 3–4
- **Bloom process descriptors:** Analyze, Create
- **evidence produced:** whether the student can convert a physics question into an actionable measurement-and-analysis plan
- **works well when:** PT/QC needs science-practice evidence beyond calculation
- **avoid when:** reducing to a cookbook procedure supplied by the prompt
- **security suitability:** Summative-safe / PT
- **demonstration example:** "Design a procedure using a cart, ramp, meter stick, and timer to test whether increasing ramp height changes the cart's speed at the bottom. State what you would measure and how you would use the data."
- **provenance:** user-requested physics FRQ language and general experimental-design conventions

### PHYS-DATA-TREND-MODEL-01
- **applicability:** Physics, AP Physics
- **destinations:** Practice, Quick Check, Summative, PT
- **content types:** experimental data, graphs, empirical relationships
- **response type:** constructed-response
- **required representation:** table/graph/data -> trend/model/physical interpretation
- **reasoning architecture:** Student identifies a meaningful trend or model from actual data, states the relationship, and interprets what the relationship means physically.
- **misconception/distractor strategy:** Target reading a graph as a picture, confusing slope/intercept with raw values, or naming correlation without physical interpretation.
- **variation axes:** linear/nonlinear; transformed data; noisy data; qualitative/quantitative interpretation
- **DOK range:** 2–3
- **Bloom process descriptors:** Analyze
- **evidence produced:** whether the student can turn data into a physical relationship and explain its meaning
- **works well when:** data reasoning is part of the learning target
- **avoid when:** asking "analyze the graph" without specifying the feature/claim needed
- **security suitability:** Summative-safe with new data
- **demonstration example:** "Use the table to determine how period changes with length, then state what the pattern implies about a longer pendulum."
- **provenance:** existing data/model structures specialized for physics evidence interpretation

### PHYS-QUALITATIVE-CHANGE-PREDICT-01
- **applicability:** Physics, AP Physics
- **destinations:** Warm-Up, Notes, Practice, Exit Ticket, Quick Check
- **content types:** dependence of one physical quantity on another
- **response type:** short constructed-response
- **required representation:** relationship/formula/diagram/scenario
- **reasoning architecture:** Student predicts increase/decrease/no-change for a target quantity when one condition changes, then names the physical relationship/constraint that supports the prediction. Calculation is optional and usually unnecessary.
- **misconception/distractor strategy:** Target one-variable reasoning that ignores a fixed/competing quantity or treats proportionality as always linear.
- **variation axes:** direct/inverse dependence; multiple simultaneous changes; qualitative only vs brief ratio reasoning
- **DOK range:** 2–3
- **Bloom process descriptors:** Apply, Analyze
- **evidence produced:** whether the student understands relationships conceptually instead of only substituting numbers
- **works well when:** conceptual Physics or pre-calculation reasoning is desired
- **avoid when:** when the relationship is too trivial to require any reasoning
- **security suitability:** Formative; Summative-safe with novel scenario
- **demonstration example:** "If the same force acts on a cart with twice the mass, predict how its acceleration changes and justify without calculating a specific value."
- **provenance:** user Conceptual Physics emphasis and general qualitative FRQ conventions

### PHYS-ASSUMPTION-MODEL-CRITIQUE-01
- **applicability:** Physics, AP Physics
- **destinations:** Quick Check, Summative, PT
- **content types:** idealized models, approximations, system assumptions
- **response type:** constructed-response / critique
- **required representation:** model/procedure/scenario + stated or implied assumption
- **reasoning architecture:** Student identifies an assumption in a physical model, explains how it affects the conclusion, and predicts what would change if the assumption were relaxed.
- **misconception/distractor strategy:** Common weak response names a generic limitation without connecting it to the predicted result.
- **variation axes:** frictionless, negligible air resistance, constant field, point mass, ideal circuit, isolated system
- **DOK range:** 3
- **Bloom process descriptors:** Analyze, Evaluate
- **evidence produced:** whether the student understands the conditions under which a model is valid
- **works well when:** students are ready to distinguish model from reality
- **avoid when:** asking for a generic "source of error" list with no consequence analysis
- **security suitability:** Summative-safe
- **demonstration example:** "The model assumes air resistance is negligible. Explain how including significant air resistance would change the predicted motion and why."
- **provenance:** general physics model-evaluation practice; supports the user's deeper QC/PT evidence goals

### DE-SLOPEFIELD-INTERPRET-01
- **applicability:** APCalc
- **destinations:** Notes, Practice, Exit Ticket, Quick Check, Summative
- **content types:** slope fields and solution behavior
- **response type:** short constructed-response or selected-response
- **required representation:** differential equation and/or slope field
- **reasoning architecture:** Student uses local slope information to match, sketch, or describe a solution curve and justify behavior such as increasing/decreasing or concavity qualitatively from the differential equation/field.
- **misconception/distractor strategy:** Target treating the slope field as a graph of y, ignoring dependence on x/y, or sketching across segments without respecting local slopes.
- **variation axes:** autonomous/nonautonomous; initial point; qualitative feature requested
- **DOK range:** 2–3
- **Bloom process descriptors:** Apply, Analyze
- **evidence produced:** whether the student interprets a differential equation as a field of local rates rather than only a symbolic expression
- **works well when:** Unit 7 slope-field learning
- **avoid when:** purely decorative slope fields with no reasoning from them
- **security suitability:** Summative-safe with new fields/equations
- **demonstration example:** "A slope field for dy/dx=x-y is shown. Sketch the solution through (0,1) and identify an interval where the solution is decreasing."
- **provenance:** AP Calculus differential-equation task conventions; original example

### DE-EULER-APPROXIMATE-01
- **applicability:** APCalc
- **destinations:** Notes, Practice, Exit Ticket, Quick Check, Summative
- **content types:** Euler's method
- **response type:** numeric entry / short constructed-response
- **required representation:** differential equation + initial condition + step size
- **reasoning architecture:** Student repeatedly evaluates the derivative at the current approximation and advances using Euler's method; intermediate approximations feed later steps.
- **misconception/distractor strategy:** Target using the original slope at every step, updating y but not x, sign errors, or using final x in the wrong slope evaluation.
- **variation axes:** step size; number of steps; symbolic/numeric derivative; contextual interpretation
- **DOK range:** 2
- **Bloom process descriptors:** Apply
- **evidence produced:** whether the student understands Euler updating rather than memorizing one formula substitution
- **works well when:** approximate solution values from rate information
- **avoid when:** inflating DOK solely by increasing the number of Euler steps
- **security suitability:** Summative-safe with new parameters
- **demonstration example:** "Given dy/dx=x+y and y(0)=1, use two Euler steps of size 0.5 to approximate y(1)."
- **provenance:** AP Calculus Unit 7 conventional structure; original example

### DE-SEPARATE-IVP-01
- **applicability:** APCalc
- **destinations:** Notes, Practice, Quick Check, Summative
- **content types:** separable differential equations and initial conditions
- **response type:** constructed-response
- **required representation:** differential equation -> separated/integrated solution -> initial-condition constant
- **reasoning architecture:** Student separates variables, integrates, and uses an initial condition to determine the specific solution; the initial-condition result is necessary for the final expression/value.
- **misconception/distractor strategy:** Target incomplete separation, missing constant, applying initial condition before integration incorrectly, or losing domain/sign constraints.
- **variation axes:** algebraic/trigonometric/exponential forms; explicit vs implicit solution; final value vs equation requested
- **DOK range:** 2–3
- **Bloom process descriptors:** Apply, Analyze
- **evidence produced:** whether the student coordinates separation, integration, and initial-condition reasoning
- **works well when:** Unit 7 IVP solving
- **avoid when:** asking for a general solution and then a completely unrelated evaluation
- **security suitability:** Summative-safe
- **demonstration example:** "Solve dy/dx=2xy with y(0)=3 for y as a function of x."
- **provenance:** AP Calculus differential-equation procedure conventions; original example

### DE-MODEL-RATE-INTERPRET-01
- **applicability:** APCalc
- **destinations:** Notes, Practice, Exit Ticket, Quick Check, Summative, PT
- **content types:** differential-equation models in context
- **response type:** constructed-response
- **required representation:** context -> differential equation / derivative interpretation
- **reasoning architecture:** Student interprets what a differential equation says about the rate of change in context, including sign, units, equilibrium/limiting behavior, or dependence on the current amount.
- **misconception/distractor strategy:** Target describing y instead of dy/dt, omitting units, or confusing a rate law with an explicit amount formula.
- **variation axes:** population, temperature, concentration, motion, accumulation; autonomous vs nonautonomous
- **DOK range:** 2–3
- **Bloom process descriptors:** Understand, Analyze
- **evidence produced:** whether the student understands a differential equation as a model of changing quantities
- **works well when:** conceptual/modeling evidence is needed, especially AP free response
- **avoid when:** turning every item into solve-the-DE when interpretation is the target
- **security suitability:** Summative-safe
- **demonstration example:** "A quantity Q satisfies dQ/dt=0.4(100-Q). Interpret the meaning of dQ/dt=12 at a particular time, including units."
- **provenance:** AP Calculus modeling conventions; original example

### INTEGRAL-NETCHANGE-CONTEXT-01
- **applicability:** APCalc
- **destinations:** Notes, Practice, Exit Ticket, Quick Check, Summative
- **content types:** net change / accumulation from rates
- **response type:** constructed-response / numeric entry
- **required representation:** rate function/table/graph -> definite integral -> contextual amount
- **reasoning architecture:** Student uses an integral of a rate over an interval to determine net change and, when needed, combines it with an initial amount to determine a final amount.
- **misconception/distractor strategy:** Target confusing total change with final amount, using absolute value when net change is intended, or omitting rate×time units.
- **variation axes:** function/table/graph rate; initial value present or absent; exact/numerical integration
- **DOK range:** 2–3
- **Bloom process descriptors:** Apply, Analyze
- **evidence produced:** whether the student connects accumulation to rate and distinguishes change from amount
- **works well when:** Unit 8 contextual accumulation
- **avoid when:** using integral notation without requiring interpretation of what accumulates
- **security suitability:** Summative-safe
- **demonstration example:** "Water enters a tank at rate r(t) liters/minute. If the tank initially contains 200 L, write and evaluate an expression for the amount after 10 minutes."
- **provenance:** AP Calculus applications-of-integration conventions; original example

### INTEGRAL-AREA-BETWEEN-CURVES-01
- **applicability:** APCalc
- **destinations:** Notes, Practice, Exit Ticket, Quick Check, Summative
- **content types:** area between curves
- **response type:** constructed-response / setup + evaluation
- **required representation:** equations and/or graph -> intersection bounds -> integral
- **reasoning architecture:** Student identifies the relevant region, determines correct bounds and top-minus-bottom or right-minus-left relationship, then evaluates or sets up the area integral.
- **misconception/distractor strategy:** Target reversed integrand, incorrect intersection bounds, failing to split when order changes, or confusing signed integral with geometric area.
- **variation axes:** x- vs y-integration; one vs multiple subintervals; exact vs calculator evaluation
- **DOK range:** 2–3
- **Bloom process descriptors:** Apply, Analyze
- **evidence produced:** whether the student can translate a geometric region into a correct accumulation model
- **works well when:** Unit 8 region/area problems
- **avoid when:** giving all bounds/order so completely that only button-pushing remains when setup is the target
- **security suitability:** Summative-safe
- **demonstration example:** "Find the area enclosed by y=x and y=x^2. Determine the intersection points and use them to set up the integral."
- **provenance:** AP Calculus applications-of-integration conventions; original example

### INTEGRAL-VOLUME-CROSSSECTIONS-01
- **applicability:** APCalc
- **destinations:** Notes, Practice, Quick Check, Summative
- **content types:** volume with known cross sections
- **response type:** constructed-response / setup + evaluation
- **required representation:** base region + cross-section rule -> area function -> volume integral
- **reasoning architecture:** Student derives the cross-sectional area as a function of position from the base-region geometry, then integrates that area over the correct interval.
- **misconception/distractor strategy:** Target using base width directly instead of cross-sectional area, wrong geometric area formula, or wrong width between boundary curves.
- **variation axes:** square/semicircle/triangle/other stated cross section; dx/dy orientation; base-region boundaries
- **DOK range:** 2–3
- **Bloom process descriptors:** Apply, Analyze
- **evidence produced:** whether the student can build a volume integral from changing geometry
- **works well when:** Unit 8 cross-section volume
- **avoid when:** providing the area function when deriving it is the important learning target
- **security suitability:** Summative-safe
- **demonstration example:** "The base is the region between y=x and y=x^2 on [0,1]. Cross sections perpendicular to the x-axis are squares. Set up an integral for the volume."
- **provenance:** AP Calculus applications-of-integration conventions; original example

### INTEGRAL-VOLUME-REVOLUTION-01
- **applicability:** APCalc
- **destinations:** Notes, Practice, Exit Ticket, Quick Check, Summative
- **content types:** solids of revolution
- **response type:** constructed-response / setup + evaluation
- **required representation:** region + axis of rotation -> radius/radii -> integral
- **reasoning architecture:** Student identifies the rotating region and correct radius/radii relative to the axis, selects an appropriate disk/washer (or course-approved alternative) setup, then evaluates or states the integral.
- **misconception/distractor strategy:** Target radius measured from wrong reference line, missing inner radius, using diameter as radius, or incorrect bounds/orientation.
- **variation axes:** horizontal/vertical axis; axis not coordinate axis; disk vs washer; dx vs dy
- **DOK range:** 2–3
- **Bloom process descriptors:** Apply, Analyze
- **evidence produced:** whether the student can convert geometric rotation into an accumulation model
- **works well when:** Unit 8 solids of revolution
- **avoid when:** reducing to memorized piR^2 with no region interpretation when setup is the target
- **security suitability:** Summative-safe
- **demonstration example:** "The region between y=x and y=x^2 on [0,1] is revolved about the x-axis. Set up a washer integral for the volume."
- **provenance:** AP Calculus applications-of-integration conventions; original example

### EVIDENCE-SHORT-MICROSET-01
- **applicability:** all courses
- **destinations:** Exit Ticket
- **content types:** one mapped I-can that can be sampled through several short executions/representations
- **response type:** 2–4 short responses
- **required representation:** one or more compact representations
- **reasoning architecture:** A 5–8 minute ticket samples the SAME explicit I-can through a few concise items so the teacher gets a cleaner read on whether performance is stable. The items may vary meaningfully but should not introduce unrelated targets.
- **misconception/distractor strategy:** Select variants that expose the most likely errors for that I-can; avoid random breadth.
- **variation axes:** 2–4 items; direct/representation mix; easy-to-core progression; one misconception-trigger item
- **DOK range:** 1–2, occasionally 3 only if the I-can itself requires strategic reasoning
- **Bloom process descriptors:** Depends on mapped I-can
- **evidence produced:** a compact, interpretable evidence sample for one I-can
- **works well when:** portfolio needs a quick clean signal on one target
- **avoid when:** using four unrelated mini-questions merely to fill a ticket
- **security suitability:** Formative evidence; replacement-safe when the explicit I-can map is preserved
- **demonstration example:** "Four short items all target evaluation of a function from equation, table, graph, and notation."
- **provenance:** user Exit Ticket philosophy: explicit I-can evidence map, 5–8 minutes, targeted replacement allowed

### EVIDENCE-SHORT-MULTIPART-01
- **applicability:** all courses
- **destinations:** Exit Ticket, Quick Check
- **content types:** two or more closely connected mapped I-cans that can be evidenced in one short shared object/context
- **response type:** one compact multi-part constructed-response
- **required representation:** shared equation/graph/table/scenario/diagram -> connected parts
- **reasoning architecture:** A 5–8 minute ticket uses one coherent object/context and a small number of dependent or connected parts to sample multiple related I-cans without turning the ticket into a mini-test.
- **misconception/distractor strategy:** Look for a shared misconception or reasoning break that affects the connected parts; preserve follow-through evidence where appropriate.
- **variation axes:** 2–4 parts; direct then interpret; representation then conclusion; compute then explain
- **DOK range:** 2–3 depending on connection
- **Bloom process descriptors:** Apply, Analyze
- **evidence produced:** how related I-cans work together on one coherent task
- **works well when:** one shared object gives more coherent evidence than several disconnected prompts
- **avoid when:** stuffing unrelated I-cans together merely to increase coverage
- **security suitability:** Formative evidence; can serve as a deeper Exit Ticket or short QC
- **demonstration example:** "From one velocity-time graph: (a) identify an interval with negative velocity, (b) determine whether speed is increasing there, and (c) justify using velocity and acceleration signs."
- **provenance:** user Exit Ticket philosophy plus shared-context FRQ coherence rules

### WTC-FRQ-PREVIEW-01
- **applicability:** Alg1, PreCalc, APCalc, Physics, science
- **destinations:** WTC, Notes
- **content types:** upcoming section concept that can be previewed through a coherent object/context before formal instruction
- **response type:** short multi-part free-response; usually 3–5 connected parts around one shared stimulus/object
- **required representation:** actual graph/table/diagram/data/scenario/object appropriate to the section when available; do not substitute a list of disconnected prose prompts
- **reasoning architecture:** Students encounter one meaningful shared object/context before direct teaching and are asked to notice/predict/attempt/compare/model in connected parts. Every part stays tied to that shared stimulus or conceptual thread. The task previews the intellectual territory without requiring mastery of content not yet taught.
- **misconception/distractor strategy:** Do not grade missing future vocabulary/procedure as failure; use responses to surface prior models and productive questions.
- **variation axes:** number of parts; representation; open noticing vs constrained prediction; amount of prior knowledge required
- **DOK range:** 1–3 depending on prior knowledge, but DOK label is secondary because this is an instructional opener
- **Bloom process descriptors:** Understand, Analyze, sometimes Create
- **evidence produced:** what students bring into the section and which conceptual bridge the later reading/examples should address
- **works well when:** every WTC should feel like a real free-response experience and feed the conceptual story of Notes
- **avoid when:** a loose generic prompt, several unrelated preview questions bundled together, or a pretest that demands procedures students have not learned
- **security suitability:** Instructional only; not summative-safe by purpose
- **demonstration example:** "A graph shows a function with two turning points. Before learning the formal terminology: (a) mark where the graph changes direction, (b) predict which points might matter when describing the function's behavior, and (c) explain what you would want to measure or calculate to make that description precise."
- **provenance:** user WTC philosophy: coherent FRQ-style section opener tied to mapped I-cans and later Notes

---

## Coverage Notes (Tranche 6 update)

Tranches 1–6 combined: **99 structures**. The goal is not to reach an arbitrary count. Add a new structure only when it creates a genuinely distinct reasoning/evidence shape not already represented.
