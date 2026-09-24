#!/usr/bin/env python3
from __future__ import annotations

import csv
import re
import shutil
import subprocess
import tempfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from portfolio_runtime import (
    github_root_from_runtime,
    portfolio_root,
    read_csv,
    roster_rows,
    scan_states,
    sha256_file,
    timestamp,
    validate_state_zip,
)


def osa(script: str) -> str:
    proc = subprocess.run(["/usr/bin/osascript", "-e", script], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
    return proc.stdout.strip() if proc.returncode == 0 else ""


def choose_target(options):
    labels = [f"{c} · Unit {u}" for c, u, _ in options]
    escaped = ",".join('"' + x.replace('"', '\\"') + '"' for x in labels)
    script = f'''set choices to {{{escaped}}}\ntry\nset picked to choose from list choices with prompt "Choose the Portfolio course and Unit to prepare for email" with title "Portfolio Email Prep"\nif picked is false then return ""\nreturn item 1 of picked\non error number -128\nreturn ""\nend try'''
    picked = osa(script)
    if not picked:
        return None
    return options[labels.index(picked)]


def find_chrome() -> Path | None:
    candidates = [
        Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"),
        Path("/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge"),
        Path("/Applications/Chromium.app/Contents/MacOS/Chromium"),
        Path.home() / "Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    ]
    for p in candidates:
        if p.is_file():
            return p
    return None


def load_contacts(state_dir: Path, root: Path):
    recipients = {}
    p = state_dir / "email_recipients_current.csv"
    if p.is_file():
        _f, rows = read_csv(p)
        for r in rows:
            sk = r.get("student_key", "").strip()
            if sk:
                recipients[sk] = r
    support = {}
    support_files = [state_dir / "student_support_contacts_current.csv", root / "00 Contact Directory" / "student_support_contacts_current.csv"]
    for sp in support_files:
        if not sp.is_file():
            continue
        _f, rows = read_csv(sp)
        for r in rows:
            if str(r.get("active", "yes")).strip().lower() in {"no", "false", "0"}:
                continue
            sid = (r.get("student_id") or "").strip()
            email = (r.get("staff_email") or "").strip()
            if sid and email:
                support.setdefault(sid, set()).add(email)
    return recipients, support


def print_pdf(chrome: Path, html_file: Path, pdf_file: Path) -> tuple[bool, str]:
    pdf_file.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        str(chrome),
        "--headless=new",
        "--disable-gpu",
        "--no-sandbox",
        "--allow-file-access-from-files",
        "--no-pdf-header-footer",
        f"--print-to-pdf={pdf_file}",
        html_file.resolve().as_uri(),
    ]
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, timeout=90)
    ok = proc.returncode == 0 and pdf_file.is_file() and pdf_file.stat().st_size > 1000
    return ok, proc.stdout[-1000:]


def main() -> int:
    github_root = github_root_from_runtime()
    root = portfolio_root(github_root)
    options = scan_states(root)
    if not options:
        print("No local Portfolio state was found.")
        return 1
    target = choose_target(options)
    if not target:
        print("Canceled. No email package was prepared.")
        return 0
    course, unit, state_zip = target
    validate_state_zip(state_zip, course, unit)
    unit_dir = root / course / f"unit {unit}"
    reports_dir = unit_dir / "03 Student Packets" / "individual"
    if not reports_dir.is_dir():
        raise ValueError(f"Individual HTML reports were not found: {reports_dir}\nRun the local grading processor or install current results first.")
    chrome = find_chrome()
    if not chrome:
        raise ValueError("Google Chrome, Microsoft Edge, or Chromium was not found in /Applications. A Chromium-based browser is required for local PDF creation.")

    with tempfile.TemporaryDirectory(prefix="portfolio_email_state_") as td:
        td = Path(td)
        with __import__("zipfile").ZipFile(state_zip) as z:
            z.extractall(td)
        state_dir = td / "state"
        _fields, roster, _by = roster_rows(state_dir)
        active = [r for r in roster if r["active"] == "yes"]
        recipients, support = load_contacts(state_dir, root)

        email_root = unit_dir / "06 Email Delivery"
        current = email_root / "Current"
        archives = email_root / "Prepared Archives"
        email_root.mkdir(parents=True, exist_ok=True)
        archives.mkdir(parents=True, exist_ok=True)
        if current.exists() and any(current.iterdir()):
            archived = archives / timestamp()
            if archived.exists():
                shutil.rmtree(archived)
            current.rename(archived)
        current.mkdir(parents=True, exist_ok=True)
        pdf_dir = current / "PDFs"
        pdf_dir.mkdir(parents=True, exist_ok=True)

        jobs = []
        manifest_rows = []
        for s in active:
            sk = s["student_key"]
            html_file = reports_dir / f"{sk}.html"
            if not html_file.is_file():
                manifest_rows.append({
                    "student_key": sk, "student_name": s["display_name"], "period": s["period"],
                    "student_email": "", "guardian_emails": "", "support_staff_emails": "",
                    "pdf_file": "", "pdf_sha256": "", "identity_verified": "FALSE", "ready_to_send": "FALSE", "status": "MISSING_HTML_REPORT",
                })
                continue
            doc = html_file.read_text(encoding="utf-8", errors="ignore")
            identity_ok = s["display_name"] in doc
            safe = re.sub(r"[^A-Za-z0-9_-]+", "_", s["display_name"]).strip("_")
            pdf_file = pdf_dir / f"{sk}_{safe}_Unit{unit}_Portfolio.pdf"
            jobs.append((s, html_file, pdf_file, identity_ok))

        pdf_results = {}
        with ThreadPoolExecutor(max_workers=4) as ex:
            future_map = {ex.submit(print_pdf, chrome, h, p): (s, h, p, identity) for s, h, p, identity in jobs}
            for fut in as_completed(future_map):
                s, html_file, pdf_file, identity_ok = future_map[fut]
                try:
                    ok, msg = fut.result()
                except Exception as exc:
                    ok, msg = False, str(exc)
                pdf_results[s["student_key"]] = (ok, msg, pdf_file, identity_ok)

        for s, html_file, pdf_file, identity_ok in jobs:
            sk = s["student_key"]
            ok, msg, pdf_file, identity_ok = pdf_results[sk]
            rec = recipients.get(sk, {})
            support_emails = sorted(support.get(s["student_id"], set()))
            student_email = (rec.get("student_email") or "").strip()
            guardian = (rec.get("guardian_emails") or "").strip()
            has_recipient = bool(student_email or guardian or support_emails)
            ready = ok and identity_ok and has_recipient
            manifest_rows.append({
                "student_key": sk,
                "student_name": s["display_name"],
                "period": s["period"],
                "student_email": student_email,
                "guardian_emails": guardian,
                "support_staff_emails": "|".join(support_emails),
                "pdf_file": str(pdf_file.relative_to(current)) if ok else "",
                "pdf_sha256": sha256_file(pdf_file) if ok else "",
                "identity_verified": "TRUE" if identity_ok else "FALSE",
                "ready_to_send": "TRUE" if ready else "FALSE",
                "status": "READY" if ready else ("PDF_FAILED" if not ok else "IDENTITY_MISMATCH" if not identity_ok else "NO_RECIPIENT"),
            })

        manifest_path = current / "email_delivery_manifest.csv"
        fields = ["student_key","student_name","period","student_email","guardian_emails","support_staff_emails","pdf_file","pdf_sha256","identity_verified","ready_to_send","status"]
        with manifest_path.open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
            w.writeheader(); w.writerows(manifest_rows)
        ready_count = sum(r["ready_to_send"] == "TRUE" for r in manifest_rows)
        (current / "README.txt").write_text(
            f"Portfolio email preparation\nCourse: {course}\nUnit: {unit}\nPrepared PDFs: {sum(bool(r['pdf_file']) for r in manifest_rows)}\nReady recipient rows: {ready_count}\n\nThis folder is preparation only. No email was sent.\n",
            encoding="utf-8",
        )
        (current / "email_message_template.txt").write_text(
            f"Subject: {course} Unit {unit} Portfolio Progress Report\n\nAttached is the current {course} Unit {unit} Portfolio progress report. The report shows current Mastery Goal evidence, I Can status, and next practice/check steps.\n",
            encoding="utf-8",
        )
        print(f"Prepared {sum(bool(r['pdf_file']) for r in manifest_rows)} local PDF report(s).")
        print(f"{ready_count} row(s) have a PDF, verified identity, and at least one stored recipient.")
        print("No email was sent.")
        print(f"Email package: {current}")
        subprocess.run(["/usr/bin/open", str(current)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print("\nFAILED to prepare email delivery. No email was sent.\n")
        print(str(exc))
        raise
