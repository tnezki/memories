# District Resource Builder - Pilot

A district-wide request builder that turns a small set of teacher inputs into one self-contained request ZIP for a finished classroom resource.

This pilot replaces the old workflow of copying long starter prompts and manually editing technical instructions. Teachers choose what they want to build; the tool packages the resource profile, teacher choices, source files, district response-build standard, locked CSS, and QA requirements automatically.

## Pilot resource profiles

1. Worksheet / Practice
2. Differentiated Worksheet
3. Extension Activity
4. Formative Assessment
5. Rubric
6. Lesson Plan / Lesson Outline
7. Presentation / Lesson Slides
8. Stations
9. Curriculum / Unit Outline
10. Blooket Review
11. Other / Custom Resource

The first ten profiles are based on recurring resource types from the district's January 2026 AI starter-prompt collection, but the old prompt engineering and technical formatting instructions have been moved behind the interface.

## Teacher flow

1. Select the resource type.
2. Enter resource name, subject/course, and at least one I Can statement / learning target. Unit/topic is optional.
3. Optionally add teacher, grade level, unit/topic, context, time/length, reading/access level, standards/framework, source files, and special directions.
4. Select learning-emphasis priorities such as practice skills/procedures, vocabulary, conceptual understanding, reasoning/problem solving, application/transfer, reading, writing, or review/retention, plus design priorities such as real-world application, accessibility, engagement, student choice, scaffolds, or extension.
5. Use the resource-specific controls that appear for the selected profile.
6. Click **Build Request ZIP**.
7. Upload the request ZIP to ChatGPT. No separate build prompt is required.
8. ChatGPT returns one response ZIP. Unzip it and open `CLICK_ME.html`.

## Architecture

This tool follows the district **tool capsule + registry + shared contract** pattern.

- `resource_profiles.json` owns the profile catalog and most resource-specific controls. This makes it possible to add or revise resource types without redesigning the entire interface.
- `RESOURCE_BUILDER_CONTRACT.md` owns the cross-profile resource rules and profile-specific build expectations.
- `DISTRICT_RESPONSE_BUILD_STANDARD.md` is a local snapshot of the shared district standard packaged by this tool. Keeping the runtime copy inside the tool capsule prevents GitHub Pages path/caching failures while preserving the same shared MathJax, graphing, diagram/visual, conflict, CSS, PDF/native-file QA, and package-integrity rules.
- `dashboard_styles.css` and `resource_styles.css` are exact locked response style snapshots. Every request records their SHA-256 hashes.
- `app.js` is browser-side only and creates ZIPs with no third-party ZIP dependency.

## Teacher intent vs. artifact engineering

The teacher interface asks for instructional decisions, not implementation details. Teachers should not need to specify MathJax CDN rules, graph-generation methods, CSS classes, print rendering rules, link structures, or QA fields. Those belong in the packaged contracts.

## Output pattern

Every response uses `CLICK_ME.html` as the teacher entry point and returns the resolved profile outputs plus teacher materials when requested and a completed `data/qa.json` record.

Typical package shape:

```text
CLICK_ME.html
assets/
  dashboard_styles.css
  resource_styles.css
  graphs/
  visuals/
resource/
  <finished classroom resource files>
teacher/
  <answer key / guide / notes when applicable>
data/
  request.json
  qa.json
```

Native resource types keep their natural format. For example, Presentation creates PPTX/PDF, while Blooket creates the strict import CSV plus a teacher answer reference.

## Expansion rule

Use the generic Resource Builder while a resource type is still broadly useful and configurable. If one profile develops enough specialized workflow, pedagogy, or output architecture, promote it into its own district tool rather than overloading the generic builder. The Tiered Task Tool is the model for that promotion path.

## Privacy

Selected files are read in the browser and packaged locally. The page does not upload files by itself. Teachers remain responsible for district policy when uploading protected or student data to an AI service.
