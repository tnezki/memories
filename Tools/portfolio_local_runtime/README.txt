PORTFOLIO LOCAL RUNTIME v3.5
============================

PURPOSE
-------
Keep ChatGPT focused on evidence interpretation while the teacher's Mac owns deterministic Portfolio history, class-opportunity counts, I Can progress, Mastery Goal report/PowerSchool status, intervention routing, reports, archives, roster maintenance, teacher-observation evidence, and selected-student email preparation.

CURRENT PROGRESS MODEL
----------------------
Read:
  Tools/PORTFOLIO_PROGRESS_MODEL_CONTRACT.json
  pms_build/portfolio_progress_model.txt

Current I Can progress is:
  Not Yet Assessed -> Started -> Developing -> Progressing -> Mastered -> Extended

Partial understanding counts when it shows the core idea. One solid independent demonstration or sufficiently consistent partial evidence can reach Progressing. Two independent convincing demonstrations reach Mastered.

The old visible/exported I / In Progress Mastery Goal grade is retired. Falling Behind is a support signal and can still have a blank PowerSchool score when meaningful growth is visible. F requires 2+ class assessment opportunities plus no meaningful growth.

NORMAL START
------------
Open:
  Tools/student_data_tools/Student Data Tools.app

Student Data Tools is the normal private-work launcher. It stops stale Portfolio runtime processes, closes only stale Student Data Tools / Portfolio Terminal windows, starts one fresh Portfolio Local Companion in Terminal, verifies the localhost health endpoint, opens the numbered private landing page, and minimizes the fresh runtime Terminal after health check.

Fallback only:
  Tools/portfolio_local_runtime/Start Portfolio Local Companion.command

The companion listens only on 127.0.0.1:8765 and runs in the interactive Terminal session. Keep that Terminal process running while using Portfolio; it may be minimized.

IMPORTANT MACOS PRIVACY RULE
----------------------------
Do NOT install the companion as a LaunchAgent/login helper while the GitHub and _portfolio_data folders live under ~/Documents. macOS privacy controls can deny background launchd/Python processes access to Documents even when the same files work normally from Terminal.

If macOS blocks the interactive process, enable Terminal access under:
  System Settings > Privacy & Security > Files and Folders > Terminal > Documents Folder
then reopen Student Data Tools.

HEALTH CHECK
------------
Student Data Tools does not report the local Portfolio runtime as ready until:
  http://127.0.0.1:8765/api/runtime-version
returns status PASS.

If the health check fails, the Terminal window remains visible so the startup error can be read directly.

COURSE CONTROL PANELS
---------------------
Each course Portfolio panel is intentionally simple:
- fixed course name;
- Unit dropdown;
- top buttons: View Reports / Email Reports;
- Grade Evidence tab;
- Teacher Observations tab;
- Update Roster tab.

There is no normal current-state picker, Drive migration control, transfer control, or report-refresh checkbox. The local runtime already knows the authoritative path:
  _portfolio_data/<Course>/unit N/02 Portfolio Data/Portfolio_State_CURRENT.zip

NORMAL EVIDENCE WORKFLOW
------------------------
1. Open Student Data Tools for the work session.
2. Choose New Evidence and open the course Portfolio Control Panel.
3. Choose Unit and Grade Evidence.
4. Add only the new student evidence. Evidence label/date/note are optional.
5. Click Build Grading Request.
6. The local companion adds exact current roster, learning map, prior I Can context, and state identity; creates portfolio_grading_request_*.zip in Downloads; and reveals it in Finder.
7. Upload that ZIP to ChatGPT.
8. ChatGPT returns the declared Portfolio grading-result artifact.
9. Download it to Downloads.
10. Double-click Apply Portfolio Grading Result.command.
11. Local Python validates the exact parent state; updates the evidence ledger, class-opportunity counts, I Can progress, Mastery Goal status/PowerSchool score, intervention routing, state/version chain; builds canonical reports/PowerSchool MG CSVs; runs identity/template QA; archives results/state; and refreshes folders 03-05.
12. Normal grading/state/report work does not use Google Drive.

TEACHER OBSERVATIONS
--------------------
Direct teacher observations remain longitudinal student evidence. One classroom observation session is one opportunity per student/I Can. Repeated checks from the same moment/session do not become extra independent opportunities.

Teacher observations do NOT advance the formal class assessment-opportunity clock used for Started/Falling Behind/F timing.

UPDATE ROSTER
-------------
Use the Update Roster tab in the course control panel.
- Upload the current PowerSchool roster/template CSV file(s) for all sections of the course.
- Existing students/history are preserved.
- Missing students become inactive instead of being deleted.
- Added students receive current Unit rows and are deterministically placed at Not Yet Assessed or Started according to current class opportunities.
- State version increments and current reports/PowerSchool exports refresh locally.

REPORTS
-------
Teacher observations and roster updates already rebuild current reports automatically. View Reports also includes a manual Refresh Reports from Current State button. This is a report-only rebuild and never adds evidence or increments the state version.

The approved student report remains the same two-page structure with only the current minimal changes:
- Status guide replaces the old Mastery Goal snapshot panel;
- the Status guide is text-only;
- each I Can shows a five-segment progress bar + status word;
- the old visible Next line is removed;
- each MG card has one equal-size status/grade box at the upper right;
- page 2 shows the four most recent assessed evidence events when available;
- the existing Your Practice / Practice Builder / Current focus structure remains.

PowerSchool CSVs contain only F/C/B/A/A+ or blank. They never export I and never export an overall Unit grade.

EMAIL PREPARATION / LIVE-SENDER PACKAGE
----------------------------------------
The Email Reports button opens the local email control panel.
- Select students and enter optional class/student notes.
- Click Prepare Selected PDFs.
- Only selected students' current individual reports are converted locally to identity-verified PDFs.
- The local runtime creates Portfolio_Email_Sender_Package.zip from current local state/recipients/reports only.
- Student-specific notes are cleared locally after the package is built; the weekly/class note may remain.
- Finder reveals/highlights the exact Portfolio_Email_Sender_Package.zip and the configured sender page opens.
- NO email is sent by local preparation.

In the Google Apps Script sender, choose the highlighted ZIP, Load Local Package, review/recheck, optionally Send Test to Me, then explicitly use LIVE SEND.

FALLBACK COMMANDS
-----------------
These remain available if the browser control panel is not convenient:
- Build Portfolio Grading Request.command
- Apply Portfolio Grading Result.command
- Prepare Portfolio Emails.command
- Start Portfolio Local Companion.command

SAFETY
------
- The local companion listens only on 127.0.0.1.
- Student data stays under _portfolio_data or the teacher's private grading request/result files.
- _portfolio_data must never be initialized as a Git repository or committed.
- ChatGPT does not calculate longitudinal state or render routine reports in the normal fast-grading path.
- Apply refuses a grading result built from a different state SHA/version/id.
- State/results installs are transactional and historical copies remain archived.
- Curriculum Transfer may update Portfolio software/contracts but must never carry student-specific Portfolio data.

CURRENT UNIT SUPPORT
--------------------
- Algebra 1 Unit 1: current local state supported.
- Physics Unit 1: current local state supported and uses the shared Portfolio progress/report model while preserving exact Physics learning authority.
- AP Calculus AB Unit 1: roster initialization can create its first local state; no Practice Builder route is fabricated until one is approved.

END
