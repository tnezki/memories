(() => {
  const $ = (id) => document.getElementById(id);
  const enc = new TextEncoder();

  const RESPONSE_STYLE_VERSION = "district-grading-response-style/1.7";
  const STATION_STYLE_VERSION = "district-grading-station-style/1.1";
  const MATH_VISUAL_QA_VERSION = "district-grading-math-visual-qa/1.6";
  const COMMON_PRACTICE_VERSION = "district-grading-common-practice/1.6";
  const RESPONSE_QA_VERSION = "district-grading-response-qa-execution/1.5";
  const GRAPH_RENDERING_STANDARD_VERSION = "district-graph-rendering-standard/1.2";
  const RESPONSE_LAYOUT_LOCK_VERSION = "district-grading-response-layout-lock/1.3";
  const RESPONSE_STYLE_SHA256 = "2ab8acdc2cfa74f288906ce88dd430c9715e74d16ed66cbf61e45f311558d7ad";
  const RESPONSE_DATA_VERSION = "district-grading-response-data/1.0";
  const RESPONSE_BUILDER_VERSION = "district-grading-response-builder/1.1";
  const EVIDENCE_REVIEW_VERSION = "district-grading-evidence-review/1.0";
  const MECHANICAL_QA_VERSION = "district-grading-mechanical-qa/1.1";
  const REQUEST_SCHEMA = "district-grading-request/1.5-pilot";

  const RESPONSE_CSS_FALLBACK = String.raw`:root{
  --ink:#172033;--muted:#5d687b;--line:#d5dde8;--soft:#f4f7fa;--panel:#fff;--hero:#eef3f8;
  --accent:#365f82;--accent-dark:#284b68;--success:#176b46;--warn:#8a5a00;--shadow:0 8px 24px rgba(20,34,50,.06)
}
*{box-sizing:border-box}
html{background:#fff;color:var(--ink)}
body{margin:0;font-family:Inter,ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;background:#fff;color:var(--ink);font-size:16px;line-height:1.5}
a{color:var(--accent-dark)}
.wrap{max-width:1180px;margin:0 auto;padding:20px}
.hero{background:var(--hero);border:1px solid var(--line);border-radius:20px;padding:24px 28px;margin:10px 0 20px}
.eyebrow{margin:0 0 2px;text-transform:uppercase;letter-spacing:.08em;font-weight:800;color:var(--muted);font-size:13px}
.hero h1{margin:0;font-size:36px;line-height:1.08;letter-spacing:-.02em}
.subtitle{margin:8px 0 0;font-size:18px;color:var(--ink)}
.quick-actions,.inline-actions{display:flex;gap:10px;flex-wrap:wrap;margin-top:16px}
.btn{display:inline-flex;align-items:center;justify-content:center;min-height:44px;padding:9px 15px;border-radius:10px;border:1px solid #9fb4c8;background:#fff;color:var(--accent);font-weight:800;text-decoration:none;font-size:15px}
.btn.primary{background:var(--accent);color:#fff;border-color:var(--accent)}
.btn.small-btn{min-height:36px;padding:6px 10px;font-size:13px}.btn:hover{filter:brightness(.98)}
.section{margin:18px 0;background:var(--panel);border:1px solid var(--line);border-radius:16px;padding:18px;box-shadow:var(--shadow)}
.section h2{margin:0 0 5px;font-size:23px;line-height:1.2}.section-intro{margin:0 0 14px;color:var(--muted)}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:10px}
.student-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(245px,1fr));gap:10px}
.card{border:1px solid var(--line);border-radius:12px;padding:14px;background:#fff}.card h3{margin:0 0 4px;font-size:17px}.card p{margin:4px 0;color:var(--muted)}.card a{font-weight:800;text-decoration:none}
.card-links{display:flex;gap:8px;flex-wrap:wrap;margin-top:9px}.card-links a{display:inline-block;padding:5px 8px;border-radius:7px;background:var(--soft);border:1px solid var(--line)}
.summary-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:10px;margin:12px 0}.stat{border:1px solid var(--line);background:var(--soft);border-radius:12px;padding:12px}.stat strong{display:block;font-size:26px;line-height:1.05}.stat span{color:var(--muted);font-size:13px}
.notice{border-left:4px solid var(--accent);background:var(--soft);border-radius:9px;padding:10px 12px;margin:12px 0}.notice.warn{border-left-color:var(--warn)}.notice.good{border-left-color:var(--success)}

/* Student reports and individual practice */
.report-page,.practice-page,.packet-page{max-width:8in;margin:0 auto;padding:.1in 0;color:#111}.report-head{border-bottom:2px solid #cfd7e2;padding-bottom:10px;margin-bottom:15px}.report-head .eyebrow{font-size:11px}.report-head h1{font-size:28px;margin:0}.report-meta{color:#555;margin-top:4px}.report-section{margin:15px 0}.report-section h2{font-size:18px;margin:0 0 6px}.report-section p,.report-section li{font-size:14.5px}ul.clean{margin:6px 0 0;padding-left:20px}ul.clean li{margin:4px 0}.feedback-box{border:1px solid #d8dee7;border-radius:10px;padding:12px 14px;margin:10px 0;background:#fafbfc}.practice-block{border:1px solid #cfd7e2;border-radius:10px;padding:12px;margin:12px 0;break-inside:avoid}.practice-block h2,.practice-block h3{margin-top:0}.name-line{display:flex;justify-content:space-between;gap:14px;border-bottom:1px solid #bfc8d3;padding-bottom:7px;margin-bottom:12px;font-weight:700}
.table-wrap{overflow-x:auto}table{width:100%;border-collapse:collapse;margin:10px 0;font-size:13.5px}th,td{border:1px solid #d6dde6;padding:7px 8px;text-align:left;vertical-align:top}th{background:#f3f6f9}.small{font-size:13px;color:var(--muted)}.page-break{break-before:page;page-break-before:always}.duplex-blank-page{display:none}.no-print{display:block}

/* Compact teacher review of generated questions */
.review-toolbar{display:flex;align-items:center;justify-content:space-between;gap:10px;flex-wrap:wrap;margin:0 0 12px}.question-review-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(270px,1fr));gap:9px}.question-review-card{border:1px solid var(--line);border-radius:10px;padding:10px;background:#fff;break-inside:avoid}.question-review-card h3{font-size:14.5px;margin:0 0 4px}.question-source{font-size:10.5px;text-transform:uppercase;letter-spacing:.05em;font-weight:800;color:var(--muted);margin-bottom:5px}.question-body{font-size:13.5px;line-height:1.32}.question-review-card .visual-block,.question-review-card .graph-frame{margin:7px 0}.question-review-card .visual-block img,.question-review-card .graph-frame img{max-height:165px;object-fit:contain}.question-review-card details{margin-top:6px;border-top:1px solid #e3e7ed;padding-top:5px}.question-review-card summary{cursor:pointer;font-weight:800;color:var(--accent-dark);font-size:11.5px}.teacher-move,.discourse-move,.answer-box{font-size:11.5px;line-height:1.35;background:var(--soft);border-radius:7px;padding:7px;margin-top:5px}.teacher-move strong,.discourse-move strong,.answer-box strong{display:block;margin-bottom:2px}

/* Set 1 shared compact headers */
.set-head,.activity-head{display:flex;justify-content:space-between;gap:14px;align-items:flex-end;border-bottom:1.5px solid var(--line);padding:0 0 8px;margin:0 0 12px}.set-head h1,.activity-head h1{font-size:23px;line-height:1.1;margin:0}.set-head p,.activity-head p{font-size:12px;color:var(--muted);margin:3px 0 0}.set-meta{font-size:12px;color:var(--muted);text-align:right}

/* One-question-at-a-time Set 1 teacher presentation */
.presentation-shell{height:100vh;display:grid;grid-template-rows:auto minmax(0,1fr) auto;background:#fff;overflow:hidden}.presentation-head{padding:9px 16px;border-bottom:1px solid var(--line);display:flex;justify-content:space-between;gap:12px;align-items:center}.presentation-head h1{font-size:20px;margin:0}.presentation-question{display:flex;align-items:center;justify-content:center;padding:14px 22px;min-height:0;overflow:auto}.presentation-card{width:min(1100px,96vw);font-size:clamp(22px,2.4vw,38px);line-height:1.3}.presentation-card .visual-block img,.presentation-card .graph-frame img{max-height:50vh;object-fit:contain}.presentation-nav{background:#fff;border-top:1px solid var(--line);padding:9px 14px;display:flex;justify-content:space-between;align-items:center;gap:8px;flex-wrap:wrap}.presentation-nav .nav-group{display:flex;gap:7px;align-items:center}.presentation-meta{font-size:12px;color:var(--muted)}

/* Print Presentation: one Letter page per problem; question top half, answer + moves bottom half */
.print-presentation-wrap{max-width:8.5in;margin:0 auto;padding:14px 0}.print-presentation-page{width:8in;height:10in;margin:0 auto 18px;background:#fff;border:1px solid #cfd7e2;box-shadow:0 3px 18px rgba(20,34,50,.08);padding:.12in;display:grid;grid-template-rows:1fr 1fr;gap:.14in;break-after:page;page-break-after:always}.print-slide{border:1.4px solid #98a5b3;border-radius:9px;padding:.17in .20in;display:flex;flex-direction:column;justify-content:flex-start;overflow:hidden;break-inside:avoid}.print-slide .slide-number{font-size:10.5px;font-weight:800;color:var(--muted);margin-bottom:4px}.print-slide .slide-question{font-size:clamp(18px,2.1vw,28px);line-height:1.24}.print-slide .math-display{margin:7px 0}.print-slide .visual-block,.print-slide .graph-frame{margin:6px auto}.print-slide img,.print-slide svg,.print-slide .graph-image{max-height:3.25in;max-width:100%;width:auto;object-fit:contain}

/* Common worksheet Review / Extension labels */
.worksheet-section-label{font-size:13px;font-weight:900;text-transform:uppercase;letter-spacing:.055em;padding:7px 10px;margin:14px 0 8px;border-left:5px solid var(--accent-dark);background:#f1f5f8}.worksheet-section-label.extension{border-left-color:#667085;background:#f6f6f7}

/* Student Set */
.student-set{max-width:8in;margin:0 auto}.student-set-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:9px 14px}.student-question{border-top:1px solid #dce2e9;padding:8px 2px 10px;break-inside:auto;page-break-inside:auto}.student-question h3{font-size:14px;margin:0 0 5px}.student-question .question-body{font-size:13.5px}.student-question .visual-block,.student-question .graph-frame{margin:7px auto}.student-question img,.student-question svg{max-height:2.7in}
.workspace{min-height:var(--workspace-height,1.1in);border-bottom:1px solid #e0e4e9;margin-top:7px}

/* Teacher Guide */
.teacher-guide{max-width:9.5in;margin:0 auto}.teacher-guide-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(330px,1fr));gap:9px}.teacher-question{border:1px solid var(--line);border-radius:10px;padding:10px;break-inside:avoid;page-break-inside:avoid}.teacher-question h3{font-size:14.5px;margin:0 0 5px}.teacher-question .question-body{font-size:13.5px}.teacher-question .guide-answer{background:#f5f8fb;border-left:3px solid var(--accent);padding:7px 8px;margin-top:7px;font-size:12.5px}.teacher-question .guide-move{font-size:11.5px;margin-top:5px;color:#39475a}

/* Classroom structure menu + projectable directions */
.structure-menu{display:grid;grid-template-columns:repeat(auto-fit,minmax(215px,1fr));gap:9px}.structure-card{border:1px solid var(--line);border-radius:10px;padding:11px}.structure-card h3{margin:0 0 3px;font-size:16px}.structure-card p{font-size:12px;color:var(--muted);margin:3px 0}.structure-directions{max-width:900px;margin:0 auto}.direction-row{display:grid;grid-template-columns:135px 1fr;gap:12px;padding:8px 0;border-top:1px solid #e1e5ea}.direction-label{font-size:11px;text-transform:uppercase;letter-spacing:.05em;font-weight:800;color:var(--muted)}.direction-goal{background:#f4f7fa;border-left:4px solid var(--accent);padding:9px 11px;border-radius:7px;margin-top:8px}

/* Printable structure transforms */
.cut-card-grid{display:grid;grid-template-columns:1fr 1fr;gap:8px}.cut-card{border:1.4px dashed #777;border-radius:7px;padding:10px;min-height:150px;break-inside:avoid;page-break-inside:avoid}.cut-card .card-number{font-size:10px;font-weight:800;color:#666}.find-someone-sheet{display:block}.find-someone-box{border:1.4px solid #222;border-left:8px solid var(--accent-dark);border-radius:0;padding:10px 12px;margin:0 0 12px;min-height:0;break-inside:avoid;page-break-inside:avoid}.find-someone-box .signature-line{font-size:12px;font-weight:800;color:#333;margin:8px 0 6px;padding-bottom:5px;border-bottom:1px solid #bbb}.find-someone-box .workspace-label{font-size:11px;font-weight:800;color:#444;margin-top:6px}.find-someone-box .workspace{min-height:1.15in;border:1px dashed #999;margin-top:4px}.find-someone-intro{font-size:12px;color:#444;margin:0 0 10px}.partner-line{margin-top:10px;border-bottom:1px solid #555;height:20px}.role-label{font-size:10.5px;text-transform:uppercase;letter-spacing:.06em;font-weight:800;color:var(--muted)}

/* Screen preview for page-bound artifacts */
.screen-page{max-width:8.5in;min-height:11in;margin:14px auto;background:#fff;border:1px solid #cfd7e2;box-shadow:0 3px 18px rgba(20,34,50,.08);padding:.45in}

.math-inline{white-space:nowrap}.math-display{margin:10px 0;overflow-x:auto;overflow-y:hidden;padding:3px 0}.visual-block{margin:13px 0;break-inside:avoid;page-break-inside:avoid}.visual-block img,.graph-frame img,.graph-image,.instructional-visual{display:block;max-width:100%;height:auto;margin:0 auto}.graph-frame{margin:13px auto;padding:8px;border:1px solid #d6dde6;border-radius:10px;background:#fff;break-inside:avoid;page-break-inside:avoid}.figure-caption{margin:5px auto 0;max-width:92%;font-size:11.5px;line-height:1.3;color:#5d687b;text-align:center}mjx-container[jax="SVG"]{max-width:100%;overflow-x:auto;overflow-y:hidden}

@media(max-width:700px){
  .wrap{padding:12px}.hero{padding:20px 17px;border-radius:16px}.hero h1{font-size:30px}.subtitle{font-size:16px}.btn{width:100%}.section{padding:15px}.presentation-question{padding:12px}.student-set-grid,.cut-card-grid{grid-template-columns:1fr}.teacher-guide-grid{grid-template-columns:1fr}.direction-row{grid-template-columns:1fr;gap:2px}.screen-page{min-height:0;margin:0;border:0;box-shadow:none;padding:14px}.print-presentation-page{width:100%;height:auto;min-height:0;box-shadow:none}.print-slide{min-height:42vh}
}

@media print{
  @page{size:letter;margin:.48in}
  @page presentation2up{size:letter portrait;margin:.25in}
  body{font-size:11pt;background:#fff}
  .wrap{max-width:none;padding:0}.hero,.section{box-shadow:none}.no-print,.quick-actions,.screen-only,.presentation-nav{display:none!important}
  .report-page,.practice-page,.packet-page,.student-set,.teacher-guide{max-width:none;padding:0}
  a{color:#000;text-decoration:none}.page-break{break-before:page;page-break-before:always}
  .duplex-blank-page{display:block;height:9.9in;min-height:9.9in;background:#fff;border:0;margin:0;padding:0;break-after:page;page-break-after:always}
  .practice-block,.feedback-box,.card,.stat,.math-display,.visual-block,.graph-frame,mjx-container,.question-review-card,.teacher-question,.cut-card,.find-someone-box{break-inside:avoid;page-break-inside:avoid}
  .presentation-shell{display:block;height:auto;overflow:visible}.presentation-question{display:block;min-height:0;padding:0}.presentation-card{width:auto;font-size:12pt}
  .screen-page{max-width:none;min-height:0;margin:0;border:0;box-shadow:none;padding:0}
  .print-presentation-wrap{max-width:none;padding:0}.print-presentation-page{page:presentation2up;width:auto;height:10.5in;min-height:10.5in;margin:0;border:0;box-shadow:none;padding:0;gap:.14in}.print-slide{height:5.18in;border-radius:0}.print-slide .slide-question{font-size:20pt}
  .student-set-grid{gap:6px 12px}.student-question{padding:6px 1px 8px}.teacher-guide-grid{gap:7px}
}

/* ========================================================================== */
/* GOLD LAYOUT LOCK ADDITIONS - 2026-09-20                                   */
/* Existing response/report/dashboard rules above are the frozen baseline.   */
/* These additions only implement the approved Set 1 activity/worksheet      */
/* changes. Do not redesign unrelated response surfaces.                     */
/* ========================================================================== */

/* Algebra-style Activity Options / projectable direction pages */
.activity-options-wrap{max-width:980px;margin:0 auto;padding:0}
.activity-page{min-height:9.3in;page-break-after:always;break-after:page;border:2px solid var(--ink);padding:16px 18px;display:flex;flex-direction:column;background:#fff;margin:14px auto;max-width:980px}
.activity-page:last-child{page-break-after:auto;break-after:auto}
.dir-header{display:flex;justify-content:space-between;align-items:flex-end;border-bottom:3px solid var(--accent-dark);padding-bottom:8px;margin-bottom:16px;gap:16px}
.act-eyebrow{font-size:12pt;font-weight:800;letter-spacing:.05em;color:var(--muted);text-transform:uppercase;margin-bottom:4px}
.act-title{font-size:18pt;font-weight:900;color:var(--accent-dark);margin:0 0 4px;line-height:1.1}
.act-subtitle{font-size:14pt;font-weight:700;color:var(--ink)}
.act-meta{font-size:11.5pt;text-align:right;line-height:1.5;flex-shrink:0}
.dir-body{display:flex;gap:.5in;flex:1;align-items:flex-start;padding-top:4px}
.dir-text{flex:1.5;font-size:12pt;line-height:1.55}
.dir-row{margin-bottom:12px}
.dir-label{font-weight:900;color:var(--accent-dark);display:block;margin-bottom:4px;font-size:12pt;text-transform:uppercase;letter-spacing:.04em}
.dir-text ol,.dir-text ul{margin:4px 0 4px 22px}.dir-text li{margin-bottom:5px}
.dir-goal{margin-top:14px;font-style:italic;color:var(--muted);font-size:11.5pt}
.looks-like{flex:1;display:flex;flex-direction:column;gap:12px;min-width:2.5in;flex-shrink:0}
.looks-good{background:#f0fdf4;border:1.5px solid #86efac;border-radius:8px;padding:12px 14px}
.looks-bad{background:#fff1f2;border:1.5px solid #fca5a5;border-radius:8px;padding:12px 14px}
.looks-header{font-size:11pt;font-weight:900;margin-bottom:8px}.looks-good .looks-header{color:#15803d}.looks-bad .looks-header{color:#b91c1c}
.looks-good ul,.looks-bad ul{margin-left:18px;font-size:11pt;line-height:1.5}.looks-good li,.looks-bad li{margin-bottom:5px}
.activity-utility-list{display:flex;flex-wrap:wrap;gap:8px;margin-top:6px}.activity-utility-list a{font-weight:800}

/* Algebra-style Set 1 Questions & Solutions projection deck */
.projection-deck{max-width:980px;margin:0 auto;padding:0}
.projection-deck .activity-page{margin:14px auto}
.prob-head{display:flex;justify-content:space-between;align-items:center;border:1.5px solid #86efac;border-bottom:2px solid #15803d;border-radius:5px;padding:8px 10px;margin-bottom:12px;font-size:12pt;font-weight:800;color:#333;background:#f0fdf4}
.solution-page .prob-head{background:#fff1f2;border-color:#fca5a5;border-bottom-color:#b91c1c}
.prob-q{font-size:16pt;margin:0 0 14px;line-height:1.35}.prob-q .graph-frame,.prob-q .visual-block{margin:12px auto}.prob-q img,.prob-q svg{max-width:5.69in;max-height:4.5in;width:auto;height:auto;object-fit:contain}
.projection-work{flex:1;background:#fff;min-height:3.5in;margin-top:8px}
.solution{font-size:16pt;margin:12px 0 8px;padding-top:10px;border-top:2px solid var(--ink);line-height:1.35}.solution b{color:var(--accent-dark)}

/* Worksheet Builder-style screen controls for Set 1 student handouts */
.layout-controls{position:sticky;top:0;z-index:20;background:#eef4f8;border:1px solid #c9d5df;padding:10px 12px;display:flex;gap:12px;align-items:center;flex-wrap:wrap;font-size:12px}
.layout-controls label{font-weight:800}.layout-controls input[type=range]{width:100%}.layout-controls input[type=number]{width:76px}.layout-controls select{width:100%;padding:6px 7px;border:1px solid #aeb8c4;border-radius:5px;background:#fff;font:inherit}.layout-controls button{cursor:pointer}.layout-controls .control-group{display:grid;gap:4px}.layout-controls .selection-note{font-size:11px;color:var(--muted);line-height:1.25}
.adjustable-set-sheet{--workspace-height:1.1in;--graph-width:100%}
.adjustable-set-sheet .student-question{--problem-workspace-height:var(--workspace-height);--problem-graph-width:var(--graph-width)}
.adjustable-set-sheet .student-question .workspace{height:var(--problem-workspace-height);min-height:0;overflow:hidden;margin-top:7px}
.adjustable-set-sheet .student-question .graph-frame,.adjustable-set-sheet .student-question .visual-block{width:min(100%,var(--problem-graph-width));max-width:100%;margin:7px auto}
.adjustable-set-sheet .student-question .graph-frame img,.adjustable-set-sheet .student-question .graph-frame svg,.adjustable-set-sheet .student-question .visual-block img,.adjustable-set-sheet .student-question .visual-block svg{display:block;width:100%;max-width:100%;height:auto;margin:0 auto}
.find-someone-student-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:9px 14px}
.find-someone-student-grid .student-question{border-top:1px solid #dce2e9;padding:8px 2px 10px;break-inside:auto;page-break-inside:auto}
.find-someone-student-grid .partner-signature{font-size:11px;font-weight:800;color:#333;margin:8px 0 5px;padding-bottom:4px;border-bottom:1px solid #aaa}
.find-someone-student-grid .workspace-label{font-size:10.5px;font-weight:800;color:#555;margin-top:5px}
.find-someone-directions{font-size:12px;color:#444;margin:0 0 10px}

@media screen and (min-width:1100px){
  body.adjustable-handout-page{padding-left:252px}
  body.adjustable-handout-page .layout-controls{position:fixed;left:14px;top:14px;width:224px;max-height:calc(100vh - 28px);overflow:auto;flex-direction:column;align-items:stretch;gap:10px;border-radius:10px;box-shadow:0 4px 14px rgba(0,0,0,.12)}
  body.adjustable-handout-page .layout-controls>*{width:100%}
  body.adjustable-handout-page .layout-controls label{display:block}
}
@media screen and (max-width:1099px){body.adjustable-handout-page{padding-left:0}.layout-controls{position:relative}}
@media(max-width:700px){.dir-body{display:block}.looks-like{min-width:0;margin-top:14px}.find-someone-student-grid{grid-template-columns:1fr}}
@media print{
  .layout-controls{display:none!important}body.adjustable-handout-page{padding-left:0!important}
  .activity-page{margin:0;min-height:9.3in}.projection-deck .activity-page{margin:0}
}

/* ========================================================================== */
/* GOLD LOCK FUNCTIONAL ADDITIONS - 2026-09-20 FINAL REVIEW PASS             */
/* Preserves the tested response design while adding true page previews,      */
/* adjustable spacing controls, HTML-first printing, and the approved Set 1   */
/* question-top / teacher-bottom presentation layout.                         */
/* ========================================================================== */

/* True Letter page fragments shared by adjustable printable HTML. */
.adjustable-print-root{--page-width:8.5in;--page-height:11in;--page-margin:.48in;--usable-height:10.04in;--question-space:1.05in;--visual-width:100%;background:#e8edf1;min-height:100vh}
.adjustable-page-stack{width:100%;padding:1px 0 18px}
.letter-preview-page{page:adjustableLetter;width:var(--page-width);height:var(--page-height);min-height:var(--page-height);margin:.22in auto;background:#fff;padding:var(--page-margin);overflow:hidden;position:relative;break-after:page;page-break-after:always;border:1px solid #d3d8de;box-shadow:0 4px 18px rgba(20,28,36,.14)}
.letter-preview-page:last-child{break-after:auto;page-break-after:auto}
.letter-preview-page::after{content:"Page " attr(data-page);position:absolute;right:.18in;bottom:.13in;font-size:9px;line-height:1;color:#8a939e;letter-spacing:.02em}
.blank-duplex-page{background:#fff}
.blank-duplex-page>*{display:none!important}

/* Left rail: same interaction language as Worksheet Builder. */
.adjustable-print-root .layout-controls{background:#eef4f8;border:1px solid #c9d5df}
.layout-controls .control-actions{display:grid;grid-template-columns:1fr 1fr;gap:6px}
.layout-controls button{border:1px solid #8da0b3;background:#fff;color:var(--accent-dark);font-weight:800;border-radius:6px;padding:7px 9px}
.layout-controls button.primary-control{background:var(--accent-dark);color:#fff;border-color:var(--accent-dark)}
.layout-controls output{font-weight:800;color:var(--accent-dark)}
.layout-controls .control-value-row{display:grid;grid-template-columns:1fr 62px;gap:6px;align-items:center}
.layout-controls .control-value-row input[type=number]{width:62px}

/* Adjustable question/workspace geometry used by Common Worksheet and practice. */
.adjustable-question{--problem-workspace-height:var(--question-space);--problem-visual-width:var(--visual-width)}
.adjustable-question .workspace,.adjustable-question .workarea{height:var(--problem-workspace-height);min-height:0;overflow:hidden}
.adjustable-question .visual-block,.adjustable-question .graph-frame{width:min(100%,var(--problem-visual-width));max-width:100%;margin-left:auto;margin-right:auto}
.adjustable-question .visual-block img,.adjustable-question .visual-block svg,.adjustable-question .graph-frame img,.adjustable-question .graph-frame svg{display:block;width:100%;max-width:100%;height:auto;margin:0 auto}

/* Combined printable report/practice HTML. */
.combined-student-document{width:100%}
.student-segment{display:contents}
.combined-report-page .report-page,.combined-practice-page .practice-page{max-width:none;margin:0;padding:0}
.combined-report-page .report-page{height:100%}
.combined-practice-page .practice-page{height:100%}

/* Set 1 teacher classroom pages: question top half, teacher support bottom half. */
.set-classroom-page{page:adjustableLetter;width:8.5in;height:11in;min-height:11in;margin:.22in auto;background:#fff;padding:.25in;display:grid;grid-template-rows:1fr 1fr;gap:.14in;overflow:hidden;position:relative;border:1px solid #d3d8de;box-shadow:0 4px 18px rgba(20,28,36,.14);break-after:page;page-break-after:always}
.set-classroom-page:last-child{break-after:auto;page-break-after:auto}
.set-classroom-page::after{content:"Page " attr(data-page);position:absolute;right:.16in;bottom:.10in;font-size:9px;color:#8a939e}
.set-half{border:1.4px solid #98a5b3;border-radius:9px;padding:.18in .21in;overflow:hidden;display:flex;flex-direction:column;justify-content:flex-start}
.set-question-half{--problem-question-space:.9in;--problem-visual-width:100%}
.set-question-half .set-label,.set-teacher-half .set-label{font-size:10.5px;font-weight:800;color:var(--muted);margin-bottom:4px}
.set-question-half .set-prompt{font-size:20pt;line-height:1.24}
.set-question-half .question-space{height:var(--problem-question-space);min-height:0;overflow:hidden}
.set-question-half .visual-block,.set-question-half .graph-frame{width:min(100%,var(--problem-visual-width));max-width:100%;margin:7px auto}
.set-question-half img,.set-question-half svg{display:block;width:100%;max-width:100%;height:auto;max-height:3.0in;object-fit:contain;margin:0 auto}
.set-teacher-half{font-size:13.5pt;line-height:1.35}
.set-teacher-half .guide-answer{background:#f5f8fb;border-left:3px solid var(--accent);padding:8px 10px;margin:4px 0 10px}
.set-teacher-half .guide-move{margin:7px 0;color:#39475a}
.set-teacher-half .guide-move strong{color:var(--ink)}

/* Activity Options group headings/material cues without changing the gold shell. */
.activity-group{margin:10px 0 16px}
.activity-group-title{font-size:11.5pt;font-weight:900;color:var(--accent-dark);text-transform:uppercase;letter-spacing:.04em;margin:0 0 5px}
.activity-material{font-size:10.5pt;color:var(--muted);font-weight:700}

@media screen and (min-width:1100px){
  body.adjustable-print-root{padding-left:252px}
  body.adjustable-print-root .layout-controls{position:fixed;left:14px;top:14px;width:224px;max-height:calc(100vh - 28px);overflow:auto;flex-direction:column;align-items:stretch;gap:10px;border-radius:10px;box-shadow:0 4px 14px rgba(0,0,0,.12)}
  body.adjustable-print-root .layout-controls>*{width:100%}
  body.adjustable-print-root .layout-controls label{display:block}
}
@media screen and (max-width:1099px){
  body.adjustable-print-root{padding-left:0}
  body.adjustable-print-root .layout-controls{position:relative}
}
@media screen and (max-width:760px){
  .letter-preview-page,.set-classroom-page{width:100%;height:auto;min-height:11in;margin:.16in auto;box-shadow:none}
  .set-question-half .set-prompt{font-size:16pt}
}

@media print{
  @page adjustableLetter{size:Letter portrait;margin:0}
  body.adjustable-print-root{padding-left:0!important;background:#fff}
  .adjustable-print-root .layout-controls{display:none!important}
  .adjustable-page-stack{padding:0}
  .letter-preview-page{width:8.5in;height:11in;min-height:11in;margin:0;border:0;box-shadow:none;padding:.48in;overflow:hidden}
  .letter-preview-page::after{display:none}
  .set-classroom-page{width:8.5in;height:11in;min-height:11in;margin:0;border:0;box-shadow:none;padding:.25in;overflow:hidden}
  .set-classroom-page::after{display:none}
}
`;

  const STATION_CSS_FALLBACK = String.raw`@page{size:letter landscape;margin:0}:root{--navy:#00003d;--page-w:11in;--page-h:8.5in}*{box-sizing:border-box}body{font-family:Arial,Helvetica,sans-serif;color:#111;background:#e8e8e8}.page{width:var(--page-w);height:var(--page-h);margin:0 auto .25in;background:#fff;padding:.32in .42in .24in;display:flex;flex-direction:column;overflow:hidden;page-break-after:always}.header{background:var(--navy);color:#fff;font-size:21pt;font-weight:800;padding:.11in .20in;margin-bottom:.12in}.station-grid{display:grid;grid-template-columns:1fr 1fr;gap:.10in .13in}.station-problem{border:1.2px solid #222;border-radius:5px;padding:.08in;font-size:10.2pt;break-inside:avoid}.figure img,.figure svg{display:block;max-width:100%;max-height:1.9in;height:auto;margin:0 auto}.page-footer{margin-top:auto;font-size:7.5pt}.station-index{width:11in;min-height:8.5in;margin:0 auto;background:#fff;padding:.45in}@media print{body{background:#fff}.page{margin:0}.station-index{display:none}}`;

  const COMMON_PRACTICE_FALLBACK = String.raw`# Common Course Practice & Question Review Guide

STATUS: REQUIRED FOR GRADING & EVIDENCE RESPONSE BUILDS  
VERSION: district-grading-common-practice/1.6  
DATE: 2026-09-20

This guide controls Common Course Practice and Set 1 delivery. If older request wording conflicts with this file, this file controls. \`RESPONSE_LAYOUT_LOCK.md\` controls visual continuity.

## 1. One approved class-level question pool - HARD
Build one coherent class-level question pool from the strongest common instructional needs plus justified extension/transfer targets. Author, solve, and validate each question exactly once. Reuse the same approved question object across every delivery format.

When a question is reused, its prompt, answer, graph/diagram asset, difficulty, teacher move, and student discourse move remain identical. Delivery templates may change presentation only. Do not re-author, re-solve, or independently re-grade the same Set 1 question for each view.

## 2. Common Worksheet / Review + Extension - GOLD
Keep the current approved two-column Common Worksheet layout.

The student worksheet visibly separates:

- **Review** - observed common needs, unfinished understanding, or prerequisites.
- **Extension / Transfer** - application/transfer for students already showing Convincing evidence or a justified class-wide extension target.

Required behavior:

- compact header with Name / Date;
- natural two-column question flow;
- no forced wasteful question-per-page breaks;
- browser-print HTML is canonical; do not generate a duplicate PDF;
- use real Letter-size screen page previews whose boundaries match browser Print;
- add the Worksheet Builder-style screen-only left control rail in this order: **All workspaces**, **Problem**, **Workspace**, **Graph / diagram** when applicable, **Reset**, **Print**;
- changing workspace or graph size repaginates immediately and visibly;
- controls disappear in print.

The same \`student_worksheet.html\` is also the student handout used for **Find Someone Who**. Do not create a second Find Someone Who worksheet with a different title or layout.

## 3. Teacher Guide - one teacher review authority
\`print/common_review_extension/teacher_guide.html\` is the single teacher-facing review for the shared Common Worksheet / Set 1 questions.

Keep the current approved two-column Teacher Guide layout:

- question number + Review or Extension / Transfer purpose;
- exact prompt;
- concise **Answer**;
- concise **Teacher move**;
- concise **Student discourse move**.

Do not generate duplicate compact Review All pages or a second Set 1 teacher guide containing the same information. Links that formerly opened those duplicates should point to this Teacher Guide.

## 4. Set 1 is the one mathematical set
Create exactly one class-level **Set 1**. Do not create Set 2.

Set 1 is the same question pool used by:

- Common Worksheet;
- Teacher Guide;
- Set 1 classroom presentation;
- Print Presentation;
- Find Someone Who, via the Common Worksheet;
- Cut-Apart Question Cards;
- classroom participation structures.

There is no fixed Set 1 size. Every Set 1 delivery uses the full approved set unless a station intentionally selects a separate station-specific subset.

## 5. \`print/question_set/index.html\` = Activity Options page
The Set 1 landing page itself is the Activity Options page, closely following the structure and hierarchy of:

\`algebra/activities/u1_1_act1/u1_1_act1.html\`

Use the locked district response colors/typography. Do not insert a six-card menu before it and do not create a second structures index/directions maze.

At the **top of the page**, before the participation structures, show:

### Teacher / Print Utilities

- **Print Presentation** -> \`print_presentation.html\`
- **Teacher Guide** -> \`../common_review_extension/teacher_guide.html\`

Also show the concise **Set 1 focus** line in this top utility area.

Do not include a Review All Questions utility; the approved Teacher Guide replaces it.

## 6. Classroom Participation Structures
Rename the old **Projection / Whiteboard Options** section to **Classroom Participation Structures** so the tool works beyond math classes.

Organize the choices into these two subgroups.

### Shared Prompt / Partner Structures
Each structure links to its directions section on the same page. Its Set 1/material link points to \`presentation.html\` unless noted otherwise.

- Whiteboard Indy
- Whiteboard Partners
- Rally Coach
- **Speed Dating**
- Showdown
- Think, Trade, Agree
- Round Table
- **Hot Seat**
- Rally Coach II

### Card-Based Structures
These use the single shared \`structures/cut_apart_cards.html\` deck. Do not create new card sets.

- **Quiz-Quiz-Trade**
- **Fan-N-Pick**
- **Mix-Pair-Share with Cards**
- **Inside-Outside Circle with Cards**

For every structure, include a corresponding directions section below using the same approved Algebra activity hierarchy:

- compact eyebrow/title/subtitle;
- **Structure**;
- **Setup**;
- concise ordered **Directions**;
- **Goal**;
- a clear Set 1 / Cards material link;
- right-side **Looks Like Success / Doesn't Look Like** boxes.

These sections are locked templates populated with the current assignment title/focus; they are not newly designed each run.

### Established directions

**Whiteboard Indy** - individual independent practice; each student has a board/marker; notes welcome; try first; write large/clearly; partners support reasoning rather than copying; revise mistakes. Goal: individual accountability + low-stakes entry.

**Whiteboard Partners** - fast partner practice; one board/marker per pair; both engaged; alternate writer; explain before erasing; resolve disagreements with evidence. Goal: engagement + quick feedback.

**Rally Coach** - partner explanation + alternating roles; one explains while one records; coach with questions not answers; switch each problem; both verify. Goal: verbal reasoning + procedural accuracy.

**Speed Dating** - independent attempt -> timed partner comparison -> rotation; share a strategy and carry one useful idea forward. Goal: repeated explanation + strategy comparison.

**Showdown** - individual think -> simultaneous reveal -> team check. Goal: individual accountability + team feedback.

**Think, Trade, Agree** - individual think -> trade explanations -> clarifying question -> justified agreement/disagreement. Goal: evidence-based comparison.

**Round Table** - team rotation of written reasoning; read prior work before adding; team checks the complete response. Goal: visible collaborative reasoning.

**Hot Seat** - describe -> reason -> reveal; use precise subject-specific language without simply giving the final response. Goal: academic language + listening.

**Rally Coach II** - solve -> coach -> restate -> switch. Goal: metacognition + partner coaching.

**Quiz-Quiz-Trade** - each student receives one card; pair; Partner A quizzes Partner B; A coaches/checks; switch roles; trade cards; find a new partner. Goal: repeated retrieval + peer explanation.

**Fan-N-Pick** - teams of four rotate roles: Fan, Pick, Answer, Coach/Check; rotate roles after each card. Goal: equal participation + structured peer feedback.

**Mix-Pair-Share with Cards** - students mix; pair on signal; use one partner's card as the prompt; each responds/explains; trade or retain cards as directed; mix again. Goal: rapid partner variety + retrieval.

**Inside-Outside Circle with Cards** - paired inner/outer circles respond to a card; partners explain/check; one circle rotates on signal; repeat with the new partner/card. Goal: repeated explanation + broad peer interaction.

## 7. Printable Handouts
List exactly:

- **Stations** - link to the existing Stations product;
- **Find Someone Who** - link directly to \`../common_review_extension/student_worksheet.html\`;
- **Cut-Apart Question Cards** - link to \`structures/cut_apart_cards.html\`.

Find Someone Who does not own a separate worksheet file. Its participation directions live on the Activity Options page; the student uses the same Common Worksheet.

## 8. Set 1 classroom presentation - gold half-page question/answer layout
\`print/question_set/presentation.html\` uses the current approved Print Presentation visual language, but with **one Set 1 problem per Letter page**:

- top half = the question, top-aligned;
- bottom half = **Answer**, **Teacher move**, and **Student discourse move**, top-aligned;
- use the locked rounded-panel presentation treatment and typography;
- no Back/Next shell;
- no alternating separate Question and Solution pages;
- all Set 1 problems, one physical page per problem.

Add a Worksheet Builder-style screen-only left rail:

1. **All question spacing** - applies to the current Set 1 pages without changing mathematics;
2. **Problem** selector;
3. **Question spacing / workspace** for the selected problem;
4. **Graph / diagram** size when applicable;
5. **Reset**;
6. **Print**.

Show true Letter-size page boundaries on screen. Slider changes must update the preview immediately. Graph controls resize geometry only; stroke weights remain canonical. The answer/moves region starts in the lower half and must not drift into the question half.

## 9. Print Presentation - one problem per Letter page
Use the same locked one-problem Letter template as the classroom Set 1 view: question top half; Answer + Teacher move + Student discourse move bottom half; left spacing/graph controls; real page preview; Print matches preview. Do not create a separate two-up question-only version.

## 10. Cut-Apart Question Cards - LOCKED
The current card artifact is approved and remains visually unchanged except for the actual Set 1 content/required visual.

- one task per card;
- dashed cut lines;
- complete Set 1 across enough pages/cards;
- no answer on the question side;
- shared by the four card-based structures above.

## 11. Stations - GOLD / HTML ONLY
Keep the exact approved Stations landing page, student-station pages, station cards, answer-key markup, and station CSS as literal mad-lib templates. Only current titles/questions/answers/visuals/counts are injected.

- exactly four review stations plus two extension stations;
- 4-6 questions each;
- separate answer key;
- \`Open Student Stations\` and \`Open Answer Key\` HTML links only;
- do not generate Student PDF or Answer Key PDF duplicates.

## 12. Combined student printing - HTML first
Top dashboard quick actions use printable HTML:

- **Print All Student Reports** -> combined printable HTML;
- **Print All Individual Practice** -> combined printable HTML;
- **View Scanned Student Work** -> preserved submitted scan/PDF.

Do not generate duplicate combined report/practice PDFs.

Combined printable HTML remains duplex-safe: each student's segment occupies an even number of physical browser-print pages. Insert one truly blank page only when a student's rendered segment is odd so the next student begins on a sheet front.

### Combined Individual Practice controls
Use true Letter-size page previews plus the left rail: **All workspaces**, **Problem**, **Workspace**, **Graph / diagram** when applicable, **Reset**, **Print**. Changing controls repaginates immediately.

### Combined Student Reports
Show true Letter-size page previews and a screen-only Print control. Question-workspace sliders are not required when the report itself contains no adjustable question workspace.

## 13. Adjustable HTML page geometry - HARD
For adjustable student/practice/set HTML:

- screen preview shows real 8.5 x 11 in page fragments on the gray background;
- browser Print uses the same page fragments and boundaries;
- use explicit page containers and deterministic repagination after MathJax, workspace changes, graph/diagram changes, or content changes;
- avoid stale page assignments and avoidable large blank regions;
- never clip content merely to preserve an old page count;
- screen page count and browser Print page count must agree.

## 14. Math, graphs, and visuals
All products inherit the packaged Math / Graph / Visual QA contract and District Graph Rendering Standard.

- supported Cartesian graphs, including blank grids, use the packaged canonical graph tool;
- reuse the exact same graph asset anywhere a question is reused;
- prefer SVG assets for adjustable HTML;
- graph size controls scale geometry, not stroke weights;
- record graph tool entrypoint + asset path in \`data/qa.json\`;
- student construction visuals remain answer-neutral.

## 15. Gold layout lock
Follow \`response_contract/RESPONSE_LAYOUT_LOCK.md\` as a HARD contract. Copy \`styles.css\` byte-for-byte. The current tested response remains the visual baseline everywhere except for the explicitly approved changes in that lock.

## 16. QA requirements
Before delivery verify:

- one Set 1 only / no Set 2;
- shared question objects are solved/validated once and reused, not regenerated per view;
- Common Worksheet visibly labels Review and Extension / Transfer;
- Common Worksheet has left controls and real Letter page previews;
- Find Someone Who links to that exact Common Worksheet file;
- Teacher Guide is the one teacher review authority; no duplicate Review All pages;
- Activity Options begins with Teacher / Print Utilities and Set 1 focus;
- Classroom Participation Structures contains both Shared Prompt / Partner and Card-Based subgroups;
- Speed Dating and Hot Seat use those exact names;
- all four card structures have full directions sections and use the one Cut-Apart deck;
- Set 1 presentation has question top half + answer/moves bottom half, with left controls and true page preview;
- Print Presentation uses one Letter page per problem with question top half and answer/moves bottom half, with live controls and page preview;
- Cut-Apart Cards match the current gold layout;
- Stations expose HTML only, no generated station PDFs;
- combined reports/practice quick actions open HTML, not generated PDFs;
- no Tarsia or Blooket;
- graph style/provenance pass the canonical standard;
- locked CSS hash matches;
- links resolve and \`data/qa.json\` has no unresolved failure.
`;

  const RESPONSE_LAYOUT_LOCK_FALLBACK = String.raw`# Grading Response Gold Layout Lock

STATUS: HARD / REQUIRED  
VERSION: district-grading-response-layout-lock/1.3  
DATE: 2026-09-20  
LOCKED CSS SHA-256: \`2ab8acdc2cfa74f288906ce88dd430c9715e74d16ed66cbf61e45f311558d7ad\`

## Purpose
The tested 2026-09-20 Precalculus Circuit Training grading response is the visual baseline for this tool. Future runs preserve that response system instead of inventing a new layout on each run.

\`response_contract/styles.css\` is the canonical response stylesheet. The response copies it byte-for-byte to \`assets/styles.css\`; \`data/qa.json\` records the expected/actual SHA and PASS only when they match.

## Stable surfaces - DO NOT REDESIGN
Keep the current gold layout/markup hierarchy for these unless a later teacher-approved contract explicitly changes one:

- \`CLICK_ME.html\` overall dashboard hierarchy and button treatment;
- **Individual Student Reports & Practice** dashboard section;
- individual student report pages;
- **Class Data** / class overview page;
- individual practice question styling;
- Common Worksheet visual language;
- Common Worksheet Teacher Guide;
- Stations landing page, student stations, and station answer key;
- Print Presentation one-problem Letter-page shell;
- Cut-Apart Question Cards.

Do not change hero sizes, card shapes, typography hierarchy, border/radius system, dashboard student-card grid, class-summary cards, report boxes, station styling, or cut-card styling because another design seems cleaner.

## Approved functional/layout changes in this revision
These changes are intentional and are now part of the gold system:

1. Top quick actions **Print All Student Reports** and **Print All Individual Practice** open combined printable HTML rather than generated PDFs. **View Scanned Student Work** remains the preserved scan/PDF.
2. Generated classroom/teacher print products are HTML-first. Duplicate generated PDFs are removed unless explicitly requested.
3. Common Worksheet keeps its current visual design but gains Worksheet Builder-style left controls plus true Letter-size screen page previews and deterministic repagination.
4. Find Someone Who links to the exact Common Worksheet HTML; it does not own a separately titled/restyled worksheet.
5. \`print/common_review_extension/teacher_guide.html\` is the one approved teacher review layout for the shared Common Worksheet / Set 1 questions. Duplicate Review All pages and duplicate Set 1 teacher guides are removed.
6. The Activity Options page begins with **Teacher / Print Utilities** and the Set 1 focus line, then **Classroom Participation Structures** with Shared Prompt / Partner and Card-Based subgroups.
7. **Speed Dating Math** is renamed **Speed Dating** and **Mathematical Hot Seat** is renamed **Hot Seat**.
8. Card-based structures are Quiz-Quiz-Trade, Fan-N-Pick, Mix-Pair-Share with Cards, and Inside-Outside Circle with Cards. They all reuse the one locked Cut-Apart Question Cards deck.
9. Set 1 classroom presentation uses the approved rounded-panel visual language with one Letter page per problem: question in the top half, Answer + Teacher move + Student discourse move in the bottom half. It gains left layout controls and real page previews.
10. Print Presentation uses the same locked one-problem Letter shell as the classroom Set 1 view: question top half; Answer + Teacher move + Student discourse move bottom half; controls/page preview.
11. Combined Individual Practice gains true Letter page previews, spacing/workspace controls, graph/diagram controls, and deterministic repagination. Combined Student Reports gains true page previews and browser Print without a duplicate PDF.
12. Stations keep their current look but expose HTML Student Stations + HTML Answer Key only.
13. Supported Cartesian graphs use the current canonical district graph tool and District Graph Rendering Standard; no page-local CSS may restyle graph strokes away from the standard.

## HTML/CSS discipline
- Existing baseline CSS remains unchanged except for appended/targeted classes needed for the approved controls/page-preview/set-half layout above.
- Do not add page-local \`<style>\` blocks that restyle shared gold classes.
- Do not invent alternate dashboard/card/page systems.
- Content may change from run to run; the shell/layout does not.
- Longer content is handled with natural deterministic pagination, not a new design language.
- Workspace/spacing/graph controls may set CSS custom properties or inline values needed for sizing; they may not restyle the page.
- Cut-Apart Cards remain visually unchanged.

## Locked page-preview behavior
Adjustable HTML uses explicit 8.5 x 11 in page containers on screen and print. Screen shows white pages against the gray preview background with visible boundaries. Browser Print uses those same page containers. Controls are screen-only and disappear in print.

## QA
Before delivery verify:

- \`assets/styles.css\` exactly matches packaged \`response_contract/styles.css\` and SHA-256 \`2ab8acdc2cfa74f288906ce88dd430c9715e74d16ed66cbf61e45f311558d7ad\`;
- every stable surface still uses the gold class hierarchy;
- only the approved changes above alter structure;
- duplicate Review All pages are absent;
- generated duplicate classroom PDFs are absent;
- Find Someone Who resolves to the Common Worksheet;
- Cut-Apart Cards are unchanged visually;
- no unapproved page-local CSS overrides the gold stylesheet.
`;

  const MATH_VISUAL_QA_CONTRACT = String.raw`# Math, Graph, Visual, and Station QA Contract

STATUS: REQUIRED
VERSION: district-grading-math-visual-qa/1.6

## Math rendering - HARD
- Use valid TeX and MathJax whenever mathematical notation is appropriate.
- Preferred delimiters are \\( ... \\) inline and \\[ ... \\] display.
- HTML is the canonical generated print surface. Ensure MathJax finishes typesetting before final pagination/print QA.
- Raw TeX, missing symbols, or clipped math is a failure.
- Prefer fraction-bar notation for symbolic division when that is the natural mathematical form.

## HTML-first print rule - HARD
- Do not generate duplicate PDFs for generated reports, practice, Common Worksheet, Stations, Set 1 presentation, Print Presentation, Teacher Guide, or Cut-Apart Cards when the HTML already provides the canonical browser-print product.
- The preserved/scanned student-work archive may remain PDF because it is source evidence, not a duplicated generated classroom artifact.
- Adjustable print HTML must show true Letter-size page boundaries on screen and use the same boundaries in browser Print.

## Graphs - HARD
- If text asks for, refers to, or depends on a graph, create the actual mathematically accurate graph.
- The request ZIP packages the current registered graph tool and District Graph Rendering Standard. For every supported Cartesian graph, including blank student construction grids, use that packaged tool directly.
- A graph that only resembles the district style but was drawn by hand-built SVG/CSS/canvas is a failure.
- Save graph assets under assets/graphs/ and embed the same asset anywhere the question is reused.
- Record renderer entrypoint + asset path for every Cartesian graph in data/qa.json.
- Never substitute prose, ASCII art, CSS sketches, browser-drawn axes, or another plotting style for a graph supported by the packaged registered graph tool.

## Images and diagrams - HARD
- If text refers to a diagram, figure, image, model, setup, or other visual, create and embed the actual visual.
- Save generated non-graph visuals under assets/visuals/.

## Evidence rating - HARD
Every student report uses exactly one of these labels: Convincing, Limited, Incorrect, Not Observed.
- Convincing: evidence clearly and sufficiently demonstrates the target.
- Limited: meaningful correct evidence is present, but incomplete, inconsistent, or insufficient.
- Incorrect: the student attempted the target and the evidence demonstrates a substantive incorrect idea, method, or conclusion.
- Not Observed: there is not enough usable evidence to judge the target, including blank, omitted, missing, or unreadable work. Not Observed is not Incorrect.

## Duplex student-document pairing - HARD
- Applies to combined student reports and combined individual-practice HTML.
- Every student's segment must occupy an EVEN number of physical browser-print pages.
- If a student's final rendered content page count is odd, append exactly one intentionally blank Letter page before the next student.
- Verify explicit page-container order and record content pages, blank backs, and physical pages in data/qa.json. Do not generate a PDF merely to prove duplex pairing.

## Required QA record
Create data/qa.json including evidence-rating checks, MathJax checks, graph/visual checks, adjustable-page checks, duplex HTML before/after page counts, links, locked-style hash, phase timings, and failures. PASS is forbidden with unresolved failures.`;

  const RESPONSE_QA_FALLBACK = String.raw`# Grading Response QA Execution Guide

STATUS: REQUIRED FOR GRADING & EVIDENCE RESPONSE BUILDS  
VERSION: district-grading-response-qa-execution/1.5  
DATE: 2026-09-20

Use the packaged mechanical tools instead of recreating them. Run evidence_review.py once for PDF/image rendering/contact sheets, response_builder.py once for locked HTML, and response_qa.py once for repeatable file/link/hash/policy QA. Do not fetch missing renderer/runtime/QA dependencies from GitHub or the web; fail closed as a packaging error.

Student evidence still receives full review. Canonical Set 1 content is authored/verified once and reused everywhere. Locked templates are trusted after hash/mechanical QA. Visual QA is bounded to generated graphs/diagrams and actual overflow/content outliers. For adjustable pages, smoke-test one default, one mid-range, and one maximum-range state only; browser subpixel overflow <=4 px is tolerance, not a correction loop.

Once response_data.json is complete, deterministic rendering + mechanical QA + bounded visual QA should normally finish in under 90 seconds. Record real phase timings and SLOW_MECHANICAL_PATH if that stage exceeds 90 seconds.
`;

  const GRAPH_STANDARD_FALLBACK = String.raw`# District Graph Rendering Standard

VERSION: district-graph-rendering-standard/1.1

Resolve the one self-contained canonical graph runtime from Tools/MANIFEST.json -> tools.graph_tool and package only that runtime. Use it for every supported Cartesian graph, including blank construction grids. Do not replace it with hand-built SVG/CSS/canvas. Preserve approved print weights and record graph-tool provenance in data/qa.json.`;

  const evidenceInput = $("evidenceFiles");
  const rosterInput = $("rosterFiles");
  const rubricInput = $("rubricFiles");
  const gradeOutputInput = $("gradeOutput");
  const notesInput = $("teacherNotes");
  const buildButton = $("buildZip");
  const status = $("buildStatus");

  document.querySelectorAll(".chip[data-note]").forEach((button) => {
    button.addEventListener("click", () => {
      const note = button.dataset.note || "";
      const current = notesInput.value.trim();
      notesInput.value = current ? `${current}\n${note}` : note;
      notesInput.focus();
    });
  });

  evidenceInput.addEventListener("change", () => { renderFiles(evidenceInput.files, $("evidenceList")); refreshStatus(); });
  rosterInput.addEventListener("change", () => renderFiles(rosterInput.files, $("rosterList")));
  rubricInput.addEventListener("change", () => { renderFiles(rubricInput.files, $("rubricList")); refreshStatus(); });
  gradeOutputInput.addEventListener("change", refreshStatus);
  $("className").addEventListener("input", refreshStatus);
  $("clearForm").addEventListener("click", clearForm);
  buildButton.addEventListener("click", buildRequestZip);

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

  function refreshStatus() {
    const className = $("className").value.trim();
    const count = evidenceInput.files.length;
    const gradeMode = gradeOutputInput.value;
    if (!className || !count || !gradeMode) {
      const missing = [];
      if (!className) missing.push("a class/group name");
      if (!count) missing.push("at least one evidence file");
      if (!gradeMode) missing.push("a grade/score handling choice");
      setStatus(`Add ${joinList(missing)}.`, "warn");
      return false;
    }
    if (gradeMode === "rubric" && !rubricInput.files.length) {
      setStatus("Grade/score handling is set to use the rubric, but no rubric/scoring guide is attached.", "bad");
      return false;
    }
    const rosterNote = rosterInput.files.length
      ? ` Roster included (${rosterInput.files.length} file${rosterInput.files.length === 1 ? "" : "s"}).`
      : " If this is one combined handwritten class scan, adding a roster is strongly recommended.";
    setStatus(`Ready to package ${count} evidence file${count === 1 ? "" : "s"}. The assignment title will be detected from the evidence.${rosterNote}`, "good");
    return true;
  }

  function joinList(items) {
    if (items.length <= 1) return items[0] || "the required information";
    if (items.length === 2) return `${items[0]} and ${items[1]}`;
    return `${items.slice(0, -1).join(", ")}, and ${items[items.length - 1]}`;
  }

  function setStatus(message, kind) {
    status.textContent = message;
    status.className = `status ${kind}`;
  }

  function clearForm() {
    $("className").value = "";
    $("gradeSubject").value = "";
    $("teacherName").value = "";
    evidenceInput.value = "";
    rosterInput.value = "";
    rubricInput.value = "";
    gradeOutputInput.value = "";
    notesInput.value = "";
    $("evidenceList").innerHTML = "";
    $("rosterList").innerHTML = "";
    $("rubricList").innerHTML = "";
    refreshStatus();
  }

  async function buildRequestZip() {
    if (!refreshStatus()) return;
    buildButton.disabled = true;
    setStatus("Packaging request...", "warn");

    try {
      const className = $("className").value.trim();
      const gradeSubject = $("gradeSubject").value.trim();
      const teacherName = $("teacherName").value.trim();
      const teacherNotes = notesInput.value.trim();
      const gradeMode = gradeOutputInput.value;
      const createdAt = new Date().toISOString();

      const usedPaths = new Set();
      const evidenceManifest = [];
      const rosterManifest = [];
      const rubricManifest = [];
      const entries = [];

      for (const file of [...evidenceInput.files]) {
        const packagedName = uniqueName(safeFileName(file.name), usedPaths, "evidence");
        const path = `evidence/${packagedName}`;
        evidenceManifest.push(fileManifest(file, path));
        entries.push({ name: path, data: new Uint8Array(await file.arrayBuffer()) });
      }
      for (const file of [...rosterInput.files]) {
        const packagedName = uniqueName(safeFileName(file.name), usedPaths, "roster");
        const path = `roster/${packagedName}`;
        rosterManifest.push(fileManifest(file, path));
        entries.push({ name: path, data: new Uint8Array(await file.arrayBuffer()) });
      }
      for (const file of [...rubricInput.files]) {
        const packagedName = uniqueName(safeFileName(file.name), usedPaths, "rubric");
        const path = `rubric/${packagedName}`;
        rubricManifest.push(fileManifest(file, path));
        entries.push({ name: path, data: new Uint8Array(await file.arrayBuffer()) });
      }

      const scannedWorkFilename = `${friendlyFilePart(className)}_Scanned_Student_Work.pdf`;
      const request = {
        schema: REQUEST_SCHEMA,
        created_at: createdAt,
        response_style_version: RESPONSE_STYLE_VERSION,
        station_style_version: STATION_STYLE_VERSION,
        math_visual_qa_version: MATH_VISUAL_QA_VERSION,
        common_practice_version: COMMON_PRACTICE_VERSION,
        response_qa_execution_version: RESPONSE_QA_VERSION,
        graph_rendering_standard_version: GRAPH_RENDERING_STANDARD_VERSION,
        teacher: {
          name: teacherName || null,
          class_or_group: className,
          grade_subject: gradeSubject || null
        },
        assignment: {
          name: null,
          detection_mode: "derive_from_uploaded_evidence",
          fallback: "Student Evidence Review",
          detection_priority: [
            "visible title on submitted student work",
            "rubric/scoring-guide title",
            "meaningful evidence filenames",
            "concise title inferred from the actual skill/content in the evidence",
            "Student Evidence Review only when no more informative title can be supported"
          ]
        },
        evidence_rating: {
          schema: "convincing-limited-incorrect-not-observed/1.0",
          required_on_each_student_report: true,
          labels: ["Convincing", "Limited", "Incorrect", "Not Observed"]
        },
        grading_defaults: {
          areas_of_strength_and_improvement: true,
          credit_reasoning_and_partial_understanding: true,
          formative_evidence_emphasis: true,
          allow_multiple_valid_methods: true,
          ignore_writing_mechanics_unless_requested: true,
          de_emphasize_minor_arithmetic_notation_unless_requested: true,
          missing_is_not_incorrect: true,
          concise_feedback: true,
          extend_convincing_students: true,
          flag_unclear_scans_instead_of_guessing: true
        },
        grade_output: {
          mode: gradeMode,
          required_teacher_selection: true,
          policy: gradePolicy(gradeMode, rubricManifest.length > 0)
        },
        teacher_exceptions_present: Boolean(teacherNotes),
        evidence_files: evidenceManifest,
        roster_files: rosterManifest,
        rubric_files: rubricManifest,
        requested_outputs: {
          student_reports: true,
          combined_student_reports_html: true,
          individual_practice: true,
          combined_individual_practice_html: true,
          class_analysis: true,
          recommended_groupings: true,
          scanned_student_work_pdf: `scanned_work/${scannedWorkFilename}`,
          generated_print_policy: {
            canonical_format: "HTML + browser Print",
            duplicate_generated_pdfs_forbidden: true,
            source_scan_pdf_allowed: true
          },
          common_course_practice: {
            common_review_extension: {
              enabled: true,
              printable_student_worksheet: true,
              visible_student_sections: ["Review", "Extension / Transfer"],
              true_letter_page_preview: true,
              deterministic_repagination: true,
              left_controls: ["All workspaces", "Problem", "Workspace", "Graph / diagram", "Reset", "Print"],
              teacher_guide_html: true,
              teacher_guide_is_single_review_authority: true,
              teacher_guide_includes_answers_and_moves: true,
              find_someone_who_reuses_exact_student_worksheet: true
            },
            stations: {
              review_stations: 4,
              extension_stations: 2,
              questions_per_station_min: 4,
              questions_per_station_max: 6,
              separate_answer_key: true,
              html_only: true,
              generated_pdfs: false,
              locked_style: STATION_STYLE_VERSION
            },
            question_solution_set: {
              set_name: "Set 1",
              count: 1,
              create_set_2: false,
              complete_set_reuse_required: true,
              reuse_class_level_question_pool: true,
              solve_validate_shared_questions_once: true,
              activity_options_index: true,
              activity_options_reference: "algebra/activities/u1_1_act1/u1_1_act1.html",
              teacher_print_utilities_first: true,
              teacher_print_utilities: ["Print Presentation", "Teacher Guide"],
              teacher_guide_target: "../common_review_extension/teacher_guide.html",
              classroom_participation_heading: "Classroom Participation Structures",
              shared_prompt_partner_structures: ["Whiteboard Indy", "Whiteboard Partners", "Rally Coach", "Speed Dating", "Showdown", "Think, Trade, Agree", "Round Table", "Hot Seat", "Rally Coach II"],
              card_based_structures: ["Quiz-Quiz-Trade", "Fan-N-Pick", "Mix-Pair-Share with Cards", "Inside-Outside Circle with Cards"],
              card_based_structures_use_one_shared_deck: true,
              presentation_layout: "one Letter page per problem; question top half; Answer + Teacher move + Student discourse move bottom half",
              presentation_true_letter_page_preview: true,
              presentation_left_controls: ["All question spacing", "Problem", "Question spacing / workspace", "Graph / diagram", "Reset", "Print"],
              print_presentation_two_up: false,
              print_presentation_layout: "one Letter page per problem; question top half; Answer + Teacher move + Student discourse move bottom half",
              print_presentation_true_letter_page_preview: true,
              print_presentation_left_controls: ["All question spacing", "Problem", "Question spacing / workspace", "Graph / diagram", "Reset", "Print"],
              print_presentation_generated_pdf: false,
              review_all_duplicate_forbidden: true,
              duplicate_set_teacher_guide_forbidden: true,
              find_someone_who_target: "../common_review_extension/student_worksheet.html",
              cut_apart_cards_locked: true,
              printable_options: ["Stations", "Find Someone Who", "Cut-Apart Question Cards"],
              prohibited_optional_links: ["Tarsia", "Blooket"],
              separate_structures_index_forbidden: true,
              separate_directions_page_forbidden: true
            }
          },
          review_all_questions: {
            enabled: false,
            reason: "The approved Common Worksheet Teacher Guide is the single teacher-review authority."
          },
          duplex_pairing: {
            combined_student_reports_html: true,
            combined_individual_practice_html: true,
            rule: "Each student's explicit Letter-page segment must occupy an even number of physical browser-print pages. Add one truly blank page only when the rendered segment is odd so the next student starts on a sheet front."
          }
        },
        click_me: {
          quick_actions: [
            "Print All Student Reports",
            "Print All Individual Practice",
            "View Scanned Student Work"
          ],
          sections: [
            "Individual Student Reports & Practice",
            "Class Data",
            "Common Course Practice"
          ],
          common_course_practice_cards: [
            "Common Worksheet / Review + Extension",
            "Stations",
            "Question / Solution Set"
          ]
        }
      };

      const [responseCss, stationCss, commonPracticeGuide, responseQaGuide, responseLayoutLock, graphRenderingStandard, responseBuilder, responseDataSchema, responseRuntimeCss, responseRuntimeJs, evidenceReviewTool, mechanicalQaTool, graphBundle] = await Promise.all([
        loadTextFile("response_styles.css", RESPONSE_CSS_FALLBACK),
        loadTextFile("station_styles.css", ""),
        loadTextFile("COMMON_PRACTICE_GUIDE.md", COMMON_PRACTICE_FALLBACK),
        loadTextFile("RESPONSE_QA_EXECUTION.md", RESPONSE_QA_FALLBACK),
        loadTextFile("RESPONSE_LAYOUT_LOCK.md", RESPONSE_LAYOUT_LOCK_FALLBACK),
        loadTextFile("../_shared/DISTRICT_GRAPH_RENDERING_STANDARD.md", GRAPH_STANDARD_FALLBACK),
        loadTextFile("response_builder.py", ""),
        loadTextFile("RESPONSE_DATA_SCHEMA.md", ""),
        loadTextFile("response_runtime.css", ""),
        loadTextFile("response_runtime.js", ""),
        loadTextFile("evidence_review.py", ""),
        loadTextFile("response_qa.py", ""),
        loadGraphToolBundle()
      ]);
      if (!stationCss || !responseBuilder || !responseDataSchema || !responseRuntimeCss || !responseRuntimeJs || !evidenceReviewTool || !mechanicalQaTool) {
        throw new Error("Deterministic grading renderer/evidence/QA utility files could not be loaded.");
      }
      const responseStyleSha256 = await sha256Hex(responseCss);
      const responseRuntimeCssSha256 = await sha256Hex(responseRuntimeCss);
      const responseRuntimeJsSha256 = await sha256Hex(responseRuntimeJs);
      const responseBuilderSha256 = await sha256Hex(responseBuilder);
      if (responseStyleSha256 !== RESPONSE_STYLE_SHA256) {
        throw new Error(`Locked response_styles.css hash mismatch. Expected ${RESPONSE_STYLE_SHA256}, got ${responseStyleSha256}.`);
      }
      request.response_layout_lock = {
        version: RESPONSE_LAYOUT_LOCK_VERSION,
        response_style_version: RESPONSE_STYLE_VERSION,
        response_style_sha256: responseStyleSha256,
        gold_baseline_date: "2026-09-20",
        stable_surfaces_must_not_restyle: true,
        html_first_printing: true,
        true_letter_page_preview_required_for_adjustable_html: true
      };
      request.deterministic_response_renderer = {
        response_data_version: RESPONSE_DATA_VERSION,
        builder_version: RESPONSE_BUILDER_VERSION,
        builder: "response_contract/response_builder.py",
        data_schema: "response_contract/RESPONSE_DATA_SCHEMA.md",
        runtime_css: "response_contract/runtime.css",
        runtime_css_sha256: responseRuntimeCssSha256,
        runtime_js: "response_contract/runtime.js",
        runtime_js_sha256: responseRuntimeJsSha256,
        builder_sha256: responseBuilderSha256,
        evidence_review_version: EVIDENCE_REVIEW_VERSION,
        evidence_review_utility: "response_contract/evidence_review.py",
        mechanical_qa_version: MECHANICAL_QA_VERSION,
        mechanical_qa_utility: "response_contract/response_qa.py",
        external_dependency_recovery_forbidden: true,
        ad_hoc_mechanical_scripting_forbidden: true,
        html_authoring_by_model_forbidden: true
      };
      request.graph_rendering = {
        standard_version: GRAPH_RENDERING_STANDARD_VERSION,
        source_manifest: "response_contract/graph_tool/MANIFEST.json",
        entrypoint: graphBundle.entrypoint,
        packaged_entrypoint: `response_contract/graph_tool/${graphBundle.entrypoint.split("/").pop()}`,
        packaged_files: Object.keys(graphBundle.files).map((path) => `response_contract/graph_tool/${path.split("/").pop()}`),
        provenance_required_in_qa: true
      };
      const requestInstructions = buildInstructions(request, teacherNotes);
      const graphEntries = Object.entries(graphBundle.files).map(([path, content]) => ({
        name: `response_contract/graph_tool/${path.split("/").pop()}`,
        data: enc.encode(content)
      }));

      entries.unshift(
        { name: "REQUEST_READ_ME_FIRST.md", data: enc.encode(requestInstructions) },
        { name: "request.json", data: enc.encode(JSON.stringify(request, null, 2)) },
        { name: "teacher_exceptions_context.txt", data: enc.encode(teacherNotes || "No teacher exceptions or additional context were provided.") },
        { name: "response_contract/styles.css", data: enc.encode(responseCss) },
        { name: "response_contract/STYLE_VERSION.txt", data: enc.encode(RESPONSE_STYLE_VERSION + "\n") },
        { name: "response_contract/STYLE_SHA256.txt", data: enc.encode(responseStyleSha256 + "\n") },
        { name: "response_contract/RESPONSE_LAYOUT_LOCK.md", data: enc.encode(responseLayoutLock) },
        { name: "response_contract/RESPONSE_LAYOUT_LOCK_VERSION.txt", data: enc.encode(RESPONSE_LAYOUT_LOCK_VERSION + "\n") },
        { name: "response_contract/stations.css", data: enc.encode(stationCss) },
        { name: "response_contract/STATION_STYLE_VERSION.txt", data: enc.encode(STATION_STYLE_VERSION + "\n") },
        { name: "response_contract/MATH_VISUAL_QA.md", data: enc.encode(MATH_VISUAL_QA_CONTRACT) },
        { name: "response_contract/MATH_VISUAL_QA_VERSION.txt", data: enc.encode(MATH_VISUAL_QA_VERSION + "\n") },
        { name: "response_contract/COMMON_PRACTICE_GUIDE.md", data: enc.encode(commonPracticeGuide) },
        { name: "response_contract/COMMON_PRACTICE_VERSION.txt", data: enc.encode(COMMON_PRACTICE_VERSION + "\n") },
        { name: "response_contract/RESPONSE_QA_EXECUTION.md", data: enc.encode(responseQaGuide) },
        { name: "response_contract/RESPONSE_QA_VERSION.txt", data: enc.encode(RESPONSE_QA_VERSION + "\n") },
        { name: "response_contract/DISTRICT_GRAPH_RENDERING_STANDARD.md", data: enc.encode(graphRenderingStandard) },
        { name: "response_contract/GRAPH_RENDERING_STANDARD_VERSION.txt", data: enc.encode(GRAPH_RENDERING_STANDARD_VERSION + "\n") },
        { name: "response_contract/response_builder.py", data: enc.encode(responseBuilder) },
        { name: "response_contract/RESPONSE_BUILDER_VERSION.txt", data: enc.encode(RESPONSE_BUILDER_VERSION + "\n") },
        { name: "response_contract/RESPONSE_DATA_SCHEMA.md", data: enc.encode(responseDataSchema) },
        { name: "response_contract/RESPONSE_DATA_VERSION.txt", data: enc.encode(RESPONSE_DATA_VERSION + "\n") },
        { name: "response_contract/runtime.css", data: enc.encode(responseRuntimeCss) },
        { name: "response_contract/runtime.js", data: enc.encode(responseRuntimeJs) },
        { name: "response_contract/evidence_review.py", data: enc.encode(evidenceReviewTool) },
        { name: "response_contract/EVIDENCE_REVIEW_VERSION.txt", data: enc.encode(EVIDENCE_REVIEW_VERSION + "\n") },
        { name: "response_contract/response_qa.py", data: enc.encode(mechanicalQaTool) },
        { name: "response_contract/MECHANICAL_QA_VERSION.txt", data: enc.encode(MECHANICAL_QA_VERSION + "\n") },
        { name: "response_contract/graph_tool/MANIFEST.json", data: enc.encode(graphBundle.manifestText) },
        ...graphEntries
      );

      // Fail closed if any deterministic renderer/runtime file is absent from the request package.
      // This prevents a grading run from having to fetch repository files or recreate locked layouts.
      const requiredDeterministicEntries = [
        "response_contract/response_builder.py",
        "response_contract/RESPONSE_BUILDER_VERSION.txt",
        "response_contract/RESPONSE_DATA_SCHEMA.md",
        "response_contract/RESPONSE_DATA_VERSION.txt",
        "response_contract/runtime.css",
        "response_contract/runtime.js",
        "response_contract/evidence_review.py",
        "response_contract/response_qa.py",
        "response_contract/styles.css",
        "response_contract/stations.css"
      ];
      const packagedEntryNames = new Set(entries.map((entry) => entry.name));
      const missingDeterministicEntries = requiredDeterministicEntries.filter((name) => !packagedEntryNames.has(name));
      if (missingDeterministicEntries.length) {
        throw new Error(`Request package is missing deterministic renderer files: ${missingDeterministicEntries.join(", ")}`);
      }

      const zipBlob = makeZip(entries);
      const filename = `grading_request_${slug(className)}_${dateStamp()}.zip`;
      downloadBlob(zipBlob, filename);
      setStatus(`Request ready: ${filename}`, "good");
    } catch (error) {
      console.error(error);
      setStatus(`Could not build the ZIP: ${error.message || error}`, "bad");
    } finally {
      buildButton.disabled = false;
    }
  }

  function buildInstructions(request, teacherNotes) {
    const rosterLine = request.roster_files.length
      ? "A roster is included under roster/. Use it only to resolve student identity, identify missing/unmatched evidence, and preserve roster order."
      : "No roster is included. Make one reasonable identity pass; if a handwritten name remains unreadable, use a stable Student 01-style label, flag the uncertainty, and continue.";
    const rubricLine = request.rubric_files.length
      ? "A rubric/scoring guide is included under rubric/. Use it where it clearly applies."
      : "No rubric/scoring guide is included.";
    return `# District Grading & Evidence Request - Deterministic Build\n\n` +
`## Task\nGrade the submitted evidence and return exactly ONE completed response ZIP. The grading/content decisions are your work; response layout is NOT. The packaged deterministic renderer owns every stable HTML surface.\n\n` +
`Class / group: ${request.teacher.class_or_group}\nGrade / subject: ${request.teacher.grade_subject || "not provided"}\n${rosterLine}\n${rubricLine}\nTeacher exceptions: ${teacherNotes || "none"}\n\n` +
`## Required execution order - HARD\n1. For PDF/image evidence, run the packaged evidence helper once before analysis: python response_contract/evidence_review.py --input <evidence-file> --out _evidence_review. If packet size is obvious, add --packet-pages N. Use its rendered pages/contact sheets; do not write a new render/contact-sheet script.\n2. Review and grade the student evidence once.\n3. Create concise canonical data for student reports/practice, class findings, one Set 1 question pool, and six stations.\n4. Independently solve/check every Set 1 question once. In response_data.json every Set 1 item must include verification.passed=true plus a short method.\n5. Write response_data.json using response_contract/RESPONSE_DATA_SCHEMA.md.\n6. Generate required graph/diagram assets once, using the packaged graph tool where applicable, and reference those same assets from response_data.json.\n7. Run: python response_contract/response_builder.py --data response_data.json --request-root . --out RESPONSE\n8. Run the packaged mechanical QA once: python response_contract/response_qa.py --response RESPONSE --request-root .\n9. Do NOT rewrite or restyle builder-generated HTML. Do NOT add page-local CSS. Do NOT fetch renderer/runtime/QA utilities from GitHub or the web; if a required packaged utility is missing, fail as a packaging error.\n10. Add data/analysis.json and data/qa.json to RESPONSE. Preserve RESPONSE/data/template_qa.json and RESPONSE/data/mechanical_qa.json.\n11. Do only bounded visual QA: generated graphs/diagrams plus actual content-overflow outliers. Do not visually re-audit stable shells.\n12. Zip RESPONSE and return that one ZIP.\n\n` +
`## Why this is locked\nThe teacher has already approved the dashboard, Class Data, reports, Common Worksheet, Teacher Guide, Stations, cut cards, Activity Options/directions, Set 1 presentation, sliders, page previews, and print behavior. They are literal templates now. A grading run must never redesign them.\n\n` +
`## Canonical content reuse\nAuthor a small Set 1 once. The deterministic renderer reuses the exact same prompt/answer/teacher move/discourse move across Common Worksheet, Teacher Guide, classroom presentation, Print Presentation, Find Someone Who (same worksheet), and Cut-Apart Cards. Do not author separate versions for each structure.\n\n` +
`## Practice pagination\nThe renderer owns true Letter-size white page previews. Questions flow naturally within pages; workspace sliders resize workspace and repaginate. A problem is NOT a page. The Print button prints the same preview pages. Combined student practice/reports remain duplex-safe.\n\n` +
`## Activities\nThe renderer owns the complete structure-specific directions. Do not regenerate generic directions. Card structures use the single Cut-Apart Question Cards deck. Find Someone Who links to the Common Worksheet.\n\n` +
`## Grade / score handling\n${request.grade_output.policy}\nEvery student report still uses exactly one evidence rating: Convincing, Limited, Incorrect, or Not Observed. Missing/unreadable evidence is Not Observed, not Incorrect.\n\n` +
`## Speed / QA\nEverything mechanical is packaged. Use evidence_review.py instead of writing PDF/contact-sheet code, response_builder.py instead of authoring HTML, and response_qa.py instead of writing link/hash/file QA scripts. For slider/page-preview QA, test one representative default, one mid-change, and one max-change only; browser subpixel overflow of 4 px or less is tolerance, not a correction loop. Once response_data.json exists, renderer + mechanical QA + bounded visual QA should normally finish in under 90 seconds. Record real elapsed timings in data/qa.json.\n\n` +
`Return only the completed response ZIP with a short note to unzip it and open CLICK_ME.html.\n`;
  }

  function gradePolicy(mode, rubricPresent) {
    if (mode === "rubric") return "Return the evidence rating and the score/grade defined by the supplied rubric or scoring guide. Do not invent a different scale.";
    if (mode === "recommend") {
      return rubricPresent
        ? "Return the evidence rating and a teacher-review grade/score recommendation. Use the supplied rubric/scale when it applies; otherwise explain the evidence basis briefly."
        : "Return the evidence rating and a clear teacher-review grade/score recommendation from the submitted evidence. For objective item-based work, points/percent correct may be used. For open-ended work, use evidence-based professional judgment and label the result as a recommendation, not a final grade.";
    }
    return "Return the evidence rating only. Do not add a separate numeric, percentage, point, or letter grade.";
  }

  async function loadGraphToolBundle() {
    const manifestText = await loadCanonicalRepoText("Tools/MANIFEST.json");
    if (!manifestText) throw new Error("Could not load the canonical Tools/MANIFEST.json graph registry.");
    let manifest;
    try { manifest = JSON.parse(manifestText); } catch (error) { throw new Error("Canonical Tools/MANIFEST.json is not valid JSON."); }
    const entrypoint = manifest?.tools?.graph_tool;
    if (!entrypoint) throw new Error("Tools/MANIFEST.json does not declare tools.graph_tool.");

    // The canonical graph runtime is intentionally self-contained. Request ZIPs
    // package exactly one current graph tool rather than a version dependency chain.
    const content = await loadCanonicalRepoText(entrypoint);
    if (!content) throw new Error(`Could not load canonical graph tool: ${entrypoint}`);
    return { manifestText, entrypoint, files: { [entrypoint]: content } };
  }

  async function loadCanonicalRepoText(repoPath) {
    const cleanPath = String(repoPath || "").replace(/^\/+/, "");
    if (!cleanPath) return "";

    // Try the GitHub Pages copy first; the canonical graph runtime uses an ordinary Pages-safe filename.
    const pagesRelative = `../../${cleanPath}`;
    const pagesText = await loadTextFile(pagesRelative, "");
    if (pagesText) return pagesText;

    // Fall back to GitHub raw content so canonical files excluded by Pages are
    // still resolved from the repository named by Tools/MANIFEST.json.
    const encodedPath = cleanPath.split("/").map(encodeURIComponent).join("/");
    const rawUrl = `https://raw.githubusercontent.com/tnezki/memories/main/${encodedPath}`;
    try {
      const response = await fetch(rawUrl, { cache: "no-store" });
      if (response.ok) return await response.text();
    } catch (error) {
      console.warn(`Raw GitHub fetch failed for ${cleanPath}.`, error);
    }

    // Final browser-safe fallback: GitHub Contents API. Keep this read-only.
    const apiUrl = `https://api.github.com/repos/tnezki/memories/contents/${encodedPath}?ref=main`;
    try {
      const response = await fetch(apiUrl, {
        cache: "no-store",
        headers: { Accept: "application/vnd.github+json" }
      });
      if (response.ok) {
        const payload = await response.json();
        if (payload && payload.encoding === "base64" && payload.content) {
          const binary = atob(String(payload.content).replace(/\s/g, ""));
          const bytes = Uint8Array.from(binary, (ch) => ch.charCodeAt(0));
          return new TextDecoder().decode(bytes);
        }
      }
    } catch (error) {
      console.warn(`GitHub Contents API fetch failed for ${cleanPath}.`, error);
    }
    return "";
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


  async function sha256Hex(value) {
    const digest = await crypto.subtle.digest("SHA-256", enc.encode(String(value)));
    return [...new Uint8Array(digest)].map((b) => b.toString(16).padStart(2, "0")).join("");
  }

  function fileManifest(file, packagedPath) {
    return { original_name: file.name, packaged_path: packagedPath, mime_type: file.type || null, size_bytes: file.size };
  }

  function friendlyFilePart(value) {
    const cleaned = String(value || "Work").normalize("NFKD").replace(/[^A-Za-z0-9]+/g, "_").replace(/^_+|_+$/g, "").slice(0, 54);
    return cleaned || "Work";
  }

  function slug(value) {
    return String(value || "request").toLowerCase().normalize("NFKD").replace(/[^a-z0-9]+/g, "_").replace(/^_+|_+$/g, "").slice(0, 48) || "request";
  }

  function safeFileName(name) {
    const cleaned = String(name || "file").replace(/[\\/:*?"<>|\u0000-\u001f]/g, "_").replace(/^\.+/, "").trim();
    return cleaned || "file";
  }

  function uniqueName(name, usedPaths, folderKey) {
    let candidate = name;
    let n = 2;
    const keyFor = (value) => `${folderKey}/${value}`.toLowerCase();
    while (usedPaths.has(keyFor(candidate))) {
      const dot = name.lastIndexOf(".");
      candidate = dot > 0 ? `${name.slice(0, dot)}_${n}${name.slice(dot)}` : `${name}_${n}`;
      n += 1;
    }
    usedPaths.add(keyFor(candidate));
    return candidate;
  }

  function dateStamp() {
    const d = new Date();
    return `${d.getFullYear()}${String(d.getMonth() + 1).padStart(2, "0")}${String(d.getDate()).padStart(2, "0")}`;
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
