#!/usr/bin/env python3
"""Private/offline canonical Core Connections Geometry extractor. No third-party dependencies.

Captures, copyright-protected cards and images NEVER enter this repository.
Generated output goes to the user's private Documents directory.
"""
import argparse
from collections import Counter, defaultdict
from datetime import datetime, timezone
import hashlib
import html
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import shutil
import sys
from urllib.parse import unquote, urlsplit

VERSION = "1.0.0"
COURSE = "geometry"
SCHEMA = "geometry_canonical_extraction/1"
# The lesson skeleton was verified against the saved Geometry Table of Contents.
LESSONS = {
  1: "1.1.1 1.1.2 1.1.3 1.1.4 1.1.5 1.2.1 1.2.2 1.2.3 1.2.4 1.2.5 1.2.6 1.3.1 1.3.2",
  2: "2.1.1 2.1.2 2.1.3 2.1.4 2.1.5 2.2.1 2.2.2 2.2.3 2.2.4 2.3.1 2.3.2",
  3: "3.1.1 3.1.2 3.1.3 3.1.4 3.2.1 3.2.2 3.2.3 3.2.4 3.2.5 3.2.6",
  4: "4.1.1 4.1.2 4.1.3 4.1.4 4.1.5 4.2.1 4.2.2 4.2.3 4.2.4 4.2.5",
  5: "5.1.1 5.1.2 5.1.3 5.1.4 5.2.1 5.2.2 5.3.1 5.3.2 5.3.3 5.3.4 5.3.5",
  6: "6.1.1 6.1.2 6.1.3 6.1.4 6.1.5 6.2.1 6.2.2 6.2.3 6.2.4 6.2.5",
  7: "7.1.1 7.1.2 7.1.3 7.1.4 7.2.1 7.2.2 7.2.3 7.2.4 7.2.5 7.2.6 7.3.1 7.3.2 7.3.3",
  8: "8.1.1 8.1.2 8.1.3 8.1.4 8.1.5 8.2.1 8.2.2 8.3.1 8.3.2 8.3.3",
  9: "9.1.1 9.1.2 9.1.3 9.1.4 9.1.5 9.2.1 9.2.2 9.2.3 9.2.4",
  10: "10.1.1 10.1.2 10.1.3 10.1.4 10.1.5 10.2.1 10.2.2 10.2.3 10.3.1 10.3.2 10.3.3 10.3.4 10.3.5",
  11: "11.1.1 11.1.2 11.1.3 11.1.4 11.1.5 11.2.1 11.2.2 11.2.3",
  12: "12.1.1 12.1.2 12.1.3 12.1.4 12.2.1 12.2.2 12.2.3 12.2.4",
}
EXPECTED_CHECKPOINTS = ("1", "2", "3", "4", "5a", "5b", "6", "7", "8", "9a", "9b", "10", "11")
EXPECTED_LESSON_TOTAL = 126
PROBLEM_ID_RE = re.compile(r"^(?:\d+-[0-9A-Za-z]+|CL\s*\d+-[0-9A-Za-z]+)$", re.I)
LESSON_RE = re.compile(r"Lesson\s+(\d+\.\d+\.\d+|\d+\.(?:opening|closure))\.html$", re.I)
TEACHER_RE = re.compile(r"Teacher Notes\s+(\d+)\.(opening|closure)\.html$", re.I)
VOID = set("area base br col embed hr img input link meta param source track wbr".split())
SKIP = set("style noscript iframe form button input template".split())
BLOCK = set("div p li header section article figure table h1 h2 h3 h4 h5 ul ol blockquote hr".split())
MEDIA = set("img video audio source".split())

class Node:
    __slots__ = ("tag", "attrs", "children", "parent")
    def __init__(self, tag, attrs=(), parent=None):
        self.tag, self.attrs, self.children, self.parent = tag, dict(attrs), [], parent
    def attr(self, key):
        return self.attrs.get(key) or ""
    def has_class(self, token):
        return token in self.attr("class").split()
    def walk(self):
        yield self
        for ch in self.children:
            if isinstance(ch, Node):
                yield from ch.walk()
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
        if tag not in VOID:
            self.stack.append(node)
    def handle_startendtag(self, tag, attrs):
        self.stack[-1].children.append(Node(tag, attrs, self.stack[-1]))
    def handle_endtag(self, tag):
        for i in range(len(self.stack) - 1, 0, -1):
            if self.stack[i].tag == tag:
                self.stack = self.stack[:i]
                break
    def handle_data(self, value):
        self.stack[-1].children.append(value)
    def handle_entityref(self, name):
        self.handle_data("&" + name + ";")
    def handle_charref(self, name):
        self.handle_data("&#" + name + ";")

def first(root, pred):
    return next((x for x in root.walk() if pred(x)), None)

def clean(value):
    return re.sub(r"\s+", " ", html.unescape(value)).strip()

def slug(value):
    return re.sub(r"[^a-z0-9_-]+", "_", str(value).lower()).strip("_")

def sha256(raw):
    return hashlib.sha256(raw).hexdigest()

def emit_json(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

def plain(node):
    if isinstance(node, str):
        return html.unescape(node)
    if node.tag in SKIP or node.tag == "script":
        return ""
    sep = "\n" if node.tag in BLOCK else ""
    return sep + "".join(plain(ch) for ch in node.children) + sep

def serialize(node):
    if isinstance(node, str):
        return node
    if node.tag == "_root":
        return "".join(serialize(x) for x in node.children)
    attrs = "".join(f' {k}="{html.escape(str(v or ""), quote=True)}"' for k, v in node.attrs.items())
    start = f"<{node.tag}{attrs}>"
    return start if node.tag in VOID else start + "".join(serialize(ch) for ch in node.children) + f"</{node.tag}>"

def render(node):
    if isinstance(node, str):
        return node
    if node.tag in SKIP or node.has_class("modal") or node.has_class("gloss"):
        return ""
    if node.tag == "c3po-media":
        t = first(node, lambda x: x.tag == "script" and x.attr("type").lower().startswith("math/tex"))
        if t is not None:
            tex = clean(t.text())
            return '<span class="math-tex" data-tex="' + html.escape(tex, quote=True) + '">' + html.escape('\\(' + tex + '\\)') + '</span>'
    if node.tag == "script":
        if node.attr("type").lower().startswith("math/tex"):
            tex = clean(node.text())
            return '<span class="source-tex" data-tex="' + html.escape(tex, quote=True) + '">' + html.escape('\\(' + tex + '\\)') + '</span>'
        return ""
    attrs = [(k, v) for k, v in node.attrs.items()
             if not k.lower().startswith("on") and k.lower() not in {"contenteditable", "tabindex"}
             and not (k.lower() in {"href", "src"} and re.match(r"(?i)\s*(?:javascript|data):", v or ""))]
    output = Node(node.tag, attrs)
    output.children = [render(ch) for ch in node.children]
    return serialize(output)

def source_role(path):
    parent = path.parent.name.lower()
    name = path.name
    m = TEACHER_RE.search(name)
    if m:
        return ("teacher_" + m.group(2).lower(), m.group(1))
    m = LESSON_RE.search(name)
    if m:
        role_id = m.group(1).lower()
        if role_id.endswith(".opening"):
            return ("opening", role_id.split(".")[0])
        if role_id.endswith(".closure"):
            return ("closure", role_id.split(".")[0])
        return ("lesson", role_id)
    if parent == "checkpoints":
        if re.fullmatch(r"\d+[a-z]?\.html", name, re.I):
            return ("checkpoint", path.stem.lower())
        return ("checkpoint_intro", slug(path.stem))
    if parent == "standards":
        return ("standards", slug(path.stem))
    if "table of contents" in name.lower():
        return ("toc", "toc")
    if "overview" in name.lower() and parent not in {"checkpoints", "standards"}:
        return ("overview", "overview")
    return ("other", slug(path.stem))

def problem(node):
    return isinstance(node, Node) and node.has_class("contentContainerReference") and node.has_class("problem")

def meaningful(node):
    if isinstance(node, str):
        return bool(clean(node))
    if node.tag in {"script", "style", "noscript"}:
        return False
    if node.has_class("c3po-metadata") or node.has_class("modal"):
        return False
    return bool(clean(plain(node)) or first(node, lambda n: n.tag in MEDIA))

def unpack_nested_problems(node):
    """Expose problem containers buried inside saved-HTML wrapper/list nodes.

    CPM occasionally wraps multiple Closure answer blocks in a single <li>.
    Keep each original problem node intact, including TeX and images; do not
    reproduce the wrapper as an extra exposition card containing those keys.
    """
    if not isinstance(node, Node) or problem(node):
        yield node
    elif any(problem(child) for child in node.walk() if child is not node):
        for child in node.children:
            yield from unpack_nested_problems(child)
    else:
        yield node


def content_nodes(content, role):
    """Preserve source order while exposing wrapped Geometry closure problems.

    Chapter 8 places all student questions *and* the key in one <ul><li>
    wrapper. Other chapters use top-level problem nodes. Never conflate them.
    """
    for node in content.children:
        if role == "closure":
            yield from unpack_nested_problems(node)
        else:
            yield node

def split_content(content, role):
    """Partition in DOM order. Numbered questions are atomic; section headings start new cards.

    Other source prose is grouped into contiguous explanatory blocks, not reworded.
    """
    out, pending = [], []
    in_review = False
    in_answers = False
    checkpoint_practice = False
    checkpoint_items = 0
    def flush():
        nonlocal pending
        if pending:
            out.append(("exposition", pending, None, in_review, in_answers))
            pending = []
    for node in content_nodes(content, role):
        if not meaningful(node):
            continue
        if isinstance(node, Node) and node.tag == "header" and node.has_class("lessonTitle"):
            continue
        line = clean(plain(node)).lower() if isinstance(node, Node) else clean(node).lower()
        if isinstance(node, Node) and node.tag in {"h1", "h2", "h3", "h4"}:
            flush()
        if "review and preview" in line and (len(line) < 250 or (isinstance(node, Node) and node.tag in {"h2", "h3", "h4"})):
            in_review = True
        if "answers and support for closure" in line:
            flush()
            in_answers = True
        if role == "checkpoint":
            if re.match(r"^(?:answers? to problem\b|answers?\s*:)", line, re.I):
                flush()
                in_answers = True
            elif line.startswith("now we can go back and solve the original problems"):
                # The worked answers to the SOURCE checkpoint problem are keys,
                # unlike the pedagogical worked examples earlier on the page.
                flush()
                in_answers = True
            elif re.match(r"^(?:example\s*\d+\s*:|here are some more to try)", line, re.I):
                flush()
                in_answers = False
            if line.startswith("here are some more to try"):
                checkpoint_practice = True
            # Preserve source order but expose numbered practice items as distinct
            # cards. Do not invent source CPM problem numbers for those items.
            if checkpoint_practice and not in_answers and isinstance(node, Node):
                items = [x for x in node.walk() if x.tag == "li"]
                if items:
                    flush()
                    for item in items:
                        checkpoint_items += 1
                        out.append(("checkpoint_practice", [item], None, in_review, False))
                    continue
        if problem(node):
            flush()
            out.append(("problem", [node], node.attr("id"), in_review, in_answers))
            continue
        pending.append(node)
        if role == "checkpoint" and in_answers and re.match(r"^(?:answers? to problem\b|answers?\s*:)", line, re.I):
            # The initial answer sentence must not leak into student notes.
            if line.startswith("answers to problem"):
                flush()
                in_answers = False
    flush()
    return out

def get_media(nodes, page, root, destination, copied, sha_cache):
    """Collect/clone only local image/media refs within the source capture root."""
    fragments, media, links, mathtex, warnings = [], [], [], [], set()
    for node in nodes:
        frag = render(node)
        if isinstance(node, Node):
            for el in node.walk():
                if el.tag == "script" and el.attr("type").lower().startswith("math/tex"):
                    tx = clean(el.text())
                    if tx:
                        mathtex.append(tx)
                if el.tag == "a" and el.attr("href").lower().startswith(("http://", "https://")):
                    links.append({"url": el.attr("href"), "label": clean(plain(el))[:120], "offline": "external_required"})
                if el.tag not in MEDIA:
                    continue
                ref = el.attr("src")
                if not ref:
                    continue
                parsed = urlsplit(ref)
                if parsed.scheme or parsed.netloc or ref.startswith("//"):
                    media.append({"ref": ref, "status": "external"})
                    continue
                file_rel = unquote(parsed.path).removeprefix("./")
                if not file_rel:
                    continue
                src = (page.parent / file_rel).resolve()
                try:
                    rel = src.relative_to(root.resolve())
                except ValueError:
                    media.append({"ref": ref, "status": "unsafe_outside_source"})
                    warnings.add("unsafe_media_path")
                    continue
                if not src.is_file():
                    media.append({"ref": ref, "status": "missing_local_file", "source_relative": rel.as_posix()})
                    warnings.add("missing_media")
                    continue
                output_rel = Path("assets") / rel
                if src not in copied:
                    dst = destination / output_rel
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(src, dst)
                    copied.add(src)
                digest = sha_cache.setdefault(src, sha256(src.read_bytes()))
                media.append({"ref": ref, "status": "copied", "output_relative": output_rel.as_posix(), "source_relative": rel.as_posix(), "sha256": digest})
                frag = frag.replace(html.escape(ref, quote=True), html.escape(output_rel.as_posix(), quote=True))
        fragments.append(frag)
    return "".join(fragments), media, links, mathtex, sorted(warnings)

def extract_page(page, root, dest, copied, sha_cache, qa):
    raw = page.read_bytes()
    try:
        markup = raw.decode("utf-8-sig")
    except UnicodeDecodeError:
        markup = raw.decode("utf-8", errors="replace")
        qa["warnings"].append({"file": page.relative_to(root).as_posix(), "warning": "invalid_utf8_replaced"})
    dom = DOM()
    dom.feed(markup)
    dom.close()
    relative = page.relative_to(root).as_posix()
    content = first(dom.root, lambda n: n.attr("id") == "contents")
    if content is None:
        qa["errors"].append({"file": relative, "error": "missing_contents_dom"})
        return []
    role, role_id = source_role(page)
    chapter = int(page.parent.name[2:]) if re.fullmatch(r"ch\d{2}", page.parent.name) else None
    heading = first(content, lambda n: n.tag == "header" and n.has_class("lessonTitle"))
    page_title = clean(plain(heading)) if heading else page.stem
    saved_url = re.search(r"<!--\s*saved from url=\(\d+\)([^ ]+)\s*-->", markup)
    prefix = (f"ch{chapter:02d}_" if chapter else "") + slug(role + "_" + role_id)
    base = {
        "course": COURSE, "chapter": chapter, "lesson_id": role_id if role == "lesson" else None,
        "source_role": role, "source_id": role_id, "page_title": page_title,
        "source_file": relative, "source_drive_url": None,
        "original_url": saved_url.group(1).strip() if saved_url else None,
        "source_sha256": sha256(raw), "source_provenance": "saved_textbook_html",
        "teacher_editable_classification": True,
    }
    cards, used_ids = [], set()
    for kind, nodes, pid, review, in_answers in split_content(content, role):
        text = clean(" ".join(plain(n) for n in nodes))
        if not text and not any(isinstance(n, Node) and first(n, lambda k: k.tag in MEDIA) for n in nodes):
            continue
        if kind == "problem" and (not pid or not PROBLEM_ID_RE.fullmatch(pid)):
            qa["warnings"].append({"file": relative, "warning": "unusual_problem_id", "id": pid})
        checkpoint_source_match = re.search(r"\bProblem\s+(\d+-[\dA-Za-z]+)\b", text[:160], re.I) if role == "checkpoint" else None
        body = first(nodes[0], lambda n: n.has_class("contentContainerReference-body")) if kind == "problem" else None
        body_text = clean(plain(body)) if body else ""
        is_solution = bool(kind == "problem" and role == "closure" and
                           (in_answers or re.match(r"^(?:more\s+)?solutions?\b(?:\s|:|\.|$)", body_text, re.I)))
        # The final problem in each original Closure asks students to rate
        # their own understanding. There is deliberately no objective key.
        is_self_assessment = bool(kind == "problem" and role == "closure" and not is_solution
                                  and ("check your answers using the table" in text.lower()
                                       or ("which problems do you feel confident about" in text.lower()
                                           and "which problems were hard" in text.lower())))
        sequence = len(cards) + 1
        cid = f"{COURSE}:{prefix}:" + ("problem_" + slug(pid) if kind == "problem" and pid else f"{kind}_{sequence:03d}")
        if is_solution:
            cid += ":solution"
        if cid in used_ids:
            cid += f":{sequence:03d}"
            qa["warnings"].append({"file": relative, "warning": "duplicate_source_problem_id", "id": pid})
        used_ids.add(cid)
        visibility = "teacher_only" if is_solution or role.startswith("teacher_") or (role in {"checkpoint", "closure"} and in_answers) else "student_candidate"
        purpose = ("review_preview" if review else "lesson_problem") if kind == "problem" else ("lesson_exposition" if role == "lesson" else role)
        if is_solution:
            purpose = "teacher_key"
        elif is_self_assessment:
            purpose = "closure_self_assessment"
        if role == "checkpoint":
            purpose = "checkpoint_answer_key" if in_answers else ("checkpoint_practice" if kind == "checkpoint_practice" else "checkpoint_reference")
        fragment, media, links, tex, warns = get_media(nodes, page, root, dest, copied, sha_cache)
        if "missing_media" in warns:
            qa["warnings"].append({"file": relative, "warning": "missing_media", "card_id": cid,
                                   "references": [x["ref"] for x in media if x["status"] == "missing_local_file"][:20]})
        if kind == "exposition" and len(text) > 6000:
            qa["warnings"].append({"file": relative, "warning": "long_exposition_boundary_review", "card_id": cid, "characters": len(text)})
        cards.append({**base, "card_id": cid, "sequence": sequence,
            "card_type": "solution" if is_solution else ("problem" if kind == "checkpoint_practice" else kind),
            "suggested_instructional_role": purpose, "visibility": visibility,
            "classification_status": "machine_suggested", "teacher_approved": False,
            "source_problem_id": pid, "referenced_textbook_problem_id": checkpoint_source_match.group(1) if checkpoint_source_match else None,
            "source_list_item_number": (
                1 + sum(c["suggested_instructional_role"] == "checkpoint_practice" for c in cards)
                if kind == "checkpoint_practice" else None),
            "source_container_id": nodes[0].attr("container-id") if kind == "problem" else None,
            "text": text, "html": fragment, "math_tex": tex, "media": media,
            "external_links": links, "offline_warnings": warns,
            "paired_student_card_id": None, "paired_teacher_key_card_id": None,
        })
    questions, keys = defaultdict(list), defaultdict(list)
    for c in cards:
        if not c["source_problem_id"]:
            continue
        identity = re.sub(r"\s+", "", c["source_problem_id"]).upper()
        (keys if c["card_type"] == "solution" else questions)[identity].append(c)
    for k, sols in keys.items():
        probs = questions.get(k, [])
        if len(sols) == len(probs) == 1:
            probs[0]["paired_teacher_key_card_id"] = sols[0]["card_id"]
            sols[0]["paired_student_card_id"] = probs[0]["card_id"]
        else:
            qa["warnings"].append({"file": relative, "warning": "unmatched_or_ambiguous_teacher_key", "id": k, "questions": len(probs), "solutions": len(sols)})
    for k, probs in questions.items():
        if (role == "closure" and k not in keys
                and not all(p["suggested_instructional_role"] == "closure_self_assessment" for p in probs)):
            qa["warnings"].append({"file": relative, "warning": "closure_question_without_key", "id": k, "questions": len(probs)})
    if not cards:
        qa["errors"].append({"file": relative, "error": "no_extracted_cards"})
    return cards

def pages(source):
    dirs = ([source] + [source / f"ch{x:02d}" for x in range(1, 13)]
            + [source / x for x in ("checkpoints", "standards")])
    for folder in dirs:
        if folder.is_dir():
            yield from sorted(x for x in folder.glob("*.html") if x.is_file())

def resources(source):
    """Index source PDFs without embedding copyrighted PDF bytes in GitHub."""
    dirs = ([source / f"ch{x:02d}" for x in range(1, 13)]
            + [source / "parent_guides", source / "standards", source / "misc"])
    records = []
    for folder in dirs:
        if folder.is_dir():
            for p in sorted(folder.glob("*.pdf")):
                chapter = int(folder.name[2:]) if re.fullmatch(r"ch\d{2}", folder.name) else None
                records.append({"course": COURSE, "source_file": p.relative_to(source).as_posix(),
                                "chapter": chapter, "source_provenance": "saved_textbook_pdf",
                                "source_sha256": sha256(p.read_bytes()),
                                "kind": ("chapter_resource" if chapter else folder.name),
                                "visibility": "teacher_review_required" if folder.name == "misc" else "reference",
                                "copyright": "private_only"})
    return records

def inventory(source):
    issues = []
    chapters = {}
    for chapter, lesson_ids in LESSONS.items():
        folder = source / f"ch{chapter:02d}"
        names = {p.name for p in folder.iterdir() if p.is_file()} if folder.is_dir() else set()
        missing = []
        for lid in lesson_ids.split():
            if not any(n.endswith(f"Lesson {lid}.html") for n in names):
                missing.append(f"lesson {lid}")
        for role in ("opening", "closure"):
            if not any(n.endswith(f"Lesson {chapter}.{role}.html") for n in names):
                missing.append(f"student_{role}")
            if not any(n.endswith(f"Teacher Notes {chapter}.{role}.html") for n in names):
                missing.append(f"teacher_{role}")
        if not (folder / f"CCG Ch {chapter} RPs.pdf").is_file():
            missing.append("chapter_resource_pdf")
        chapters[str(chapter)] = {"expected_lessons": len(lesson_ids.split()), "missing": missing}
        issues.extend(f"ch{chapter:02d}/{m}" for m in missing)
    for title in ("Table of Contents", "Overview"):
        if not any(title in p.name for p in source.glob("*.html")):
            issues.append(f"root/{title}.html")
    cp_folder = source / "checkpoints"
    existing_checkpoints = {p.stem.lower() for p in cp_folder.glob("*.html")}
    missing_checkpoints = [x for x in EXPECTED_CHECKPOINTS if x not in existing_checkpoints]
    if not any("Checkpoints" in p.name for p in cp_folder.glob("*.html")):
        issues.append("checkpoints/index")
    parent = source / "parent_guides"
    missing_guides = [x for x in range(1, 13) if not (parent / f"CCG_PG_Ch{x}.pdf").is_file()]
    for d in ("standards", "misc"):
        if not any((source / d).glob("*.pdf")):
            issues.append(f"{d}/pdf")
    if not any((source / "standards").glob("*.html")):
        issues.append("standards/html")
    missing_asset_folders = [p.relative_to(source).as_posix() for p in pages(source)
                             if not p.with_name(p.stem + "_files").is_dir()]
    issues.extend("asset_folder: " + x for x in missing_asset_folders)
    return {"chapters": chapters, "missing_checkpoints": missing_checkpoints,
            "missing_parent_guides": missing_guides,
            "missing_asset_folders": missing_asset_folders, "errors": issues,
            "supplemental_reference_review": ["Student Hunt", "Teacher Hunt", "Credits", "Student Note", "Glossary", "Index"]}

def report_markdown(run):
    a, inv, qa = run["summary"], run["inventory"], run["qa"]
    lines = ["# Geometry canonical card extraction — QA report", "",
        f"Extractor {VERSION} | UTC {run['generated_utc']}", "", "## Source coverage", "",
        f"- HTML pages processed: **{a['source_pages']}**",
        f"- Canonical cards: **{a['cards']}**",
        f"- Numbered lessons: **{a['numbered_lessons_found']}/{EXPECTED_LESSON_TOTAL}**",
        f"- Student problem cards: **{a['student_problem_cards']}**",
        f"- Teacher-only solution cards: **{a['teacher_solution_cards']}**",
        f"- Teacher-only cards (all types): **{a['teacher_only_cards']}**",
        f"- Paired keys: **{a['paired_solution_cards']}**",
        f"- Distinct assets copied: **{a['unique_assets_copied']}**",
        f"- Indexed reference PDFs (kept at local source): **{a['indexed_reference_pdfs']}**",
        f"- TeX expressions: **{a['math_expressions']}**",
        f"- External links: **{a['external_links']}**",
        f"- Missing local media references: **{a['missing_media']}**", "", "## Inventory", ""]
    if not inv["errors"] and not inv["missing_checkpoints"] and not inv["missing_parent_guides"]:
        lines.append("- No missing expected pages, resource PDFs, guides, or matching `_files` folders.")
    else:
        lines.extend("- MISSING: " + x for x in inv["errors"])
        for field in ("missing_checkpoints", "missing_parent_guides"):
            if inv[field]:
                lines.append("- MISSING " + field + ": " + repr(inv[field]))
    lines += ["", "## Extraction review", ""]
    lines.extend("- ERROR: " + json.dumps(x, ensure_ascii=False) for x in qa["errors"][:250])
    lines.extend("- REVIEW: " + json.dumps(x, ensure_ascii=False) for x in qa["warnings"][:250])
    if len(qa["warnings"]) > 250:
        lines.append(f"- Additional warnings in qa_report.json: {len(qa['warnings']) - 250}")
    if not qa["errors"] and not qa["warnings"]:
        lines.append("- No extraction warnings observed.")
    lines += ["", "## Boundaries and limitations", "",
        "- Closure answer blocks, including nested list-wrapped keys, are teacher-only; paired questions are linked by source ID.",
        "- Closure self-assessment/reflection questions do not require answer keys and retain their original IDs.",
        "- Teacher Notes are teacher-only, including chapter closures. Do not silently add them to student handouts.",
        "- Image-based checkpoint practice items are separated into their original list boundaries; source labels are never invented.",
        "- Checkpoint answer sections and original-problem answers are teacher-only.",
        "- Geometry Hunts and optional reference pages are not required for core extraction; capture them separately if available.",
        "- This verifies the presence of local media files and source TeX; it does not certify browser rendering or interactive eTools.",
        "- Content boundaries and duplicate labels need teacher review; do not treat machine suggestions as approved.",
        "- Keep generated CPM cards and images PRIVATE, out of public GitHub and shared static sites.", ""]
    return "\n".join(lines)

def run(argv=None):
    ap = argparse.ArgumentParser(description="Private, offline Geometry canonical extraction")
    ap.add_argument("--source", required=True, help="Downloaded/synced Geometry folder containing ch01 through ch12")
    ap.add_argument("--output", help="Private output folder (default ~/Documents/CPM_Private_Extracted/geometry_canonical_cards_v1)")
    ap.add_argument("--replace-output", action="store_true", help="Replace only a directory bearing the Geometry output marker")
    opts = ap.parse_args(argv)
    source = Path(opts.source).expanduser().resolve()
    if not source.is_dir() or not all((source / f"ch{c:02d}").is_dir() for c in range(1, 13)):
        ap.error("Select the Geometry textbook capture ROOT folder containing all ch01...ch12 folders; no changes made")
    destination = Path(opts.output).expanduser().resolve() if opts.output else (Path.home() / "Documents" / "CPM_Private_Extracted" / "geometry_canonical_cards_v1").resolve()
    if source == destination or source in destination.parents or destination in source.parents:
        ap.error("Output must not overlap the original source directory")
    marker = destination / "GEOMETRY_GENERATED_OUTPUT.marker"
    if destination.exists():
        if not opts.replace_output or not marker.is_file():
            ap.error("Output exists; refusing to replace unless --replace-output AND Geometry marker are present")
        shutil.rmtree(destination)
    destination.mkdir(parents=True, exist_ok=True)
    marker.write_text("Geometry generated canonical cards; safe to regenerate; never publish.\n", encoding="utf-8")
    qa, copied, digests, all_cards, counts = {"errors": [], "warnings": []}, set(), {}, [], []
    inv = inventory(source)
    try:
        for page in pages(source):
            cards = extract_page(page, source, destination, copied, digests, qa)
            all_cards.extend(cards)
            counts.append({"file": page.relative_to(source).as_posix(), "cards": len(cards),
                           "student_problems": sum(c["card_type"] == "problem" and c["visibility"] == "student_candidate" for c in cards),
                           "teacher_solutions": sum(c["card_type"] == "solution" for c in cards)})
        duplicates = [k for k, v in Counter(c["card_id"] for c in all_cards).items() if v > 1]
        if duplicates:
            qa["errors"].append({"error": "duplicate_card_ids", "ids": duplicates[:20]})
        for c in all_cards:
            group = f"ch{c['chapter']:02d}" if c["chapter"] is not None else c["source_role"]
            emit_json(destination / "cards" / group / (c["card_id"].replace(":", "__") + ".json"), c)
        with (destination / "cards.jsonl").open("w", encoding="utf-8") as f:
            for c in all_cards:
                f.write(json.dumps(c, ensure_ascii=False, separators=(",", ":")) + "\n")
        fields = ("card_id", "chapter", "lesson_id", "source_role", "source_id", "sequence", "card_type", "source_problem_id", "suggested_instructional_role", "visibility", "paired_student_card_id", "paired_teacher_key_card_id", "source_list_item_number", "source_file", "page_title")
        emit_json(destination / "card_index.json", [{k: c.get(k) for k in fields} for c in all_cards])
        summary = {"source_pages": len(counts), "cards": len(all_cards),
            "numbered_lessons_found": sum(source_role(source / p["file"])[0] == "lesson" for p in counts),
            "student_problem_cards": sum(c["card_type"] == "problem" and c["visibility"] == "student_candidate" for c in all_cards),
            "teacher_solution_cards": sum(c["card_type"] == "solution" for c in all_cards),
            "teacher_only_cards": sum(c["visibility"] == "teacher_only" for c in all_cards),
            "paired_solution_cards": sum(c["card_type"] == "solution" and c["paired_student_card_id"] is not None for c in all_cards),
            "unique_assets_copied": len(copied), "indexed_reference_pdfs": 0, "math_expressions": sum(len(c["math_tex"]) for c in all_cards),
            "external_links": sum(len(c["external_links"]) for c in all_cards),
            "missing_media": sum(m["status"] == "missing_local_file" for c in all_cards for m in c["media"])}
        if summary["numbered_lessons_found"] != EXPECTED_LESSON_TOTAL:
            qa["errors"].append({"error": "numbered_lesson_coverage", "found": summary["numbered_lessons_found"], "expected": EXPECTED_LESSON_TOTAL})
        pdf_index = resources(source)
        emit_json(destination / "resource_index.json", pdf_index)
        summary["indexed_reference_pdfs"] = len(pdf_index)
        run_info = {"schema": SCHEMA, "generated_utc": datetime.now(timezone.utc).isoformat(),
                    "extractor_version": VERSION, "source_directory_local_only": source.name,
                    "summary": summary, "inventory": inv, "pages": counts, "qa": qa}
        emit_json(destination / "qa_report.json", run_info)
        report = report_markdown(run_info)
        (destination / "QA_REPORT.md").write_text(report, encoding="utf-8")
        (destination / "PRIVATE_CONTENT_NOTICE.txt").write_text("Copyright-protected CPM textbook content. Keep local/private; do not commit, publish, or redistribute.\n", encoding="utf-8")
        print(report)
        print("\nPRIVATE OUTPUT:", destination)
        return 2 if qa["errors"] or inv["errors"] or inv["missing_checkpoints"] or inv["missing_parent_guides"] else 0
    except Exception:
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(run())
