# Math Worksheet Builder — Pilot

Cross-course district tool for generating original math worksheets from reusable question structures.

## Pilot scope

The architecture supports Grade 6 Math through Calculus. The initial authored catalog is intentionally narrow: **Grade 7 Ratios & Proportional Relationships**. This lets the teacher test the workflow before the topic catalog is expanded.

The pilot combines:

- fluency-oriented parameterized practice;
- visual/conceptual structures such as scale drawings, dilations, tables, double number lines, and diagrams;
- configurable Intro / Standard / Mastery balance;
- one, two, or four parallel versions;
- two-column student print by default;
- independent workspace and graph/diagram scaling in the finished HTML;
- optional custom teacher-described question structures.

## Source philosophy

Public/free worksheet collections and teacher-supplied examples are used to identify broad question architectures and presentation patterns. The builder contract requires original wording, values, contexts, diagrams, and answer choices. The reference catalog does not store copied source questions.

## Request flow

1. Open `index.html`.
2. Choose course/topic and worksheet settings.
3. Select question families or add a custom family.
4. Set workspace and graph/diagram scale defaults.
5. Download the request ZIP.
6. Upload the request ZIP to ChatGPT; no extra prompt is required.
7. The response returns one ZIP with `CLICK_ME.html`, printable worksheet/PDF, optional answer key, and QA.
