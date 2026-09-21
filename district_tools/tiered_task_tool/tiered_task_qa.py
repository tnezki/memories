#!/usr/bin/env python3
"""Fast deterministic mechanical QA for District Tiered Task responses."""
from __future__ import annotations
import argparse, hashlib, json, re
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

VERSION = "district-tiered-task-mechanical-qa/1.0"
REQUIRED = [
    "CLICK_ME.html",
    "assets/task_card_styles.css",
    "assets/guide_styles.css",
    "student/task_card.html",
    "student/task_card.pdf",
    "teacher/teacher_guide.html",
    "teacher/teacher_guide.pdf",
    "data/request.json",
]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

class Parser(HTMLParser):
    def __init__(self):
        super().__init__(); self.refs=[]; self.styles=0
    def handle_starttag(self, tag, attrs):
        d=dict(attrs)
        if tag.lower()=="style": self.styles += 1
        for k in ("href","src"):
            if d.get(k): self.refs.append(d[k])


def pdf_page_count(path: Path):
    try:
        from pypdf import PdfReader
        return len(PdfReader(str(path)).pages)
    except Exception:
        try:
            data=path.read_bytes()
            return len(re.findall(rb"/Type\s*/Page\b", data)) or None
        except Exception:
            return None


def main() -> int:
    ap=argparse.ArgumentParser()
    ap.add_argument("--request-root",default=".")
    ap.add_argument("--response",required=True)
    ap.add_argument("--out",default="")
    args=ap.parse_args()
    root=Path(args.request_root).resolve(); response=Path(args.response).resolve()
    out=Path(args.out).resolve() if args.out else response/"data/mechanical_qa.json"
    request=json.loads((root/"request.json").read_text(encoding="utf-8"))
    checks={}; failures=[]

    missing=[p for p in REQUIRED if not (response/p).exists()]
    checks["required_files"]={"status":"PASS" if not missing else "FAIL","missing":missing}
    if missing: failures.append("required_files")

    for key in ("task_card","guide"):
        meta=(request.get("locked_styles") or {}).get(key) or {}
        p=response/str(meta.get("response_path") or "")
        expected=meta.get("sha256"); actual=sha256(p) if p.exists() else None
        ok=bool(expected and expected==actual)
        checks[f"locked_style_{key}"]={"status":"PASS" if ok else "FAIL","expected":expected,"actual":actual}
        if not ok: failures.append(f"locked_style_{key}")

    broken=[]; inline=[]; external=[]
    response_resolved=response.resolve()
    for h in sorted(response.rglob("*.html")):
        parser=Parser()
        try: parser.feed(h.read_text(encoding="utf-8",errors="replace"))
        except Exception as exc:
            broken.append({"file":h.relative_to(response).as_posix(),"ref":"<parse>","error":str(exc)}); continue
        if parser.styles: inline.append(h.relative_to(response).as_posix())
        for ref in parser.refs:
            ref=ref.strip()
            if not ref or ref.startswith(("#","mailto:","tel:","javascript:","data:")): continue
            u=urlparse(ref)
            if u.scheme in ("http","https"):
                external.append({"file":h.relative_to(response).as_posix(),"ref":ref}); continue
            target=(h.parent/u.path).resolve()
            try: target.relative_to(response_resolved)
            except ValueError:
                broken.append({"file":h.relative_to(response).as_posix(),"ref":ref,"error":"outside response"}); continue
            if not target.exists(): broken.append({"file":h.relative_to(response).as_posix(),"ref":ref,"error":"missing"})
    checks["links"]={"status":"PASS" if not broken else "FAIL","broken":broken,"external":external}
    if broken: failures.append("links")
    checks["inline_style_tags"]={"status":"PASS" if not inline else "FAIL","files":inline}
    if inline: failures.append("inline_style_tags")

    pdfs={}
    for rel in ("student/task_card.pdf","teacher/teacher_guide.pdf"):
        p=response/rel
        ok=p.exists() and p.stat().st_size>100 and p.read_bytes()[:4]==b"%PDF"
        pdfs[rel]={"open_signature":ok,"page_count":pdf_page_count(p) if ok else None}
        if not ok: failures.append(f"pdf:{rel}")
    student_pages=pdfs["student/task_card.pdf"]["page_count"]
    one_page = student_pages == 1 if student_pages is not None else False
    if not one_page: failures.append("student_task_card_page_count")
    checks["pdfs"]={"status":"PASS" if all(v["open_signature"] for v in pdfs.values()) and one_page else "FAIL","files":pdfs,"student_card_one_page":one_page}

    click=(response/"CLICK_ME.html").read_text(encoding="utf-8",errors="replace") if (response/"CLICK_ME.html").exists() else ""
    required_links=["student/task_card.pdf","student/task_card.html","teacher/teacher_guide.pdf","teacher/teacher_guide.html","data/qa.json"]
    absent=[x for x in required_links if x not in click]
    checks["click_me_links"]={"status":"PASS" if not absent else "FAIL","missing":absent}
    if absent: failures.append("click_me_links")

    result={"version":VERSION,"status":"PASS" if not failures else "FAIL","checks":checks,"failures":sorted(set(failures))}
    out.parent.mkdir(parents=True,exist_ok=True); out.write_text(json.dumps(result,indent=2),encoding="utf-8")
    print(json.dumps(result,indent=2))
    return 0 if not failures else 2

if __name__=="__main__":
    raise SystemExit(main())
