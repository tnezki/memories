#!/usr/bin/env python3
from __future__ import annotations
import argparse,re
from pathlib import Path
from bs4 import BeautifulSoup

def err(errors,msg): errors.append(msg)

def audit_main(p:Path,errors:list[str]):
    raw=p.read_text(encoding='utf-8',errors='replace')
    s=BeautifulSoup(raw,'html.parser')
    links=[x.get('href','') for x in s.find_all('link',rel=lambda v:v and 'stylesheet' in v)]
    if links!=['../../css/review.css']:
        err(errors,f'{p}: stylesheet contract must be exactly ../../css/review.css; got {links}')
    if not s.select_one('header.hero .hero-inner .jump-nav'):
        err(errors,f'{p}: missing canonical hero/jump-nav shell')
    for rid in ('glance','vocabulary','structures','dok','final-check'):
        if not s.select_one(f'section#{rid}.review-panel'):
            err(errors,f'{p}: missing #{rid}.review-panel')
    nav=[re.sub(r'\s+',' ',a.get_text(' ',strip=True)).strip() for a in s.select('nav.jump-nav a')]
    for label in ('At a Glance','Vocabulary','Rules & Structures','DOK Perspective','Final Check','Practice Problems'):
        if label not in nav: err(errors,f'{p}: nav missing {label!r}')
    if any(re.fullmatch(r'MG\s*\d+',x,re.I) for x in nav):
        err(errors,f'{p}: raw MG-number navigation is prohibited')
    if not s.select_one('a.floating-top[href="#top"]'):
        err(errors,f'{p}: missing floating Top control')
    focuses=s.select('section.section-review[data-mastery-goal]')
    if not focuses: err(errors,f'{p}: no mastery focus sections')
    for i,sec in enumerate(focuses,1):
        h=sec.find('h2'); title=re.sub(r'\s+',' ',h.get_text(' ',strip=True)).strip() if h else ''
        if not title: err(errors,f'{p}: focus {i} missing h2')
        if re.match(r'^MG\s*\d+\b',title,re.I): err(errors,f'{p}: focus {i} uses MG-number heading')
        if len(title.split())>10: err(errors,f'{p}: focus {i} heading too long/raw: {title!r}')
    body=re.sub(r'\s+',' ',s.get_text(' ',strip=True))
    m=re.search(r'Unit\s+(\d+)\s+Review',body,re.I)
    if m:
        u=m.group(1)
        # no Assigned-during wording or explicit source/review target unit labels
        if re.search(r'Assigned\s+during\s+Unit',body,re.I): err(errors,f'{p}: Assigned during Unit wording leaked')
        if re.search(r'(?:source|review target)\s+Unit\s+\d+',body,re.I): err(errors,f'{p}: historical/source Unit wording leaked')

def audit_practice(p:Path,errors:list[str]):
    s=BeautifulSoup(p.read_text(encoding='utf-8',errors='replace'),'html.parser')
    links=[x.get('href','') for x in s.find_all('link',rel=lambda v:v and 'stylesheet' in v)]
    if links!=['../../css/review_practice.css']:
        err(errors,f'{p}: stylesheet contract must be exactly ../../css/review_practice.css; got {links}')
    if not s.select('section.dok-section[data-mastery-goal]'):
        err(errors,f'{p}: practice sections missing data-mastery-goal')

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('root'); args=ap.parse_args(); root=Path(args.root)
    errors=[]
    mains=[]; practices=[]
    for p in root.rglob('review_*.html'):
        if '_practice' in p.stem.lower(): practices.append(p)
        elif re.fullmatch(r'review_\d+',p.stem,re.I): mains.append(p)
    for p in mains:audit_main(p,errors)
    for p in practices:audit_practice(p,errors)
    if not mains: errors.append('No main Review HTML found')
    if not practices: errors.append('No Review Practice HTML found')
    if errors:
        print('\n'.join('ERROR: '+x for x in errors)); raise SystemExit(1)
    print(f'Review shell contract: PASS ({len(mains)} main, {len(practices)} practice)')
if __name__=='__main__': main()
