#!/usr/bin/env python3
"""Fast deterministic mechanical QA for District Resource Builder responses."""
from __future__ import annotations
import argparse, hashlib, json, re
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

VERSION = "district-resource-mechanical-qa/1.0"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class RefParser(HTMLParser):
    def __init__(self):
        super().__init__(); self.refs=[]; self.style_tags=0
    def handle_starttag(self, tag, attrs):
        d = dict(attrs)
        if tag.lower() == "style": self.style_tags += 1
        for key in ("href", "src"):
            if d.get(key): self.refs.append(d[key])


def expected_exists(response: Path, rel: str) -> tuple[bool, list[str]]:
    if "*" in rel:
        matches = sorted(p.relative_to(response).as_posix() for p in response.glob(rel))
        return bool(matches), matches
    p = response / rel
    return p.exists(), [rel] if p.exists() else []


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--request-root", default=".")
    ap.add_argument("--response", required=True)
    ap.add_argument("--out", default="")
    args = ap.parse_args()
    root = Path(args.request_root).resolve()
    response = Path(args.response).resolve()
    out = Path(args.out).resolve() if args.out else response / "data/mechanical_qa.json"
    request = json.loads((root / "request.json").read_text(encoding="utf-8"))
    checks = {}; failures = []

    required = [p for p in ((request.get("resolved_outputs") or {}).get("required_files") or []) if p != "data/qa.json"]
    required.extend(["CLICK_ME.html", "assets/dashboard_styles.css", "assets/resource_styles.css", "data/request.json"])
    required = sorted(set(required))
    missing=[]; resolved={}
    for rel in required:
        ok, matches = expected_exists(response, rel)
        resolved[rel] = matches
        if not ok: missing.append(rel)
    checks["required_files"] = {"status":"PASS" if not missing else "FAIL", "missing":missing, "resolved":resolved}
    if missing: failures.append("required_files")

    for key in ("dashboard", "resource"):
        meta=(request.get("locked_styles") or {}).get(key) or {}
        p=response / str(meta.get("response_path") or "")
        actual=sha256(p) if p.exists() else None
        expected=meta.get("sha256")
        ok=bool(expected and actual == expected)
        checks[f"locked_style_{key}"]={"status":"PASS" if ok else "FAIL","expected":expected,"actual":actual}
        if not ok: failures.append(f"locked_style_{key}")

    broken=[]; inline_styles=[]; external=[]
    for h in sorted(response.rglob("*.html")):
        parser=RefParser()
        try: parser.feed(h.read_text(encoding="utf-8",errors="replace"))
        except Exception as exc:
            broken.append({"file":h.relative_to(response).as_posix(),"ref":"<parse>","error":str(exc)}); continue
        if parser.style_tags: inline_styles.append(h.relative_to(response).as_posix())
        for ref in parser.refs:
            if ref.startswith(("#","mailto:","tel:","javascript:","data:")): continue
            u=urlparse(ref)
            if u.scheme in ("http","https"):
                external.append({"file":h.relative_to(response).as_posix(),"ref":ref}); continue
            target=(h.parent / u.path).resolve()
            try: target.relative_to(response)
            except ValueError:
                broken.append({"file":h.relative_to(response).as_posix(),"ref":ref,"error":"escapes response root"}); continue
            if u.path and not target.exists(): broken.append({"file":h.relative_to(response).as_posix(),"ref":ref,"error":"missing"})
    checks["local_links"]={"status":"PASS" if not broken else "FAIL","broken":broken,"external_count":len(external)}
    if broken: failures.append("local_links")
    checks["page_local_style_tags"]={"status":"PASS" if not inline_styles else "FAIL","files":inline_styles}
    if inline_styles: failures.append("page_local_style_tags")

    pdfs=[]; bad_pdfs=[]
    for p in sorted(response.rglob("*.pdf")):
        ok = p.stat().st_size > 100 and p.read_bytes()[:4] == b"%PDF"
        row={"path":p.relative_to(response).as_posix(),"size_bytes":p.stat().st_size,"signature_ok":ok}
        pdfs.append(row)
        if not ok: bad_pdfs.append(row["path"])
    checks["pdf_integrity"]={"status":"PASS" if not bad_pdfs else "FAIL","files":pdfs,"bad":bad_pdfs}
    if bad_pdfs: failures.append("pdf_integrity")

    graph_dir=response / "assets/graphs"
    graphs=sorted(p.relative_to(response).as_posix() for p in graph_dir.rglob("*") if p.is_file()) if graph_dir.exists() else []
    prov=response / "data/graph_provenance.json"
    graph_ok=True; detail={"graph_count":len(graphs),"assets":graphs,"provenance_present":prov.exists()}
    if graphs:
        graph_ok=prov.exists()
        if prov.exists():
            try:
                pdata=json.loads(prov.read_text(encoding="utf-8")); listed={str(x.get("asset")) for x in (pdata.get("assets") or []) if isinstance(x,dict)}
                missing_prov=[g for g in graphs if g not in listed]
                detail["missing_provenance"]=missing_prov
                graph_ok=graph_ok and not missing_prov
            except Exception as exc:
                detail["error"]=str(exc); graph_ok=False
    checks["graph_provenance"]={"status":"PASS" if graph_ok else "FAIL",**detail}
    if not graph_ok: failures.append("graph_provenance")

    payload={"version":VERSION,"overall_status":"PASS" if not failures else "FAIL","checks":checks,"failures":failures}
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(payload,indent=2),encoding="utf-8")
    print(payload["overall_status"],VERSION,out)
    return 0 if not failures else 2


if __name__ == "__main__":
    raise SystemExit(main())
