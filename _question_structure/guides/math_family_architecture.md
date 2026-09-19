# Math Question Family Architecture

## Canonical ownership
A **family** is a reusable student-action/evidence architecture, not a stored question and not a grade-specific prompt. The canonical family definition lives in `catalogs/math_question_family_registry.json`. Course/grade visibility lives separately in `catalogs/math_course_family_maps.json`.

The worksheet builder catalog and compatibility generator bank are **derived outputs**. Edit the registry/maps, then regenerate with `Tools/build_math_question_catalogs.py`. Do not hand-maintain a second family truth inside the district tool.

## Family lock
Before authoring any question, resolve exactly one `family_id`. The final item must preserve that family's:
- evidence job;
- student action;
- response mode;
- representation role;
- generator validity constraints;
- answer rule;
- difficulty band.

A family summary is not a prompt. Do not free-write a vaguely related question and attach the family ID afterward. If the requested task cannot satisfy the family contract, choose a different family or fail closed.

## What is stored
Store the generator contract: prompt pattern, parameter names, configurable mathematical property controls, validity constraints, render route, answer rule, variation axes, difficulty policy, and QA gates. **Do not store source questions.** Teacher-provided parallel forms and external worksheet catalogs are structural references only.

Property controls are the reusable mathematical knobs of the family—for example coefficient domain, denominator range, sign policy, scale-factor type, coordinate range, answer form, rounding policy, or representation choice. They describe what may change inside the family without changing the family itself.

## Course maps
The same family may appear in multiple courses. Example: one-step equation solving can be mapped to Grade 6, Grade 7, Grade 8 review, or Algebra 1 without cloning the family definition. Course maps control teacher browsing labels and topic placement.

## Wording
Math worksheet generation defaults to `direct_concise`. Context is included only when it contributes mathematical information, interpretation, modeling, units, or transfer. Decorative names, backstories, and filler sentences are prohibited.

## Parallel forms
Parallel forms instantiate the same family with different legal parameters. Numbers/names/context/diagram orientation may vary only when the evidence job and computational/reasoning demand remain equivalent.

## Source/reference policy
Use external or teacher-supplied sources to identify:
- useful task architectures;
- representation patterns;
- parameter options;
- natural difficulty progressions;
- topic coverage gaps.

Never reproduce source wording, names, values, answer choices, or diagrams.
