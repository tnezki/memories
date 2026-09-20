(() => {
  const $ = (id) => document.getElementById(id);
  const enc = new TextEncoder();

  const RESPONSE_STYLE_VERSION = "district-grading-response-style/1.6";
  const STATION_STYLE_VERSION = "district-grading-station-style/1.0";
  const MATH_VISUAL_QA_VERSION = "district-grading-math-visual-qa/1.5";
  const COMMON_PRACTICE_VERSION = "district-grading-common-practice/1.3";
  const RESPONSE_QA_VERSION = "district-grading-response-qa-execution/1.1";
  const GRAPH_RENDERING_STANDARD_VERSION = "district-graph-rendering-standard/1.2";
  const RESPONSE_LAYOUT_LOCK_VERSION = "district-grading-response-layout-lock/1.0";
  const RESPONSE_STYLE_SHA256 = "59d49d36e4d660a0c6a3bb80254eac0867cfb50d86561cbc664c495f0eefa8df";
  const REQUEST_SCHEMA = "district-grading-request/1.1-pilot";

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

/* Print Presentation: true page preview, two questions per letter page */
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
`;

  const STATION_CSS_FALLBACK = String.raw`@page{size:letter landscape;margin:0}:root{--navy:#00003d;--page-w:11in;--page-h:8.5in}*{box-sizing:border-box}body{font-family:Arial,Helvetica,sans-serif;color:#111;background:#e8e8e8}.page{width:var(--page-w);height:var(--page-h);margin:0 auto .25in;background:#fff;padding:.32in .42in .24in;display:flex;flex-direction:column;overflow:hidden;page-break-after:always}.header{background:var(--navy);color:#fff;font-size:21pt;font-weight:800;padding:.11in .20in;margin-bottom:.12in}.station-grid{display:grid;grid-template-columns:1fr 1fr;gap:.10in .13in}.station-problem{border:1.2px solid #222;border-radius:5px;padding:.08in;font-size:10.2pt;break-inside:avoid}.figure img,.figure svg{display:block;max-width:100%;max-height:1.9in;height:auto;margin:0 auto}.page-footer{margin-top:auto;font-size:7.5pt}.station-index{width:11in;min-height:8.5in;margin:0 auto;background:#fff;padding:.45in}@media print{body{background:#fff}.page{margin:0}.station-index{display:none}}`;

  const COMMON_PRACTICE_FALLBACK = String.raw`# Common Course Practice & Question Review Guide

STATUS: REQUIRED FOR GRADING & EVIDENCE RESPONSE BUILDS  
VERSION: district-grading-common-practice/1.3  
DATE: 2026-09-20

This guide controls Common Course Practice and Set 1 delivery. If older request wording conflicts with this file, this file controls. \`RESPONSE_LAYOUT_LOCK.md\` controls visual continuity.

## 1. One approved class-level question pool
Build one coherent class-level pool from the strongest common instructional needs plus justified extension targets. Reuse approved questions across Common Worksheet / Review + Extension, Stations when appropriate, Set 1, projection pages, review pages, and participation structures.

Do not manufacture unrelated extra questions just because multiple delivery formats exist. When a question is reused, the mathematics, answer, graph/diagram, and difficulty remain identical.

## 2. Common Worksheet / Review + Extension
Keep the current gold worksheet/teacher-guide layout. The student worksheet visibly separates:

- **Review** — observed common needs, unfinished understanding, or prerequisites.
- **Extension / Transfer** — application/transfer for students already showing Convincing evidence or a justified class-wide extension target.

Use clear labels on the worksheet. Keep the header compact. Teacher-facing HTML is named **Teacher Guide**, not merely HTML. Do not add redundant print buttons when browser print already gives the intended product.

## 3. Set 1 is the one mathematical set
Create exactly one class-level **Set 1**. Do not create Set 2.

Set 1 is reused by:

- Set 1 Questions & Solutions projection deck;
- Print Presentation;
- Review All Questions;
- Teacher Guide;
- Find Someone Who;
- Cut-Apart Question Cards;
- projection/whiteboard participation structures.

There is no fixed Set 1 size. Every Set 1 artifact uses the entire set unless it is intentionally paginating/cards the same complete set.

## 4. \`print/question_set/index.html\` = Activity Options page
The old six-card Set 1 menu is retired. \`index.html\` itself must closely mirror the structure and hierarchy of:

\`algebra/activities/u1_1_act1/u1_1_act1.html\`

Adaptations for this grading tool:

- one Set 1 only;
- no Set 2;
- no Tarsia;
- no Blooket;
- do not invent unrelated activity types;
- add **Cut-Apart Question Cards** under Printable Handouts;
- use the current gold response colors/typography from locked \`styles.css\` rather than introducing a new theme.

The Activity Options page contains the projectable direction sections in the same HTML page using internal anchors, just like the Algebra activity page. Do not create a second \`structures/index.html\` card menu or a separate \`directions.html\` maze.

### Projection / Whiteboard Options
List these routines as simple linked rows/list items. Each routine name links to its directions anchor and its **Set 1** link points to the same \`presentation.html\` Questions & Solutions deck:

- Whiteboard Indy
- Whiteboard Partners
- Rally Coach
- Speed Dating Math
- Showdown
- Think, Trade, Agree
- Round Table
- Mathematical Hot Seat
- Rally Coach II

No standalone **Presentation / Open Presentation** card belongs on the Activity Options page.

### Printable Handouts
List:

- **Stations** — link to the already-generated Stations product;
- **Find Someone Who** — link to \`structures/find_someone_who.html\`;
- **Cut-Apart Question Cards** — link to \`structures/cut_apart_cards.html\`.

The card deck remains visually unchanged from the current gold run.

### Teacher / Print Utilities
Keep direct utility links available without turning them into the old card menu:

- **Print Presentation** — two-up student-question printout;
- **Review All Questions** — compact teacher QA;
- **Teacher Guide** — answers/moves.

## 5. Set 1 Questions & Solutions projection deck
\`presentation.html\` is no longer the compact Back/Next shell from the previous run.

Build it like the Algebra \`u1_1_set1_questions_solutions.html\` pattern:

- one large **Question** page for Set 1 Problem 1;
- immediately followed by one large **Solution** page for Problem 1;
- repeat Question then Solution for every Set 1 problem;
- large projectable math/figures;
- question page has useful white space for board discussion;
- solution page repeats the prompt and gives the concise solution plus teacher/discourse move only when useful;
- use the locked \`.activity-page\`, \`.prob-head\`, \`.prob-q\`, \`.projection-work\`, and \`.solution\` classes;
- no Back/Next shell, no question counter bar, no giant empty browser page created only to imitate printing.

Every projection/whiteboard structure reuses this same deck.

## 6. Print Presentation - keep the current gold two-up format
Create \`print_presentation.html\` + PDF from the exact Set 1 questions.

- Letter portrait;
- exactly two large question panels per physical page;
- top-align each question within its half-page panel;
- no answers/moves/workspace;
- all Set 1 questions;
- final lower half may be blank when the set count is odd.

Do not redesign the current approved two-up panel styling.

## 7. Review All Questions - keep current gold layout
\`review_all.html\` remains the compact zero-workspace teacher QA view of all Set 1 questions with required visuals and collapsible Answer / Teacher Move / Student Discourse Move.

## 8. Find Someone Who = Student Set worksheet look + signatures
The separate generic Student Set is no longer a teacher-facing Activity Options choice. Use the **current gold Student Set visual layout** as the base for Find Someone Who.

\`structures/find_someone_who.html\` requirements:

- compact Set 1 worksheet header;
- current two-column \`.student-set-grid\` / \`.student-question\` look;
- all Set 1 questions in natural flow;
- each problem adds a compact **Partner signature** line;
- each problem keeps useful workspace;
- required graph/diagram remains readable;
- no cut-card boxes;
- no giant activity title block;
- browser print is the canonical handout.

### Screen-only left controls - match Worksheet Builder
Add the Worksheet Builder-style left rail on wide screens. Use this order:

1. **All workspaces in this sheet** — 0-300%, default 100%;
2. **Problem** selector;
3. **Workspace** — 0-1200% for the selected problem;
4. **Graph / diagram** — 70-160% for the selected problem when a visual exists;
5. **Reset**;
6. **Print**.

There is no Version control and no New Question button because this is one fixed Set 1.

Controls are screen-only and disappear in print. Workspace and graph size are independent. Resizing changes geometry only; graph stroke weights never change. Preserve current problem order and mathematics.

If a generic \`student_set.html\` is retained internally for compatibility, do not expose it as a primary Activity Options link and do not give it a second competing visual design.

## 9. Teacher Guide - keep current gold layout
Keep the current compact Teacher Guide styling/order. It follows Set 1 and provides concise answer/solution plus brief teacher/discourse moves where useful.

## 10. Activity direction sections - mirror Algebra u1_1
The Activity Options HTML includes one direction section per routine using the Algebra hierarchy:

- compact eyebrow/title/subtitle;
- **Structure**;
- **Setup**;
- concise ordered **Directions**;
- **Goal**;
- one **Set 1** link;
- right-side **Looks Like Success / Doesn't Look Like** boxes.

Use these established routine meanings:

### Whiteboard Indy
Structure: Individual independent practice. Setup: each student has a whiteboard/marker. Directions: notes welcome; try something first; write large/clearly; use partners for reasoning not copying; revise mistakes. Goal: individual accountability + low-stakes entry.

### Whiteboard Partners
Structure: fast partner practice. Setup: one board/marker per pair. Directions: both engaged; alternate writer; explain before erasing; resolve disagreements with evidence. Goal: engagement + quick feedback.

### Rally Coach
Structure: partner explanation + alternating roles. Setup: shared workspace. Directions: A explains/B records; coach with questions not answers; switch each problem; both verify. Goal: verbal reasoning + procedural accuracy.

### Speed Dating Math
Structure: independent attempt -> timed partner comparison -> rotation. Goal: repeated explanation + strategy comparison.

### Showdown
Structure: individual think -> simultaneous reveal -> team check. Goal: individual accountability + team feedback.

### Think, Trade, Agree
Structure: individual think -> trade explanations -> clarifying question -> justified agreement/disagreement. Goal: evidence-based comparison.

### Round Table
Structure: team rotation of written reasoning. Goal: visible collaborative reasoning.

### Mathematical Hot Seat
Structure: describe -> reason -> reveal. Goal: mathematical language + listening.

### Rally Coach II
Structure: solve -> coach -> restate -> switch. Goal: metacognition + partner coaching.

Use the same concise success/non-example language pattern as the Algebra activity page. Do not invent new rule systems.

## 11. Cut-Apart Question Cards - LOCKED
The current card artifact is approved. Keep it visually and structurally unchanged except for the actual Set 1 content/required visual.

- one task per card;
- dashed cut lines;
- complete Set 1 across enough cards/pages;
- no answer on question side;
- supports Quiz-Quiz-Trade and Fan-N-Pick.

Do not use the cards for Find Someone Who.

## 12. Global Review All Questions - teacher QA
Keep the current gold \`class/review_all_questions.html\` layout. Show all generated follow-up questions from Common Worksheet, Stations, Set 1, and Individual Practice with zero workspace and collapsible teacher information.

## 13. Stations remain unchanged
Exactly four review stations plus two extension stations, 4-6 questions each, separate answer key, locked station CSS. Do not redesign.

## 14. Math, graphs, and visuals
All products inherit the packaged Math / Graph / Visual QA contract and District Graph Rendering Standard.

- supported Cartesian graphs, including blank grids, use the packaged canonical graph tool;
- use the same graph asset wherever a question is reused;
- prefer SVG for adjustable student handouts;
- graph size controls scale the asset geometry, not its stroke weights;
- record graph tool entrypoint + asset in \`data/qa.json\`;
- student construction visuals remain answer-neutral.

## 15. Gold layout lock
Follow \`response_contract/RESPONSE_LAYOUT_LOCK.md\` as a HARD contract. Copy \`styles.css\` byte-for-byte. Apart from the explicitly approved Set 1 changes in that lock, do not restyle the response package.

## 16. QA requirements
Before delivery verify:

- one Set 1 only / no Set 2;
- every Set 1 delivery uses the full set;
- Common Worksheet visibly labels Review and Extension / Transfer;
- \`question_set/index.html\` is the Algebra-style Activity Options page, not the old six-card menu;
- no standalone Presentation card;
- every projection routine's Set 1 link points to the same Questions & Solutions deck;
- projection deck alternates Question then Solution for every problem;
- Print Presentation remains exactly two top-aligned questions per physical page;
- Find Someone Who uses the current Student Set look, partner signatures, useful workspace, and the left control rail;
- controls work at all-workspace 0/100/300%, per-problem workspace 0/100/500/1200%, graph 70/100/160%;
- Cut-Apart Cards match the gold layout;
- no Tarsia or Blooket;
- no separate structures card menu/directions maze;
- graph style/provenance pass the canonical standard;
- locked CSS hash matches;
- links resolve and \`data/qa.json\` has no unresolved failure.
`;

  const RESPONSE_LAYOUT_LOCK_FALLBACK = String.raw`# Grading Response Gold Layout Lock

STATUS: HARD / REQUIRED  
VERSION: district-grading-response-layout-lock/1.0  
DATE: 2026-09-20  
LOCKED CSS SHA-256: \`59d49d36e4d660a0c6a3bb80254eac0867cfb50d86561cbc664c495f0eefa8df\`

## Purpose
The 2026-09-20 Precalculus Circuit Training grading response is the visual baseline for this tool. Future grading runs must preserve that response system instead of inventing a new layout on each run.

\`response_contract/styles.css\` is the canonical response stylesheet. The response must copy it byte-for-byte to \`assets/styles.css\`; \`data/qa.json\` must record the SHA-256 above and PASS only when it matches.

## Stable surfaces - DO NOT REDESIGN
Keep the current gold layout/markup hierarchy for all of these unless a later teacher-approved contract explicitly changes one:

- \`CLICK_ME.html\`
- individual student reports
- class overview
- individual practice packets
- combined report/practice print documents
- Common Worksheet / Review + Extension
- Common Worksheet Teacher Guide
- Stations and station answer key
- Review All Questions pages
- Set 1 Teacher Guide
- Print Presentation two-up pages
- Cut-Apart Question Cards

Do not change hero sizes, card shapes, button treatment, typography hierarchy, spacing system, report boxes, dashboard organization, station styling, or card-deck styling simply because another layout seems cleaner.

## Approved Set 1 exceptions in this revision
Only these Set 1 surfaces intentionally differ from the previous run:

1. \`print/question_set/index.html\` becomes the Algebra-style **Activity Options** page modeled on \`algebra/activities/u1_1_act1/u1_1_act1.html\`, adapted to one Set 1.
2. \`presentation.html\` becomes the Algebra-style **Set 1 Questions & Solutions** projection deck (question page followed by solution page), not the prior Back/Next presentation shell.
3. **Find Someone Who** adopts the current Student Set worksheet look: compact two-column problem flow, with a partner signature line and workspace added to each problem.
4. Find Someone Who gets the Worksheet Builder-style screen-only left control rail for workspace and graph/diagram size.
5. Cartesian construction graphs use the current canonical district graph tool and the worksheet/Quick-Check coordinate visual rules in the District Graph Rendering Standard.

Everything else remains visually frozen.

## HTML/CSS discipline
- Do not add page-local \`<style>\` blocks that restyle shared gold classes.
- Do not invent alternate dashboard/card/page systems.
- Use the class structures named by \`COMMON_PRACTICE_GUIDE.md\` and this lock.
- Content may change from one evidence set to another; the shell/layout does not.
- If content is longer, solve it with natural pagination/content fitting, not a new design language.
- Graph/workspace controls may set CSS custom properties or inline values needed for sizing; they may not restyle the page.

## QA
Before delivery, verify:

- \`assets/styles.css\` exactly matches packaged \`response_contract/styles.css\` and SHA-256 \`59d49d36e4d660a0c6a3bb80254eac0867cfb50d86561cbc664c495f0eefa8df\`;
- every stable surface above still uses the gold class hierarchy;
- only the five approved exceptions changed layout;
- Cut-Apart Cards remain visually unchanged from the gold run;
- no unapproved page-local CSS overrides the gold stylesheet.
`;

  const MATH_VISUAL_QA_CONTRACT = String.raw`# Math, Graph, Visual, and Station QA Contract

STATUS: REQUIRED
VERSION: district-grading-math-visual-qa/1.5

## Math rendering - HARD
- Use valid TeX and MathJax whenever mathematical notation is appropriate.
- Preferred delimiters are \\( ... \\) inline and \\[ ... \\] display.
- Generate PDFs only after MathJax has finished typesetting.
- Raw TeX, missing symbols, or clipped math is a failure.
- Prefer fraction-bar notation for symbolic division when that is the natural mathematical form.

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
- Applies to combined student reports and combined individual-practice documents.
- Every student's segment must occupy an EVEN number of physical pages.
- If a student's final content page count is odd, append exactly one intentionally blank page before the next student.
- Verify actual PDF page order after creation and record before/after counts in data/qa.json.

## Required QA record
Create data/qa.json including evidence-rating checks, MathJax checks, graph/visual checks, duplex before/after page counts, links, PDF validation, question-review coverage, and failures. PASS is forbidden with unresolved failures.`;

  const RESPONSE_QA_FALLBACK = String.raw`# Grading Response QA Execution Guide

VERSION: district-grading-response-qa-execution/1.0

Run programmatic checks first, then targeted visual QA. Preserve full evidence review. Visually render every graph/diagram page and representative pages for each stable template. After a local correction, rerender only the changed artifact and direct dependents, not the entire already-stable package. Record QA coverage in data/qa.json.`;

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
          combined_student_reports_pdf: true,
          individual_practice: true,
          combined_individual_practice_pdf: true,
          class_analysis: true,
          recommended_groupings: true,
          scanned_student_work_pdf: `scanned_work/${scannedWorkFilename}`,
          common_course_practice: {
            common_review_extension: {
              enabled: true,
              printable_student_worksheet: true,
              teacher_guide_html: true,
              teacher_guide_includes_answers_and_moves: true,
              visible_student_sections: ["Review", "Extension / Transfer"]
            },
            stations: {
              review_stations: 4,
              extension_stations: 2,
              questions_per_station_min: 4,
              questions_per_station_max: 6,
              separate_answer_key: true,
              locked_style: STATION_STYLE_VERSION
            },
            question_solution_set: {
              set_name: "Set 1",
              count: 1,
              create_set_2: false,
              complete_set_reuse_required: true,
              reuse_class_level_question_pool: true,
              activity_options_index: true,
              activity_options_reference: "algebra/activities/u1_1_act1/u1_1_act1.html",
              activity_options_one_set_only: true,
              projection_questions_solutions: true,
              standalone_presentation_card: false,
              print_presentation_two_up: true,
              compact_review_all: true,
              generic_student_set_primary_link: false,
              find_someone_who_uses_student_set_layout: true,
              find_someone_who_left_controls: true,
              teacher_guide: true,
              redundant_print_buttons_forbidden: true,
              projection_structures: [
                "Whiteboard Indy",
                "Whiteboard Partners",
                "Rally Coach",
                "Speed Dating Math",
                "Showdown",
                "Think, Trade, Agree",
                "Round Table",
                "Mathematical Hot Seat",
                "Rally Coach II"
              ],
              printable_options: ["Stations", "Find Someone Who", "Cut-Apart Question Cards"],
              teacher_print_utilities: ["Print Presentation", "Review All Questions", "Teacher Guide"],
              card_artifact_supports: ["Quiz-Quiz-Trade", "Fan-N-Pick"],
              prohibited_optional_links: ["Tarsia", "Blooket"],
              separate_structures_index_forbidden: true,
              separate_directions_page_forbidden: true
            }
          },
          review_all_questions: {
            enabled: true,
            include_common_review: true,
            include_stations: true,
            include_question_solution_set: true,
            include_individual_practice: true,
            zero_workspace: true,
            show_answer: true,
            teacher_move: true,
            student_discourse_move: true
          },
          duplex_pairing: {
            combined_student_reports: true,
            combined_individual_practice: true,
            rule: "Each student's segment must occupy an even number of physical pages. After final rendering, add one intentionally blank page only when that student's page count is odd so the next student starts on a sheet front."
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

      const [responseCss, stationCss, commonPracticeGuide, responseQaGuide, responseLayoutLock, graphRenderingStandard, graphBundle] = await Promise.all([
        loadTextFile("response_styles.css", RESPONSE_CSS_FALLBACK),
        loadTextFile("station_styles.css", STATION_CSS_FALLBACK),
        loadTextFile("COMMON_PRACTICE_GUIDE.md", COMMON_PRACTICE_FALLBACK),
        loadTextFile("RESPONSE_QA_EXECUTION.md", RESPONSE_QA_FALLBACK),
        loadTextFile("RESPONSE_LAYOUT_LOCK.md", RESPONSE_LAYOUT_LOCK_FALLBACK),
        loadTextFile("../_shared/DISTRICT_GRAPH_RENDERING_STANDARD.md", GRAPH_STANDARD_FALLBACK),
        loadGraphToolBundle()
      ]);
      const responseStyleSha256 = await sha256Hex(responseCss);
      if (responseStyleSha256 !== RESPONSE_STYLE_SHA256) {
        throw new Error(`Locked response_styles.css hash mismatch. Expected ${RESPONSE_STYLE_SHA256}, got ${responseStyleSha256}.`);
      }
      request.response_layout_lock = {
        version: RESPONSE_LAYOUT_LOCK_VERSION,
        response_style_version: RESPONSE_STYLE_VERSION,
        response_style_sha256: responseStyleSha256,
        gold_baseline_date: "2026-09-20",
        stable_surfaces_must_not_restyle: true
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
        { name: "response_contract/graph_tool/MANIFEST.json", data: enc.encode(graphBundle.manifestText) },
        ...graphEntries
      );

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
      : "No roster is included. Make one reasonable identity pass; if a handwritten name remains unreadable, assign a stable label such as Student 01, preserve the evidence/page mapping, flag the uncertainty, and continue rather than stalling the run.";
    const rubricLine = request.rubric_files.length
      ? "A rubric/scoring guide is included under rubric/. Use it where it clearly applies."
      : "No rubric/scoring guide is included.";
    const scannedPath = request.requested_outputs.scanned_student_work_pdf;
    const gradeMode = request.grade_output.mode;

    return `# District Grading & Evidence Request - Pilot\n\n` +
`## Task\n` +
`Analyze the student evidence in this ZIP and return exactly ONE response ZIP. This package is the complete build contract; no separate teacher prompt is required. The teacher should only need to unzip the response and open CLICK_ME.html.\n\n` +
`Class / group: ${request.teacher.class_or_group}\n` +
`Grade / subject: ${request.teacher.grade_subject || "Not provided; infer only when reasonably clear from the evidence."}\n` +
`${rubricLine}\n${rosterLine}\n\n` +
`Teacher exceptions / context:\n${teacherNotes || "No exceptions or additional context provided."}\n\n` +
`## Detect the assignment / evidence title - REQUIRED\n` +
`The teacher intentionally did NOT type an assignment name. Determine a concise, useful title from the submitted evidence in this order: visible title on student work; rubric/scoring-guide title; meaningful filenames; concise title inferred from the actual skill/content; Student Evidence Review only as a last resort. Save the title and its basis in data/analysis.json and use it consistently.\n\n` +
`## Evidence rating - REQUIRED\n` +
`Every student report must use exactly one evidence rating: Convincing, Limited, Incorrect, or Not Observed. Convincing = clear/sufficient evidence. Limited = meaningful correct evidence but incomplete/inconsistent/insufficient. Incorrect = attempted evidence demonstrates a substantive incorrect idea/method/conclusion. Not Observed = insufficient usable evidence, including blank, omitted, missing, or unreadable work. Missing is not Incorrect.\n\n` +
`## Grade / score handling - REQUIRED AND AUTHORITATIVE\n` +
`Selected mode: ${gradeMode}\n${request.grade_output.policy}\n` +
`This teacher selection outranks free-form notes if they conflict. Record any conflict in data/qa.json and continue.\n\n` +
`## Default grading behavior - AUTOMATIC\n` +
`These are system defaults, not optional teacher requests: list Areas of Strength and Areas for Improvement; highlight and credit reasoning; treat all evidence as formative; allow multiple valid methods/solution paths; focus on mathematical/scientific reasoning rather than writing mechanics unless the teacher explicitly opts in; de-emphasize minor arithmetic/notation slips unless the teacher explicitly says to count them; credit partial understanding; do not equate missing with incorrect; keep feedback concise; give Convincing students extension/transfer; and flag unclear scans/uncertainty instead of guessing. Teacher exceptions/context may override only the specific item named.\n\n` +
`Exception semantics: "Ignore a question" means do not use that question as evidence. "Feedback only / don't grade" means review and comment on the question but do not let it affect the grade/score recommendation.\n\n` +
`## Evidence and identity rules\n` +
`Judge only from submitted evidence, rubric if present, roster for identity/order only, and teacher exceptions/context. Do not research students or use prior personal/student records. If a roster student has no identifiable work, use Not Observed/no evidence rather than Incorrect.\n\n` +
`## Locked styling and shared contracts\n` +
`Copy response_contract/styles.css exactly to assets/styles.css and verify its SHA against response_contract/STYLE_SHA256.txt. Copy response_contract/stations.css exactly to assets/stations.css. Follow response_contract/RESPONSE_LAYOUT_LOCK.md, response_contract/MATH_VISUAL_QA.md, response_contract/COMMON_PRACTICE_GUIDE.md, response_contract/DISTRICT_GRAPH_RENDERING_STANDARD.md, and response_contract/RESPONSE_QA_EXECUTION.md as executable HARD contracts. Do not restyle stable gold surfaces. If older wording elsewhere in this request conflicts with COMMON_PRACTICE_GUIDE.md about Common Course Practice or Question / Solution Set layout, COMMON_PRACTICE_GUIDE.md controls.\n\n` +
`## Required response ZIP structure\n` +
`~~~text\n` +
`CLICK_ME.html\n` +
`assets/\n  styles.css\n  stations.css\n  graphs/\n  visuals/\n` +
`scanned_work/\n  ${scannedPath.split('/').pop()}\n` +
`students/\n  <one report HTML per identified student>\n` +
`class/\n  class_overview.html\n  review_all_questions.html\n` +
`print/\n` +
`  all_student_reports.html\n  all_student_reports.pdf\n` +
`  common_review_extension/\n    student_worksheet.html\n    student_worksheet.pdf\n    teacher_guide.html\n` +
`  individualized/\n    <one HTML practice packet per student>\n` +
`  individual_practice_packets.pdf\n` +
`  stations/\n    index.html\n    stations.html\n    stations.pdf\n    answer_key.html\n    answer_key.pdf\n` +
`  question_set/\n    index.html                      # Activity Options + direction sections\n    presentation.html               # Set 1 Questions & Solutions projection deck\n    print_presentation.html\n    print_presentation.pdf\n    review_all.html\n    teacher_guide.html\n    structures/\n      find_someone_who.html          # adjustable Student-Set-style handout\n      cut_apart_cards.html\n` +
`data/\n  analysis.json\n  qa.json\n  request.json\n` +
`~~~\n\n` +
`All navigation, CSS, graph assets, and visual assets must use local relative links. PDFs must be finished printable files, not placeholders.\n\n` +
`## Scanned student work archive\n` +
`Create ${scannedPath}. Preserve submitted work exactly; combine readable scan/image pages into one teacher-friendly PDF when needed. Do not rewrite or clean up student answers.\n\n` +
`## CLICK_ME.html layout - LOCKED\n` +
`Keep the current simple dashboard hierarchy. 1) Hero/header with class, detected evidence title, grade/subject. 2) One quick-action row with exactly Print All Student Reports, Print All Individual Practice, View Scanned Student Work. 3) Individual Student Reports & Practice; each student card has Open Report and Individual Practice. 4) Class Data. 5) Common Course Practice with exactly three primary cards: Common Worksheet / Review + Extension, Stations, Question / Solution Set. Add a teacher-only Review All Questions link near the Common Course Practice heading. Do not create duplicate individual-practice or quick-action sections.\n\n` +
`## Individual reports and practice\n` +
`Each report includes student name/label; detected evidence title; Evidence Rating; optional grade/score only according to selected mode; specific strengths; highest-leverage improvement; evidence references when feasible; 1-3 next steps; and uncertainty when needed. Create one individual practice packet per student. For Convincing students favor extension/transfer. Create combined duplex-safe reports and practice PDFs in roster/identified order.\n\n` +
`## Duplex pairing - HARD\n` +
`For combined reports and combined individual practice, every student's segment must occupy an even number of physical pages. If final content count is odd, append exactly one intentionally blank page before the next student. Verify actual PDF page order and record before/after counts in data/qa.json.\n\n` +
`## Class analysis\n` +
`Include evidence sets analyzed, major strengths, top actionable errors/unfinished understandings, reliable pattern counts/percentages, suggested instructional groupings, Convincing students ready for extension, and evidence/identity limitations.\n\n` +
`## Common Worksheet / Review + Extension\n` +
`Create one compact class-wide student worksheet based on actual common needs, with targeted review and justified extension. On the student worksheet itself, visibly label the two sections **Review** and **Extension / Transfer** so students and teachers can tell which questions serve which purpose. The student-facing printable artifact is Student Worksheet. The HTML page that includes answers, teacher moves, and discourse moves is Teacher Guide. Do not call the teacher-facing HTML merely "HTML" and do not expose redundant Print buttons when browser print already produces the same intended layout.\n\n` +
`## Stations\n` +
`Create exactly four review stations plus two extension stations, 4-6 questions per station, with a complete separate answer key. Preserve the existing locked stations style. Do not redesign stations in this pass.\n\n` +
`## Question / Solution Set - SET 1 ONLY
` +
`Set 1 is the one approved mathematical set. Create no Set 2. Follow response_contract/COMMON_PRACTICE_GUIDE.md and RESPONSE_LAYOUT_LOCK.md exactly. question_set/index.html is the Algebra u1_1-style Activity Options page itself, with internal direction anchors; do not recreate the old six-card menu and do not create a second structures/index.html or directions.html.

` +
`### Activity Options / projection
` +
`List the nine approved projection/whiteboard routines in the Algebra activity format. Each routine name links to its directions anchor and each Set 1 link points to the same presentation.html. Do not show a standalone Presentation/Open Presentation card. presentation.html is an Algebra-style Question page then Solution page sequence for every Set 1 problem, not the prior Back/Next shell.

` +
`### Printable / utilities
` +
`Printable Handouts are Stations, Find Someone Who, and Cut-Apart Question Cards. Find Someone Who uses the current Student Set two-column worksheet look with partner signature + workspace and the Worksheet Builder-style screen-only left rail (All workspaces, Problem, Workspace, Graph/diagram, Reset, Print). Cut-Apart Cards keep the current approved layout. Teacher/Print Utilities are Print Presentation, Review All Questions, and Teacher Guide. No Tarsia or Blooket.

` +
`### Print Presentation
` +
`Keep the approved two-up gold layout: exactly two top-aligned questions per Letter page, no answers/moves/workspace.

` +
`## Review All Questions - teacher QA across all products
` +
`Create class/review_all_questions.html and link it from CLICK_ME. Show ALL generated follow-up questions from Common Worksheet, Stations, Set 1, and Individual Practice by student. Use zero workspace, compact cards/rows, required visuals, tiny source/purpose labels, and collapsible Answer / Teacher Move / Student Discourse Move. Reused common questions may be labeled as reused instead of visually duplicated.\n\n` +
`## Math, graph, and visual rendering - HARD\n` +
`Follow response_contract/MATH_VISUAL_QA.md and response_contract/DISTRICT_GRAPH_RENDERING_STANDARD.md. The request packages the current registered graph tool under response_contract/graph_tool/. For every supported Cartesian graph, including blank student grids, execute that packaged entrypoint directly. Do not substitute hand-built SVG/CSS/canvas or another plotting style just because it looks similar. Record renderer entrypoint + graph asset path for every Cartesian graph in data/qa.json. Apply these rules to every common/individual artifact.\n\n` +
`## data/analysis.json\n` +
`Include detected evidence title plus basis; student identifiers; evidence mapping; evidence ratings; optional grade results; roster matching; strengths; needs; class patterns; groupings; common-practice targets; individual-practice targets; station targets; Set 1 question/source mapping; and uncertainty flags. Copy request.json into data/request.json.\n\n` +
`## QA execution order - REQUIRED\n` +
`Follow response_contract/RESPONSE_QA_EXECUTION.md. Preserve full evidence review, but do programmatic package checks before expensive visual rendering. Visually render every graph/diagram page plus representative/outlier pages for each stable template. After a local fix, rerender only the changed artifact and direct dependents; do not automatically rerender the entire already-stable package. Record visual-QA coverage in data/qa.json.\n\n` +
`## Final QA before delivery\n` +
`- Required locked CSS/contracts are used.\n` +
`- Detected title follows the required priority.\n` +
`- CLICK_ME retains the locked three-part hierarchy and quick actions.\n` +
`- Common Worksheet exposes Student Worksheet + Teacher Guide.\n` +
`- Stations remain four review + two extension with complete key.\n` +
`- Exactly one Question / Solution Set exists and every Set 1 artifact includes the full set.\n` +
`- question_set/index.html is the Algebra u1_1-style Activity Options page; the old six-card Set 1 menu is absent.\n` +
`- No standalone Presentation card; projection routines reuse one Question/Solution deck.\n` +
`- Find Someone Who uses the gold Student Set worksheet look + partner signatures + left layout controls.\n` +
`- Cut-Apart Cards remain visually unchanged from the gold run.\n` +
`- assets/styles.css SHA matches the packaged gold lock.\n` +
`- Common Worksheet visibly labels Review and Extension / Transfer.\n` +
`- Print Presentation is present, exactly two questions per printed page, and top-aligned within each half-page.\n` +
`- No redundant Print buttons are shown when browser print is equivalent.\n` +
`- Review All pages are compact, zero-workspace, and complete.\n` +
`- MathJax, graphs, and visuals are rendered and checked.\n` +
`- Combined student PDFs are duplex-safe and verified.\n` +
`- All relative links resolve after unzip and data/qa.json reports PASS with no unresolved failures.\n\n` +
`Return only the single completed response ZIP as the authoritative artifact, with a short note telling the teacher to unzip it and open CLICK_ME.html.\n`;
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
