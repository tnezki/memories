PORTFOLIO LOCAL RUNTIME v3
==========================

PURPOSE
-------
Keep ChatGPT focused on evidence interpretation while the teacher's Mac owns deterministic Portfolio history, grades, reports, PowerSchool exports, roster maintenance, teacher-observation evidence, and selected-student email PDF preparation.

START ONCE PER COMPUTER
-----------------------
Double-click:
  Tools/portfolio_local_runtime/Start Portfolio Local Companion.command

The launcher installs/refreshes a private macOS login helper bound only to 127.0.0.1:8765, starts it, and opens the local companion page. After it reports Ready, the Terminal window may be closed. The helper restarts automatically for that user on future logins.

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

If the local companion is offline, the top report/email buttons do not open a dead localhost page. The panel instead shows the Start Portfolio Local Companion.command instruction.

NORMAL EVIDENCE WORKFLOW
------------------------
1. Open the course Portfolio Control Panel.
2. Choose Unit and Grade Evidence.
3. Add only the new student evidence. Evidence label/date/note are optional.
4. Click Build Grading Request.
5. The local companion adds exact current roster, learning map, prior I Can context, and state identity; creates portfolio_grading_request_*.zip in Downloads; and reveals it in Finder.
6. Upload that ZIP to ChatGPT.
7. ChatGPT returns ONE file: Portfolio_Grading_Result.json.
8. Download it to Downloads.
9. Double-click Apply Portfolio Grading Result.command.
10. Local Python validates the exact parent state; updates evidence history, I Can/MG status, intervention routing, state/version chain; builds canonical HTML reports and PowerSchool MG CSVs; runs identity/template QA; archives results/state; and refreshes folders 03-05.
11. Google Drive is not used.

TEACHER OBSERVATIONS
--------------------
The Teacher Observations tab supports three paths.

A. DIRECT ENTRY
- Choose Hour/period.
- Choose student.
- Select one or more exact current I Can statements.
- Evidence strength defaults to CONVINCING = observed them do it; Partial/Limited/Unusable are available when needed.
- Optional date/note.
- Record Observation Locally.
- The observation is appended as one teacher-observation opportunity for each selected student/I Can and the local state/reports/PowerSchool exports refresh transactionally.

B. PRINTABLE WALK-AROUND CHECKLIST
- Choose Hour/period and up to 8 I Can columns.
- Open Printable Checklist.
- The local companion builds landscape HTML with students down the left and selected I Cans across the top.
- Check a cell only when that student directly demonstrates that I Can. Blank means not observed, not incorrect.

C. UPLOAD COMPLETED CHECKLIST
- Scan/photo/PDF the completed paper checklist.
- Upload it in the same Teacher Observations tab.
- Build Observation Request.
- The generated grading request tells ChatGPT that checked cells are teacher-observed evidence and blank cells are NOT_OBSERVED.
- Apply the returned Portfolio_Grading_Result.json with the normal local applier.

Observation independence rule: one classroom observation session is one opportunity per student/I Can. Repeated checks from the same moment/session do not become extra independent opportunities.

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
The View Reports button opens the local report hub for the selected course/Unit. It includes:
- Student Reports: 03 Student Packets
- Teacher Report: 04 Class & Intervention Summaries
- PowerSchool Exports: 05 PowerSchool Exports

EMAIL PREPARATION
-----------------
The Email Reports button opens the local email control panel.
- Current active students are shown with checkboxes by hour/period.
- Select All and Deselect All are provided.
- Leave checked only the students whose current reports you want prepared (for example, students who just made up work).
- Click Prepare Selected PDFs.
- Only selected students' current individual HTML reports are converted locally to PDFs with Chrome/Edge/Chromium.
- Stable student identity is checked before a PDF is considered sendable.
- Stored student/guardian/support recipients are matched by durable student ID.
- Output goes to 06 Email Delivery/Current with PDFs + email_delivery_manifest.csv.
- Existing Current is archived under 06 Email Delivery/Prepared Archives.
- NO email is sent by this preparation step.

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
