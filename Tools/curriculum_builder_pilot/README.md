# Curriculum Builder Pilot v0.4

Narrow local pilot for the Algebra Bank pipeline.

## Normal Audit + Rebuild flow

The teacher should not need to remember the internal steps.

1. Choose course, unit, and **Audit + Rebuild — Bank Map**.
2. Click **Run Audit**.
3. The pilot runs preflight + local mechanical/semantic lint automatically.
4. If no semantic candidates remain, it stops at PASS with no AI handoff.
5. If AI is needed, the pilot automatically creates the constrained handoff and copies it to `~/Downloads` with an easy filename such as `AI_HANDOFF_Algebra1_U1_BANK_MAP.zip`.
6. Upload that ZIP to ChatGPT.
7. Download the returned `AI_SEMANTIC_REVIEW.json` normally into Downloads.
8. Click **Finish Audit from Downloads**.
9. The pilot finds the matching review automatically, validates the run/pins/candidate IDs/current structures/library IDs, stages only allowed repairs, re-audits locally, and creates the `github_transfer/2` ZIP.
10. Run the existing **Apply Curriculum Transfers.command**, review in GitHub Desktop, and only the teacher decides whether to commit/push.

Technical details remain available under a disclosure panel, but are not part of the normal workflow.

## Safety

- No public web.
- No File Library.
- No Git commands.
- No GitHub writes.
- No direct canonical repo writes by the pilot.
- Mechanical facts outrank AI speculation.
- AI receives only the locked unresolved semantic boundary.

## Scope

v0.4 simplifies the proven Bank Map Audit + Rebuild loop. Build Bank Map and Complete Bank still retain pilot/manual controls while their deterministic/AI boundaries are being developed.

## v0.5 Complete Bank pilot

When **3b — Build Complete Bank** is selected, use **Prepare Complete Bank**.
The pilot first verifies the accepted Bank Map locally, requires zero unresolved map semantic candidates, locks every finished-task design slot and destination count, preserves Seeds locally, and creates one easy-to-find file in Downloads:

`AI_HANDOFF_Algebra1_U1_COMPLETE_BANK.zip`

The AI step is content-only. It may not change map IDs, counts, routing, targets, evidence jobs, structures, response modes, representation routes, security roles, or Seeds. It returns `AI_BANK_CONTENT.json`; local import/render/QA is the next pilot stage.

## v0.6 Complete Bank finish stage

After the AI returns `AI_BANK_CONTENT.json`, leave the file in `~/Downloads` and click **Finish Complete Bank from Downloads**.

The pilot then performs the rest locally:

- matches the JSON to the exact prior Complete Bank run and repository pins;
- re-verifies the accepted Bank Map snapshot did not change;
- validates the exact 208 locked design-slot IDs and 5 WTC shared-stimulus IDs;
- preserves all map-owned identity/routing fields and the six mapped Seeds;
- renders prose/equations/tables and graph assets;
- uses the registered graph tool through an append-only generation script;
- writes canonical destination slices, ITEM_INDEX, provenance, inspection viewer, MAP_FIDELITY_REPORT, and RENDER_QA_REPORT;
- hides secure Summative prompts/keys from the inspection viewer;
- runs universal finalization and requires `FINALIZATION_QA: PASS`;
- creates a fail-closed `github_transfer/2` ZIP in `_github_transfers`;
- never writes directly into the canonical course repository.


## v0.6.1 graphics runtime fix

The registered graph tool requires `matplotlib` and `numpy`. The pilot now probes local Python interpreters first. If none can run the graph tool, it creates a cached virtual environment under the pilot staging root (`_curriculum_builder_pilot/_runtime/graph_python`) and installs those runtime packages once. This is package/runtime setup only; it is not curriculum web research and never changes the course or memories repositories. Later graph builds reuse the cached local environment.

## v0.6.2 graphics runtime repair
Graph generation now bootstraps matplotlib/numpy and executes the registered graph tool in the exact same Python process that passed the dependency check. This avoids macOS virtual-environment launcher mismatches while preserving the registered graph tool unchanged.
