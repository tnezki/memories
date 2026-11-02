#!/usr/bin/env python3
"""Student Data Tools entry point with permanent student/family contact storage.

This extends the current Portfolio maintenance UI without changing evidence,
report generation, sender verification, or support staff contact handling.
"""
from __future__ import annotations

import subprocess
import threading
import urllib.parse

import portfolio_companion as core
import portfolio_companion_home_plus as base
import portfolio_recipient_contacts as family
import prepare_portfolio_emails as email_prepare

# The existing email review and email preparation routes use two references to
# the same loader. Wrap both so all current-unit reports resolve the saved
# cross-unit directory. Existing state contacts remain a fallback.
_prior_load_contacts = email_prepare.load_contacts


def saved_load_contacts(state_dir, root):
    recipients, support = _prior_load_contacts(state_dir, root)
    return family.merge_recipients(state_dir, root, recipients), support


email_prepare.load_contacts = saved_load_contacts
core.load_contacts = saved_load_contacts

# Match the email review readiness to the existing sender's requirement that
# every outgoing message has a valid student To address. Parent-only rows are
# saved but shown as needing attention rather than falsely marked READY.
_prior_email_review_data = core.email_review_data


def email_review_with_student_address_check(course: str, unit: int):
    data = _prior_email_review_data(course, unit)
    for row in data.get("rows", []):
        if not family.EMAIL_RE.fullmatch(str(row.get("student_email") or "").strip().lower()):
            row.setdefault("issues", []).append("Valid student email required by sender")
            row["status"] = "CHECK"
    return data


core.email_review_data = email_review_with_student_address_check


def family_page() -> str:
    body = '''
<div class="row"><a class="buttonlink secondary" href="/">Portfolio Home</a><a class="buttonlink secondary" href="/support-staff-contacts">Support-staff Contacts</a></div>
<h1>Student &amp; Family Contacts</h1>
<p class="lead">Save your class contacts <b>once</b>. Every unit's Email Reports page will use this private, local directory. New assessment results or a roster update will not erase it.</p>
<div class="card">
  <h2>1. Upload class contacts once</h2>
  <p>Import a CSV or TSV containing student IDs or uniquely matched student names plus parent/guardian emails. Student emails may come from the saved unit roster, but the email sender requires a valid student email to send. Re-importing merges addresses; existing saved contacts are not deleted.</p>
  <label for="contactFile">Student / parent contact file(s)</label>
  <input id="contactFile" type="file" multiple accept=".csv,.tsv,.txt,text/csv,text/tab-separated-values,text/plain">
  <div class="row"><button type="button" id="importContacts">Import &amp; Save Contacts</button></div>
  <div id="importStatus" class="notice muted">Saved locally, not in GitHub. Email is never sent during import.</div>
  <details><summary>Accepted column headings and sample layout</summary>
  <p class="muted">Use <b>Student ID</b>, <b>Student Name</b>, <b>Parent Email</b>, and optionally <b>Student Email</b>, <b>Parent Name</b>, <b>Parent Email 2</b>. Multiple guardian addresses may be separated with a semicolon or vertical bar. Rows without an ID are accepted only when the name matches exactly one student in the existing local rosters.</p>
  <div class="notice muted"><code>Student ID,Student Name,Parent Email,Parent Email 2,Student Email</code></div></details>
</div>
<div class="card">
  <h2>2. Add a new student or update a parent contact</h2>
  <p>Add new students here as they enroll, or select an existing row below to edit. The Student ID must match the ID used by Portfolio. Adding a contact does <b>not</b> add a student to the class roster or change grades.</p>
  <form id="manualForm">
  <div class="grid2">
    <div><label for="sid">Student ID *</label><input id="sid" name="student_id" required autocomplete="off" placeholder="District student ID"></div>
    <div><label for="sname">Student name</label><input id="sname" name="student_name" autocomplete="off" placeholder="First Last"></div>
    <div><label for="semail">Student email (required by sender)</label><input id="semail" name="student_email" type="email" autocomplete="off" placeholder="student@school.org"></div>
    <div><label for="gnames">Parent/guardian name(s) (optional)</label><input id="gnames" name="guardian_names" autocomplete="off" placeholder="Parent / Guardian"></div>
  </div>
  <label for="gemails">Parent/guardian email(s) *</label>
  <textarea id="gemails" name="guardian_emails" rows="2" required placeholder="parent@example.com; secondparent@example.com"></textarea>
  <label for="active">Use saved contacts for report delivery</label>
  <select id="active" name="active"><option value="yes">Yes</option><option value="no">No - withhold saved family addresses</option></select>
  <div class="row"><button type="submit" id="saveStudent">Save Student Contact</button><button type="button" id="clearStudent" class="secondary">Clear Form</button></div>
  <div id="manualStatus" class="notice muted">New student or edit: save before leaving.</div>
  </form>
</div>
<div class="card">
  <h2>Saved student and family contacts</h2>
  <div id="familySummary" class="notice muted">Loading saved contacts...</div>
  <div id="familyTable"></div>
  <p class="muted">Only matched student IDs in the current Portfolio roster can receive reports. The sender requires a valid student email, even when parent emails are saved. Review all recipients before LIVE SEND.</p>
</div>
<div class="card"><h2>Support staff contacts</h2><p>Case managers and support teachers are managed separately from family emails. <a href="/support-staff-contacts">Open support-staff directory</a>.</p></div>
<style>
#manualForm input,#manualForm select,#manualForm textarea,#contactFile{width:100%;max-width:100%;box-sizing:border-box;font:inherit;border:1px solid #bcc8d5;border-radius:7px;padding:9px;background:#fff}
#manualForm label,.card label{display:block;margin:12px 0 5px;font-weight:700}
#familyTable{overflow:auto}#familyTable table{width:100%;border-collapse:collapse;margin-top:12px;font-size:13px;min-width:620px}
#familyTable th,#familyTable td{padding:8px;text-align:left;border-bottom:1px solid #e0e6ed;vertical-align:top}
#familyTable th{background:#eef3f8}#familyTable button{padding:5px 9px}summary{cursor:pointer;margin-top:10px;font-weight:700}
</style>
<script>
const $=id=>document.getElementById(id);
const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
let familyRows=[];
function message(id,msg,ok){const el=$(id);el.className='notice '+(ok?'good':'bad');el.textContent=msg;}
async function loadFamily(){
  try{const r=await fetch('/api/family-contacts',{cache:'no-store'});const d=await r.json();if(!r.ok||d.status!=='PASS')throw Error(d.message||'Could not load contacts');
  familyRows=d.rows||[];$('familySummary').className='notice good';$('familySummary').textContent=`${familyRows.length} student(s) in the permanent local directory`;
  $('familyTable').innerHTML=familyRows.length?'<table><thead><tr><th>Student</th><th>Student email</th><th>Parent / guardian contact</th><th>Use</th><th></th></tr></thead><tbody>'+familyRows.map((x,i)=>`<tr><td><b>${esc(x.student_name||'No name')}</b><div>${esc(x.student_id)}</div></td><td>${esc(x.student_email||'—')}</td><td>${esc(x.guardian_names||'')}<div>${esc((x.guardian_emails||'').replaceAll('|',', '))}</div></td><td>${x.active==='yes'?'Yes':'No'}</td><td><button type="button" data-edit="${i}" class="secondary">Edit</button></td></tr>`).join('')+'</tbody></table>':'<p class="muted">No family contacts stored. Start with the upload above or add a student manually.</p>';
  $('familyTable').querySelectorAll('[data-edit]').forEach(b=>b.onclick=()=>{const x=familyRows[Number(b.dataset.edit)];$('sid').value=x.student_id;$('sname').value=x.student_name;$('semail').value=x.student_email;$('gnames').value=x.guardian_names;$('gemails').value=(x.guardian_emails||'').replaceAll('|','; ');$('active').value=x.active;window.scrollTo({top:$('manualForm').getBoundingClientRect().top+window.scrollY-90,behavior:'smooth'});$('sid').focus();});
  }catch(e){message('familySummary',e.message,false)}
}
$('importContacts').onclick=async()=>{const fs=$('contactFile').files;if(!fs.length){message('importStatus','Choose a CSV or TSV file first.',false);return}const btn=$('importContacts');btn.disabled=true;const fd=new FormData();for(const f of fs)fd.append('contacts',f,f.name);try{const r=await fetch('/api/family-contacts/import',{method:'POST',body:fd});const d=await r.json();if(!r.ok||d.status!=='PASS')throw Error(d.message||'Import failed');message('importStatus',d.message+' Saved total: '+d.stored_count+'.',true);$('contactFile').value='';await loadFamily()}catch(e){message('importStatus',e.message,false)}finally{btn.disabled=false}};
$('manualForm').onsubmit=async e=>{e.preventDefault();const btn=$('saveStudent');btn.disabled=true;try{const fd=new FormData($('manualForm'));const r=await fetch('/api/family-contacts/save',{method:'POST',body:fd});const d=await r.json();if(!r.ok||d.status!=='PASS')throw Error(d.message||'Save failed');message('manualStatus',d.message,true);$('manualForm').reset();await loadFamily()}catch(e){message('manualStatus',e.message,false)}finally{btn.disabled=false}};
$('clearStudent').onclick=()=>{$('manualForm').reset();$('manualStatus').className='notice muted';$('manualStatus').textContent='New student or edit: save before leaving.'};
loadFamily();
</script>'''
    return base.live.page_shell("Student & Family Contacts", body)


class Handler(base.Handler):
    server_version = "PortfolioLocalCompanion/2.6-saved-family-contacts"

    def email_page(self, course: str, unit: int) -> str:
        doc = super().email_page(course, unit)
        anchor = '<a class="buttonlink" href="/open-email-sender"'
        if anchor in doc:
            doc = doc.replace(anchor, '<a class="buttonlink" href="/contacts-support" style="margin-left:8px">Manage Student &amp; Parent Contacts</a>' + anchor, 1)
        return doc

    def _allow_local_origin(self) -> bool:
        origin = self.headers.get("Origin", "")
        if not origin:
            return True
        parsed = urllib.parse.urlsplit(origin)
        return parsed.scheme == "http" and parsed.hostname in {"127.0.0.1", "localhost"} and parsed.port == self.server.server_port

    def do_GET(self) -> None:
        path = urllib.parse.urlparse(self.path).path
        if path in {"/contacts-support", "/support-staff-contacts", "/api/family-contacts"}:
            if not self._allow_local_origin():
                self.send_json({"status": "FAIL", "message": "Local application origin required."}, status=403)
                return
            try:
                if path == "/contacts-support":
                    self.send_html(family_page())
                elif path == "/support-staff-contacts":
                    self.send_html(base.contacts_page())
                else:
                    self.send_json(family.api_payload())
            except Exception as exc:
                self.send_json({"status": "FAIL", "message": str(exc)}, status=400)
            return
        super().do_GET()

    def do_POST(self) -> None:
        path = urllib.parse.urlparse(self.path).path
        if path in {"/api/family-contacts/import", "/api/family-contacts/save"}:
            if not self._allow_local_origin():
                self.send_json({"status": "FAIL", "message": "Local application origin required."}, status=403)
                return
            try:
                if int(self.headers.get("Content-Length") or 0) > 4 * 1024 * 1024:
                    raise ValueError("Contact upload is too large (4 MB maximum).")
                fields, files = core.parse_form(self)
                if path.endswith("/import"):
                    result = family.import_files(files.get("contacts", []))
                else:
                    result = family.save_manual({key: core.one(fields, key) for key in family.FIELDS})
                self.send_json(result)
            except Exception as exc:
                self.send_json({"status": "FAIL", "message": str(exc)}, status=400)
            return
        super().do_POST()


def main() -> int:
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=core.PORT)
    ap.add_argument("--no-open", action="store_true")
    args = ap.parse_args()
    server = core.ThreadingHTTPServer((core.HOST, args.port), Handler)
    url = f"http://{core.HOST}:{args.port}/"
    print("Portfolio Local Companion is running.")
    print("Runtime: 2.6 authoritative + persistent family contacts")
    print(f"Local URL: {url}")
    print("Private student/family contacts remain under _portfolio_data.")
    print("Press Control-C to stop this foreground instance.\n")
    if not args.no_open:
        threading.Timer(0.5, lambda: subprocess.run(["/usr/bin/open", url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nPortfolio Local Companion stopped.")
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
