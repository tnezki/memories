#!/usr/bin/env python3
from pathlib import Path
from bs4 import BeautifulSoup
import math, sys, re

root=Path(sys.argv[1] if len(sys.argv)>1 else '.').resolve()
errors=[]; checks=0

def fail(msg): errors.append(msg)
def check(cond,msg):
    global checks
    checks += 1
    if not cond: fail(msg)

def soup(p): return BeautifulSoup(p.read_text(encoding='utf-8'),'html.parser')
def reps(node):
    return (len(node.find_all('table')), len(node.find_all('img')), len(node.find_all('svg')))


# Final-byte / stylesheet contract.
for p in root.rglob('*.html'):
    raw=p.read_text(encoding='utf-8',errors='replace')
    stripped=raw.lstrip()
    check(bool(re.match(r'(?is)^(?:<!doctype\s+html\b|<html\b)',stripped)),
          f'{p}: visible/raw token before HTML document (expected doctype/html first)')
    s=soup(p); name=p.name.lower()
    hrefs=[x.get('href','') for x in s.find_all('link',rel=lambda v: v and 'stylesheet' in v)]
    if 'stations' in name:
        check('../../css/base.css' in hrefs, f'{p}: Stations missing ../../css/base.css')
        check('../../css/activities/activity_stations.css' in hrefs,
              f'{p}: Stations must link ../../css/activities/activity_stations.css')
        check('../../css/activity_stations.css' not in hrefs,
              f'{p}: Stations uses obsolete root activity_stations.css path')
    if 'find_someone_who' in name:
        check('../../css/base.css' in hrefs, f'{p}: Find Someone Who missing ../../css/base.css')
        check('../../css/activities/activity_find_someone_who.css' in hrefs,
              f'{p}: Find Someone Who must link ../../css/activities/activity_find_someone_who.css')
        check('../../css/activity_find_someone_who.css' not in hrefs,
              f'{p}: Find Someone Who uses obsolete root activity_find_someone_who.css path')

for p in root.rglob('*.html'):
    s=soup(p); name=p.name.lower()

    # Teacher-approved Activity hub placement.
    if name.endswith('_act1.html') and 'questions_solutions' not in name:
        options=s.select_one('section#activity-options.page')
        moves=s.select_one('section#teacher-student-moves.page')
        check(bool(options),f'{p}: Activity hub missing #activity-options')
        check(bool(moves),f'{p}: Activity hub missing #teacher-student-moves')
        if options and moves:
            sibling=options.find_next_sibling('section')
            check(sibling is moves,f'{p}: Teacher & Student Moves Guide must be page 2 immediately after Activity Options')
            labels=[x.get_text(' ',strip=True) for x in moves.select('.dir-label')]
            check('I-Can Moves' in labels,f'{p}: Moves Guide missing I-Can Moves')
            check('Participation-Structure Moves' in labels,f'{p}: Moves Guide missing Participation-Structure Moves')

    # Philosophy / shell rule: no descriptive figure captions in Activities output.
    check(not s.find('figcaption'), f'{p}: descriptive figcaption present')

    if 'questions_solutions' in name:
        for fig in s.select('.prob-q figure'):
            if fig.find('img'):
                check('graph-block' in (fig.get('class') or []), f'{p}: projection image figure must use graph-block')

    if 'find_someone_who' in name:
        spages=s.select('section.student-worksheet-page')
        kpages=s.select('section.teacher-key-page')
        sprobs=s.select('.student-problem')
        kprobs=s.select('.teacher-key-page .answer-problem')
        check(bool(sprobs), f'{p}: no student problems found')
        check(len(spages)==math.ceil(len(sprobs)/3), f'{p}: student page count must be ceil(items/3)')
        check(len(kpages)==math.ceil(len(kprobs)/4), f'{p}: key page count must be ceil(items/4)')
        for i,node in enumerate(sprobs,1):
            check(bool(node.select_one('.signature-line')), f'{p}: student problem {i} missing signature-line')
            check(bool(node.select_one('.workspace-label')), f'{p}: student problem {i} missing workspace-label')
            check(bool(node.select_one('.workspace')), f'{p}: student problem {i} missing workspace')

    if 'stations' in name:
        wrap=s.body.find('div',class_='wrap',recursive=False) if s.body else None
        check(bool(wrap),f'{p}: Stations body missing direct .wrap')
        if wrap:
            pages=wrap.find_all('section',class_='page',recursive=False)
            qpages=[x for x in pages if 'station-question-page' in (x.get('class') or [])]
            first_answer=next((i for i,x in enumerate(pages) if 'station-answer-page' in (x.get('class') or [])),len(pages))
            prompt_region=pages[:first_answer]
            sol_region=pages[first_answer:]
            check(len(prompt_region)==2*len(qpages),f'{p}: Stations prompt region must be station/blank pairs')
            for j in range(0,len(prompt_region),2):
                if j+1>=len(prompt_region): break
                qpage,blank=prompt_region[j],prompt_region[j+1]
                check('station-question-page' in (qpage.get('class') or []),f'{p}: prompt pair {j//2+1} must start with station question page')
                check(len(qpage.select(':scope > .station-grid > .station-problem'))==4,f'{p}: station prompt page {j//2+1} must have four problems')
                check(not qpage.select('.workspace, .work-space, .answer-space, textarea, input[type="text"]'),f'{p}: station prompt page {j//2+1} must not contain workspace')
                check('station-blank-page' in (blank.get('class') or []),f'{p}: station prompt page {j//2+1} must be followed by blank page')
                check(not blank.get_text(' ',strip=True),f'{p}: blank page after station {j//2+1} must be truly blank')
            check(len(sol_region)==2*len(qpages),f'{p}: Stations solutions must use exactly two pages per station')
            for j in range(0,len(sol_region),2):
                if j+1>=len(sol_region): break
                a1,a2=sol_region[j],sol_region[j+1]
                check('station-solution-page-1' in (a1.get('class') or []),f'{p}: solution block {j//2+1} missing page 1 class')
                check('station-solution-page-2' in (a2.get('class') or []),f'{p}: solution block {j//2+1} missing page 2 class')
                if 'solution-blank-page' in (a2.get('class') or []):
                    check(not a2.get_text(' ',strip=True),f'{p}: blank solution page {j//2+1} contains visible text')


    if 'stations' in name:
        # Match representations by bank id where traceability ids exist.
        q={}
        a={}
        for node in s.select('.station-question-page [data-bank-id], .station-problem[data-bank-id]'):
            q.setdefault(node.get('data-bank-id'), []).append(reps(node))
        for node in s.select('.station-answer-page [data-bank-id], .solution-item[data-bank-id]'):
            a.setdefault(node.get('data-bank-id'), []).append(reps(node))
        for bid in set(q)&set(a):
            check(any(r in a[bid] for r in q[bid]), f'{p}: station representation dropped for {bid}')

print(f'ACTIVITY_SHELL_CHECKS={checks}')
print(f'ERRORS={len(errors)}')
for e in errors: print('ERROR:',e)
sys.exit(1 if errors else 0)
