# Curriculum Builder Pilot v0.1

A local, standard-library-only pilot for the Curriculum Build system.

## Purpose

Move deterministic Curriculum Build work out of ChatGPT and into a local app:

1. resolve local canonical authorities from the `memories` repo;
2. resolve course/unit targets from the selected local course repo;
3. show a visible pass/fail run log;
4. create exact, minimal AI authoring work orders only when language-model judgment is required;
5. keep all normal execution off the public web and out of File Library;
6. use no Git commands and perform no commit/push/pull/branch/merge/PR operations.

The pilot starts with the Algebra Bank pipeline:

- Bank Map / Step 3a
- Audit + Rebuild Bank Map
- Complete Bank / Step 3b

## What v0.1 does now

- Runs entirely on the local Mac with Python 3 standard library only.
- Reads `/Users/troynezki/Documents/GitHub` by default.
- Reads local repository HEAD identities by inspecting `.git` metadata directly; it does not run Git.
- Resolves `SYSTEM_MANIFEST.json`, Framework registry/front door, build/maintenance PM registries, Bank profile, Algebra operational maps, exact Unit Assessment Plan, and required Bank target paths.
- Performs a mechanical preflight for the selected pipeline stage.
- Creates a timestamped run folder in `~/Downloads/_curriculum_builder_pilot/runs/`.
- Creates an AI work-order bundle containing only the exact source files needed for the selected stage.
- Never searches the web, File Library, old chat output, or historical Bank folders.
- Stops on a missing declared dependency instead of hunting for substitutes.

## AI boundary in v0.1

The first pilot intentionally uses a **manual AI handoff** rather than embedding an API key or local model.

The app prepares:

- `AI_WORK_ORDER.txt`
- `RUN_MANIFEST.json`
- `inputs/` snapshot of exact authorities/target files
- `AI_HANDOFF.zip`

That package is the clean AI boundary. A future provider can send the same bundle directly to a model without changing the mechanical pipeline.

## Start

Double-click:

`Start Curriculum Builder.command`

The app opens:

`http://127.0.0.1:8765`

If macOS blocks the command the first time, right-click it and choose **Open**.

## Safety

This pilot is read-only with respect to the GitHub working repos.

It creates runtime work only under:

`/Users/troynezki/Downloads/_curriculum_builder_pilot`

No Git commands are used anywhere in the pilot.

## Environment overrides for testing

- `CURRICULUM_GITHUB_ROOT`
- `CURRICULUM_BUILDER_STAGING`
- `CURRICULUM_BUILDER_PORT`

