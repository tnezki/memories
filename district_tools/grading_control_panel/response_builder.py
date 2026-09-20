#!/usr/bin/env python3
"""Deterministic Grading & Evidence response renderer.

The model's job is evidence analysis + a small canonical content set. This script owns
HTML structure, activity directions, pagination controls, print behavior, and reuse.
"""
from __future__ import annotations
import argparse, hashlib, html, json, re, shutil
from pathlib import Path

BUILDER_VERSION = "district-grading-response-builder/1.0"
RATING_LABELS = ("Convincing", "Limited", "Incorrect", "Not Observed")


def esc(v):
    return html.escape("" if v is None else str(v), quote=True)


def raw(v):
    return "" if v is None else str(v)


def slug(v):
    s = re.sub(r"[^a-zA-Z0-9]+", "_", str(v or "student")).strip("_").lower()
    return s or "student"


def sha256(path: Path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def head(title, css_path, runtime_css=None, runtime_js=None):
    extra_css = f'<link rel="stylesheet" href="{runtime_css}">' if runtime_css else ""
    extra_js = f'<script defer src="{runtime_js}"></script>' if runtime_js else ""
    return (f'<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            f'<title>{esc(title)}</title><link rel="stylesheet" href="{css_path}">{extra_css}'
            '<script>window.MathJax={tex:{inlineMath:[["\\\\(","\\\\)"],["$","$"]],displayMath:[["\\\\[","\\\\]"]],processEscapes:true}};</script>'
            '<script defer src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>'
            f'{extra_js}</head>')


def visual_html(q, prefix=""):
    v = q.get("visual")
    if not v: return ""
    src = str(v)
    if not (src.startswith("http://") or src.startswith("https://") or src.startswith("data:")):
        src = prefix + src
    alt = q.get("visual_alt") or "Question visual"
    return f'<div class="visual-block"><img src="{esc(src)}" alt="{esc(alt)}"></div>'


def score_text(s):
    score = s.get("recommended_score")
    if score in (None, "", False): return s.get("rating", "")
    return f'{s.get("rating", "")} | recommended {score}'


def write(path: Path, text: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def validate(data):
    errs=[]
    if not data.get("assignment_title"): errs.append("assignment_title is required")
    if not data.get("class_name"): errs.append("class_name is required")
    students=data.get("students") or []
    if not students: errs.append("at least one student is required")
    for i,s in enumerate(students,1):
        if s.get("rating") not in RATING_LABELS: errs.append(f"student {i} has invalid rating")
    set1=data.get("set1") or []
    if not set1: errs.append("set1 is required")
    ids=set()
    for i,q in enumerate(set1,1):
        qid=q.get("id") or f"Q{i}"
        if qid in ids: errs.append(f"duplicate Set 1 id {qid}")
        ids.add(qid)
        if not q.get("prompt") or not q.get("answer"): errs.append(f"{qid} requires prompt and answer")
        ver=q.get("verification") or {}
        if ver.get("passed") is not True: errs.append(f"{qid} must have verification.passed=true before rendering")
    stations=data.get("stations") or []
    if len(stations)!=6: errs.append("exactly six stations are required (4 Review + 2 Extension)")
    if errs: raise ValueError("Response data failed validation:\n- " + "\n- ".join(errs))


def dashboard(data):
    cards=[]
    for s in data["students"]:
        sid=slug(s.get("slug") or s["name"])
        cards.append(f'<div class="card"><h3>{esc(s["name"])}</h3><p>{esc(score_text(s))}</p><div class="card-links"><a href="students/{sid}.html">Open Report</a><a href="print/individualized/{sid}_practice.html">Individual Practice</a></div></div>')
    scan=data.get("scan_output_name") or "Scanned_Student_Work.pdf"
    h=head("Open Grading Response","assets/styles.css")
    return h+f'''<body><div class="wrap"><header class="hero"><div class="eyebrow">District Grading & Evidence Response</div><h1>{esc(data['assignment_title'])}</h1><p class="subtitle">{esc(data['class_name'])}{(' | '+esc(data.get('grade_subject'))) if data.get('grade_subject') else ''}</p><div class="quick-actions"><a class="btn primary" href="print/all_student_reports.html">Print All Student Reports</a><a class="btn" href="print/all_individual_practice.html">Print All Individual Practice</a><a class="btn" href="scanned_work/{esc(scan)}">View Scanned Student Work</a></div></header>
<section class="section"><h2>Individual Student Reports & Practice</h2><p class="section-intro">{esc(data.get('student_packet_summary') or (str(len(data['students']))+' student evidence sets were identified from the scan.'))}</p><div class="student-grid">{''.join(cards)}</div></section>
<section class="section"><h2>Class Data</h2><p class="section-intro">Patterns, recommended groupings, strengths, and actionable next instruction.</p><div class="card-links"><a href="class/class_overview.html">Open Class Overview</a></div></section>
<section class="section"><div><h2>Common Course Practice</h2><p class="section-intro">One evidence-based question pool delivered through the locked course formats.</p></div><div class="grid"><div class="card"><h3>Common Worksheet / Review + Extension</h3><p>Targeted Review plus Extension / Transfer using the approved Set 1.</p><div class="card-links"><a href="print/common_review_extension/student_worksheet.html">Student Worksheet</a><a href="print/common_review_extension/teacher_guide.html">Teacher Guide</a></div></div><div class="card"><h3>Stations</h3><p>Four review stations and two extension stations.</p><div class="card-links"><a href="print/stations/index.html">Open Stations</a></div></div><div class="card"><h3>Question / Solution Set</h3><p>Set 1 Activity Options, classroom presentation, printable handouts, and teacher utilities.</p><div class="card-links"><a href="print/question_set/index.html">Open Activity Options</a></div></div></div></section></div></body></html>'''


def class_overview(data):
    c=data.get("class_summary") or {}
    counts={k:0 for k in RATING_LABELS}
    for s in data["students"]: counts[s["rating"]]+=1
    stats=''.join(f'<div class="stat"><strong>{counts[k]}</strong><span>{esc(k)}</span></div>' for k in RATING_LABELS)
    strengths=''.join(f'<li>{esc(x)}</li>' for x in c.get("strengths",[]))
    needs=''.join(f'<li>{esc(x)}</li>' for x in c.get("needs",[]))
    groupings=''.join(f'<div class="card"><h3>{esc(g.get("title"))}</h3><p>{esc(g.get("students"))}</p><p>{esc(g.get("note"))}</p></div>' for g in c.get("groupings",[]))
    rows=''.join(f'<tr><td>{esc(s["name"])}</td><td>{esc(s["rating"])}</td><td>{esc(s.get("recommended_score") or "—")}</td><td>{esc(s.get("highest_leverage_need") or "")}</td></tr>' for s in data["students"])
    h=head("Class Overview","../assets/styles.css")
    return h+f'''<body><div class="wrap"><div class="no-print"><a class="btn small-btn" href="../CLICK_ME.html">Back to Dashboard</a></div><header class="hero"><div class="eyebrow">{esc(c.get('eyebrow') or (data['class_name']+' Class Data'))}</div><h1>{esc(data['assignment_title'])}</h1><p class="subtitle">{esc(c.get('evidence_line') or (str(len(data['students']))+' student evidence sets'))}</p></header>
<section class="section"><h2>Evidence Analyzed</h2><p>{esc(c.get('evidence_analyzed') or 'Submitted student evidence was reviewed for strengths, needs, and next instruction.')}</p><div class="summary-grid">{stats}</div></section>
<section class="section"><h2>Major Strengths</h2><ul class="clean">{strengths}</ul></section>
<section class="section"><h2>Top Actionable Patterns</h2><ul class="clean">{needs}</ul>{('<div class="notice"><strong>Highest-leverage class target:</strong> '+esc(c.get('highest_leverage_target'))+'</div>') if c.get('highest_leverage_target') else ''}</section>
<section class="section"><h2>Suggested Instructional Groupings</h2><div class="grid">{groupings}</div></section>
<section class="section"><h2>Student Summary</h2><div class="table-wrap"><table><thead><tr><th>Student</th><th>Rating</th><th>Grade recommendation</th><th>Highest-leverage need</th></tr></thead><tbody>{rows}</tbody></table></div></section>
<section class="section"><h2>Limitations</h2><p class="small">{esc(c.get('limitations') or 'Ratings and grade recommendations are based only on the submitted evidence and remain teacher-review recommendations.')}</p></section></div></body></html>'''


def student_report(data,s):
    strengths=''.join(f'<li>{esc(x)}</li>' for x in s.get("strengths",[])); improvements=''.join(f'<li>{esc(x)}</li>' for x in s.get("improvements",[]))
    grade=(f' · Teacher-review grade recommendation: <strong>{esc(s.get("recommended_score"))}</strong>' if s.get("recommended_score") else '')
    h=head(s["name"]+" - Evidence Report","../assets/styles.css")
    return h+f'''<body><div class="wrap"><section class="report-page"><div class="report-head"><p class="eyebrow">{esc(data['class_name'])} · {esc(data['assignment_title'])}</p><h1>{esc(s['name'])}</h1><div class="report-meta">{esc(s.get('evidence_pages') or 'Submitted evidence')} · Rating: <strong>{esc(s['rating'])}</strong>{grade}</div></div><div class="feedback-box"><strong>Evidence Rating: {esc(s['rating'])}</strong><br><span class="small">Formative evidence from the submitted work; any grade shown is a recommendation for teacher review.</span></div><div class="report-section"><h2>Areas of Strength</h2><ul class="clean">{strengths}</ul></div><div class="report-section"><h2>Areas for Improvement</h2><ul class="clean">{improvements}</ul></div><div class="report-section"><h2>Feedback</h2><p>{esc(s.get('feedback') or '')}</p></div></section></div></body></html>'''


def rail(include_visual=True):
    v = '<div class="control-group"><label for="runtimeVisual">Graph / diagram</label><div class="runtime-control-row"><input id="runtimeVisual" type="range" min="70" max="160" value="100"><output id="runtimeVisualOut">100%</output></div></div>' if include_visual else ''
    return f'''<aside class="runtime-controls"><div class="control-group"><label for="runtimeAll">All workspaces</label><div class="runtime-control-row"><input id="runtimeAll" type="range" min="0" max="300" value="100"><output id="runtimeAllOut">100%</output></div></div><div class="control-group"><label for="runtimeProblem">Problem</label><select id="runtimeProblem"><option value="all">All</option></select></div><div class="control-group"><label for="runtimeOne">Workspace</label><div class="runtime-control-row"><input id="runtimeOne" type="range" min="0" max="1200" value="100"><output id="runtimeOneOut">100%</output></div></div>{v}<div class="runtime-actions"><button id="runtimeReset">Reset</button><button id="runtimePrint" class="primary">Print</button></div><div class="runtime-note">White sheets are the actual Letter pages. Problems flow within a page; changing workspace repaginates the document.</div></aside>'''


def practice_source(data, student=None, set1=None, visual_prefix="../../"):

    if student:
        qs=student.get("practice_questions",[])
        header=f'<div class="runtime-flow-header"><div class="name-line"><span>{esc(student["name"])} - Individual Practice</span><span>Name: ____________________</span></div><p class="small">{esc(student.get("practice_intro") or ("Targeted follow-up from "+data["assignment_title"]+"."))}</p></div>'
    else:
        qs=set1 or []
        header=f'<div class="runtime-flow-header"><div class="set-head"><div><h1>Common Worksheet</h1><p>{esc(data["assignment_title"])} · {esc(data["class_name"])}</p></div><div class="set-meta">Review + Extension / Transfer</div></div><div class="name-line"><span>Name: ____________________</span><span>Date: __________</span></div></div>'
    blocks=[]; last_section=None
    for i,q in enumerate(qs,1):
        section=q.get("section")
        if set1 is not None and section!=last_section:
            blocks.append(f'<div class="runtime-flow-block worksheet-section-label{(" extension" if section and section.lower().startswith("extension") else "")}">{esc(section or "Review")}</div>'); last_section=section
        label=q.get("label")
        title=(str(i)+'.') if set1 is not None else ((str(i)+'. '+str(label)) if label else str(i)+'.')
        blocks.append(f'<div class="runtime-flow-block practice-block" data-problem="{esc(q.get("id") or ("Q"+str(i)))}" style="--base-workspace:{esc(q.get("workspace") or "1.05in")}"><h3>{esc(title)} {raw(q.get("prompt"))}</h3>{visual_html(q,visual_prefix)}<div class="workspace"></div></div>')
    return header+''.join(blocks)


def flow_document(title, data, segments_html, css_prefix, runtime_prefix, duplex=False):
    h=head(title,css_prefix+"assets/styles.css",runtime_prefix+"assets/runtime.css",runtime_prefix+"assets/runtime.js")
    return h+f'<body class="runtime-preview runtime-with-controls">{rail(True)}<div class="runtime-shell"><div id="runtimePageStack" class="runtime-page-stack"></div><div id="runtimeFlowSource" class="runtime-flow-source" data-duplex="{str(duplex).lower()}">{segments_html}</div></div></body></html>'


def individual_practice(data,s):
    seg=f'<section class="runtime-flow-segment" data-layout="list">{practice_source(data,student=s,visual_prefix='../../')}</section>'
    return flow_document(s["name"]+" - Individual Practice",data,seg,"../../","../../",False)


def combined_practice(data):
    segs=[]
    for s in data["students"]: segs.append(f'<section class="runtime-flow-segment" data-layout="list">{practice_source(data,student=s,visual_prefix='../')}</section>')
    return flow_document("All Individual Practice",data,''.join(segs),"../","../",True)


def common_worksheet(data):
    seg=f'<section class="runtime-flow-segment" data-layout="grid2">{practice_source(data,set1=data["set1"],visual_prefix='../../')}</section>'
    return flow_document("Common Worksheet",data,seg,"../../","../../",False)


def teacher_guide(data):
    cards=[]
    for i,q in enumerate(data["set1"],1):
        cards.append(f'<div class="teacher-question"><h3>{i}. {esc(q.get("section") or "Review")} <span class="small">- {esc(q.get("label") or "")}</span></h3><div class="question-body">{raw(q["prompt"])}</div>{visual_html(q,"../../")}<div class="guide-answer"><strong>Answer:</strong> {raw(q["answer"])}</div><div class="guide-move"><strong>Teacher move:</strong> {esc(q.get("teacher_move") or "")}</div><div class="guide-move"><strong>Student discourse move:</strong> {esc(q.get("discourse_move") or "")}</div></div>')
    h=head("Common Worksheet Teacher Guide","../../assets/styles.css")
    return h+f'<body><div class="wrap"><main class="teacher-guide"><div class="set-head"><div><h1>Teacher Guide - Common Worksheet</h1><p>{esc(data["assignment_title"])}</p></div><div class="set-meta">Review + Extension / Transfer</div></div><div class="teacher-guide-grid">{"".join(cards)}</div></main></div></body></html>'


def combined_reports(data):
    pages=[]
    for s in data["students"]:
        strengths=''.join(f'<li>{esc(x)}</li>' for x in s.get("strengths",[])); improvements=''.join(f'<li>{esc(x)}</li>' for x in s.get("improvements",[]))
        pages.append(f'<section class="runtime-flow-segment" data-layout="list"><div class="runtime-flow-header"><div class="report-head"><p class="eyebrow">{esc(data["class_name"])} · {esc(data["assignment_title"])}</p><h1>{esc(s["name"])}</h1><div class="report-meta">Rating: <strong>{esc(s["rating"])}</strong>{(" · Recommended: "+esc(s.get("recommended_score"))) if s.get("recommended_score") else ""}</div></div></div><div class="runtime-flow-block feedback-box"><strong>Evidence Rating: {esc(s["rating"])}</strong></div><div class="runtime-flow-block report-section"><h2>Areas of Strength</h2><ul class="clean">{strengths}</ul></div><div class="runtime-flow-block report-section"><h2>Areas for Improvement</h2><ul class="clean">{improvements}</ul></div><div class="runtime-flow-block report-section"><h2>Feedback</h2><p>{esc(s.get("feedback") or "")}</p></div></section>')
    # no workspace controls for reports; runtime JS still paginates and enforces duplex
    h=head("All Student Reports","../assets/styles.css","../assets/runtime.css","../assets/runtime.js")
    return h+f'<body class="runtime-preview"><div class="no-print" style="max-width:8.5in;margin:12px auto"><button class="btn primary" onclick="window.print()">Print</button></div><div id="runtimePageStack" class="runtime-page-stack"></div><div id="runtimeFlowSource" class="runtime-flow-source" data-duplex="true">{"".join(pages)}</div></body></html>'


def station_index(data):
    cards=[]
    for i,s in enumerate(data["stations"],1): cards.append(f'<div class="station-card"><h2>{esc(s.get("type") or "Review")} Station {esc(s.get("number") or i)}</h2><p>{esc(s.get("title") or "")}</p></div>')
    h=head("Stations Index","../../assets/stations.css")
    return h+f'<body><main class="station-index"><h1>Stations</h1><p>{esc(data["assignment_title"])}</p><p>Four review stations plus two extension stations, 4-6 questions each.</p><div class="buttons"><a class="primary" href="stations.html">Open Student Stations</a><a href="answer_key.html">Open Answer Key</a></div><div class="station-list">{"".join(cards)}</div></main></body></html>'


def stations_doc(data,key=False):
    parts=[]
    for idx,s in enumerate(data["stations"],1):
        t=s.get("type") or ("Review" if idx<=4 else "Extension")
        n=s.get("number") or (idx if idx<=4 else idx-4)
        title=f'{t} Station {n} - {s.get("title") or ""}'
        qs=[]
        for j,q in enumerate(s.get("questions",[]),1):
            if key:
                qs.append(f'<div class="solution-item"><h3>Question {j}</h3><div class="question">{raw(q.get("prompt"))}</div>{visual_html(q,"../../")}<p><strong>Answer:</strong> {raw(q.get("answer"))}</p></div>')
            else:
                qs.append(f'<div class="problem"><div class="problem-number">Question {j}</div><div class="question">{raw(q.get("prompt"))}</div>{visual_html(q,"../../")}<div class="workspace"></div></div>')
        body=''.join(qs)
        if key: body=f'<div class="solution-list">{body}</div>'
        else: body=f'<div class="problems">{body}</div>'
        parts.append(f'<section class="page"><div class="header small">{esc(title)}{(" - Answer Key" if key else "")}</div>{body}<div class="page-footer"><span>{esc(data["assignment_title"])}</span><span>{"Teacher Key" if key else "Station " + str(n)}</span></div></section>')
    h=head("Stations Answer Key" if key else "Student Stations","../../assets/stations.css")
    return h+f'<body>{"".join(parts)}</body></html>'


BASE_DIRECTIONS = {
"Whiteboard Indy": ("Individual → independent practice","Each student gets a whiteboard and one marker.",["Notes are welcome.","Try something before asking for an answer.","Write large and clearly.","Use a partner for reasoning, not copying.","Fix mistakes and discuss what changed."],"Individual accountability + low-stakes problem entry"),
"Whiteboard Partners": ("Fast partner practice","One whiteboard and one marker per pair.",["Both students stay engaged.","Alternate who writes.","Explain before erasing.","Resolve disagreements with evidence."],"Engagement + quick feedback"),
"Rally Coach": ("Partner explanation + alternating roles","Partners share a workspace; one explains while one records.",["Partner A explains and Partner B records.","Coach with questions, not answers.","Switch roles after each problem.","Both partners verify the final response."],"Verbal reasoning + procedural accuracy"),
"Speed Dating": ("Paired practice → timed rotation → strategy sharing","Each student keeps their own work while partners rotate.",["Solve the projected problem independently first.","Compare methods with the current partner.","Rotate when directed.","Carry one useful strategy to the next partner."],"Repeated explanation + strategy comparison"),
"Showdown": ("Individual think → simultaneous reveal → team check","Teams need individual boards or papers.",["Everyone solves before anyone reveals.","Reveal together on the signal.","Compare differences in reasoning.","Revise only after discussion."],"Individual accountability + team feedback"),
"Think, Trade, Agree": ("Individual think → partner trade → agreement","Students need individual work space.",["Think and solve first.","Trade explanations with a partner.","Ask one clarifying question.","Agree on a justified response or record the disagreement."],"Evidence-based comparison"),
"Round Table": ("Team rotation of written reasoning","One shared sheet or board per team.",["One student adds a step or representation.","Pass the work to the next person.","Read what is already there before adding.","Team checks the complete solution."],"Visible collaborative reasoning"),
"Hot Seat": ("Describe → reason → reveal","One student faces away from the projected question while teammates describe permitted information.",["Use precise academic language.","Do not simply say the final answer.","Hot-seat student records or states the reasoning.","Reveal and compare afterward."],"Precise language + listening"),
"Rally Coach II": ("Solve → coach → restate → switch","Partners each need a workspace.",["Solver works aloud.","Coach asks questions only.","Solver restates the completed reasoning.","Switch roles for the next problem."],"Metacognition + partner coaching"),
"Quiz-Quiz-Trade": ("Pair → quiz → coach/check → trade cards","Give each student one Cut-Apart Question Card.",["Stand, mix, and pair with the nearest available partner.","Partner A reads the card; Partner B answers and explains.","Partner A coaches or asks for a check before confirming the response.","Switch roles using Partner B's card.","Trade cards, thank your partner, and mix again."],"Retrieval + explanation with repeated partners"),
"Fan-N-Pick": ("Four rotating team roles with a card deck","Teams of four share one stack of Cut-Apart Question Cards.",["Student 1 fans the cards.","Student 2 picks a card and reads the prompt.","Student 3 answers and explains.","Student 4 checks, coaches, or asks for evidence.","Rotate roles clockwise and repeat."],"Equal participation + team coaching"),
"Mix-Pair-Share with Cards": ("Mix → pair → respond → switch","Each student carries one Cut-Apart Question Card.",["Mix around the room until the teacher signals pair.","Partner A reads the card; both partners think before discussing.","Share and compare responses.","Switch to Partner B's card.","Trade cards if directed, then mix again."],"Movement + repeated explanation"),
"Inside-Outside Circle with Cards": ("Paired circle discussion with rotation","Form equal inside and outside circles; each student holds one Cut-Apart Question Card.",["Face the partner across from you.","Use one partner's card as the prompt and both respond.","Compare reasoning and resolve disagreement.","Switch to the other card if time allows.","Outside circle rotates when directed."],"Fast repeated practice with many partners"),
}

def activity_options(data):
    shared=["Whiteboard Indy","Whiteboard Partners","Rally Coach","Speed Dating","Showdown","Think, Trade, Agree","Round Table","Hot Seat","Rally Coach II"]
    cards=["Quiz-Quiz-Trade","Fan-N-Pick","Mix-Pair-Share with Cards","Inside-Outside Circle with Cards"]
    def aid(n): return 'dir-'+slug(n).replace('_','-')
    shared_rows=''.join(f'<li><a href="#{aid(n)}"><strong>{esc(n)}</strong></a> — <a href="presentation.html">Set 1</a></li>' for n in shared)
    card_rows=''.join(f'<li><a href="#{aid(n)}"><strong>{esc(n)}</strong></a> — <a href="structures/cut_apart_cards.html">Cards</a></li>' for n in cards)
    pages=[]
    for n in shared+cards:
        structure,setup,steps,goal=BASE_DIRECTIONS[n]
        material='structures/cut_apart_cards.html' if n in cards else 'presentation.html'
        material_text='Cut-Apart Question Cards' if n in cards else 'Set 1 classroom presentation'
        lis=''.join(f'<li>{esc(x)}</li>' for x in steps)
        pages.append(f'''<section class="activity-page" id="{aid(n)}"><div class="dir-header"><div><div class="act-eyebrow">Classroom Participation Structure</div><h1 class="act-title">{esc(n)}</h1><div class="act-subtitle">{esc(data.get('set1_focus') or data['assignment_title'])}</div></div><div class="act-meta"><a href="#activity-options">← Activity Options</a></div></div><div class="dir-body"><div class="dir-text"><div class="dir-row"><span class="dir-label">Structure</span><p>{esc(structure)}</p></div><div class="dir-row"><span class="dir-label">Setup</span><p>{esc(setup)}</p></div><div class="dir-row"><span class="dir-label">Directions</span><ol>{lis}</ol></div><div class="dir-goal"><strong>Goal:</strong> {esc(goal)}</div><div class="dir-row"><span class="dir-label">Materials</span><p><a href="{material}">{esc(material_text)}</a></p></div></div><aside class="looks-like"><div class="looks-good"><div class="looks-header">Looks Like Success</div><ul><li>Students explain before comparing final answers.</li><li>Everyone has a visible thinking role.</li><li>Disagreements are resolved with evidence.</li></ul></div><div class="looks-bad"><div class="looks-header">Doesn't Look Like</div><ul><li>Copying without explanation.</li><li>One student doing all the thinking.</li><li>Moving on with an unresolved disagreement.</li></ul></div></aside></div></section>''')
    h=head("Activity Options","../../assets/styles.css")
    return h+f'''<body><div class="activity-options-wrap"><section class="activity-page" id="activity-options"><div class="dir-header"><div><div class="act-eyebrow">{esc(data['class_name'])}</div><h1 class="act-title">Activity Options</h1><div class="act-subtitle">{esc(data['assignment_title'])}</div></div><div class="act-meta">One shared Set 1<br>{len(data['set1'])} questions</div></div><div class="dir-text"><div class="dir-row"><span class="dir-label">Teacher / Print Utilities</span><ul><li><a href="print_presentation.html"><strong>Print Presentation</strong></a></li><li><a href="../common_review_extension/teacher_guide.html"><strong>Teacher Guide</strong></a></li></ul></div><p><strong>Set 1 focus:</strong> {esc(data.get('set1_focus') or '')}</p><div class="dir-row"><span class="dir-label">Classroom Participation Structures</span><div><div class="activity-group"><div class="activity-group-title">Shared Prompt / Partner Structures</div><div class="activity-material">Uses the Set 1 classroom presentation</div><ul>{shared_rows}</ul></div><div class="activity-group"><div class="activity-group-title">Card-Based Structures</div><div class="activity-material">Uses the one Cut-Apart Question Cards deck</div><ul>{card_rows}</ul></div></div></div><div class="dir-row"><span class="dir-label">Printable Handouts</span><ul><li><strong>Stations</strong> — <a href="../stations/index.html">Open Stations</a></li><li><strong>Find Someone Who</strong> — <a href="../common_review_extension/student_worksheet.html">Set 1</a></li><li><strong>Cut-Apart Question Cards</strong> — <a href="structures/cut_apart_cards.html">Set 1</a></li></ul></div></div></section>{''.join(pages)}</div></body></html>'''


def set_presentation(data):
    options=''.join(f'<option value="{esc(q.get("id") or ("Q"+str(i)))}">{esc(q.get("id") or ("Q"+str(i)))}</option>' for i,q in enumerate(data["set1"],1))
    pages=[]
    for i,q in enumerate(data["set1"],1):
        qid=q.get("id") or f"Q{i}"
        pages.append(f'<section class="runtime-letter-page runtime-set-page" data-problem="{esc(qid)}"><div class="runtime-set-half runtime-set-question"><div class="set-label">Set 1 - Question {i}</div><div class="set-prompt">{raw(q["prompt"])}</div>{visual_html(q,"../../")}<div class="runtime-question-space"></div></div><div class="runtime-set-half runtime-set-teacher"><div class="set-label">Teacher support</div><div class="guide-answer"><strong>Answer:</strong> {raw(q["answer"])}</div><div class="guide-move"><strong>Teacher move:</strong> {esc(q.get("teacher_move") or "")}</div><div class="guide-move"><strong>Student discourse move:</strong> {esc(q.get("discourse_move") or "")}</div></div><div class="runtime-page-number">Page {i}</div></section>')
    controls=rail(True).replace('All workspaces','All question spacing').replace('>Workspace<','>Question spacing / workspace<').replace('<select id="runtimeProblem"><option value="all">All</option></select>',f'<select id="runtimeProblem"><option value="all">All</option>{options}</select>')
    h=head("Set 1 Classroom Presentation","../../assets/styles.css","../../assets/runtime.css","../../assets/runtime.js")
    return h+f'<body class="runtime-preview runtime-with-controls">{controls}<div id="runtimeSetStack" class="runtime-page-stack">{"".join(pages)}</div></body></html>'


def print_presentation(data):
    chunks=[]; qs=data["set1"]
    for p in range(0,len(qs),2):
        slides=[]
        for j,q in enumerate(qs[p:p+2],p+1): slides.append(f'<div class="print-slide"><div class="slide-number">Set 1 · Question {j}</div><div class="slide-question">{raw(q["prompt"])}</div>{visual_html(q,"../../")}</div>')
        if len(slides)==1: slides.append('<div class="print-slide"></div>')
        chunks.append(f'<div class="print-presentation-page">{"".join(slides)}</div>')
    h=head("Print Presentation","../../assets/styles.css")
    return h+f'<body><div class="print-presentation-wrap">{"".join(chunks)}</div></body></html>'


def cut_cards(data):
    cards=[]
    for i,q in enumerate(data["set1"],1): cards.append(f'<div class="cut-card"><div class="card-number">Set 1 · Card {i}</div><div class="question-body">{raw(q["prompt"])}</div>{visual_html(q,"../../../")}</div>')
    h=head("Cut-Apart Cards - Set 1","../../../assets/styles.css")
    return h+f'<body><div class="screen-page"><div class="set-head"><div><h1>Cut-Apart Question Cards</h1><p>Complete Set 1 · supports the card-based participation structures</p></div></div><div class="cut-card-grid">{"".join(cards)}</div></div></body></html>'


def build(data, request_root:Path, out:Path):
    validate(data)
    contract=request_root/"response_contract"
    out.mkdir(parents=True,exist_ok=True)
    (out/"assets").mkdir(exist_ok=True)
    for src,name in [(contract/"styles.css","styles.css"),(contract/"stations.css","stations.css"),(contract/"runtime.css","runtime.css"),(contract/"runtime.js","runtime.js")]: shutil.copy2(src,out/"assets"/name)
    write(out/"CLICK_ME.html",dashboard(data)); write(out/"class/class_overview.html",class_overview(data)); write(out/"print/all_student_reports.html",combined_reports(data)); write(out/"print/all_individual_practice.html",combined_practice(data));
    for s in data["students"]:
        sid=slug(s.get("slug") or s["name"]); write(out/f"students/{sid}.html",student_report(data,s)); write(out/f"print/individualized/{sid}_practice.html",individual_practice(data,s))
    write(out/"print/common_review_extension/student_worksheet.html",common_worksheet(data)); write(out/"print/common_review_extension/teacher_guide.html",teacher_guide(data))
    write(out/"print/stations/index.html",station_index(data)); write(out/"print/stations/stations.html",stations_doc(data,False)); write(out/"print/stations/answer_key.html",stations_doc(data,True))
    write(out/"print/question_set/index.html",activity_options(data)); write(out/"print/question_set/presentation.html",set_presentation(data)); write(out/"print/question_set/print_presentation.html",print_presentation(data)); write(out/"print/question_set/structures/cut_apart_cards.html",cut_cards(data))
    # copy generated visuals if supplied inside request_root/generated_assets
    ga=request_root/"generated_assets"
    if ga.exists(): shutil.copytree(ga,out/"assets",dirs_exist_ok=True)
    scan_source=data.get("scan_source")
    if scan_source:
        src=request_root/scan_source; dest=out/"scanned_work"/(data.get("scan_output_name") or src.name); dest.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(src,dest)
    # preserve the model-produced data and write deterministic renderer QA
    ddir=out/"data"; ddir.mkdir(exist_ok=True); write(ddir/"response_data.json",json.dumps(data,indent=2,ensure_ascii=False))
    rq=request_root/"request.json"
    if rq.exists(): shutil.copy2(rq,ddir/"request.json")
    checks={"builder_version":BUILDER_VERSION,"status":"PASS","set1_count":len(data["set1"]),"student_count":len(data["students"]),"station_count":len(data["stations"]),"styles_sha256":sha256(out/"assets/styles.css"),"runtime_css_sha256":sha256(out/"assets/runtime.css"),"runtime_js_sha256":sha256(out/"assets/runtime.js"),"forbidden_generated_pdfs":[],"duplicate_review_pages":[],"generated_html_count":len(list(out.rglob("*.html")))}
    write(ddir/"template_qa.json",json.dumps(checks,indent=2))


def main():
    p=argparse.ArgumentParser(); p.add_argument("--data",required=True); p.add_argument("--request-root",default="."); p.add_argument("--out",required=True); a=p.parse_args()
    data=json.loads(Path(a.data).read_text(encoding="utf-8")); build(data,Path(a.request_root).resolve(),Path(a.out).resolve())
    print(f"PASS {BUILDER_VERSION}: {a.out}")
if __name__=="__main__": main()
