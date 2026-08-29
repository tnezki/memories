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


# Unresolved renderer/template expressions are never valid final HTML.
for p in root.rglob('*.html'):
    raw=p.read_text(encoding='utf-8',errors='replace')
    low=raw.lower()
    check('join(bubble_rows)' not in low and '{{ bubble_rows' not in low and '{"".join(bubble_rows)' not in low,
          f'{p}: unresolved Physics bubble-row template expression leaked into final HTML')

# Stable Exit projector + four-version print/collect shell contract.
for p in root.rglob('exit_*.html'):
    s=BeautifulSoup(p.read_text(encoding='utf-8',errors='replace'),'html.parser')
    raw=p.read_text(encoding='utf-8',errors='replace')
    check('function printExitTicket' in raw or 'printExitTicket=' in raw, f'{p}: missing universal printExitTicket() function')
    check('print-active' in raw, f'{p}: Exit HTML must activate the matching .print-active packet')
    check('document.body.dataset.printTarget' not in raw, f'{p}: obsolete body.dataset.printTarget print mechanism is prohibited')
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

    tickets=s.select('section.exit-ticket.project-only')
    check(bool(tickets), f'{p}: no .exit-ticket.project-only sections')
    print_packets=s.select('section.exit-print.print-only')
    check(len(print_packets)==len(tickets), f'{p}: projector/print ticket count mismatch ({len(tickets)} vs {len(print_packets)})')
    print_by_source={x.get('data-source-ticket',''):x for x in print_packets}

    for j,ticket in enumerate(tickets,1):
        tid=ticket.get('id','')
        check(bool(tid), f'{p}: ticket {j} missing id')
        check(bool(ticket.select_one('.ticket-head .ticket-kicker')), f'{p}: ticket {j} missing .ticket-kicker')
        check(bool(ticket.select_one('.ticket-head .ticket-title')), f'{p}: ticket {j} missing .ticket-title')
        check(bool(ticket.select_one('.ticket-head .ticket-meta')), f'{p}: ticket {j} missing .ticket-meta')
        check(bool(ticket.select_one('.ticket-print-button')), f'{p}: ticket {j} missing .ticket-print-button')
        qgrid=ticket.select_one('.question-grid')
        check(bool(qgrid), f'{p}: ticket {j} missing .question-grid')
        pqs=qgrid.select(':scope > .qtext, :scope > article, :scope > .question-cell') if qgrid else []
        check(len(pqs)==4, f'{p}: ticket {j} projector must contain exactly 4 questions, got {len(pqs)}')
        projector_ids=[]
        for q in pqs:
            bid=q.get('data-bank-id','')
            check(bool(bid), f'{p}: ticket {j} projector question missing data-bank-id')
            projector_ids.append(bid)
            for img in q.find_all('img'):
                check('graph-img' in (img.get('class') or []), f'{p}: ticket {j} image must use graph-img')
            for table in q.find_all('table'):
                check('data-mini' in (table.get('class') or []), f'{p}: ticket {j} data table must use data-mini')

        packet=print_by_source.get(tid)
        check(bool(packet), f'{p}: ticket {j} ({tid}) missing matching .exit-print packet')
        if not packet:
            continue
        versions=packet.select(':scope > .exit-print-version')
        check(len(versions)==4, f'{p}: ticket {j} print packet must contain exactly 4 versions, got {len(versions)}')
        version_nums=[v.get('data-version','') for v in versions]
        check(version_nums==['1','2','3','4'], f'{p}: ticket {j} versions must be ordered 1,2,3,4; got {version_nums}')
        role_positions={'anchor':[], 'parallel-a':[], 'parallel-b':[], 'variation':[]}
        role_sources={}
        for vi,v in enumerate(versions,1):
            pages=v.select(':scope > .exit-print-page')
            check(len(pages)==2, f'{p}: ticket {j} V{vi} must contain exactly 2 print pages, got {len(pages)}')
            allq=[]
            for pi,page in enumerate(pages,1):
                grid=page.select_one('.print-question-grid')
                check(bool(grid), f'{p}: ticket {j} V{vi} page {pi} missing .print-question-grid')
                qs2=grid.select(':scope > .qtext, :scope > article, :scope > .question-cell') if grid else []
                check(len(qs2)==2, f'{p}: ticket {j} V{vi} page {pi} must contain exactly 2 questions, got {len(qs2)}')
                allq.extend(qs2)
            check(len(allq)==4, f'{p}: ticket {j} V{vi} must contain 4 print questions total')
            for pos,q in enumerate(allq,1):
                role=q.get('data-evidence-role','')
                srcid=q.get('data-source-bank-id','')
                check(role in role_positions, f'{p}: ticket {j} V{vi} Q{pos} invalid/missing data-evidence-role={role!r}')
                check(bool(srcid), f'{p}: ticket {j} V{vi} Q{pos} missing data-source-bank-id')
                if role in role_positions:
                    role_positions[role].append(pos)
                    if role in role_sources:
                        check(role_sources[role]==srcid, f'{p}: ticket {j} role {role} changed source Bank ID across versions')
                    else:
                        role_sources[role]=srcid
                if vi==1:
                    check(q.get('data-bank-id','')==srcid and srcid in projector_ids, f'{p}: ticket {j} V1 Q{pos} must preserve exact projector/Bank ID')
                else:
                    if role!='anchor':
                        check(not q.get('data-bank-id'), f'{p}: ticket {j} V{vi} {role} must not claim canonical data-bank-id for a newly authored parallel/variation')
                for img in q.find_all('img'):
                    check('graph-img' in (img.get('class') or []), f'{p}: ticket {j} V{vi} print image must use graph-img')
                for table in q.find_all('table'):
                    check('data-mini' in (table.get('class') or []), f'{p}: ticket {j} V{vi} print data table must use data-mini')
        for role,positions in role_positions.items():
            check(sorted(positions)==[1,2,3,4], f'{p}: ticket {j} role {role} must appear once in each display position; got {positions}')
        check(role_sources.get('anchor')==(projector_ids[0] if projector_ids else None), f'{p}: ticket {j} Anchor must source projector/Bank Q1')
        check(role_sources.get('parallel-a')==(projector_ids[1] if len(projector_ids)>1 else None), f'{p}: ticket {j} Parallel A must source projector/Bank Q2')
        check(role_sources.get('parallel-b')==(projector_ids[2] if len(projector_ids)>2 else None), f'{p}: ticket {j} Parallel B must source projector/Bank Q3')
        check(role_sources.get('variation')==(projector_ids[3] if len(projector_ids)>3 else None), f'{p}: ticket {j} Variation must source projector/Bank Q4')


# Physical two-page Progress Tracker shell.
for p in root.rglob('unit_*_progress.html'):
    s=BeautifulSoup(p.read_text(encoding='utf-8'),'html.parser')
    pages=s.select('section.tracker-page')
    check(len(pages)==2,f'{p}: standard Progress Tracker must contain exactly 2 .tracker-page sections; got {len(pages)}')
    if len(pages)==2:
        check('page-one' in (pages[0].get('class') or []),f'{p}: first tracker page missing .page-one')
        check('page-two' in (pages[1].get('class') or []),f'{p}: second tracker page missing .page-two')
        for hook in ('page-header','identity'):
            check(bool(pages[0].select_one('.'+hook)),f'{p}: page 1 missing .{hook}')
        for hook in ('essential','status-key','owner-note'):
            check(bool(pages[0].select_one('.'+hook)),f'{p}: page 1 missing .{hook}')
        check(bool(pages[1].select_one('.reflection-box')),f'{p}: page 2 missing .reflection-box')
    goals=s.select('.goal-card[data-mastery-goal]')
    if len(goals)==4 and len(pages)==2:
        check(len(pages[0].select('.goal-card[data-mastery-goal]'))==2 and len(pages[1].select('.goal-card[data-mastery-goal]'))==2,
              f'{p}: four-goal physical tracker must place two goals on each page')
    for i,g in enumerate(goals,1):
        for hook in ('goal-head','goal-grid','ican-list','evidence-table','next-move'):
            check(bool(g.select_one('.'+hook)),f'{p}: goal card {i} missing canonical .{hook}')

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


# Physics selected-response answer sheet must be fully materialized.
for p in root.rglob('*summative_assessment.html'):
    s=BeautifulSoup(p.read_text(encoding='utf-8',errors='replace'),'html.parser')
    sheet=s.select_one('section.page.answersheet')
    fr=s.select_one('section.fr-sheet-page')
    if sheet and fr:
        rows=sheet.select('.sheetgrid .bubble-row')
        check(len(rows)==16,f'{p}: Physics answer sheet must contain exactly 16 materialized .bubble-row nodes; got {len(rows)}')
        nums=[]
        for i,row in enumerate(rows,1):
            txt=row.get_text(' ',strip=True)
            m=re.search(r'\b(\d{1,2})\b',txt)
            nums.append(int(m.group(1)) if m else None)
            choices=row.select('.bubble-choice')
            check(len(choices)==4,f'{p}: bubble row {i} must contain four .bubble-choice nodes')
            for c in choices:
                check(bool(c.select_one('.bubble')),f'{p}: bubble row {i} choice missing separate .bubble element')
        check(nums==list(range(1,17)),f'{p}: answer-sheet rows must be numbered 1..16; got {nums}')

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
