#!/usr/bin/env python3
from __future__ import annotations
import argparse, re
from pathlib import Path
from bs4 import BeautifulSoup
CHECK_GLYPHS="□☐☑✓✔"
def clean_leading_check(text:str)->str: return re.sub(rf"^[\s{re.escape(CHECK_GLYPHS)}]+","",text or "").strip()
def normalize(path:Path):
    raw=path.read_text(encoding="utf-8",errors="replace"); soup=BeautifulSoup(raw,"html.parser")
    for row in soup.select(".ican-list .ican"):
        text=clean_leading_check(row.get_text(" ",strip=True)); row.clear()
        check=soup.new_tag("span",attrs={"class":"check","aria-hidden":"true"}); txt=soup.new_tag("span",attrs={"class":"ican-text"}); txt.string=text; row.append(check); row.append(txt)
    for choice in soup.select(".status-row .status-choice"):
        text=clean_leading_check(choice.get_text(" ",strip=True)); choice.clear(); choice.string=text
    path.write_text(str(soup),encoding="utf-8")
def audit(path:Path):
    errors=[]; soup=BeautifulSoup(path.read_text(encoding="utf-8",errors="replace"),"html.parser")
    for i,row in enumerate(soup.select(".ican-list .ican"),1):
        children=[c for c in row.find_all(recursive=False)]; check=row.select_one(":scope > .check"); text=row.select_one(":scope > .ican-text")
        if len(children)!=2 or not check or not text: errors.append(f"I-can row {i} must have exactly .check + .ican-text"); continue
        if check.get_text(strip=True): errors.append(f"I-can row {i} .check must be empty")
        if not re.match(r"^I\s+can\b",text.get_text(" ",strip=True),re.I): errors.append(f"I-can row {i} text must begin with 'I can'")
    choices=soup.select(".status-row .status-choice")
    if len(choices)!=4: errors.append(f"Expected 4 status choices, found {len(choices)}")
    for c in choices:
        if re.search(r"[□☐☑✓✔]",c.get_text()): errors.append("Status choice contains checkbox glyph even though CSS supplies it")
    return errors
def main():
    ap=argparse.ArgumentParser(); ap.add_argument("root"); args=ap.parse_args(); root=Path(args.root); files=list(root.rglob("unit_*_progress.html"))
    if not files: raise SystemExit("No Progress Tracker HTML found.")
    all_errors=[]
    for p in files:
        normalize(p); all_errors += [f"{p}: {e}" for e in audit(p)]
    if all_errors: print("\n".join("ERROR: "+e for e in all_errors)); raise SystemExit(1)
    print("Progress Tracker shell normalizer: PASS")
if __name__=="__main__": main()
