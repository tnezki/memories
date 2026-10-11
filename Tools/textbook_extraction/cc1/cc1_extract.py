#!/usr/bin/env python3
"""Private, offline CC1 source-to-cards extractor. Standard library only.

Run with the local CC1 HTML captures (not a public repo).
This preserves the original textbook files untouched.
"""
import argparse
import datetime as dt
import hashlib
import html
from html.parser import HTMLParser
import json
import os
from pathlib import Path
import re
import shutil
import sys
from collections import Counter, defaultdict

VERSION = "1.0.0"
COURSE = "cc1"
LESSONS = {
    1: "1.1.1 1.1.2 1.1.3 1.1.4 1.1.5 1.2.1 1.2.2 1.2.3 1.2.4",
    2: "2.1.1 2.1.2 2.2.1 2.2.2 2.2.3 2.3.1 2.3.2 2.3.3 2.3.4",
    3: "3.1.1 3.1.2 3.1.3 3.1.4 3.1.5 3.1.6 3.2.1 3.2.2 3.2.3 3.2.4",
    4: "4.1.1 4.1.2 4.1.3 4.2.1 4.2.2 4.2.3 4.2.4",
    5: "5.1.1 5.1.2 5.1.3 5.1.4 5.2.1 5.2.2 5.3.1 5.3.2 5.3.3 5.3.4",
    6: "6.1.1 6.1.2 6.1.3 6.1.4 6.2.1 6.2.2 6.2.3 6.2.4 6.2.5",
    7: "7.1.1 7.1.2 7.1.3 7.2.1 7.2.2 7.2.3 7.2.4 7.3.1 7.3.2 7.3.3 7.3.4",
    8: "8.1.1 8.1.2 8.1.3 8.1.4 8.1.5 8.2.1 8.3.1 8.3.2 8.3.3",
    9: "9.1.1 9.1.2 9.2.1 9.2.2 9.2.3 9.2.4 9.3.1 9.3.2 9.3.3",
}
EXPECTED_PROBLEMS_RE = re.compile(r"^\d+-[\dA-Za-z]+$")
LESSON_FILENAME_RE = re.compile(r"Lesson (\d+(?:\.\d+){0,2}|\d+\.(?:opening|closure))\.html$", re.I)
SKIP_TAGS = {"script", "style", "noscript"}
VOID_TAGS = {"area","base","br","col","embed","hr","img","input","link","meta","param","source","track","wbr"}
BLOCK_TAGS = {"div","p","li","header","section","article","figure","table","h1","h2","h3","h4","ul","ol","blockquote"}

class Node:
    __slots__ = ("tag", "attrs", "children", "parent")
    def __init__(self, tag, attrs=None, parent=None):
        self.tag, self.attrs, self.children, self.parent = tag, dict(attrs or []), [], parent
    def attr(self, k, default=""):
        return self.attrs.get(k) or default
    def has_class(self, c):
        return c in self.attr("class").split()
    def walk(self):
        yield self
        for x in self.children:
            if isinstance(x, Node):
                yield from x.walk()
    def text(self):
        return "".join(x.text() if isinstance(x, Node) else x for x in self.children)

class DOM(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=False)
        self.root = Node("_root")
        self.stack = [self.root]
    def handle_starttag(self, tag, attrs):
        node = Node(tag, attrs, self.stack[-1])
        self.stack[-1].children.append(node)
        if tag not in VOID_TAGS:
            self.stack.append(node)
    def handle_startendtag(self, tag, attrs):
        node = Node(tag, attrs, self.stack[-1]); self.stack[-1].children.append(node)
    def handle_endtag(self, tag):
        for i in range(len(self.stack) - 1, 0, -1):
            if self.stack[i].tag == tag:
                self.stack = self.stack[:i]
                return
    def handle_data(self, data): self.stack[-1].children.append(data)
    def handle_entityref(self, name): self.stack[-1].children.append("&" + name + ";")
    def handle_charref(self, name): self.stack[-1].children.append("&#" + name + ";")

def serialize(n):
    if isinstance(n, str): return n
    if n.tag == "_root": return "".join(serialize(c) for c in n.children)
    pairs = "".join(f' {k}="{html.escape(str(v or ""), quote=True)}"' for k, v in n.attrs.items())
    opening = f"<{n.tag}{pairs}>"
    if n.tag in VOID_TAGS: return opening
    return opening + "".join(serialize(x) for x in n.children) + f"</{n.tag}>"

def plain(node):
    if isinstance(node, str): return html.unescape(node)
    if node.tag in SKIP_TAGS: return ""
    sep = "\n" if node.tag in BLOCK_TAGS else ""
    return sep + "".join(plain(c) for c in node.children) + sep

def cleantext(s): return re.sub(r"\s+", " ", s).strip()

def safe_slug(s): return re.sub(r"[^a-z0-9_-]+", "_", s.lower()).strip("_")

def sha(b): return hashlib.sha256(b).hexdigest()

def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

def find_first(root, pred):
    return next((x for x in root.walk() if pred(x)), None)

def source_name(path):
    m = LESSON_FILENAME_RE.search(path.name)
    if m:
        section = m.group(1)
        if re.fullmatch(r"\d+\.\d+\.\d+", section): return ("lesson", section)
        if section.endswith(".opening"): return ("opening", section.split(".")[0])
        if section.endswith(".closure"): return ("closure", section.split(".")[0])
    if re.search(r"Teacher Notes (\d+)\.opening\.html$",path.name,re.I):return ("teacher_opening", re.search(r"(\d+)\.opening",path.name).group(1))
    if re.search(r"Teacher Notes (\d+)\.closure\.html$",path.name,re.I):return ("teacher_closure", re.search(r"(\d+)\.closure",path.name).group(1))
    if path.parent.name == "ch02" and path.name == "intro.html":return ("opening", "2")
    if path.parent.name == "ch05" and path.name.endswith("Lesson 5.4.html"):return ("reflection", "5.4")
    if path.parent.name == "pip":
        if path.name == "CPM eBooks - CC Course 1 PIP.html": return ("pip_intro", "intro")
        if re.fullmatch(r"\d+\.html",path.name):return ("pip",str(int(path.stem)))
    if path.parent.name == "checkpoints":
        if "Checkpoints.html" in path.name:return ("checkpoint_intro", "intro")
        if re.fullmatch(r"[\d]+[a-z]?\.html",path.name):return ("checkpoint", path.stem.lower())
    if path.parent.name == "standards":return ("standards", path.stem)
    if path.parent.name == "cc1" and "Table of Contents" in path.name:return ("toc", "toc")
    return ("other", safe_slug(path.stem))

def render_content(n, removed_scripts=False):
    """Rebuild a standalone fragment without authoring/extension scripts, but retain original MathJax TeX.
    MathJax's SVG snapshots are intentionally kept as source-compatible markup, not assumed independently renderable.
    """
    if isinstance(n, str): return n
    if n.tag in {"style", "noscript", "iframe", "form", "button", "input"}: return ""
    if n.tag == "c3po-media":
        scripts=[m for m in n.walk() if m.tag=="script" and m.attr("type").lower().startswith("math/tex")]
        if scripts:
            tex=cleantext(html.unescape(scripts[0].text()))
            return '<span class="math-tex" data-tex="'+html.escape(tex,quote=True)+'">'+html.escape("\\("+tex+"\\)")+"</span>"
    if n.tag == "script":
        if n.attr("type").lower().startswith("math/tex"):
            tex=cleantext(html.unescape(n.text()))
            return '<span class="source-tex" data-tex="' + html.escape(tex,quote=True) + '">' + html.escape('\\('+tex+'\\)') + '</span>'
        return ""
    attrs = []
    for k,v in n.attrs.items():
        if k.lower().startswith("on") or k.lower() in {"contenteditable", "tabindex"}:continue
        if k.lower() in {"href","src"} and re.match(r"(?i)\s*(?:javascript|data):",v or ""):continue
        attrs.append((k,v))
    s=Node(n.tag,attrs)
    s.children=[render_content(x) if isinstance(x,Node) else x for x in n.children]
    return serialize(s)

def media_refs(node, original, copied, content_root, output, warnings):
    media=[]; links=[]; math_tex=[]; frag=render_content(node)
    for n in node.walk():
        if n.tag == "script" and n.attr("type").lower().startswith("math/tex"):
            tx = cleantext(html.unescape(n.text()))
            if tx: math_tex.append(tx)
        for attr in (["src"] if n.tag in {"img","video","audio","source"} else []):
            v=n.attr(attr)
            if not v:continue
            path_only=v.split("#",1)[0].split("?",1)[0]
            if re.match(r"^(?:https?:|data:|blob:|//)",v,re.I):
                media.append({"ref":v,"status":"external"}); continue
            from urllib.parse import unquote
            rel=unquote(path_only).removeprefix("./")
            candidate = (original.parent/rel).resolve()
            try: candidate.relative_to(content_root.resolve())
            except ValueError:
                media.append({"ref":v,"status":"unsafe_outside_source"});warnings.add("unsafe_media_path");continue
            if not candidate.is_file():
                media.append({"ref":v,"status":"missing_local_file","source_relative":candidate.relative_to(content_root).as_posix()});warnings.add("missing_media");continue
            out_rel=Path("assets")/candidate.relative_to(content_root)
            if candidate not in copied:
                dest=output/out_rel;dest.parent.mkdir(parents=True,exist_ok=True)
                shutil.copy2(candidate,dest); copied.add(candidate)
            media.append({"ref":v,"status":"copied","output_relative":out_rel.as_posix(),"source_relative":candidate.relative_to(content_root).as_posix(),"sha256":sha(candidate.read_bytes())})
            # Replace source paths inside fragment with standalone copied asset paths; exact attribute values may be escaped.
            frag=frag.replace(html.escape(v,quote=True),html.escape(out_rel.as_posix(),quote=True))
        if n.tag == "a":
            h=n.attr("href")
            if h and re.match(r"^https?://",h,re.I):
                links.append({"url":h,"label":cleantext(plain(n))[:120],"offline":"external_required"})
    return frag, media, links, math_tex

def node_is_problem(n):return isinstance(n,Node) and n.has_class("contentContainerReference") and n.has_class("problem")

def extract_page(source_path, source_root, output, copied, report):
    raw=source_path.read_bytes()
    try:markup=raw.decode("utf-8-sig")
    except UnicodeDecodeError:markup=raw.decode("utf-8",errors="replace");report["warnings"].append({"file":str(source_path.relative_to(source_root)),"warning":"non_utf8_bytes"})
    parser=DOM();parser.feed(markup);parser.close()
    role,role_id=source_name(source_path)
    content=find_first(parser.root,lambda n:n.attr("id")=="contents")
    if content is None:
        report["errors"].append({"file":str(source_path.relative_to(source_root)),"error":"missing_contents_dom"});return []
    title_node=find_first(content,lambda n:n.tag=="header" and n.has_class("lessonTitle"))
    chapter=int(source_path.parent.name[2:]) if re.fullmatch(r"ch\d\d",source_path.parent.name) else None
    lesson_title=cleantext(plain(title_node)) if title_node else ("PI-" + role_id if role=="pip" else source_path.stem)
    original_url=re.search(r"<!-- saved from url=\(\d+\)([^ ]+) -->",markup)
    source_url=original_url.group(1) if original_url else None
    page_key=(f"ch{chapter:02d}_" if chapter else "")+safe_slug(role+"_"+role_id)
    base={"course":COURSE,"chapter":chapter,"lesson_id":role_id if role=="lesson" else None,"source_role":role,"source_id":role_id,"page_title":lesson_title,"source_file":source_path.relative_to(source_root).as_posix(),"source_drive_url":None,"original_url":source_url,"source_sha256":sha(raw),"source_provenance":"saved_textbook_html","teacher_editable_classification":True}
    sequence=[];pending=[];is_review=False
    # The entire #contents is the body of the selected textbook tab. Skip logging scripts and metadata;
    # explicitly partition around first-class numbered problem containers, preserving connective prose.
    for ch in content.children:
        if isinstance(ch,Node) and ch.tag in SKIP_TAGS and not ch.attr("type").startswith("math/tex"):continue
        if isinstance(ch,Node) and (ch.has_class("c3po-metadata") or (ch.tag=="header" and ch.has_class("lessonTitle"))):continue
        if isinstance(ch,str) and not cleantext(html.unescape(ch)):continue
        if node_is_problem(ch):
            if pending:
                sequence.append(("exposition",pending,None,is_review));pending=[]
            sequence.append(("problem",[ch],ch.attr("id"),is_review))
        else:
            pending.append(ch)
            text=cleantext(plain(ch)).lower() if isinstance(ch,Node) else cleantext(html.unescape(ch)).lower()
            if "review and preview" in text or (isinstance(ch,Node) and any(n.tag=="img" and "review and preview" in n.attr("alt").lower() for n in ch.walk())):is_review=True
    if pending:sequence.append(("exposition",pending,None,is_review))
    cards=[];seq_count=0;seen_ids=set()
    for kind,nodes,problem_id,review in sequence:
        label=cleantext(" ".join(plain(x) if isinstance(x,Node) else html.unescape(x) for x in nodes))
        if not label and not any(isinstance(n,Node) and any(x.tag=="img" for x in n.walk()) for n in nodes):continue
        if kind=="problem" and (not problem_id or not EXPECTED_PROBLEMS_RE.match(problem_id)):
            report["warnings"].append({"file":base["source_file"],"warning":"unusual_problem_id","id":problem_id})
        seq_count+=1
        card_id=f"cc1:{page_key}:" + (f"problem_{safe_slug(problem_id)}" if kind=="problem" and problem_id else f"{kind}_{seq_count:03d}")
        if card_id in seen_ids:
            card_id += f":{seq_count:03d}"
            report["warnings"].append({"file":base["source_file"],"warning":"duplicate_source_problem_id","id":problem_id})
        seen_ids.add(card_id)
        role_suggestion = ("review_preview" if review else "lesson_problem") if kind=="problem" else ("lesson_exposition" if role=="lesson" else role)
        if role=="pip":role_suggestion="puzzle_investigator"
        if role=="checkpoint":role_suggestion="checkpoint_reference"
        if role=="reflection":role_suggestion="midcourse_reflection"
        warnings=set();fragments=[];media=[];links=[];maths=[]
        for node in nodes:
            if isinstance(node,str):fragments.append(node);continue
            fragment,m,l,t=media_refs(node,source_path,copied,source_root,output,warnings)
            fragments.append(fragment);media.extend(m);links.extend(l);maths.extend(t)
        card={**base,"card_id":card_id,"sequence":seq_count,"card_type":kind,"suggested_instructional_role":role_suggestion,"classification_status":"machine_suggested","source_problem_id":problem_id,"source_container_id":nodes[0].attr("container-id") if kind=="problem" else None,"text":label,"html":"".join(fragments),"math_tex":maths,"media":media,"external_links":links,"offline_warnings":sorted(warnings),"teacher_approved":False}
        cards.append(card)
    if not cards:report["errors"].append({"file":base["source_file"],"error":"no_extracted_cards"})
    return cards

def inventory(source):
    errors=[];chapter_stats={};expected_html=[]
    for chapter,lesson_text in LESSONS.items():
        directory=source/f"ch{chapter:02d}";names={p.name for p in directory.glob("*") if p.is_file()} if directory.is_dir() else set()
        missing=[]
        for lesson in lesson_text.split():
            suffix=f"Lesson {lesson}.html"
            if not any(n.endswith(suffix) for n in names):missing.append(lesson)
        for role in ("opening","closure"):
            suffix=f"Lesson {chapter}.{role}.html"
            if not any(n.endswith(suffix) for n in names) and not (chapter==2 and role=="opening" and "intro.html" in names):missing.append(role)
        for role in ("opening","closure"):
            if not any(n.endswith(f"Teacher Notes {chapter}.{role}.html") for n in names):missing.append("teacher_"+role)
        if not any(n.endswith(".pdf") for n in names):missing.append("resource_pdf")
        chapter_stats[str(chapter)]={"numbered_lessons_expected":len(lesson_text.split()),"missing":missing}
        errors.extend(f"ch{chapter:02d}/{n}" for n in missing)
    p={z.stem.lower() for z in (source/"pip").glob("*.html")}
    checkpoints={z.stem.lower() for z in (source/"checkpoints").glob("*.html")}
    miss_pip=[i for i in range(1,15) if str(i) not in p]
    miss_check=[x for x in ["1","2","3","4","5","6","7a","7b","8a","8b","9a","9b"] if x not in checkpoints]
    miss_guides=[i for i in range(1,10) if not (source/"parent_guides"/f"CC1_PG_Ch{i}.pdf").is_file()]
    if not any("Table of Contents.html" in q.name for q in source.glob("*.html")):errors.append("table_of_contents")
    for pth in source.rglob("*.html"):
        if any(part.endswith("_files") for part in pth.parts):continue
        if not (pth.parent==source or pth.parent.name.startswith("ch") or pth.parent.name in {"pip","checkpoints","standards"}):continue
        if not pth.with_name(pth.stem+"_files").is_dir(): errors.append("asset_folder: "+pth.relative_to(source).as_posix())
    return {"chapters":chapter_stats,"pip_missing":miss_pip,"checkpoint_missing":miss_check,"parent_guides_missing":miss_guides,"errors":errors}

def all_pages(source):
    for directory in [source] + [source/f"ch{i:02d}" for i in range(1,10)] + [source/x for x in ["pip","checkpoints","standards"]]:
        if directory.is_dir():
            for path in sorted(directory.glob("*.html")):
                if path.is_file():yield path

def report_md(run):
    qa=run["qa"]; summary=run["summary"];inven=run["inventory"]
    lines=["# CC1 extraction / offline audit", "", f"Version: {VERSION}  ", f"Generated (UTC): {run['generated_utc']}  ","", "## Coverage", "",f"- Source HTML pages processed: **{summary['source_pages']}**",f"- Cards extracted: **{summary['cards']}**",f"- Numbered lesson coverage: **{summary['numbered_lessons_found']}/83**",f"- Numbered problem cards: **{summary['numbered_problem_cards']}**",f"- Source images copied: **{summary['unique_images_copied']}**",f"- MathJax TeX expressions preserved: **{summary['math_expressions']}**",f"- External web/eTool links: **{summary['external_links']}**",f"- Missing local asset references: **{summary['missing_media']}**", "", "## Capture gaps",""]
    if inven["errors"]: lines.extend("- "+s for s in inven["errors"])
    else:lines.append("- No missing lesson, opening/closure, or matching asset-folder names.")
    if inven["pip_missing"]:lines.append(f"- Missing PIP: {inven['pip_missing']}")
    if inven["checkpoint_missing"]:lines.append(f"- Missing checkpoints: {inven['checkpoint_missing']}")
    if inven["parent_guides_missing"]:lines.append(f"- Missing Parent Guides: {inven['parent_guides_missing']}")
    lines += ["", "## Quality issues",""]
    for issue in qa["errors"][:200]:lines.append("- ERROR: "+json.dumps(issue,ensure_ascii=False))
    for issue in qa["warnings"][:200]:lines.append("- REVIEW: "+json.dumps(issue,ensure_ascii=False))
    if not qa["errors"] and not qa["warnings"]:lines.append("- No extraction-level problems found.")
    lines += ["", "## Important limitations", "", "- This is an extraction and reference integrity audit, **not** proof that every figure, equation, or embedded activity renders correctly.", "- MathJax TeX and the original source file SHA-256 are retained. Saved MathJax SVG fragments may depend on browser page-level glyph definitions; the card library needs a deliberate math renderer before classroom use.", "- External eTools, videos, and dynamic links require internet or a separate licensed/offline substitute. They are linked, **not duplicated**.", "- Teacher approval is required for lesson roles and card boundaries, especially exposition, worked examples, and Closure activities.", "- Original files, captures, and Parent Guides remain unchanged. Store the generated cards privately; do not publish the copied textbook assets.", ""]
    return "\n".join(lines)

def main(argv=None):
    ap=argparse.ArgumentParser(description="Offline CC1 -> canonical card extraction and source QA")
    ap.add_argument("--source",required=True,help="Local folder containing ch01 ... ch09, pip, checkpoints, parent_guides")
    ap.add_argument("--output",help="Output folder; default sibling cc1_canonical_cards_v1")
    ap.add_argument("--replace-output",action="store_true",help="Allow deleting a previous generated extraction output (not source files)")
    args=ap.parse_args(argv)
    source=Path(args.source).expanduser().resolve()
    if not source.is_dir() or not (source/"ch01").is_dir() or not (source/"ch09").is_dir():
        ap.error("Source must be your CC1 capture folder containing ch01 through ch09; no files were changed")
    dest=Path(args.output).expanduser().resolve() if args.output else (Path.home()/"Documents"/"CPM_Private_Extracted"/"cc1_canonical_cards_v1").resolve()
    if dest == source or source in dest.parents or dest in source.parents:
        ap.error("Output must be outside the original source folder and not its ancestor")
    if dest.exists():
        if not args.replace_output:ap.error("Output exists; supply --replace-output to replace generated cards")
        marker=dest/"CC1_GENERATED_OUTPUT.marker"
        if not marker.is_file():ap.error("Refusing to delete an output folder without our marker")
        shutil.rmtree(dest)
    dest.mkdir(parents=True)
    (dest/"CC1_GENERATED_OUTPUT.marker").write_text("CC1 local canonical extraction output; regenerable.\n",encoding="utf-8")
    qa={"errors":[],"warnings":[]};inven=inventory(source);allcards=[];copied=set();page_counts=[]
    try:
        for page in all_pages(source):
            cards=extract_page(page,source,dest,copied,qa)
            allcards.extend(cards)
            page_counts.append({"file":page.relative_to(source).as_posix(),"cards":len(cards),"problem_cards":sum(bool(c["source_problem_id"]) for c in cards)})
        ids=[c["card_id"] for c in allcards]
        duplicates=[k for k,v in Counter(ids).items() if v>1]
        if duplicates:qa["errors"].append({"error":"duplicate_card_ids","sample":duplicates[:20]})
        folder=dest/"cards";folder.mkdir(exist_ok=True)
        for c in allcards:
            chapter=f"ch{c['chapter']:02d}" if c['chapter'] is not None else c["source_role"]
            safe=c["card_id"].replace(":","__")
            write_json(folder/chapter/(safe+".json"),c)
        with (dest/"cards.jsonl").open("w",encoding="utf-8") as f:
            for c in allcards:f.write(json.dumps(c,ensure_ascii=False,separators=(",",":"))+"\n")
        indexed=[]
        for c in allcards:
            indexed.append({k:c.get(k) for k in ["card_id","chapter","lesson_id","source_role","source_id","sequence","card_type","source_problem_id","suggested_instructional_role","source_file","page_title"]})
        write_json(dest/"card_index.json",indexed)
        summary={"source_pages":len(page_counts),"cards":len(allcards),"numbered_lessons_found":sum(1 for p in page_counts if source_name(source/p["file"])[0]=="lesson"),"numbered_problem_cards":sum(bool(c["source_problem_id"]) for c in allcards),"unique_images_copied":len(copied),"math_expressions":sum(len(c["math_tex"]) for c in allcards),"external_links":sum(len(c["external_links"]) for c in allcards),"missing_media":sum(sum(m["status"]=="missing_local_file" for m in c["media"]) for c in allcards)}
        run={"schema":"cc1_canonical_extraction/1","generated_utc":dt.datetime.now(dt.timezone.utc).isoformat(),"extractor_version":VERSION,"source_directory_local_only":source.name,"summary":summary,"inventory":inven,"pages":page_counts,"qa":qa}
        write_json(dest/"qa_report.json",run)
        (dest/"QA_REPORT.md").write_text(report_md(run),encoding="utf-8")
        (dest/"PRIVATE_CONTENT_NOTICE.txt").write_text("Contains copyrighted CPM textbook-derived content and images. Keep local/private. Do not commit or publish this folder.\n",encoding="utf-8")
        print(report_md(run))
        print("Output:",dest)
        return 0 if not qa["errors"] and not inven["errors"] and not inven["pip_missing"] and not inven["checkpoint_missing"] and not inven["parent_guides_missing"] else 2
    except Exception:
        import traceback
        traceback.print_exc()
        return 1

if __name__=="__main__":sys.exit(main())
