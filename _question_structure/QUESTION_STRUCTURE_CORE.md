# Question Structure Core — v1.0

## 1. Plan before prose
The question ecosystem is designed before individual prompts are written.

Required sequence:
1. Resolve the exact I-can/target and evidence job.
2. Classify the content mode(s): quantitative/formula, conceptual, vocabulary, representation, modeling, data/graph, experimental, or mixed.
3. Map which question structures naturally fit and which should be avoided.
4. Map useful representations and available tools (graph tool, diagram/FBD, table, equation, image, model).
5. Map formula relationships and bidirectional/reverse possibilities when applicable.
6. Map legitimate parallel-variation axes.
7. Build a machine-readable question-design plan.
8. Author the actual question from that plan.
9. Independently solve/check the final instantiated question and representation.
10. Assign DOK/Bloom and final metadata from what the student actually must do.

## 2. Wording profiles
These are sentence architectures, never quotas.

### Standard
Givens/situation first; action/question last.

> A crane lifts a 600 kg load upward at a constant speed of 0.50 m/s. Determine the power required.

### Inverted
Action/quantity first; givens follow.

> Determine the power required by a crane that lifts a 600 kg load at a constant upward speed of 0.50 m/s.

### Context-rich
A short authentic situation earns its space and ends in one clear task.

> A contractor building a bridge needs a crane that can lift a 600 kg load at a constant upward speed of 0.50 m/s. Determine the required power.

Not every structure supports all three profiles naturally. Record allowed profiles in the design map; do not manufacture context or awkward inversion merely for surface variety.

## 3. Vocabulary directions
Vocabulary evidence may be authored in four distinct directions:
- **term → definition**
- **definition → term**
- **concept/example → term**
- **term → concept/example**

Matching is a presentation mode that may group several vocabulary relationships when that is more efficient than isolated items. Vocabulary questions should not dominate an I-can whose real evidence job is quantitative/model-based unless vocabulary itself is the target.

## 4. Formula / quantitative structures
When an I-can genuinely requires mathematical use of a relationship, quantitative/formula questions should be planned deliberately rather than treated as optional decoration.

Useful quantitative structures include:
- direct solve for the conventional unknown
- solve for a different variable / inverse direction
- interpret a formula/relationship physically
- representation → quantity
- quantity → representation
- compare/rank from a relationship
- dependent multi-step transfer
- mixed conceptual + quantitative check when the interpretation is part of the target

For Physics, use physical situations that naturally supply measurements. Do not present naked variable assignments as the default student experience.

## 5. Multi-step means dependency
A task is multi-step only when an intermediate result is needed for the final requested result. Two dependent stages are enough.

Do **not** create fake multi-step by labeling unrelated prompts (a) and (b).

For a relationship such as `d = r t`, legitimate dependency chains include:
- given `d,t` → infer `r` → new `d` → find `t`
- given `r,t` → find `d` → same `r` + new `t` → find new `d`
- given `d,r` → find `t` → same `r` + new `d` → find new `t`
- compare two trips → infer whether rate is constant → use the supported rate for a prediction

When varying parallel multi-step questions, vary the dependency path when useful, not merely names/numbers.

Within one problem, keep units internally compatible unless unit conversion is itself the target. Do not accidentally add conversion load to a relationship problem whose I-can is not about conversion.

## 6. Parallel variety
A family is a shared learning/evidence architecture. A finished prompt is one instance of that family.

Good parallel variation may change one or more of:
- unknown quantity / solve direction
- dependency order
- givens/evidence set
- representation type or representation values
- misconception/error target
- response mode
- context when context changes the evidence naturally
- numerical values and units when procedure/fluency is the point
- sentence profile (Standard/Inverted/Context-rich) as a secondary variation

Weak variation changes only:
- a person's name
- an object noun
- question number/version ID
- sentence order
- answer-choice order
- arbitrary irrelevant values

For procedural fluency, numeric parallels may be legitimate. For conceptual/secure evidence, stronger semantic variation is required.

## 7. Representation planning
Before authoring, decide whether the target is best evidenced through:
- direct text/equation
- diagram/FBD/vector/model
- graph
- table/data set
- image/phenomenon
- multiple representations with a real translation job

Use the course graph/diagram tool when it supports the evidence cleanly. Do not force a graph or diagram merely to increase variety. Conversely, do not describe an imaginary representation in prose when the evidence job is interpretation/critique of that representation.

## 8. Destination-specific design
Destination changes the job.

- **WTC:** coherent FRQ morphology; shared stimulus; connected parts; decomposition/navigation practice.
- **Example/YTI:** model then apply; when the I-can naturally supports formula use, a strong quantitative pair has priority over generic vocabulary/conceptual filler.
- **Practice:** intentionally mixed menu based on I-can fit; may include formula, inverse, matching, vocabulary, diagrams, graphs, short answer, multi-step, conceptual/application. Repetition is allowed when purposeful.
- **Warm-Up:** predictable retrieval/bridging; controlled repetition is useful.
- **Exit Ticket:** four evidence opportunities should be varied within a ticket and across forms when the target supports it; not four same-shell clones.
- **Summative:** preserve evidence coverage/rigor while using genuinely independent secure stimuli; family IDs describe semantic families and may not manufacture uniqueness from version/question numbers.

## 9. Anti-patterns
Reject or repair:
- question text generated before the evidence map exists
- mechanical equal I-can allocations caused by container counts
- one generic shell spread across unrelated I-cans
- context-noun collisions (objects/locations that do not fit the physics/setup)
- fake multipart questions with independent parts
- decorative diagrams/graphs
- unseen “diagram” described only in prose when students must critique/interpret it
- DOK/Bloom used as generation targets
- version/question numbers embedded into family IDs to hide parallelism
- contexts or extra measurements that do not affect the model/inference/calculation

## 10. Derived metadata rule
The design plan may predeclare intended structure/response/representation. It may **not** predeclare final DOK/Bloom as a quota. After authoring and independent solution verification, assign:
- DOK
- Bloom
- final `question_family_id`
- final `task_architecture`
- final variation description
- audit status according to the owning PM
