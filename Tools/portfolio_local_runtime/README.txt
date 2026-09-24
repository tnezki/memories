PORTFOLIO LOCAL RUNTIME v2
==========================

PURPOSE
-------
Keep ChatGPT focused on evidence interpretation while the teacher's Mac owns deterministic Portfolio history, grades, reports, PowerSchool exports, roster maintenance, and email PDF preparation.

START ONCE PER COMPUTER SESSION
-------------------------------
Double-click:
  Tools/portfolio_local_runtime/Start Portfolio Local Companion.command

Keep that Terminal window open while using a course Portfolio Control Panel. The companion binds only to 127.0.0.1 on this Mac.

COURSE CONTROL PANELS
---------------------
Each course Portfolio panel is intentionally simple:
- fixed course name;
- Unit dropdown;
- top links: View Reports / Email Reports;
- Grade Evidence tab;
- Update Roster tab.

There is no normal current-state picker, Drive migration control, transfer control, or report-refresh checkbox. The local runtime already knows the authoritative path:
  _portfolio_data/<Course>/unit N/02 Portfolio Data/Portfolio_State_CURRENT.zip

NORMAL EVIDENCE WORKFLOW
------------------------
1. Start Portfolio Local Companion.command once.
2. Open the course Portfolio Control Panel.
3. Choose Unit and Grade Evidence.
4. Add only the new student evidence. Evidence label/date/note are optional.
5. Click Build Grading Request.
6. The local companion adds the exact current roster, learning map, prior I Can context, and state identity, creates portfolio_grading_request_*.zip in Downloads, and reveals it in Finder.
7. Upload that ZIP to ChatGPT.
8. ChatGPT returns ONE file: Portfolio_Grading_Result.json.
9. Download it to Downloads.
10. Double-click Apply Portfolio Grading Result.command.
11. Local Python validates the exact parent state; updates evidence history, I Can/MG status, intervention routing, state/version chain; builds canonical HTML reports and PowerSchool MG CSVs; runs identity/template QA; archives results/state; and refreshes folders 03-05.
12. Google Drive is not used.

UPDATE ROSTER
-------------
Use the Update Roster tab in the course control panel.
- Upload the current PowerSchool roster/template CSV file(s) for all sections of the course.
- Optional note only.
- Existing students/history are preserved.
- Missing students become inactive instead of being deleted.
- Added students receive current Unit I Can/MG rows with No Evidence / Not assessed.
- State version increments and current reports/PowerSchool exports refresh locally.
- When no local state exists and the course Unit has a registered learning map, the roster update initializes the first local state automatically. This supports AP Calculus AB Unit 1 first-run initialization without a visible state/reset control.

REPORTS
-------
The View Reports link opens the local companion report browser for the selected course/Unit. It exposes the current private local files only from:
- 03 Student Packets
- 04 Class & Intervention Summaries
- 05 PowerSchool Exports

EMAIL PREPARATION
-----------------
The Email Reports link opens the local email control panel.
- Click Prepare Email PDFs.
- Current individual HTML reports are converted locally to PDFs with Chrome/Edge/Chromium.
- Stable student identity is checked before a PDF is considered sendable.
- Stored student/guardian/support recipients are matched by durable student ID.
- Output goes to 06 Email Delivery/Current with PDFs + email_delivery_manifest.csv.
- Existing Current is archived under 06 Email Delivery/Prepared Archives.
- NO email is sent by this step.

FALLBACK COMMANDS
-----------------
These remain available if the browser control panel is not convenient:
- Build Portfolio Grading Request.command
- Apply Portfolio Grading Result.command
- Prepare Portfolio Emails.command

SAFETY
------
- The local companion listens only on 127.0.0.1.
- Student data stays under _portfolio_data or the teacher's private Downloads grading request/result files.
- _portfolio_data must never be initialized as a Git repository or committed.
- ChatGPT does not calculate longitudinal state or render routine reports in the normal fast-grading path.
- Apply refuses a grading result built from a different state SHA/version/id.
- State/results installs are transactional and historical copies remain archived.

CURRENT UNIT SUPPORT
--------------------
- Algebra 1 Unit 1: current local state supported.
- Physics Unit 1: current local state supported; student report is locked to the same Algebra-approved canonical visual system including the Practice Builder link box and QR.
- AP Calculus AB Unit 1: roster initialization can create its first local state; no Practice Builder QR/link is fabricated until an approved route exists.

END
