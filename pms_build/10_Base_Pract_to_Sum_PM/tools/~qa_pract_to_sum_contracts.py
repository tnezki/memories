#!/usr/bin/env python3
from pathlib import Path
from bs4 import BeautifulSoup
import re, sys

root=Path(sys.argv[1] if len(sys.argv)>1 else '.').resolve()
errors=[]; checks=0; warnings=[]

def check(cond,msg):
    global checks
    checks+=1
    if not cond: errors.append(msg)

# Raw-byte MathJax corruption detector. A correct row break before x/y/z is \\x etc.;
# this flags a single invalid slash such as \x, \y, \z when followed by row content.
bad_row=re.compile(r'(?<!\\)\\([xyz])(?=[\s+\-=,;:&<>\)\]\}])')
for p in root.rglob('*.html'):
    raw=p.read_text(encoding='utf-8',errors='replace')
    hits=list(bad_row.finditer(raw))
    check(not hits, f'{p}: malformed MathJax row break(s): '+', '.join('\\'+h.group(1) for h in hits[:8])+(f' ... ({len(hits)} total)' if len(hits)>8 else ''))

# Progress tracker stale-unit / shell / exact-I-can checks.
for p in root.rglob('unit_*_progress.html'):
    m=re.search(r'unit_(\d+)_progress\.html$',p.name,re.I)
    if not m: continue
    u=m.group(1); s=BeautifulSoup(p.read_text(encoding='utf-8'),'html.parser'); txt=s.get_text(' ',strip=True)
    check(bool(s.select('.tracker-page')),f'{p}: missing tracker-page shell')
    goals=s.select('.goal-card[data-mastery-goal]')
    check(bool(goals),f'{p}: missing goal-card MG blocks')
    for g in goals:
        gid=g.get('data-mastery-goal','')
        check(gid.startswith(f'U{u}-'),f'{p}: stale/wrong-unit Mastery Goal ID {gid}')
        rows=g.select('.ican-list .ican')
        check(bool(rows),f'{p}: {gid} has no explicit .ican rows')
        seen=[]
        for j,row in enumerate(rows,1):
            t=row.get_text(' ',strip=True)
            t=re.sub(r'^[\s□☐☑✓✔•-]+','',t).strip()
            check(bool(re.match(r'^I\s+can\b',t,re.I)),f'{p}: {gid} I-can row {j} is not an explicit I-can statement: {t[:120]!r}')
            seen.append(re.sub(r'\s+',' ',t).lower())
        check(len(seen)==len(set(seen)),f'{p}: {gid} contains duplicate I-can rows')
    stale=set(re.findall(r'\bUnit\s+(\d+)\b',txt,re.I))-{u}
    # Other Unit labels may be legitimate only if explicitly in a review/evidence citation, not in the tracker shell.
    check(not stale,f'{p}: stale Unit labels present: {sorted(stale)}')

# Cross-family physical-shell regression checks.
for p in root.rglob('unit_*_progress.html'):
    s=BeautifulSoup(p.read_text(encoding='utf-8'),'html.parser')
    check(len(s.select('section.tracker-page'))==2,f'{p}: Progress Tracker must be exactly two physical pages')

for p in root.rglob('exit_*.html'):
    raw=p.read_text(encoding='utf-8',errors='replace')
    check('document.body.dataset.printTarget' not in raw,f'{p}: obsolete Physics-only Exit print JS detected')
    check('printExitTicket' in raw and 'print-active' in raw,f'{p}: universal Exit print-active mechanism missing')

for p in root.rglob('*summative_assessment.html'):
    raw=p.read_text(encoding='utf-8',errors='replace')
    check('join(bubble_rows)' not in raw.lower(),f'{p}: unresolved bubble_rows renderer expression')
    s=BeautifulSoup(raw,'html.parser')
    sheet=s.select_one('section.page.answersheet')
    if sheet and s.select_one('section.fr-sheet-page'):
        check(len(sheet.select('.sheetgrid .bubble-row'))==16,f'{p}: Physics answer sheet requires 16 bubble rows')

# Unit Review = current-unit Mastery contract, NOT Retrieval-stage contract.
progress_mg={}
for p in root.rglob('unit_*_progress.html'):
    m=re.search(r'unit_(\d+)_progress\.html$',p.name,re.I)
    if not m: continue
    u=m.group(1); s=BeautifulSoup(p.read_text(encoding='utf-8'),'html.parser')
    progress_mg[u]={g.get('data-mastery-goal','').strip() for g in s.select('.goal-card[data-mastery-goal]') if g.get('data-mastery-goal')}

for p in root.rglob('review_*.html'):
    if '_practice' in p.stem.lower():
        continue
    m=re.fullmatch(r'review_(\d+)',p.stem,re.I)
    if not m: continue
    u=m.group(1)
    s=BeautifulSoup(p.read_text(encoding='utf-8'),'html.parser')
    body=s.body
    check(body is not None,f'{p}: missing body')
    if not body: continue
    h1=s.find('h1'); htxt=h1.get_text(' ',strip=True) if h1 else ''
    check(bool(re.search(rf'\bUnit\s+{re.escape(u)}\s+Review\b',htxt,re.I)),f'{p}: visible title must be current Unit {u} Review: {htxt!r}')
    txt=s.get_text(' ',strip=True)
    stale=set(re.findall(r'\bUnit\s+(\d+)\b',txt,re.I))-{u}
    check(not stale,f'{p}: prior/source Unit labels leaked into student-facing Review: {sorted(stale)}')
    sections=s.select('.section-review[data-mastery-goal]')
    check(bool(sections),f'{p}: Review must be organized by current Unit Mastery Goals with data-mastery-goal')
    mids=[x.get('data-mastery-goal','').strip() for x in sections]
    for gid in mids: check(gid.startswith(f'U{u}-MG'),f'{p}: wrong-unit/invalid Mastery Goal {gid}')
    if u in progress_mg and progress_mg[u]:
        check(set(mids)==progress_mg[u],f'{p}: Review Mastery Goal set {sorted(set(mids))} != Progress Tracker {sorted(progress_mg[u])}')

for p in root.rglob('review_*_practice.html'):
    m=re.fullmatch(r'review_(\d+)_practice',p.stem,re.I)
    if not m: continue
    u=m.group(1); s=BeautifulSoup(p.read_text(encoding='utf-8'),'html.parser'); txt=s.get_text(' ',strip=True)
    stale=set(re.findall(r'\bUnit\s+(\d+)\b',txt,re.I))-{u}
    check(not stale,f'{p}: prior/source Unit labels leaked into Review Practice: {sorted(stale)}')
    sections=s.select('section[data-mastery-goal]')
    check(bool(sections),f'{p}: Review Practice missing data-mastery-goal sections')
    mids=[]
    for sec in sections:
        gid=(sec.get('data-mastery-goal') or '').strip(); mids.append(gid)
        check(gid.startswith(f'U{u}-MG'),f'{p}: wrong-unit/invalid Mastery Goal {gid}')
        probs=sec.select('.problem')
        check(len(probs)==4,f'{p}: {gid} must contain exactly 4 Review Practice questions; found {len(probs)}')
    if u in progress_mg and progress_mg[u]:
        check(set(mids)==progress_mg[u],f'{p}: Review Practice Mastery Goal set {sorted(set(mids))} != Progress Tracker {sorted(progress_mg[u])}')

# Math Summative shell + deterministic workspace-choice checks.
allowed={'q-compact','q-standard','q-large','q-xlarge'}
rank={'q-compact':0,'q-standard':1,'q-large':2,'q-xlarge':3}
compact_patterns=(
    re.compile(r'\bfind\s+\$?f\s*\(',re.I),
    re.compile(r'^rewrite\b',re.I),
    re.compile(r'^determine whether\b.*\bequivalent\b',re.I),
    re.compile(r'^solve\b.*\bcheck\b',re.I),
    re.compile(r'\bidentify the error\b.*\bcorrect\b',re.I),
    re.compile(r'^write one expression equivalent\b',re.I),
)

def workspace_signal(prompt):
    text=re.sub(r'\s+',' ',prompt.get_text(' ',strip=True)).strip().lower()
    has_rep=bool(prompt.find(['img','svg','table','canvas']))
    if len(text)<=210 and not has_rep and any(rx.search(text) for rx in compact_patterns):
        return 'compact'
    rep_reason=has_rep and any(w in text for w in ('write an equation','classify','justify','explain','cite','evidence'))
    create_combo=('create' in text and 'table' in text and ('describe' in text or 'context' in text) and 'explain' in text)
    claim_combo=('student claims' in text and ('evaluate' in text or 'critique' in text) and 'evidence' in text)
    verify_combo=('verify the result in the original relationship' in text)
    if rep_reason or create_combo or claim_combo or verify_combo:
        return 'large'
    return None

for p in root.rglob('*summative_assessment.html'):
    s=BeautifulSoup(p.read_text(encoding='utf-8'),'html.parser')
    qs=s.select('.assessment-question')
    if not qs: continue
    sizes=[]
    for i,q in enumerate(qs,1):
        cls=set(q.get('class') or [])
        chosen=list(cls & allowed)
        check(len(chosen)==1,f'{p}: Q{i} missing/excess approved q-* size class')
        prompt=q.select_one('.question-prompt')
        if not prompt: continue
        for fig in prompt.find_all('figure'):
            if fig.find('img'):
                check('figure-block' in (fig.get('class') or []),f'{p}: Q{i} image figure missing figure-block')
                check('question-graph' in (fig.find('img').get('class') or []),f'{p}: Q{i} image missing question-graph')
        for table in prompt.find_all('table'):
            check(bool(set(table.get('class') or []) & {'data-table','values'}),f'{p}: Q{i} bare/unstyled table')
        check(not prompt.find('figcaption'),f'{p}: Q{i} descriptive figcaption')
        if chosen:
            actual=chosen[0]; sizes.append(actual)
            signal=workspace_signal(prompt)
            if signal=='compact' and actual!='q-compact':
                override=(q.get('data-workspace-override') or '').strip()
                check(bool(override),f'{p}: Q{i} is an obvious compact-response item but uses {actual} without data-workspace-override')
            elif signal=='large':
                check(rank[actual]>=rank['q-large'],f'{p}: Q{i} workspace too small for a representation/reasoning-heavy response: got {actual}')
    if sizes:
        standard_share=sizes.count('q-standard')/len(sizes)
        if standard_share>=0.50:
            warnings.append(f'{p}: {sizes.count("q-standard")}/{len(sizes)} questions are q-standard; confirm this is intentional after deterministic sizing')

print(f'PRACT_TO_SUM_CHECKS={checks}')
print(f'ERRORS={len(errors)}')
print(f'WARNINGS={len(warnings)}')
for e in errors: print('ERROR:',e)
for w in warnings: print('WARNING:',w)
sys.exit(1 if errors else 0)
