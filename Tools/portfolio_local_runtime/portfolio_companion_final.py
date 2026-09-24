#!/usr/bin/env python3
from __future__ import annotations

import html
import subprocess
import threading
import urllib.parse
from pathlib import Path

import portfolio_companion as base


class Handler(base.Handler):
    """Final Portfolio local UI shell.

    The base companion owns state/evidence/report/email logic. This subclass keeps
    the teacher-facing report hub intentionally simple and uses the current
    email-review layout from the base companion.
    """

    server_version = "PortfolioLocalCompanion/1.5-final"

    def reports_page(self, course: str, unit: int) -> str:
        rebuilt = base.ensure_current_html_reports(course, unit)
        st = base.state_status(course, unit)
        u = base.unit_dir(course, unit)
        dashboard = base.teacher_dashboard_url(course)
        roster = base.observation_data(course, unit)

        q_course = urllib.parse.quote(course)
        student_dir = u / "03 Student Packets"
        individual_dir = student_dir / "individual"
        teacher_dir = u / "04 Class & Intervention Summaries"
        powerschool_dir = u / "05 PowerSchool Exports"

        def file_url(rel: str) -> str:
            return f"/file?course={q_course}&unit={unit}&path={urllib.parse.quote(rel)}"

        body: list[str] = [
            '<div class="row">'
            f'<a class="buttonlink secondary" href="{html.escape(dashboard)}" target="_blank">Back to {html.escape(course)} Teacher Dashboard</a>'
            '<button id="refreshReports" type="button">Refresh Reports from Current State</button>'
            '</div>',
            f'<p class="lead"><b>{html.escape(course)} - Unit {unit}</b> &nbsp; State v{st.get("state_version") if st.get("state_ready") else "not initialized"}</p>',
            '<div id="refreshStatus" class="notice muted">Teacher observations and grading runs already refresh reports automatically. Use this only when you want a clean report-only rebuild.</div>',
        ]
        if rebuilt:
            body.append('<div class="notice good">Current HTML reports were rebuilt from the installed local Portfolio state. No evidence, grades, or state version changed.</div>')

        # Student reports: teacher-facing names, never raw student-key filenames.
        body.append('<div class="card"><h2>Student Reports</h2>')
        combined = student_dir / "class_student_packet.html"
        if combined.is_file():
            body.append(f'<p><a class="buttonlink" href="{file_url("03 Student Packets/class_student_packet.html")}" target="_blank">Open Combined Class Student Reports</a></p>')
        by_period: dict[str, list[dict]] = {}
        for student in roster.get("students", []):
            by_period.setdefault(student.get("period", ""), []).append(student)
        any_student = False
        for period in roster.get("periods", []):
            links = []
            for student in by_period.get(period, []):
                sk = student.get("student_key", "")
                report = individual_dir / f"{sk}.html"
                if not report.is_file():
                    continue
                any_student = True
                rel = f"03 Student Packets/individual/{sk}.html"
                links.append(f'<a class="student-report-link" href="{file_url(rel)}" target="_blank">{html.escape(student.get("student_name", sk))}</a>')
            if links:
                body.append(f'<h3>{html.escape(period)}</h3><div class="student-report-grid">{"".join(links)}</div>')
        if not any_student:
            body.append('<p class="muted">No current individual HTML reports were found.</p>')
        body.append(f'<p class="folder-note"><a href="/open-folder?course={q_course}&unit={unit}&kind=student" target="_blank">Reveal Student Reports folder in Finder</a></p></div>')

        # Teacher report: canonical HTML only. Legacy seeded PDFs remain on disk but are hidden here.
        body.append('<div class="card"><h2>Teacher Report</h2>')
        teacher_html = teacher_dir / "teacher_summary.html"
        if teacher_html.is_file():
            body.append(f'<p><a class="buttonlink" href="{file_url("04 Class & Intervention Summaries/teacher_summary.html")}" target="_blank">Open Current Teacher Summary</a></p>')
        else:
            body.append('<p class="muted">No current teacher HTML report was found.</p>')
        body.append(f'<p class="folder-note"><a href="/open-folder?course={q_course}&unit={unit}&kind=teacher" target="_blank">Reveal Teacher Report folder in Finder</a></p></div>')

        # PowerSchool: do not clutter the hub with individual CSV links.
        body.append('<div class="card"><h2>PowerSchool Exports</h2>')
        rel_folder = f'_portfolio_data/{course}/unit {unit}/05 PowerSchool Exports'
        csv_count = len(list(powerschool_dir.glob("*.csv"))) if powerschool_dir.is_dir() else 0
        body.append(
            f'<p><b>Already local.</b> You do not need to download these from this page. When PowerTeacher asks for the import file, open <code>{html.escape(rel_folder)}</code>.</p>'
            f'<p class="muted">{csv_count} current CSV export(s) are in that folder.</p>'
            f'<p><a class="buttonlink secondary" href="/open-folder?course={q_course}&unit={unit}&kind=powerschool" target="_blank">Reveal PowerSchool Exports in Finder</a></p>'
        )
        body.append('</div>')

        script = f'''<script>
        document.getElementById('refreshReports').addEventListener('click',async()=>{{
          const b=document.getElementById('refreshReports'),st=document.getElementById('refreshStatus');
          b.disabled=true;st.className='notice';st.textContent='Rebuilding current reports from state...';
          const fd=new FormData();fd.append('course',{course!r});fd.append('unit',{str(unit)!r});
          try{{const r=await fetch('/api/refresh-reports',{{method:'POST',body:fd}});const d=await r.json();if(!r.ok||d.status!=='PASS')throw new Error(d.message||'Refresh failed');st.className='notice good';st.textContent=d.message;setTimeout(()=>location.reload(),650)}}
          catch(e){{st.className='notice bad';st.textContent=e.message;b.disabled=false}}
        }});
        </script>'''

        doc = base.page(f"{course} Unit {unit} Reports", ''.join(body) + script)
        extra_css = '''<style>
        .student-report-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:8px 12px;margin:8px 0 14px}
        .student-report-link{display:block;padding:8px 10px;border:1px solid #d5dce5;border-radius:8px;background:#f8fafc;text-decoration:none}
        .student-report-link:hover{background:#eef5fb}.folder-note{margin-top:14px}.folder-note a{font-size:13px}
        @media(max-width:760px){.student-report-grid{grid-template-columns:1fr 1fr}}
        </style>'''
        return doc.replace('</head>', extra_css + '</head>', 1)


def main() -> int:
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=base.PORT)
    ap.add_argument("--no-open", action="store_true")
    args = ap.parse_args()

    server = base.ThreadingHTTPServer((base.HOST, args.port), Handler)
    url = f"http://{base.HOST}:{args.port}/"
    print("Portfolio Local Companion is running.")
    print("Runtime: final-ui-1.5")
    print(f"Local URL: {url}")
    print("Teacher observations and grading runs refresh reports automatically.")
    print("The helper is local to this Mac and does not expose Portfolio data to the network.")
    print("Press Control-C to stop this foreground instance.\n")

    if not args.no_open:
        threading.Timer(
            0.5,
            lambda: subprocess.run(
                ["/usr/bin/open", url],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            ),
        ).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nPortfolio Local Companion stopped.")
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
