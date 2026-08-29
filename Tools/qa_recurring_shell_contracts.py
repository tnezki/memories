#!/usr/bin/env python3
"""Fast structural QA for recurring assessment outputs.

This checker intentionally focuses on cheap deterministic failures that previously
caused expensive reruns: leaked template expressions, malformed MathJax row breaks,
Progress Tracker physical-shell shape, Review shell anchors, Exit ticket packet
shape, and Physics Summative answer-sheet materialization.
"""
from pathlib import Path
import re, sys
from html.parser import HTMLParser

root=Path(sys.argv[1] if len(sys.argv)>1 else '.').resolve()
errors=[]; checks=0

def check(cond,msg):
    global checks
    checks += 1
    if not cond: errors.append(msg)

def raw(path): return path.read_text(encoding='utf-8',errors='replace')

def count_class(text, cls):
    return len(re.findall(r'class=["\'][^"\']*\b'+re.escape(cls)+r'\b[^"\']*["\']',text,re.I))

def has_class(text, cls): return count_class(text,cls)>0

def has_id_class(text, ident, cls):
    pats=[
      rf'<section\b(?=[^>]*\bid=["\']{re.escape(ident)}["\'])(?=[^>]*\bclass=["\'][^"\']*\b{re.escape(cls)}\b[^"\']*["\'])[^>]*>',
      rf'<section\b(?=[^>]*\bclass=["\'][^"\']*\b{re.escape(cls)}\b[^"\']*["\'])(?=[^>]*\bid=["\']{re.escape(ident)}["\'])[^>]*>'
    ]
    return any(re.search(p,text,re.I) for p in pats)

bad_row=re.compile(r'(?<!\\)\\([xyz])(?=[\s+\-=,;:&<>\)\]\}])')
for p in root.rglob('*.html'):
    t=raw(p)
    hits=list(bad_row.finditer(t))
    check(not hits,f'{p}: malformed MathJax row break(s)')
    low=t.lower()
    check('join(bubble_rows)' not in low and '{{ bubble_rows' not in low and '{"".join(bubble_rows)' not in low,
          f'{p}: unresolved bubble-row template expression')

for p in root.rglob('unit_*_progress.html'):
    t=raw(p)
    check(count_class(t,'tracker-page')==2,f'{p}: Progress Tracker must contain exactly two tracker-page sections')
    check(has_class(t,'page-one') and has_class(t,'page-two'),f'{p}: Progress Tracker missing page-one/page-two')
    check(count_class(t,'status-choice')==4,f'{p}: Progress Tracker must contain four status choices')
    check('class="check"' in t or "class='check'" in t,f'{p}: Progress Tracker missing .check cells')
    check('class="ican-text"' in t or "class='ican-text'" in t,f'{p}: Progress Tracker missing .ican-text cells')

for p in root.rglob('review_*.html'):
    if '_practice' in p.stem.lower() or not re.fullmatch(r'review_\d+',p.stem,re.I): continue
    t=raw(p)
    for rid in ('glance','vocabulary','structures','dok','final-check'):
        check(has_id_class(t,rid,'review-panel'),f'{p}: Review missing #{rid}.review-panel')
    check('floating-top' in t and 'href="#top"' in t,f'{p}: Review missing floating Top control')

for p in root.rglob('exit_*.html'):
    t=raw(p)
    project=count_class(t,'project-only')
    packets=count_class(t,'exit-print')
    check(project>0,f'{p}: Exit has no project-only tickets')
    check(packets>=project,f'{p}: Exit missing print packets')
    check('printExitTicket' in t,f'{p}: Exit missing printExitTicket')
    check('print-active' in t,f'{p}: Exit missing print-active mechanism')

for p in root.rglob('*summative_assessment.html'):
    t=raw(p)
    if has_class(t,'answersheet') and has_class(t,'fr-sheet-page'):
        check(count_class(t,'bubble-row')==16,f'{p}: Physics answer sheet must materialize 16 bubble rows')

if errors:
    print('\n'.join('ERROR: '+x for x in errors))
    print(f'FAIL: {len(errors)} error(s), {checks} deterministic checks')
    raise SystemExit(1)
print(f'Recurring shell contract: PASS ({checks} deterministic checks)')
