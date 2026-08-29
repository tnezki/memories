#!/usr/bin/env python3
from pathlib import Path
from bs4 import BeautifulSoup
import re, sys
root=Path(sys.argv[1] if len(sys.argv)>1 else '.').resolve()
errors=[]; checks=0; warnings=[]
allowed={'q-compact','q-standard','q-large','q-xlarge'}
bare={'compact','standard','large','xlarge'}
rank={'q-compact':0,'q-standard':1,'q-large':2,'q-xlarge':3}

def check(c,m):
    global checks
    checks+=1
    if not c: errors.append(m)

# Raw-byte row-break corruption is a hard error.
bad_row=re.compile(r'(?<!\\)\\([xyz])(?=[\s+\-=,;:&<>\)\]\}])')
for p in root.rglob('*.html'):
    raw=p.read_text(encoding='utf-8',errors='replace')
    hits=list(bad_row.finditer(raw))
    check(not hits, f'{p}: malformed MathJax row break(s): '+', '.join('\\'+h.group(1) for h in hits[:8])+(f' ... ({len(hits)} total)' if len(hits)>8 else ''))


# Stable Exit shell contract.
for p in root.rglob('exit_*.html'):
    s=BeautifulSoup(p.read_text(encoding='utf-8',errors='replace'),'html.parser')
    idx=s.select_one('section.exit-index')
    check(bool(idx), f'{p}: missing .exit-index')
    if idx:
        check(bool(idx.select_one('header.index-head')), f'{p}: Exit index missing header.index-head')
        check(bool(idx.select_one('.index-kicker')), f'{p}: Exit index missing .index-kicker')
        grid=idx.select_one('.index-grid')
        check(bool(grid), f'{p}: Exit index missing .index-grid')
        if grid:
            rows=grid.select(':scope > .index-row')
            check(bool(rows), f'{p}: Exit index has no .index-row children')
            for j,row in enumerate(rows,1):
                check(bool(row.select_one('.index-section .index-number')), f'{p}: index row {j} missing .index-number')
                check(bool(row.select_one('.index-section .index-title')), f'{p}: index row {j} missing .index-title')
                links=row.select('.index-links .index-link')
                check(len(links)==3, f'{p}: index row {j} must have exactly 3 .index-link anchors')
    tickets=s.select('section.exit-ticket')
    check(bool(tickets), f'{p}: no .exit-ticket sections')
    for j,ticket in enumerate(tickets,1):
        check(bool(ticket.select_one('.ticket-head .ticket-kicker')), f'{p}: ticket {j} missing .ticket-kicker')
        check(bool(ticket.select_one('.ticket-head .ticket-title')), f'{p}: ticket {j} missing .ticket-title')
        check(bool(ticket.select_one('.ticket-head .ticket-meta')), f'{p}: ticket {j} missing .ticket-meta')
        for img in ticket.find_all('img'):
            check('graph-img' in (img.get('class') or []), f'{p}: ticket {j} image must use graph-img')
        for table in ticket.find_all('table'):
            if 'question-grid' in (table.get('class') or []):
                continue
            check('data-mini' in (table.get('class') or []), f'{p}: ticket {j} data table must use data-mini')


# Tracker shell and exact-I-can rows.
for p in root.rglob('unit_*_progress.html'):
    s=BeautifulSoup(p.read_text(encoding='utf-8'),'html.parser')
    goals=s.select('.goal-card[data-mastery-goal]')
    check(bool(goals),f'{p}: missing goal cards')
    for g in goals:
        gid=g.get('data-mastery-goal','')
        rows=g.select('.ican-list .ican')
        check(bool(rows),f'{p}: {gid} has no .ican rows')
        for i,row in enumerate(rows,1):
            t=re.sub(r'^[\s□☐☑✓✔•-]+','',row.get_text(' ',strip=True)).strip()
            check(bool(re.match(r'^I\s+can\b',t,re.I)),f'{p}: {gid} row {i} is not an explicit I-can: {t[:120]!r}')



# Progress Tracker DOM/CSS contract.
for p in root.rglob('unit_*_progress.html'):
    s=BeautifulSoup(p.read_text(encoding='utf-8'),'html.parser')
    for j,row in enumerate(s.select('.ican-list .ican'),1):
        checkel=row.select_one(':scope > .check')
        txt=row.select_one(':scope > .ican-text')
        check(bool(checkel),f'{p}: I-can row {j} missing direct .check child')
        check(bool(txt),f'{p}: I-can row {j} missing direct .ican-text child')
        if checkel:
            check(not checkel.get_text(strip=True),f'{p}: I-can row {j} .check must be empty')
        if txt:
            check(bool(re.match(r'^I\s+can\b',txt.get_text(' ',strip=True),re.I)),
                  f'{p}: I-can row {j} .ican-text must begin with I can')
    choices=s.select('.status-row .status-choice')
    check(len(choices)==4,f'{p}: expected 4 .status-choice items, got {len(choices)}')
    for j,c in enumerate(choices,1):
        check(not re.search(r'[□☐☑✓✔]',c.get_text()),
              f'{p}: status choice {j} contains checkbox glyph but CSS supplies it')


# Locked Review study-guide shell.
for p in root.rglob('review_*.html'):
    if '_practice' in p.stem.lower() or not re.fullmatch(r'review_\d+',p.stem,re.I):
        continue
    s=BeautifulSoup(p.read_text(encoding='utf-8'),'html.parser')
    required_ids=('glance','vocabulary','structures','dok','final-check')
    for rid in required_ids:
        check(bool(s.select_one(f'section#{rid}.review-panel')),
              f'{p}: Review shell missing #{rid}.review-panel')
    navtexts=[re.sub(r'\s+',' ',a.get_text(' ',strip=True)).strip() for a in s.select('nav a')]
    for label in ('At a Glance','Vocabulary','Rules & Structures','DOK Perspective','Final Check','Practice Problems'):
        check(label in navtexts,f'{p}: Review nav missing {label!r}')
    check(not any(re.fullmatch(r'MG\s*\d+',x,re.I) for x in navtexts),
          f'{p}: raw MG-number navigation is not allowed')
    focus=s.select('section.section-review[data-mastery-goal]')
    for sec in focus:
        h2=sec.find('h2')
        title=re.sub(r'\s+',' ',h2.get_text(' ',strip=True)).strip() if h2 else ''
        check(bool(title),f'{p}: Mastery focus missing visible heading')
        check(len(title.split())<=10,
              f'{p}: Mastery focus heading must be concise, not raw Goal sentence: {title!r}')
        check(not re.match(r'^MG\s*\d+\b',title,re.I),
              f'{p}: Mastery focus heading may not be an MG number: {title!r}')


# Unit Review is current-unit Mastery preparation, not the Retrieval stage.
progress_mg={}
for p in root.rglob('unit_*_progress.html'):
    m=re.search(r'unit_(\d+)_progress\.html$',p.name,re.I)
    if not m: continue
    u=m.group(1); s=BeautifulSoup(p.read_text(encoding='utf-8'),'html.parser')
    progress_mg[u]={g.get('data-mastery-goal','').strip() for g in s.select('.goal-card[data-mastery-goal]') if g.get('data-mastery-goal')}

for p in root.rglob('review_*.html'):
    if '_practice' in p.stem.lower() or not re.fullmatch(r'review_\d+',p.stem,re.I):
        continue
    u=re.search(r'(\d+)$',p.stem).group(1)
    s=BeautifulSoup(p.read_text(encoding='utf-8'),'html.parser'); txt=s.get_text(' ',strip=True)
    h1=s.find('h1'); htxt=h1.get_text(' ',strip=True) if h1 else ''
    check(bool(re.search(rf'\bUnit\s+{re.escape(u)}\s+Review\b',htxt,re.I)),f'{p}: title must be current Unit {u} Review: {htxt!r}')
    stale=set(re.findall(r'\bUnit\s+(\d+)\b',txt,re.I))-{u}
    check(not stale,f'{p}: prior/source Unit labels leaked into visible Review: {sorted(stale)}')
    sections=s.select('.section-review[data-mastery-goal]')
    check(bool(sections),f'{p}: missing Mastery Goal review sections')
    mids=[x.get('data-mastery-goal','').strip() for x in sections]
    for gid in mids: check(gid.startswith(f'U{u}-MG'),f'{p}: wrong-unit/invalid Mastery Goal {gid}')
    if u in progress_mg and progress_mg[u]:
        check(set(mids)==progress_mg[u],f'{p}: Review Mastery Goals do not match Progress Tracker')

for p in root.rglob('review_*_practice.html'):
    m=re.fullmatch(r'review_(\d+)_practice',p.stem,re.I)
    if not m: continue
    u=m.group(1); s=BeautifulSoup(p.read_text(encoding='utf-8'),'html.parser'); txt=s.get_text(' ',strip=True)
    stale=set(re.findall(r'\bUnit\s+(\d+)\b',txt,re.I))-{u}
    check(not stale,f'{p}: prior/source Unit labels leaked into visible Review Practice: {sorted(stale)}')
    sections=s.select('section[data-mastery-goal]')
    check(bool(sections),f'{p}: missing Mastery Goal practice sections')
    mids=[]
    for sec in sections:
        gid=(sec.get('data-mastery-goal') or '').strip(); mids.append(gid)
        check(gid.startswith(f'U{u}-MG'),f'{p}: wrong-unit/invalid Mastery Goal {gid}')
        check(len(sec.select('.problem'))==4,f'{p}: {gid} must contain exactly 4 problems')
    if u in progress_mg and progress_mg[u]:
        check(set(mids)==progress_mg[u],f'{p}: Review Practice Mastery Goals do not match Progress Tracker')

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

for p in root.rglob('*.html'):
    s=BeautifulSoup(p.read_text(encoding='utf-8'),'html.parser')
    qs=s.select('.assessment-question')
    if not qs: continue
    sizes=[]
    for i,q in enumerate(qs,1):
        cls=set(q.get('class') or [])
        chosen=list(cls & allowed)
        check(len(chosen)==1, f'{p}: question {i} missing/excess q-* size class: {sorted(cls)}')
        check(not (cls & bare), f'{p}: question {i} uses bare size class: {sorted(cls & bare)}')
        prompt=q.select_one('.question-prompt')
        if prompt:
            for fig in prompt.find_all('figure'):
                if fig.find('img'):
                    check('figure-block' in (fig.get('class') or []), f'{p}: question {i} image figure missing figure-block')
                    img=fig.find('img')
                    check('question-graph' in (img.get('class') or []), f'{p}: question {i} image missing question-graph')
            for table in prompt.find_all('table'):
                tc=set(table.get('class') or [])
                check(bool(tc & {'data-table','values'}), f'{p}: question {i} has unstyled/bare data table')
            check(not prompt.find('figcaption'), f'{p}: question {i} has descriptive figcaption')
            if chosen:
                actual=chosen[0]; sizes.append(actual); signal=workspace_signal(prompt)
                if signal=='compact' and actual!='q-compact':
                    check(bool((q.get('data-workspace-override') or '').strip()), f'{p}: question {i} obvious compact item uses {actual} without data-workspace-override')
                elif signal=='large':
                    check(rank[actual]>=rank['q-large'], f'{p}: question {i} workspace too small for a representation/reasoning-heavy response: got {actual}')
    if sizes and sizes.count('q-standard')/len(sizes)>=0.50:
        warnings.append(f'{p}: {sizes.count("q-standard")}/{len(sizes)} questions are q-standard; confirm intentional sizing')

print(f'RECURRING_SHELL_CHECKS={checks}')
print(f'ERRORS={len(errors)}')
print(f'WARNINGS={len(warnings)}')
for e in errors: print('ERROR:',e)
for w in warnings: print('WARNING:',w)
sys.exit(1 if errors else 0)
