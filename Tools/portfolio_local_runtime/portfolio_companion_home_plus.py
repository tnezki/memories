#!/usr/bin/env python3
from __future__ import annotations

import html
import json
import subprocess
import threading
import urllib.parse

import portfolio_companion as core
import portfolio_companion_live as live
import portfolio_support_contacts as support_contacts


def button(label: str, href: str, secondary: bool = False, target: str = "") -> str:
    return live.nav_button(label, href, secondary, target)


def maintenance_card() -> str:
    return (
        '<div class="card">'
        '<h2>Portfolio Maintenance</h2>'
        '<p class="muted">Shared setup used by the course Portfolios.</p>'
        '<div class="row">'
        f'{button("Contacts & Support", "/contacts-support")}'
        f'{button("Update Roster", "/update-roster", True)}'
        '</div></div>'
    )


def contacts_page() -> str:
    body = '''
<div class="row"><a class="buttonlink secondary" href="/">Portfolio Home</a></div>
<h1>Contacts & Support</h1>
<p class="muted">Maintain the local student-to-support-staff directory used when Portfolio reports are emailed. This file stays under <code>_portfolio_data</code>.</p>
<div class="card">
  <div id="summary" class="notice muted">Loading current support contacts...</div>
  <div id="current"></div>
</div>
<div class="card">
  <h2>Update support contacts</h2>
  <p class="muted">Upload CSV/TSV/TXT or paste student-to-staff mappings. Merge is safest for normal updates.</p>
  <label>File</label><input id="supportFile" type="file" accept=".csv,.tsv,.txt,text/csv,text/plain">
  <label>Paste mappings <span class="muted">(optional)</span></label><textarea id="pasted" placeholder="Student, staff name, staff email, role"></textarea>
  <label>Update mode</label><select id="mode"><option value="merge" selected>Merge with current contacts</option><option value="replace">Replace current contacts</option></select>
  <div class="row"><button id="save">Update Contacts</button></div>
  <div id="status" class="notice muted">No changes made.</div>
</div>
<script>
function esc(s){return String(s??'').replace(/[&<>\"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','\"':'&quot;'}[c]))}
async function load(){
  const r=await fetch('/api/support-contacts',{cache:'no-store'});const d=await r.json();
  const sum=document.getElementById('summary');
  if(!r.ok||d.status!=='PASS'){sum.className='notice bad';sum.textContent=d.message||'Could not load contacts.';return}
  sum.className='notice good';sum.textContent=`${d.active_count} active support assignment(s) · ${d.row_count} total row(s)`;
  const rows=d.rows||[];
  document.getElementById('current').innerHTML=rows.length?'<div style="overflow:auto"><table style="width:100%;border-collapse:collapse;margin-top:12px"><thead><tr><th align="left">Student</th><th align="left">Staff</th><th align="left">Email</th><th align="left">Role</th><th align="left">Active</th></tr></thead><tbody>'+rows.map(x=>`<tr><td style="padding:6px;border-top:1px solid #e3e8ef">${esc(x.student_name||x.student_id)}</td><td style="padding:6px;border-top:1px solid #e3e8ef">${esc(x.staff_name)}</td><td style="padding:6px;border-top:1px solid #e3e8ef">${esc(x.staff_email)}</td><td style="padding:6px;border-top:1px solid #e3e8ef">${esc(x.role)}</td><td style="padding:6px;border-top:1px solid #e3e8ef">${esc(x.active)}</td></tr>`).join('')+'</tbody></table></div>':'<p class="muted">No support contacts saved yet.</p>';
}
document.getElementById('save').onclick=async()=>{
  const fd=new FormData();const f=document.getElementById('supportFile').files[0];if(f)fd.append('support',f,f.name);fd.append('pasted',document.getElementById('pasted').value);fd.append('mode',document.getElementById('mode').value);
  const st=document.getElementById('status');st.className='notice';st.textContent='Updating local support contacts...';
  const r=await fetch('/api/support-contacts',{method:'POST',body:fd});const d=await r.json();
  if(!r.ok||d.status!=='PASS'){st.className='notice bad';st.textContent=d.message||'Update failed.';return}
  st.className='notice good';st.textContent=`Saved ${d.row_count} row(s); ${d.active_count} active.`;document.getElementById('supportFile').value='';document.getElementById('pasted').value='';load();
};
load();
</script>'''
    return live.page_shell("Contacts & Support", body)


def roster_page() -> str:
    courses = ''.join(f'<option value="{html.escape(c)}">{html.escape(c)}</option>' for c in core.COURSE_CONFIG)
    units = ''.join(f'<option value="{n}">Unit {n}</option>' for n in range(1, 9))
    body = f'''
<div class="row"><a class="buttonlink secondary" href="/">Portfolio Home</a></div>
<h1>Update Roster</h1>
<p class="muted">Upload current PowerSchool roster/template CSV files. Existing Portfolio history stays intact; students missing from the new roster become inactive.</p>
<div class="card">
  <div class="grid2"><div><label>Course</label><select id="course">{courses}</select></div><div><label>Unit</label><select id="unit">{units}</select></div></div>
  <label>Current roster CSV file(s)</label><input id="files" type="file" multiple accept=".csv,text/csv">
  <label>Optional note</label><textarea id="note"></textarea>
  <div class="row"><button id="update">Update Roster Locally</button></div>
  <div id="status" class="notice muted">Choose the current roster CSV file(s).</div>
</div>
<script>
document.getElementById('update').onclick=async()=>{{
  const files=document.getElementById('files').files;const st=document.getElementById('status');if(!files.length){{st.className='notice bad';st.textContent='Choose at least one roster CSV file.';return}}
  const fd=new FormData();fd.append('course',document.getElementById('course').value);fd.append('unit',document.getElementById('unit').value);fd.append('note',document.getElementById('note').value.trim());for(const f of files)fd.append('roster',f,f.name);
  st.className='notice';st.textContent='Updating roster and rebuilding current reports...';const r=await fetch('/api/update-roster',{{method:'POST',body:fd}});const d=await r.json();if(!r.ok||d.status!=='PASS'){{st.className='notice bad';st.textContent=d.message||'Roster update failed.';return}}st.className='notice good';st.textContent=`Roster updated. Active students: ${{d.active_roster}} · State v${{d.state_version}}.`;
}};
</script>'''
    return live.page_shell("Update Roster", body)


class Handler(live.Handler):
    server_version = "PortfolioLocalCompanion/2.5-authoritative"

    def home_page(self) -> str:
        cards = ''.join(live.course_card(course) for course in live.base.core.COURSE_CONFIG)
        intro = '<p class="lead">Private local Portfolio work. New Evidence, Teacher Observations, reports, and email preparation all live here.</p>'
        return live.base.core.page("Portfolio Local Companion", intro + maintenance_card() + cards)

    def do_GET(self) -> None:
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == '/contacts-support':
            self.send_html(contacts_page()); return
        if parsed.path == '/update-roster':
            self.send_html(roster_page()); return
        if parsed.path == '/api/support-contacts':
            try:
                self.send_json(support_contacts.api_payload())
            except Exception as exc:
                self.send_json({'status':'FAIL','message':str(exc)}, status=400)
            return
        super().do_GET()

    def do_POST(self) -> None:
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == '/api/support-contacts':
            try:
                fields, files = core.parse_form(self)
                pasted = core.one(fields, 'pasted', '')
                mode = core.one(fields, 'mode', 'merge')
                result = support_contacts.update_from_sources(files.get('support', []), pasted, replace=(mode == 'replace'))
                result['status'] = 'PASS'
                self.send_json(result)
            except Exception as exc:
                self.send_json({'status':'FAIL','message':str(exc)}, status=400)
            return
        super().do_POST()


def main() -> int:
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument('--port', type=int, default=live.base.core.PORT)
    ap.add_argument('--no-open', action='store_true')
    args = ap.parse_args()
    server = live.base.core.ThreadingHTTPServer((live.base.core.HOST, args.port), Handler)
    url = f'http://{live.base.core.HOST}:{args.port}/'
    print('Portfolio Local Companion is running.')
    print('Runtime: 2.5 authoritative + maintenance navigation')
    print(f'Local URL: {url}')
    print(f'Workspace root: {live.base.core.github_root_from_runtime()}')
    print('Private Portfolio data remains under sibling _portfolio_data.')
    print('Press Control-C to stop this foreground instance.\\n')
    if not args.no_open:
        threading.Timer(0.5, lambda: subprocess.run(['/usr/bin/open', url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\\nPortfolio Local Companion stopped.')
    finally:
        server.server_close()
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
