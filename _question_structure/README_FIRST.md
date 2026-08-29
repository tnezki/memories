# _question_structure v1.0 — READ FIRST

This package is the dedicated authority for **question-design planning and question structure**. It is intentionally small and travels with build PMs independently of large visual libraries.

It does not replace the current Curriculum Philosophy, Base PM, course Framework, Assessment Plan, or course-specific visual/graph tools. It answers a narrower question:

> **Before writing questions, what evidence structures and variation should be planned for this exact learning target and destination?**

## Authority / precedence
When bundled with a build PM, use this order for question authoring:
1. current explicit teacher instruction
2. current Curriculum Philosophy
3. current executable Base PM
4. current course Framework + exact Assessment Plan/I-can map
5. **this `_question_structure` package for question-design workflow/structure/variation**
6. current visual/source toolkit for graphics, source examples, and enrichment

If an older Question Structure + Visual Toolkit conflicts with this package on authoring sequence, wording profiles, vocabulary directionality, multi-step dependency, parallel variation, destination variety, or metadata planning, **this package wins**.

## Core workflow
Do not start by generating question text.

**Map I-cans → map evidence/question variety → map representations/formulas → build JSON design skeleton → author questions → solve/verify → assign derived metadata.**

DOK/Bloom remain descriptive and are assigned only after the final task exists.

## Scope levels
This package supports planning at five nested levels:
- **artifact** — what kinds of evidence the whole artifact needs
- **section** — how evidence/representations/variety are distributed across a section
- **I-can** — best-fit question modes for the exact target
- **family** — what makes parallel questions legitimately related without becoming clones
- **item** — the exact planned structure, wording profile, response mode, representation, dependency chain, and variation axes for one question

## Critical rule
Variety is **not a quota**. Do not force every I-can into every structure. Map what actually fits the target, then author to that map.

## Files to read first
1. `QUESTION_STRUCTURE_CORE.md`
2. `contracts/question_design_workflow.json`
3. `contracts/question_design_schema.json`
4. `catalogs/destination_design_patterns.json`
5. `catalogs/variation_axes.json`
6. relevant guides
7. legacy universal structure library/catalog only as a menu after the target and evidence job are known
