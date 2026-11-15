#!/usr/bin/env python3
"""Fast conservative question-bank prompt/figure hygiene gate.

Usage: python3 check_student_question_hygiene.py path/to/CH03.json

This is a static gate, not a proof of mathematical correctness or visual fidelity.
Teacher-only metadata and source_original_html are intentionally excluded.
"""
from __future__ import annotations
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
import json
import re
import sys

BANNED_CAPTIONS = (
    'A partitioned rectangle',
    'Each section is a rectangle. Find the combined area.',
    'Cell areas; side labels omitted',
    'Equivalent area model reconstructed from textbook tile layout.',
)

class StudentMarkup(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.attrs = []
        self.svg_depth = 0
        self.svg_lines = []
        self.figcaption_depth = 0
        self.figcaption_text = ''
        self.figcaptions = []
    def handle_starttag(self, tag, attrs):
        d = dict(attrs)
        self.attrs.append((tag,d))
        if tag == 'svg':self.svg_depth += 1
        if tag == 'line' and self.svg_depth:self.svg_lines.append(d)
        if tag == 'figcaption':self.figcaption_depth += 1
    def handle_endtag(self, tag):
        if tag == 'svg':self.svg_depth = max(0,self.svg_depth-1)
        if tag == 'figcaption':
            self.figcaption_depth = max(0,self.figcaption_depth-1)
            if not self.figcaption_depth:
                self.figcaptions.append(self.figcaption_text.strip())
                self.figcaption_text = ''
    def handle_data(self, d):
        if self.figcaption_depth:self.figcaption_text += d

def check(path:Path):
    obj=json.loads(path.read_text(encoding='utf-8'))
    failures=[]; counts=Counter()
    for fam in obj['families']:
        if fam.get('pilot_hidden'):continue
        for v in fam.get('candidates',[]):
            counts['candidates'] += 1
            ident=v['variant_id']; s=v['student_html']; parser=StudentMarkup()
            try:parser.feed(s);parser.close()
            except Exception as ex:failures.append((ident,'invalid HTML parse '+str(ex)))
            if re.search(r'<p>\s*<strong>Original CPM 3-\d+</strong>\s*</p>',s):
                failures.append((ident,'teacher-only source badge in student prompt'))
            if re.search(r'<(?:div|p|span|section)[^>]*(?:class|id)="[^\"]*(?:answer-key|worked-solution|correct-answer)[^\"]*"',s,re.I):
                failures.append((ident,'solution element in student prompt'))
            if re.search(r'(?i)(correct answer\s*:|answer key\s*:|solution\s*:)',s):
                failures.append((ident,'explicit solution prose in student prompt'))
            for caption in parser.figcaptions:
                if caption in BANNED_CAPTIONS or (caption=='Label each partial product.' and 'ch3-answer-space' not in s):
                    failures.append((ident,'unnecessary caption: '+caption))
            if 'Which expression equals for nonzero x?' in s:
                failures.append((ident,'incomplete question wording'))
            if s.count(r'\(')!=s.count(r'\)') or s.count(r'\[')!=s.count(r'\]'):
                failures.append((ident,'unbalanced MathJax delimiters'))
            for tag,d in parser.attrs:
                if any(k in d for k in ('data-answer','data-solution','data-correct-answer')):
                    failures.append((ident,'answer data attribute in student HTML'))
                if tag=='img' and re.search(r'\b(?:solution|correct answer|final answer)\b',d.get('alt',''),re.I):
                    failures.append((ident,'image alt suggests solution'))
            # Student must draw these graphs. No thick plotted relation should be in the student grid.
            if re.search(r'\b(graph (?:each|both|the|a) (?:line|lines|equation|equations|function|functions)|sketch the graph)\b',s[:320],re.I):
                counts['graph_construction_candidates'] += 1
                for line in parser.svg_lines:
                    try:w=float(line.get('stroke-width') or 0)
                    except ValueError:continue
                    if w>=2.3:
                        failures.append((ident,'possible pre-plotted answer in construction graph'))
            counts['tables']+=s.count('<table')
            counts['svg']+=s.count('<svg')
            counts['images']+=s.count('<img')
    print('Chapter:',obj.get('chapter'),'visible variants:',counts['candidates'], 'tables:',counts['tables'], 'svg:',counts['svg'],'images:',counts['images'],'graph-to-construct:',counts['graph_construction_candidates'])
    print('Static QA findings:',len(failures))
    for ident,reason in failures[:80]:print('-',ident,reason)
    return 1 if failures else 0

if __name__=='__main__':
    if len(sys.argv)!=2:
        print(__doc__.strip());raise SystemExit(2)
    raise SystemExit(check(Path(sys.argv[1])))
