(() => {
  const $ = (id) => document.getElementById(id);
  const enc = new TextEncoder();

  const REQUEST_SCHEMA = "district-tiered-task-request/0.2-pilot";
  const TOOL_VERSION = "district-tiered-task-tool/0.2-pilot";
  const CONTRACT_VERSION = "district-tiered-task-generation/0.2-pilot";
  const TASK_CARD_STYLE_VERSION = "district-tiered-task-card-style/0.2-pilot";
  const GUIDE_STYLE_VERSION = "district-tiered-task-guide-style/0.2-pilot";

  const SHARED_STANDARD_VERSION = "district-response-build-standard/1.0";
  const REQUIRED_DELIVERY_LINE = "Unzip it and open **`CLICK_ME.html`**. The student card is one landscape page with DOK 1-4, and the package includes the teacher evidence guide plus completed QA.";

  const SHARED_STANDARD_FALLBACK = "# District Response Build Standard\n\nSTATUS: REQUIRED WHEN PACKAGED BY A DISTRICT TOOL\nVERSION: district-response-build-standard/1.0\n\nThis is the shared response-quality contract for district and course request builders that create self-contained response ZIPs. Tool-specific contracts may add requirements, but they may not silently weaken this standard.\n\nThe goal is predictable, reusable output: mathematically correct notation, accurate graphs, real diagrams when needed, consistent styling, finished PDFs, clear conflict handling, and one teacher-friendly `CLICK_ME.html` entry point.\n\n## 1. Authority and conflict resolution - HARD\n\nUse this precedence order when instructions disagree:\n\n1. **Safety, platform, and file-integrity requirements.**\n2. **This shared response-build standard and any tool-specific requirement explicitly marked HARD.**\n3. **Explicit structured teacher choices in `request.json`** such as selected products, output mode, time, work mode, or research policy.\n4. **Tool-specific defaults and non-HARD guidance.**\n5. **Free-form teacher notes.**\n6. **Included source files for content, examples, data, and context.**\n7. **Model inference or default assumptions.**\n\nAdditional rules:\n\n- Teacher notes may refine content but may not silently override locked output structure, required QA, or locked CSS.\n- Included source files are authoritative for the content they actually contain. Do not invent missing facts, quotes, data, labels, or requirements.\n- A source file does not change response architecture merely because its original formatting differs from the locked response style.\n- If two HARD requirements truly cannot both be satisfied, do not guess which one to ignore. Record the conflict in `data/qa.json`, set overall status to FAIL, and explain the unresolved conflict briefly.\n- If a lower-priority instruction conflicts with a higher-priority instruction, follow the higher-priority instruction and record the resolved conflict in QA when it materially affected the build.\n- Never resolve a conflict by omitting a required output without saying so.\n\n`data/qa.json` must include a conflict record with:\n\n- `conflicts.detected_count`;\n- `conflicts.resolved_count`;\n- `conflicts.unresolved_count`;\n- `conflicts.items`, each naming the issue, competing instructions, winning authority, and resolution.\n\n## 2. Self-contained response package - HARD\n\n- Return the exact response structure required by the owning tool.\n- `CLICK_ME.html` is the teacher entry point unless the tool contract explicitly says otherwise.\n- Use local relative links for package navigation and locally generated assets.\n- Do not return placeholder PDFs, empty shell files, fake links, or prose that says a missing resource will be created later.\n- Before delivery, resolve every relative link after the package is assembled.\n- If the response contract requires HTML and PDF versions, both must be finished and openable.\n- Preserve teacher-facing simplicity. Implementation details belong in contracts and QA, not in the teacher workflow.\n\n## 3. MathJax and mathematical notation - HARD\n\nWhen mathematical notation appears, use a consistent MathJax workflow rather than improvised HTML styling.\n\n### Authoring\n\n- Use valid TeX with `\\\\( ... \\\\)` for inline math and `\\\\[ ... \\\\]` for display math unless the owning tool explicitly defines another MathJax delimiter convention.\n- Use MathJax for expressions, equations, inequalities, vectors, exponents, radicals, fractions, subscripts, Greek letters, matrices, and other mathematical notation that benefits from typesetting.\n- Use semantic math notation rather than approximating math with `<i>`, superscript text, Unicode lookalikes, or manually positioned characters.\n- Put units in mathematically appropriate upright text when they are inside an expression, for example `\\\\(4\\\\,\\\\mathrm{m/s^2}\\\\)`.\n- Avoid raw `$...$` delimiters unless the MathJax configuration in the finished page explicitly enables and verifies them.\n\n### Rendering\n\n- MathJax must finish typesetting before PDF generation.\n- Prefer MathJax SVG output or another MathJax output mode that is stable in print.\n- Final HTML must not show raw TeX if a viewer opens the package normally.\n- A final package should not depend on a remote-only math renderer when a local or pre-rendered MathJax result can reasonably be produced. If an external runtime is unavoidable, record that dependency in QA and ensure the finished PDF is already fully rendered.\n- Do not rasterize ordinary equations merely to avoid MathJax.\n\n### QA\n\nFor every page containing math, visually inspect both HTML and the finished PDF. `data/qa.json` must record at least:\n\n- `mathjax.pages_with_math`;\n- `mathjax.rendered_and_checked`;\n- `mathjax.raw_tex_visible_count`;\n- `mathjax.pdf_generated_after_typeset`;\n- `mathjax.external_runtime_dependency`.\n\nPASS is not allowed if raw TeX is visible, symbols are missing, formulas are clipped, or the PDF was generated before MathJax finished.\n\n## 4. Graphs and grapher use - HARD\n\nIf a task, answer, explanation, or source requires a mathematical graph, create or supply the actual accurate graph.\n\n- Prefer the platform's dedicated graphing/grapher capability when available.\n- If a dedicated grapher is not available, use a deterministic math/plotting method that computes the graph from the actual function/data.\n- Do **not** use a generative image model to fabricate a quantitatively accurate mathematical graph.\n- Do not substitute prose, ASCII art, a decorative sketch, or a blank box for a required graph.\n- Save generated graph assets under the owning tool's graph asset folder, normally `assets/graphs/`.\n- Prefer SVG when practical for crisp printing; PNG is acceptable when appropriate.\n- Include readable axes, scale, tick marks, labels, units, plotted points/curves, and legends when the task requires them.\n- Verify that the plotted relationship, coordinates, intercepts, asymptotes, domain/range cues, and scale are mathematically correct for the task.\n- If students are supposed to create the graph themselves, do not reveal the completed answer graph. Supply only the prompt, data, axes/grid, or other neutral scaffold the task actually requires.\n\n`data/qa.json` must include:\n\n- `graphs.required_count`;\n- `graphs.created_or_supplied_count`;\n- `graphs.dedicated_grapher_available`;\n- `graphs.dedicated_grapher_used_when_available`;\n- `graphs.assets`, including each path, generation method, and accuracy-check result.\n\nPASS is not allowed if a required graph is missing or mathematically inaccurate.\n\n## 5. Diagrams, figures, and instructional visuals - HARD\n\nUse real visuals when the task depends on spatial, structural, or representational information.\n\nExamples include force setups, circuits, geometric figures, maps, experimental apparatus, labeled biological structures, tables/data displays, coordinate grids, vector layouts, timelines, and process diagrams.\n\n- If the task refers to a diagram, figure, image, setup, model, map, table, or other visual, that visual must actually exist in the response or in an explicitly included source file.\n- Prefer clean vector/SVG instructional diagrams for simple line art, geometry, force setups, circuits, arrows, and labeled models.\n- Use generated raster imagery only when a realistic image is genuinely useful; decorative imagery is not a substitute for an instructional diagram.\n- If a visual would materially reduce ambiguity or reading load, include it even when the prompt could technically be written without one.\n- If **creating the diagram is the assessed skill**, do not give away the completed answer. Provide only a neutral setup sketch, blank grid, unlabeled structure, or other scaffold when useful.\n- In physics, a scenario sketch and a force diagram are not automatically the same thing. If students are being assessed on constructing the force diagram, a neutral object/setup sketch may be supplied without pre-drawing the answer vectors.\n- Save generated non-graph visuals under the owning tool's visual asset folder, normally `assets/visuals/`.\n- Every referenced visual must have a resolvable path and appear at readable print size.\n\n`data/qa.json` must include:\n\n- `visuals.required_count`;\n- `visuals.created_or_supplied_count`;\n- `visuals.assets`, with path, purpose, generation method, and visual-check result.\n\nPASS is not allowed if a prompt refers to a visual that is absent, unreadable, misleading, or answer-revealing when the student is supposed to construct it.\n\n## 6. Locked CSS and visual consistency - HARD\n\nEach tool owns an exact response stylesheet snapshot. The shared district standard defines the behavior; the owning tool's packaged CSS defines the final appearance.\n\n- Copy each locked CSS file from the request package **byte-for-byte** to the required response asset path.\n- Do not restyle the response because another source file uses different fonts, colors, spacing, or page layout.\n- Do not silently add inline CSS that defeats the locked stylesheet.\n- If the content does not fit, improve wording, chunking, or layout **within the existing CSS contract first**. Do not solve overflow by shrinking text to an unreadable size.\n- If the owning tool requires one page, one landscape page, duplex-safe pages, or another print rule, satisfy that rule and verify the actual rendered PDF.\n- Extra pages that are not explicitly assigned another style should inherit the owning tool's teacher/dashboard style rather than inventing a third visual system.\n- Keep common district response conventions when they exist: white background, dark readable text, restrained blue/navy accent, clear sections/cards, prominent action buttons, high-contrast print, and uncluttered teacher navigation.\n- Tool-specific student artifacts may use a specialized locked layout when that improves classroom use.\n\nThe request should provide a style version and, when practical, a SHA-256 hash for each locked CSS file. `data/qa.json` must record expected and actual hashes and whether they match.\n\nPASS is not allowed when locked CSS does not match the request snapshot or when the final PDF is clipped/unreadable despite a hash match.\n\n## 7. PDF generation and visual QA - HARD\n\nA file existing is not enough. Finished PDFs must be rendered and visually inspected.\n\n- Generate PDFs only after fonts, MathJax, graphs, diagrams, and linked assets are ready.\n- Verify page size/orientation, margins, page breaks, clipping, overlap, unreadably small text, missing images, broken math, and accidental blank pages.\n- Verify that print-specific rules such as one-page cards, landscape stations, or duplex padding are true in the **actual PDF**, not merely intended by CSS.\n- Open every required PDF after generation.\n- When the environment supports page rendering/screenshots, inspect the rendered pages rather than relying only on text extraction.\n\n`data/qa.json` must include:\n\n- `pdfs.rendered_and_visually_checked`;\n- `pdfs.openable`;\n- per-file page size/orientation and page count when the tool contract depends on them;\n- `pdfs.failures` for clipping, missing assets, or layout problems.\n\n## 8. Content integrity and teacher review - HARD\n\n- Do not invent source facts, quotations, student evidence, measurements, citations, or teacher decisions.\n- When a teacher has explicitly chosen an option in the request UI, treat that structured selection as authoritative over conflicting free-form notes.\n- Flag uncertainty instead of pretending it is resolved.\n- Answer keys/evidence guides must match the exact student tasks in the final student artifact.\n- If a task changes during layout editing, update the guide/answer key too and rerun QA.\n- Do not rank students, classes, teachers, or political choices unless the owning tool explicitly calls for a permitted non-political ranking.\n\n## 9. QA record - HARD\n\nEvery response package covered by this standard must create `data/qa.json` or the owning tool's equivalent QA path.\n\nAt minimum record:\n\n- shared-standard version;\n- tool-specific contract version;\n- overall PASS/FAIL;\n- conflict resolution summary;\n- MathJax status;\n- graph status;\n- visual/diagram status;\n- locked CSS expected/actual hashes;\n- relative-link resolution;\n- required-file existence;\n- PDF open/visual checks;\n- tool-specific checks;\n- `failures` array.\n\n`overall_status: PASS` is not allowed while `failures` contains an unresolved item.\n\n## 10. Delivery - HARD\n\nReturn one authoritative response ZIP when the owning tool requests one. Keep the user-facing delivery note short and useful. Do not present internal component files as competing required deliverables unless the teacher explicitly asked for them separately.\n";

  const CONTRACT_FALLBACK = "# Tiered Task Generation Contract\n\nSTATUS: REQUIRED\nVERSION: district-tiered-task-generation/0.2-pilot\n\nThis contract is executable. It defines how one teacher request becomes one integrated student Tiered Task Card plus one Teacher Guide / Evidence Guide.\n\nThis tool also packages `DISTRICT_RESPONSE_BUILD_STANDARD.md`. Follow both contracts. The shared district standard governs MathJax, graph accuracy, diagrams/visuals, locked CSS, PDF QA, links, package integrity, and conflict precedence. This Tiered Task contract adds the content and layout requirements specific to the DOK card.\n\nIf a true HARD-to-HARD conflict remains after applying the shared conflict rules, record it in `data/qa.json`, set overall status to FAIL, and do not silently drop either requirement.\n\n## Purpose\n\nCreate a ready-to-use extension/enrichment task that increases **cognitive complexity** from DOK 1 through DOK 4 while staying anchored to the teacher's 1-4 I Can statements. This is not an \"easy / medium / hard / hardest\" worksheet and it is not four separate task cards.\n\n## One-card rule - HARD\n\n- Create exactly ONE integrated student task card.\n- The card contains exactly four labeled task areas: DOK 1, DOK 2, DOK 3, DOK 4.\n- All four tasks belong to the same task card and draw from the submitted I Can statements as a coherent target set.\n- Do not generate one card per I Can statement.\n- The finished student card must remain one readable letter-landscape PDF page.\n\n## DOK meaning - HARD\n\nDepth of Knowledge is the cognitive processing required, not how difficult, lengthy, or obscure a task feels. Do not assign DOK from verbs alone.\n\n### DOK 1 - Recall and Reproduction\nUse direct retrieval, identification, description, representation, routine calculation, or reproduction of foundational knowledge needed for the target.\n\n### DOK 2 - Skills and Concepts\nRequire application of concepts or procedures with some decision making: compare/classify, interpret information, organize or represent relationships, choose a method, explain how/why, or apply learning in a familiar but not purely routine context.\n\n### DOK 3 - Strategic Thinking\nRequire non-routine reasoning, justification, critique, defense, revision, evidence-based conclusion, or selection among plausible approaches. The path should not be completely specified for the student.\n\n### DOK 4 - Extended Thinking\nRequire genuine extended reasoning: investigation, synthesis across ideas/sources/data, design, modeling, transfer to a new situation, iterative revision, or development/defense of a substantial solution. DOK 4 must not be \"DOK 3 plus more questions.\"\n\nIf the teacher's listed time is too short for authentic DOK 4, keep an authentic extended task and make the time expectation transparent in the Teacher Guide. The student card may frame it as an extended pathway/project continuation. Never falsely label a short routine task DOK 4 just to fit the period.\n\n## Alignment to learning targets - HARD\n\n- Every DOK task must trace to at least one submitted I Can statement.\n- Across the card, all submitted I Can statements should be meaningfully represented unless they are contradictory or too unrelated to combine. If that happens, preserve one card, prioritize the common conceptual thread, and flag the limitation in the Teacher Guide rather than inventing alignment.\n- Do not introduce an unrelated standard or content target merely to make a higher DOK task sound sophisticated.\n- The Teacher Guide must show the I Can mapping for each DOK task.\n- If the task is revised to solve a layout issue, update the Teacher Guide so it still repeats the exact final student task.\n\n## Reading/access level - HARD\n\nWhen a target reading level is supplied, adjust student-facing wording, sentence length, vocabulary support, chunking, and directions to approximately that access level.\n\nThe reading level may NOT reduce:\n\n- the academic content target;\n- the required reasoning;\n- the DOK level;\n- the evidence standard.\n\nPrefer plain language and short directions. Define or support unavoidable domain-specific vocabulary rather than replacing important content vocabulary with inaccurate simplifications.\n\n## Product choice - HARD\n\nThe teacher's selected product types are authoritative.\n\n- Show only the selected/entered product types on the student task card.\n- Do not silently add an unselected product type.\n- If multiple products are allowed, students may choose among them.\n- If only one product is allowed, present it as the required product rather than pretending there is a choice.\n- The same intellectual evidence must be required regardless of product medium. A video, poster, discussion, model, written response, etc. cannot become academically easier merely because the format changes.\n- Product choices are ways to demonstrate learning, not separate DOK levels.\n\n## Teacher constraints and source files\n\n- Follow teacher-provided time, work mode, research/internet policy, and special directions where they do not conflict with HARD contracts.\n- Structured choices in `request.json` outrank conflicting free-form notes.\n- Use included source files when they provide task context, required readings, data, images, assignments, or other constraints.\n- Do not invent quotations, data, source details, or teacher requirements that are not present.\n- If a task calls for a source/graph/image/diagram, make the necessary resource available to the student in the response package or clearly rely on an included source file. Never refer students to a missing resource.\n- Record any material instruction conflict according to the shared district standard.\n\n## MathJax, graphs, diagrams, and visuals - HARD\n\nFollow `response_contract/DISTRICT_RESPONSE_BUILD_STANDARD.md` exactly.\n\nFor this tool specifically:\n\n- Any mathematical expression in the final student card or Teacher Guide should use valid MathJax/TeX rather than improvised italic HTML when true mathematical notation is present. For example, render Newton's Second Law as `\\\\(F=ma\\\\)` rather than `<i>F</i> = <i>ma</i>`.\n- The PDF must be generated only after MathJax typesetting completes.\n- If a DOK task requires interpreting a graph, include the actual accurate graph unless creating that graph is itself the student task.\n- Prefer a dedicated grapher for mathematical graphs. If unavailable, use a deterministic accurate plotting method, not generative imagery.\n- If a DOK task depends on a physical setup, spatial relationship, geometry, circuit, force setup, or other diagram-worthy scenario, include a clean instructional diagram when it materially reduces ambiguity.\n- Do not give away an assessed diagram. For example, if students are being assessed on drawing a free-body diagram, a neutral cart/object/setup sketch may be included, but do not pre-draw the answer force vectors.\n- Save mathematical graphs under `assets/graphs/` and other generated instructional visuals under `assets/visuals/`.\n- The Teacher Guide must show/describe the same graph/diagram references used by the exact student task and must not answer a different version of the prompt.\n\n## Student Task Card requirements\n\nCreate `student/task_card.html` and `student/task_card.pdf`.\n\nThe task card must fit on ONE letter landscape page using the locked `assets/task_card_styles.css` without clipping or unreadably shrinking text.\n\nRequired content:\n\n1. Assignment/task title.\n2. Subject/course and unit/topic.\n3. Compact I Can statement strip.\n4. Concise directions that explain the DOK 1 -> 4 progression and when students move forward.\n5. Four task areas labeled:\n   - DOK 1 - Recall and Reproduction\n   - DOK 2 - Skills and Concepts\n   - DOK 3 - Strategic Thinking\n   - DOK 4 - Extended Thinking\n6. Allowed product type(s), exactly matching the teacher selection.\n7. Any concise teacher-supplied constraint students need to know, such as individual/partner work or source restrictions.\n8. Any graph/diagram/visual the task genuinely needs, embedded at readable size without revealing an answer the student is supposed to create.\n\nDo not place teacher answers, scoring commentary, DOK rationales, QA details, or hidden implementation notes on the student card.\n\n### One-page fit policy\n\n- Keep the locked CSS unchanged.\n- If content overflows, first tighten wording, remove redundancy, use shorter student directions, and simplify the task presentation without reducing the academic demand.\n- Do not silently shrink fonts or margins below the locked style.\n- Do not delete a required graph/diagram merely to make the page fit.\n- If the requested combination of required content truly cannot fit legibly on one landscape page, record the limitation and FAIL rather than returning a clipped or unreadable card.\n\n## Teacher Guide / Evidence Guide requirements\n\nCreate `teacher/teacher_guide.html` and `teacher/teacher_guide.pdf` using `assets/guide_styles.css`.\n\nInclude:\n\n- request overview and intended use;\n- submitted I Can statements;\n- a DOK 1-4 table or sections with the **exact final student task**, I Can mapping, why the task is that DOK level, and what convincing evidence would look like;\n- exemplar reasoning/solutions or evidence notes when appropriate to the subject/task;\n- likely misconceptions or weak evidence to watch for when useful;\n- product-neutral evidence expectations;\n- reading/access adjustments made, when a target reading level was supplied;\n- pacing/facilitation notes, including an honest time note for DOK 4;\n- graph/diagram/visual notes when a visual is used or intentionally withheld because construction is assessed;\n- source/resource notes;\n- any limitation, uncertainty, or resolved conflict that should be reviewed by the teacher.\n\nThis guide is for teacher review; it is not a student-facing rubric unless the request explicitly asks for one.\n\n## Locked styling - HARD\n\nThe response package must use the exact CSS snapshots included in the request.\n\n- Copy `response_contract/task_card_styles.css` byte-for-byte to `assets/task_card_styles.css`.\n- Copy `response_contract/guide_styles.css` byte-for-byte to `assets/guide_styles.css`.\n- Use the task-card CSS for the student card.\n- Use the guide CSS for `CLICK_ME.html` and the Teacher Guide.\n- Do not replace the styles with CSS from an attached source file.\n- Do not add inline overrides that change the locked page geometry, fonts, colors, or layout rules.\n- Math/graph/visual support classes are already part of the locked CSS snapshot; use them rather than inventing a conflicting visual system.\n- The expected CSS SHA-256 hashes are stored in `request.json`. Compute the response copies' hashes and record exact-match results in `data/qa.json`.\n\n## Response package - HARD\n\nReturn exactly ONE ZIP with this structure:\n\n```text\nCLICK_ME.html\nassets/\n  task_card_styles.css\n  guide_styles.css\n  graphs/             (when needed)\n  visuals/            (when needed)\nstudent/\n  task_card.html\n  task_card.pdf\nteacher/\n  teacher_guide.html\n  teacher_guide.pdf\ndata/\n  request.json\n  qa.json\n```\n\nEmpty `graphs/` and `visuals/` folders may be omitted when no such assets are needed.\n\n`CLICK_ME.html` is the teacher entry point. It must show the task title/subject/unit and prominent links to:\n\n- Student Task Card (PDF)\n- Student Task Card (HTML)\n- Teacher Guide / Evidence Guide (PDF)\n- Teacher Guide / Evidence Guide (HTML)\n\nKeep those four resources as the primary actions. Also provide a small non-primary QA status/link to `data/qa.json` so the completed QA is easy to inspect without cluttering the main workflow.\n\nUse local relative links only. The response must work after the ZIP is unzipped.\n\n## QA - HARD\n\nCreate `data/qa.json` and verify at least:\n\n### Contract and conflict checks\n\n- `overall_status` is PASS or FAIL.\n- shared response standard version matches the request.\n- Tiered Task generation-contract version matches the request.\n- `conflicts.detected_count`, `resolved_count`, `unresolved_count`, and `items` are present.\n- PASS requires `conflicts.unresolved_count` = 0.\n\n### Tiered Task checks\n\n- `one_card.exactly_one_student_task_card` is true.\n- `dok.exactly_four_levels` is true.\n- `dok.levels_present` contains 1, 2, 3, 4.\n- `dok.cognitive_complexity_not_verb_matching` is true.\n- `dok.dok4_is_genuine_extended_thinking` is true.\n- `alignment.each_task_maps_to_submitted_i_can` is true.\n- `alignment.all_submitted_i_can_statements_meaningfully_represented` is true unless a documented limitation explains otherwise.\n- `alignment.unrelated_targets_invented` is false.\n- `alignment.teacher_guide_repeats_exact_student_tasks` is true.\n- `reading_level.academic_demand_reduced` is false.\n- `products.only_teacher_allowed_products_shown` is true.\n- `products.evidence_standard_constant_across_products` is true.\n\n### Student-card layout checks\n\n- `student_card.letter_landscape_one_page` is true.\n- `student_card.pdf_page_count` = 1.\n- `student_card.clipped_or_unreadable_content` is false.\n- `student_card.visually_checked` is true.\n\n### MathJax checks\n\nFollow the shared standard and record:\n\n- pages containing math;\n- rendered/checked status;\n- raw TeX visible count = 0;\n- PDF generated after MathJax typesetting;\n- external-runtime dependency status.\n\n### Graph checks\n\n- `graphs.required_count` equals `graphs.created_or_supplied_count`.\n- dedicated grapher availability/use is recorded.\n- every graph asset includes generation method and accuracy-check result.\n\n### Visual/diagram checks\n\n- `visuals.required_count` equals `visuals.created_or_supplied_count`.\n- every referenced diagram/visual exists and is readable.\n- no provided scaffold reveals an answer that the student is supposed to construct.\n\n### PDF and link checks\n\n- `pdfs.rendered_and_visually_checked` is true.\n- `pdfs.openable` is true.\n- `links.all_relative_links_resolve` is true.\n- `links.click_me_has_all_four_required_resource_links` is true.\n- `links.click_me_links_qa_record` is true.\n\n### Locked CSS checks\n\n- `locked_css.task_card_expected_sha256` matches the value in `request.json`.\n- `locked_css.task_card_actual_sha256` is computed from `assets/task_card_styles.css`.\n- `locked_css.task_card_matches_request` is true.\n- corresponding guide-style expected/actual hash fields exist and match.\n\n### Failure rule\n\n`failures` must be an array. `overall_status: PASS` is not allowed if `failures` contains an unresolved failure.\n\nPASS is not allowed if the response has four separate cards, a falsely labeled DOK 4 task, lowered academic demand caused by reading-level simplification, unselected product choices, missing referenced resources, raw TeX, inaccurate/missing required graphs, missing required diagrams, answer-revealing visual scaffolds, broken links, clipped student-card content, placeholder PDFs, mismatched locked CSS, unresolved conflicts, or unresolved QA failures.\n\n## Delivery - HARD\n\nReturn only the completed response ZIP as the authoritative artifact.\n\nThe user-facing response that returns the ZIP must end with this exact final line:\n\nUnzip it and open **`CLICK_ME.html`**. The student card is one landscape page with DOK 1-4, and the package includes the teacher evidence guide plus completed QA.\n";

  const TASK_CSS_FALLBACK = "@page{size:letter landscape;margin:.28in}\n:root{--ink:#15191f;--muted:#5b6472;--line:#aeb7c3;--soft:#f2f5f8;--accent:#234f73;--accent2:#dfeaf3;--page-w:10.44in;--page-h:7.94in}\n*{box-sizing:border-box}\nhtml,body{margin:0;padding:0;background:#fff;color:var(--ink);font-family:Arial,Helvetica,sans-serif}\n.task-card-page{width:var(--page-w);height:var(--page-h);margin:0 auto;display:flex;flex-direction:column;overflow:hidden;background:#fff}\n.task-head{display:grid;grid-template-columns:1.7fr 1fr;gap:.18in;border-bottom:2px solid #222;padding-bottom:.09in;margin-bottom:.09in}.task-title{font-size:20pt;font-weight:800;line-height:1.05}.task-meta{text-align:right;font-size:9.5pt;line-height:1.28;color:#333}.target-strip{border:1px solid var(--line);background:var(--soft);padding:.08in .10in;margin-bottom:.08in;border-radius:5px}.target-strip b{font-size:9.5pt}.target-list{display:flex;gap:.12in;flex-wrap:wrap;margin-top:.035in;font-size:8.8pt;line-height:1.2}.directions{font-size:9.2pt;line-height:1.25;margin:0 0 .08in}.dok-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:.08in;flex:1;min-height:0}.dok{border:1.2px solid #222;border-radius:5px;display:flex;flex-direction:column;min-height:0;overflow:hidden}.dok-head{background:var(--accent);color:#fff;padding:.07in .08in;font-weight:800;font-size:11pt;line-height:1.1}.dok-sub{background:var(--accent2);padding:.045in .08in;font-size:8.2pt;font-weight:800;border-bottom:1px solid var(--line)}.dok-body{padding:.08in;font-size:9.5pt;line-height:1.24;overflow:hidden}.dok-body p{margin:0 0 .055in}.dok-body ul,.dok-body ol{margin:.04in 0 .04in .16in;padding:0}.dok-body li{margin:.025in 0}.product-bar{border:1px solid var(--line);border-radius:5px;margin-top:.08in;padding:.07in .09in;background:#fafbfc;font-size:8.8pt;line-height:1.22}.product-bar b{font-size:9.2pt}.product-options{margin-top:.03in}.footer{display:flex;justify-content:space-between;gap:.18in;margin-top:.05in;font-size:7.5pt;color:#555}.no-print{display:none}\n@media print{html,body{width:11in;height:8.5in}.task-card-page{margin:0}.no-print{display:none!important}}\n\n/* Math, graph, and instructional-visual support - style contract 0.2 */\n.math-inline{white-space:nowrap}\n.math-display{margin:.035in 0;overflow:visible}\n.task-figure,.graph-frame{margin:.04in auto;text-align:center;break-inside:avoid;page-break-inside:avoid}\n.task-figure img,.task-figure svg,.graph-frame img,.graph-frame svg,.dok-body img,.dok-body svg{display:block;max-width:100%;max-height:1.15in;height:auto;object-fit:contain;margin:0 auto}\n.figure-caption{margin:.025in auto 0;max-width:96%;font-size:7.2pt;line-height:1.18;color:var(--muted);text-align:center}\n.blank-grid{display:block;max-width:100%;height:auto;margin:.035in auto;border:1px solid var(--line);background:#fff}\nmjx-container{max-width:100%;overflow:visible!important}\n.dok-body mjx-container{font-size:.96em}\nmjx-container[jax=\"SVG\"]>svg{max-width:100%;height:auto}\n@media print{.task-figure,.graph-frame,.math-display,mjx-container{break-inside:avoid;page-break-inside:avoid}}\n";

  const GUIDE_CSS_FALLBACK = "@page{size:letter portrait;margin:.55in}\n:root{--ink:#172033;--muted:#5d687b;--line:#d5dde8;--soft:#f4f7fa;--accent:#365f82;--accent-dark:#284b68;--good:#176b46;--shadow:0 8px 24px rgba(20,34,50,.06)}\n*{box-sizing:border-box}html{background:#fff;color:var(--ink)}body{margin:0;font-family:Inter,Arial,Helvetica,sans-serif;background:#fff;color:var(--ink);font-size:15px;line-height:1.5}.wrap{max-width:980px;margin:0 auto;padding:22px}.hero{background:#eef3f8;border:1px solid var(--line);border-radius:20px;padding:26px 30px;margin:8px 0 22px}.eyebrow{margin:0;text-transform:uppercase;letter-spacing:.08em;font-weight:800;color:var(--muted);font-size:12px}.hero h1{margin:2px 0 0;font-size:34px;line-height:1.08}.subtitle{margin:8px 0 0;color:#38465b}.quick-actions{display:flex;gap:10px;flex-wrap:wrap;margin-top:18px}.btn{display:inline-flex;align-items:center;justify-content:center;padding:11px 16px;border-radius:10px;border:1px solid #9fb4c8;background:#fff;color:var(--accent-dark);font-weight:800;text-decoration:none}.btn.primary{background:var(--accent);color:#fff;border-color:var(--accent)}.section{margin:18px 0;border:1px solid var(--line);border-radius:14px;padding:18px;box-shadow:var(--shadow)}.section h2{margin:0 0 8px;font-size:23px}.section h3{margin:16px 0 5px}.muted{color:var(--muted)}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:10px}.card{border:1px solid var(--line);border-radius:12px;padding:14px;background:#fff}.card h3{margin:0 0 5px;font-size:17px}.notice{border-left:4px solid var(--accent);background:var(--soft);border-radius:8px;padding:11px 13px;margin:12px 0}.notice.good{border-left-color:var(--good)}table{width:100%;border-collapse:collapse;margin:10px 0;font-size:13px}th,td{border:1px solid #cbd5df;padding:8px;vertical-align:top;text-align:left}th{background:#f3f6f9}.guide-page{max-width:7.4in;margin:0 auto}.guide-head{border-bottom:2px solid #cfd7e2;padding-bottom:10px;margin-bottom:15px}.guide-head h1{margin:0;font-size:28px}.guide-meta{color:#555;margin-top:4px}.guide-section{margin:16px 0}.guide-section h2{font-size:19px;border-bottom:1px solid #d7dee8;padding-bottom:4px}.dok-block{border:1px solid #d5dde8;border-radius:10px;padding:12px;margin:10px 0;break-inside:avoid}.dok-label{font-weight:850;color:var(--accent-dark)}ul{padding-left:20px}.qa-pass{font-weight:800;color:var(--good)}\n@media print{body{font-size:11pt}.wrap{padding:0}.hero,.section{box-shadow:none}.quick-actions{display:none}.guide-page{max-width:none}.dok-block,.card,table{break-inside:avoid;page-break-inside:avoid}}\n\n/* Math, graph, and instructional-visual support - style contract 0.2 */\n.math-inline{white-space:nowrap}\n.math-display{margin:12px 0;overflow-x:auto;overflow-y:hidden;padding:3px 0}\n.visual-block,.graph-frame{margin:14px 0;break-inside:avoid;page-break-inside:avoid}\n.visual-block img,.visual-block svg,.graph-frame img,.graph-frame svg,.instructional-visual{display:block;max-width:100%;height:auto;margin:0 auto}\n.graph-frame{padding:10px;border:1px solid var(--line);border-radius:10px;background:#fff}\n.figure-caption{margin:6px auto 0;max-width:92%;font-size:12px;line-height:1.35;color:var(--muted);text-align:center}\nmjx-container{max-width:100%}\nmjx-container[jax=\"SVG\"]{overflow-x:auto;overflow-y:hidden}\nmjx-container[jax=\"SVG\"]>svg{max-width:100%;height:auto}\n.qa-link{font-size:13px;color:var(--muted);margin-top:10px}\n.qa-link a{font-weight:800}\n@media print{.math-display,.visual-block,.graph-frame,mjx-container{break-inside:avoid;page-break-inside:avoid}.figure-caption{color:#333}}\n";

  const sourceInput = $("sourceFiles");
  const buildButton = $("buildZip");
  const status = $("buildStatus");
  const productInputs = [...document.querySelectorAll('#productChoices input[type="checkbox"]')];

  sourceInput.addEventListener("change", () => {
    renderFiles(sourceInput.files, $("sourceList"));
    refreshStatus();
  });

  ["taskName", "subjectCourse", "unitTopic", "ican1", "ican2", "ican3", "ican4", "customProduct"].forEach((id) => {
    $(id).addEventListener("input", refreshStatus);
  });
  productInputs.forEach((input) => input.addEventListener("change", refreshStatus));
  buildButton.addEventListener("click", buildRequestZip);
  $("clearForm").addEventListener("click", clearForm);

  function renderFiles(files, target) {
    target.innerHTML = "";
    [...files].forEach((file) => {
      const li = document.createElement("li");
      li.textContent = `${file.name} (${formatBytes(file.size)})`;
      target.appendChild(li);
    });
  }

  function formatBytes(bytes) {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  }

  function getICans() {
    return [1, 2, 3, 4]
      .map((n) => $(`ican${n}`).value.trim())
      .filter(Boolean);
  }

  function getProducts() {
    const checked = productInputs.filter((input) => input.checked).map((input) => input.value);
    const custom = $("customProduct").value.trim();
    if (custom) checked.push(custom);
    return [...new Set(checked)];
  }

  function refreshStatus() {
    const taskName = $("taskName").value.trim();
    const subjectCourse = $("subjectCourse").value.trim();
    const unitTopic = $("unitTopic").value.trim();
    const iCans = getICans();
    const products = getProducts();

    if (!taskName || !subjectCourse || !unitTopic || !iCans.length || !products.length) {
      setStatus("Add the required fields, at least one I Can statement, and at least one product type.", "warn");
      return false;
    }

    setStatus(`Ready: 1 task card, ${iCans.length} I Can statement${iCans.length === 1 ? "" : "s"}, ${products.length} allowed product type${products.length === 1 ? "" : "s"}${sourceInput.files.length ? `, and ${sourceInput.files.length} supporting file${sourceInput.files.length === 1 ? "" : "s"}` : ""}.`, "good");
    return true;
  }

  function setStatus(message, kind) {
    status.textContent = message;
    status.className = `status ${kind}`;
  }

  function clearForm() {
    ["taskName", "subjectCourse", "unitTopic", "teacherName", "gradeLevel", "readingLevel", "timeAvailable", "ican1", "ican2", "ican3", "ican4", "customProduct", "teacherNotes"].forEach((id) => { $(id).value = ""; });
    $("useCase").value = "extension_after_mastery";
    $("workMode").value = "teacher_choice";
    $("researchPolicy").value = "teacher_choice";
    productInputs.forEach((input, index) => { input.checked = index < 8; });
    sourceInput.value = "";
    $("sourceList").innerHTML = "";
    refreshStatus();
  }

  async function buildRequestZip() {
    if (!refreshStatus()) return;

    buildButton.disabled = true;
    setStatus("Packaging request...", "warn");

    try {
      const sourceManifest = [];
      const entries = [];
      const used = new Set();

      for (const file of [...sourceInput.files]) {
        const packagedName = uniqueName(safeFileName(file.name), used);
        const path = `sources/${packagedName}`;
        sourceManifest.push({
          original_name: file.name,
          packaged_path: path,
          mime_type: file.type || null,
          size_bytes: file.size
        });
        entries.push({ name: path, data: new Uint8Array(await file.arrayBuffer()) });
      }

      const teacherNotes = $("teacherNotes").value.trim();
      const request = {
        schema: REQUEST_SCHEMA,
        tool_version: TOOL_VERSION,
        created_at: new Date().toISOString(),
        generation_contract_version: CONTRACT_VERSION,
        shared_response_standard_version: SHARED_STANDARD_VERSION,
        task_card_style_version: TASK_CARD_STYLE_VERSION,
        guide_style_version: GUIDE_STYLE_VERSION,
        teacher: {
          name: valueOrNull("teacherName"),
          subject_course: $("subjectCourse").value.trim(),
          grade_level: valueOrNull("gradeLevel")
        },
        task: {
          name: $("taskName").value.trim(),
          unit_topic: $("unitTopic").value.trim(),
          intended_use: $("useCase").value,
          target_reading_access_level: valueOrNull("readingLevel"),
          time_available: valueOrNull("timeAvailable"),
          work_mode: $("workMode").value,
          research_policy: $("researchPolicy").value
        },
        i_can_statements: getICans(),
        product_choices: {
          allowed: getProducts(),
          rule: "Only these product types may appear on the student task card. The academic evidence standard must remain constant across product formats."
        },
        teacher_notes_present: Boolean(teacherNotes),
        source_files: sourceManifest,
        dok_progression: {
          DOK1: "Recall and Reproduction",
          DOK2: "Skills and Concepts",
          DOK3: "Strategic Thinking",
          DOK4: "Extended Thinking",
          rule: "DOK is cognitive complexity, not difficulty or verb matching. DOK 4 must be genuine extended thinking, not DOK 3 with more work."
        },
        requested_outputs: {
          integrated_task_cards: 1,
          student_task_card_html: "student/task_card.html",
          student_task_card_pdf: "student/task_card.pdf",
          teacher_guide_html: "teacher/teacher_guide.html",
          teacher_guide_pdf: "teacher/teacher_guide.pdf",
          click_me: "CLICK_ME.html",
          qa_record: "data/qa.json",
          request_copy: "data/request.json"
        },
        response_structure: {
          click_me_links: [
            "Student Task Card (PDF)",
            "Student Task Card (HTML)",
            "Teacher Guide / Evidence Guide (PDF)",
            "Teacher Guide / Evidence Guide (HTML)"
          ],
          click_me_qa_link: "data/qa.json",
          student_card_page: "letter landscape, one page",
          all_links_relative: true
        },
        rendering_contract: {
          mathjax: {
            required_when_math_present: true,
            pdf_only_after_typeset: true,
            raw_tex_visible_allowed: false
          },
          graphs: {
            dedicated_grapher_preferred: true,
            deterministic_math_plot_fallback_allowed: true,
            generative_image_for_quantitative_graph_allowed: false
          },
          visuals: {
            create_or_supply_every_referenced_instructional_visual: true,
            avoid_revealing_an_assessed_diagram: true
          },
          locked_css_byte_exact: true,
          conflict_record_required: true
        },
        delivery: {
          required_final_line: REQUIRED_DELIVERY_LINE
        }
      };

      const [sharedStandardText, contractText, taskCss, guideCss] = await Promise.all([
        loadTextFile("../_shared/DISTRICT_RESPONSE_BUILD_STANDARD.md", SHARED_STANDARD_FALLBACK),
        loadTextFile("TIERED_TASK_GENERATION_CONTRACT.md", CONTRACT_FALLBACK),
        loadTextFile("task_card_styles.css", TASK_CSS_FALLBACK),
        loadTextFile("guide_styles.css", GUIDE_CSS_FALLBACK)
      ]);

      request.locked_styles = {
        task_card: {
          version: TASK_CARD_STYLE_VERSION,
          sha256: await sha256Hex(taskCss)
        },
        guide: {
          version: GUIDE_STYLE_VERSION,
          sha256: await sha256Hex(guideCss)
        }
      };

      entries.unshift(
        { name: "REQUEST_READ_ME_FIRST.md", data: enc.encode(buildInstructions(request, teacherNotes)) },
        { name: "request.json", data: enc.encode(JSON.stringify(request, null, 2)) },
        { name: "teacher_notes.txt", data: enc.encode(teacherNotes || "No additional teacher directions were provided.") },
        { name: "response_contract/DISTRICT_RESPONSE_BUILD_STANDARD.md", data: enc.encode(sharedStandardText) },
        { name: "response_contract/TIERED_TASK_GENERATION_CONTRACT.md", data: enc.encode(contractText) },
        { name: "response_contract/task_card_styles.css", data: enc.encode(taskCss) },
        { name: "response_contract/guide_styles.css", data: enc.encode(guideCss) },
        { name: "response_contract/SHARED_STANDARD_VERSION.txt", data: enc.encode(SHARED_STANDARD_VERSION + "\n") },
        { name: "response_contract/CONTRACT_VERSION.txt", data: enc.encode(CONTRACT_VERSION + "\n") },
        { name: "response_contract/TASK_CARD_STYLE_VERSION.txt", data: enc.encode(TASK_CARD_STYLE_VERSION + "\n") },
        { name: "response_contract/GUIDE_STYLE_VERSION.txt", data: enc.encode(GUIDE_STYLE_VERSION + "\n") }
      );

      const zipBlob = makeZip(entries);
      const filename = `tiered_task_request_${slug(request.task.name)}_${dateStamp()}.zip`;
      downloadBlob(zipBlob, filename);
      setStatus(`Request ready: ${filename}`, "good");
    } catch (error) {
      console.error(error);
      setStatus(`Could not build the ZIP: ${error.message || error}`, "bad");
    } finally {
      buildButton.disabled = false;
    }
  }

  function valueOrNull(id) {
    const value = $(id).value.trim();
    return value || null;
  }

  function buildInstructions(request, teacherNotes) {
    const sourceLine = request.source_files.length
      ? `${request.source_files.length} supporting source file(s) are included under sources/. Use them when they provide required task context or resources.`
      : "No supporting source files were attached. Build from the teacher inputs without inventing quotations, data, or missing resource details.";
    const readingLine = request.task.target_reading_access_level
      ? `Target reading/access level: ${request.task.target_reading_access_level}. Adjust wording/access only; do NOT reduce the academic target, DOK, or evidence standard.`
      : "No target reading/access level was specified; use clear grade-appropriate teacher/student language based on the supplied context.";

    return `# District Tiered Task Request - Pilot\n\n` +
`## Run this request automatically\n` +
`Build the complete Tiered Task response from this ZIP and return exactly ONE response ZIP. This request package contains the full instructions and contracts; no additional teacher prompt is required.\n\n` +
`Task: ${request.task.name}\n` +
`Subject/course: ${request.teacher.subject_course}\n` +
`Unit/topic: ${request.task.unit_topic}\n` +
`Grade level: ${request.teacher.grade_level || "Not specified"}\n` +
`Intended use: ${request.task.intended_use}\n` +
`${readingLine}\n` +
`Time available: ${request.task.time_available || "Not specified"}\n` +
`Work mode: ${request.task.work_mode}\n` +
`Research policy: ${request.task.research_policy}\n` +
`${sourceLine}\n\n` +
`## I Can statements\n` +
request.i_can_statements.map((text, i) => `${i + 1}. ${text}`).join("\n") + `\n\n` +
`## Allowed student product types - AUTHORITATIVE\n` +
request.product_choices.allowed.map((text) => `- ${text}`).join("\n") + `\n\n` +
`Show only these allowed product types on the student task card. If exactly one is allowed, present it as required rather than as a choice. Keep the same intellectual evidence standard across formats.\n\n` +
`## Teacher directions\n${teacherNotes || "No additional teacher directions were provided."}\n\n` +
`## Executable contracts - REQUIRED\n` +
`Follow BOTH packaged contracts:\n` +
`1. response_contract/DISTRICT_RESPONSE_BUILD_STANDARD.md - shared MathJax, grapher, diagram/visual, locked CSS, PDF, link, conflict, and QA rules.\n` +
`2. response_contract/TIERED_TASK_GENERATION_CONTRACT.md - one-card DOK 1-4 content and Tiered Task output rules.\n\n` +
`The shared standard and tool-specific HARD requirements outrank conflicting lower-priority notes. Structured teacher choices in request.json outrank conflicting free-form teacher notes. Record material resolved/unresolved conflicts in data/qa.json.\n\n` +
`## Core Tiered Task requirements\n` +
`- Create exactly ONE integrated student task card, not one card per I Can statement.\n` +
`- Include exactly DOK 1, DOK 2, DOK 3, and DOK 4 tasks on that one card.\n` +
`- Treat DOK as cognitive complexity rather than difficulty or verb matching.\n` +
`- Make DOK 4 genuine extended thinking, not simply more/harder questions.\n` +
`- Keep reading/access adjustments from lowering academic demand.\n` +
`- Map every task to submitted I Can statement(s) in the Teacher Guide.\n\n` +
`## MathJax - HARD\n` +
`Use valid TeX/MathJax for actual mathematical notation. Prefer \\( ... \\) inline and \\[ ... \\] display. Do not substitute italic HTML for equations such as F=ma. Finish MathJax typesetting before PDF generation. Visually inspect HTML/PDF and fail QA for raw TeX, clipped formulas, or missing symbols.\n\n` +
`## Graphs / grapher - HARD\n` +
`If a task or guide requires a mathematical graph, include the actual accurate graph. Use the dedicated graphing/grapher capability when available; otherwise use a deterministic accurate plotting method. Do not fabricate quantitative graphs with a generative image model. Record graph generation method and accuracy checks in QA.\n\n` +
`## Diagrams and instructional visuals - HARD\n` +
`If a task depends on a diagram, figure, setup, table, map, model, circuit, force setup, geometry figure, or other visual, include the real resource. If constructing the diagram is the assessed skill, do not reveal the completed answer; provide only a neutral scaffold/setup when useful. Save graphs under assets/graphs/ and other generated visuals under assets/visuals/.\n\n` +
`## Locked styling - HARD\n` +
`Copy response_contract/task_card_styles.css byte-for-byte to assets/task_card_styles.css and use it for the one-page landscape student card. Expected SHA-256: ${request.locked_styles.task_card.sha256}.\n` +
`Copy response_contract/guide_styles.css byte-for-byte to assets/guide_styles.css and use it for CLICK_ME.html and the Teacher Guide. Expected SHA-256: ${request.locked_styles.guide.sha256}.\n` +
`Do not solve overflow by replacing the locked CSS or shrinking text until it is unreadable. Improve wording/layout within the contract. Record expected and actual CSS hashes in QA.\n\n` +
`## Required response ZIP\n` +
`~~~text\n` +
`CLICK_ME.html\n` +
`assets/\n` +
`  task_card_styles.css\n` +
`  guide_styles.css\n` +
`  graphs/        (when needed)\n` +
`  visuals/       (when needed)\n` +
`student/\n` +
`  task_card.html\n` +
`  task_card.pdf\n` +
`teacher/\n` +
`  teacher_guide.html\n` +
`  teacher_guide.pdf\n` +
`data/\n` +
`  request.json\n` +
`  qa.json\n` +
`~~~\n\n` +
`CLICK_ME.html must prominently link to both student-card files and both teacher-guide files using local relative links. Keep those four as the primary actions. Also include a small link/status for the completed data/qa.json record. Copy this request.json to data/request.json.\n\n` +
`## Student Task Card\n` +
`Fit the complete student card on one readable letter-landscape page. Include task title, subject/course, unit/topic, compact I Can statements, concise directions, the four DOK tasks, allowed product type(s), student-relevant constraints, and any required non-answer-revealing graph/diagram/visual. Do not put teacher answers/DOK rationales on the student card.\n\n` +
`## Teacher Guide / Evidence Guide\n` +
`Include the exact final four student tasks, I Can mapping, why each task is that DOK level, convincing evidence, exemplar reasoning/solutions when appropriate, useful misconceptions/weak evidence, product-neutral evidence expectations, reading/access adjustments, pacing/facilitation notes, graph/visual notes, resource notes, and any limitation/uncertainty/conflict needing teacher review.\n\n` +
`## QA before delivery\n` +
`Create data/qa.json and perform every check listed in BOTH contracts. PASS is not allowed with multiple task cards, missing DOK levels, a fake DOK 4 task, reduced academic demand from reading simplification, unselected product choices, missing referenced resources, raw TeX, inaccurate/missing required graphs, missing required diagrams, clipped/unreadable card content, placeholder PDFs, broken relative links, mismatched locked CSS, unresolved conflicts, or unresolved failures. Open and visually inspect the HTML/PDF outputs before delivery.\n\n` +
`## Delivery\n` +
`Return only the single completed response ZIP as the authoritative artifact. The final user-facing line must be exactly:\n\n` +
`${request.delivery.required_final_line}\n`;
  }

  async function loadTextFile(filename, fallback) {
    try {
      const url = new URL(filename, window.location.href);
      const response = await fetch(url, { cache: "no-store" });
      if (response.ok) return await response.text();
    } catch (error) {
      console.warn(`Using embedded fallback for ${filename}.`, error);
    }
    return fallback;
  }

  async function sha256Hex(textValue) {
    const bytes = enc.encode(String(textValue));
    const digest = await crypto.subtle.digest("SHA-256", bytes);
    return [...new Uint8Array(digest)].map((b) => b.toString(16).padStart(2, "0")).join("");
  }

  function safeFileName(name) {
    const cleaned = String(name || "file")
      .replace(/[\\/:*?"<>|\u0000-\u001f]/g, "_")
      .replace(/^\.+/, "")
      .trim();
    return cleaned || "file";
  }

  function uniqueName(name, used) {
    let candidate = name;
    let n = 2;
    while (used.has(candidate.toLowerCase())) {
      const dot = name.lastIndexOf(".");
      candidate = dot > 0 ? `${name.slice(0, dot)}_${n}${name.slice(dot)}` : `${name}_${n}`;
      n += 1;
    }
    used.add(candidate.toLowerCase());
    return candidate;
  }

  function slug(value) {
    return String(value || "request")
      .toLowerCase()
      .normalize("NFKD")
      .replace(/[^a-z0-9]+/g, "_")
      .replace(/^_+|_+$/g, "")
      .slice(0, 48) || "request";
  }

  function dateStamp() {
    const d = new Date();
    const y = d.getFullYear();
    const m = String(d.getMonth() + 1).padStart(2, "0");
    const day = String(d.getDate()).padStart(2, "0");
    return `${y}${m}${day}`;
  }

  function downloadBlob(blob, filename) {
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    a.remove();
    setTimeout(() => URL.revokeObjectURL(url), 1500);
  }

  function makeZip(entries) {
    const localParts = [];
    const centralParts = [];
    let offset = 0;
    let count = 0;

    for (const entry of entries) {
      const nameBytes = enc.encode(entry.name.replace(/\\/g, "/"));
      const data = entry.data instanceof Uint8Array ? entry.data : new Uint8Array(entry.data);
      const crc = crc32(data);
      const { time, date } = dosTimeDate(new Date());

      const local = new Uint8Array(30 + nameBytes.length);
      const lv = new DataView(local.buffer);
      lv.setUint32(0, 0x04034b50, true);
      lv.setUint16(4, 20, true);
      lv.setUint16(6, 0x0800, true);
      lv.setUint16(8, 0, true);
      lv.setUint16(10, time, true);
      lv.setUint16(12, date, true);
      lv.setUint32(14, crc, true);
      lv.setUint32(18, data.length, true);
      lv.setUint32(22, data.length, true);
      lv.setUint16(26, nameBytes.length, true);
      lv.setUint16(28, 0, true);
      local.set(nameBytes, 30);
      localParts.push(local, data);

      const central = new Uint8Array(46 + nameBytes.length);
      const cv = new DataView(central.buffer);
      cv.setUint32(0, 0x02014b50, true);
      cv.setUint16(4, 20, true);
      cv.setUint16(6, 20, true);
      cv.setUint16(8, 0x0800, true);
      cv.setUint16(10, 0, true);
      cv.setUint16(12, time, true);
      cv.setUint16(14, date, true);
      cv.setUint32(16, crc, true);
      cv.setUint32(20, data.length, true);
      cv.setUint32(24, data.length, true);
      cv.setUint16(28, nameBytes.length, true);
      cv.setUint16(30, 0, true);
      cv.setUint16(32, 0, true);
      cv.setUint16(34, 0, true);
      cv.setUint16(36, 0, true);
      cv.setUint32(38, 0, true);
      cv.setUint32(42, offset, true);
      central.set(nameBytes, 46);
      centralParts.push(central);

      offset += local.length + data.length;
      count += 1;
    }

    const centralSize = centralParts.reduce((sum, part) => sum + part.length, 0);
    const end = new Uint8Array(22);
    const ev = new DataView(end.buffer);
    ev.setUint32(0, 0x06054b50, true);
    ev.setUint16(4, 0, true);
    ev.setUint16(6, 0, true);
    ev.setUint16(8, count, true);
    ev.setUint16(10, count, true);
    ev.setUint32(12, centralSize, true);
    ev.setUint32(16, offset, true);
    ev.setUint16(20, 0, true);

    return new Blob([...localParts, ...centralParts, end], { type: "application/zip" });
  }

  function dosTimeDate(d) {
    const year = Math.max(1980, d.getFullYear());
    const time = (d.getHours() << 11) | (d.getMinutes() << 5) | Math.floor(d.getSeconds() / 2);
    const date = ((year - 1980) << 9) | ((d.getMonth() + 1) << 5) | d.getDate();
    return { time, date };
  }

  const crcTable = (() => {
    const table = new Uint32Array(256);
    for (let n = 0; n < 256; n++) {
      let c = n;
      for (let k = 0; k < 8; k++) c = (c & 1) ? (0xedb88320 ^ (c >>> 1)) : (c >>> 1);
      table[n] = c >>> 0;
    }
    return table;
  })();

  function crc32(bytes) {
    let crc = 0xffffffff;
    for (const b of bytes) crc = crcTable[(crc ^ b) & 0xff] ^ (crc >>> 8);
    return (crc ^ 0xffffffff) >>> 0;
  }

  refreshStatus();
})();
