#!/usr/bin/env python3
from __future__ import annotations
import argparse
import re
from pathlib import Path
from bs4 import BeautifulSoup

def ensure_stylesheet(soup, href, before=None):
    links = soup.find_all("link", rel=lambda v: v and "stylesheet" in v)
    for link in links:
        if link.get("href") == href:
            return
    tag = soup.new_tag("link", rel="stylesheet", href=href)
    if before is not None:
        before.insert_before(tag)
    elif soup.head:
        soup.head.append(tag)

def normalize_html(path: Path):
    raw = path.read_text(encoding="utf-8", errors="replace")

    # Remove accidental Markdown/language-label leakage before the HTML document.
    raw = re.sub(r"^\s*(?:```html\s*|html\s*)(?=(?:<!doctype\s+html\b|<html\b))",
                 "", raw, count=1, flags=re.I)

    name = path.name.lower()
    if "stations" not in name and "find_someone_who" not in name:
        path.write_text(raw, encoding="utf-8")
        return

    soup = BeautifulSoup(raw, "html.parser")

    # Teacher-approved Stations print shell: all printable pages live inside one `.wrap`.
    if "stations" in name and soup.body:
        wrap = soup.body.find("div", class_="wrap", recursive=False)
        if wrap is None:
            wrap = soup.new_tag("div", attrs={"class":"wrap"})
            for child in list(soup.body.contents):
                # Move substantive body children into the wrapper.
                if getattr(child, "name", None) is not None or str(child).strip():
                    wrap.append(child.extract())
            soup.body.append(wrap)

    links = soup.find_all("link", rel=lambda v: v and "stylesheet" in v)

    # Remove obsolete root-level Activity stylesheet hrefs.
    obsolete = {
        "../../css/activity_stations.css",
        "../../css/activity_find_someone_who.css",
    }
    for link in list(links):
        if link.get("href") in obsolete:
            link.decompose()

    # Always preserve the shared base stylesheet.
    first_style = soup.find("link", rel=lambda v: v and "stylesheet" in v)
    ensure_stylesheet(soup, "../../css/base.css", before=first_style)

    if "stations" in name:
        ensure_stylesheet(soup, "../../css/activities/activity_stations.css")
        # Stations CSS expects content-bearing image figures to use `.figure`.
        for fig in soup.find_all("figure"):
            if fig.find("img"):
                classes = [c for c in (fig.get("class") or []) if c != "graph-block"]
                if "figure" not in classes:
                    classes.append("figure")
                fig["class"] = classes

    if "find_someone_who" in name:
        ensure_stylesheet(soup, "../../css/activities/activity_find_someone_who.css")

    # Restore a doctype if BeautifulSoup serialization removed it.
    out = str(soup)
    if not re.match(r"(?is)^\s*<!doctype\s+html\b", out):
        out = "<!doctype html>" + out
    path.write_text(out, encoding="utf-8")

def audit(root: Path):
    errors=[]
    for p in root.rglob("*.html"):
        raw=p.read_text(encoding="utf-8",errors="replace")
        if not re.match(r"(?is)^\s*(?:<!doctype\s+html\b|<html\b)", raw):
            errors.append(f"{p}: visible token before HTML document")
        name=p.name.lower()
        if "stations" not in name and "find_someone_who" not in name:
            continue
        soup=BeautifulSoup(raw,"html.parser")
        hrefs=[x.get("href","") for x in soup.find_all("link",
                rel=lambda v: v and "stylesheet" in v)]
        if "../../css/base.css" not in hrefs:
            errors.append(f"{p}: missing ../../css/base.css")
        if "stations" in name:
            if "../../css/activities/activity_stations.css" not in hrefs:
                errors.append(f"{p}: wrong Stations stylesheet path")
            if "../../css/activity_stations.css" in hrefs:
                errors.append(f"{p}: obsolete Stations stylesheet path remains")

            wrap = soup.body.find("div", class_="wrap", recursive=False) if soup.body else None
            if wrap is None:
                errors.append(f"{p}: Stations body missing direct .wrap")
            else:
                pages = wrap.find_all("section", class_="page", recursive=False)
                qpages = [x for x in pages if "station-question-page" in (x.get("class") or [])]
                answer_pages = [x for x in pages if "station-answer-page" in (x.get("class") or [])]
                # Prompt/blank pairs must come first.
                first_answer = next((i for i,x in enumerate(pages) if "station-answer-page" in (x.get("class") or [])), len(pages))
                prompt_region = pages[:first_answer]
                if len(prompt_region) != 2 * len(qpages):
                    errors.append(f"{p}: prompt region must be station/blank pairs")
                for i in range(0,len(prompt_region),2):
                    if i >= len(prompt_region): break
                    q = prompt_region[i]
                    if "station-question-page" not in (q.get("class") or []):
                        errors.append(f"{p}: prompt pair {i//2+1} does not start with station question page")
                        continue
                    probs = q.select(":scope > .station-grid > .station-problem")
                    if len(probs) != 4:
                        errors.append(f"{p}: station prompt page must contain exactly 4 problems")
                    if q.select('.workspace, .work-space, .answer-space, textarea, input[type="text"]'):
                        errors.append(f"{p}: station prompt cards must not contain student workspace")
                    if i+1 >= len(prompt_region) or "station-blank-page" not in (prompt_region[i+1].get("class") or []):
                        errors.append(f"{p}: each station prompt page must be followed by one blank duplex page")
                    elif prompt_region[i+1].get_text(" ",strip=True):
                        errors.append(f"{p}: station blank duplex page must contain no visible text")

                # Solutions: exactly 2 pages per station, after all prompt pairs.
                sol_region = pages[first_answer:]
                if len(sol_region) != 2 * len(qpages):
                    errors.append(f"{p}: solution region must contain exactly two pages per station")
                for i in range(0,len(sol_region),2):
                    if i+1 >= len(sol_region): break
                    a1,a2=sol_region[i],sol_region[i+1]
                    if "station-solution-page-1" not in (a1.get("class") or []):
                        errors.append(f"{p}: solution block {i//2+1} missing page-1 class")
                    if "station-solution-page-2" not in (a2.get("class") or []):
                        errors.append(f"{p}: solution block {i//2+1} missing page-2 class")
                    # A blank page 2 is valid; a content page 2 is also valid.
                    if "solution-blank-page" in (a2.get("class") or []) and a2.get_text(" ",strip=True):
                        errors.append(f"{p}: blank solution page contains visible text")

            for fig in soup.find_all("figure"):
                if fig.find("img") and "figure" not in (fig.get("class") or []):
                    errors.append(f"{p}: Stations image figure missing .figure")
        if "find_someone_who" in name:
            if "../../css/activities/activity_find_someone_who.css" not in hrefs:
                errors.append(f"{p}: wrong Find Someone Who stylesheet path")
            if "../../css/activity_find_someone_who.css" in hrefs:
                errors.append(f"{p}: obsolete Find Someone Who stylesheet path remains")
    return errors

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("root")
    args=ap.parse_args()
    root=Path(args.root)
    for p in root.rglob("*.html"):
        normalize_html(p)
    errors=audit(root)
    if errors:
        print("\n".join("ERROR: "+e for e in errors))
        raise SystemExit(1)
    print("Activity shell normalizer: PASS")

if __name__=="__main__":
    main()
