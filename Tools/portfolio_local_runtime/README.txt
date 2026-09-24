PORTFOLIO LOCAL RUNTIME v3.3
============================

PURPOSE
-------
Keep ChatGPT focused on evidence interpretation while the teacher's Mac owns deterministic Portfolio history, grades, reports, PowerSchool exports, roster maintenance, teacher-observation evidence, and selected-student email PDF preparation.

START EACH WORK SESSION
-----------------------
Double-click:
  Tools/portfolio_local_runtime/Start Portfolio Local Companion.command

The companion listens only on 127.0.0.1:8765 and runs in the interactive Terminal session.

IMPORTANT MACOS PRIVACY RULE
----------------------------
Do NOT install the companion as a LaunchAgent/login helper while the GitHub and _portfolio_data folders live under ~/Documents. macOS privacy controls can deny background launchd/Python processes access to Documents even when the same files work normally from Terminal.

The launcher removes the retired login-helper plist if present, stops stale companion processes, and starts the companion directly from Terminal. Keep that Terminal window open while using Portfolio; it may be minimized. Press Control-C in that Terminal window when finished.

If macOS blocks the interactive process, enable Terminal access under:
  System Settings > Privacy & Security > Files and Folders > Terminal > Documents Folder
then start the companion again.

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

If the local companion is offline, start Start Portfolio Local Companion.command and keep its Terminal window open while working.

The local Portfolio pages do NOT replace the existing course Teacher Dashboard. The Teacher Dashboard remains the normal navigation shell. Local Portfolio report/email pages handle private local student data and include a link back to the course Teacher Dashboard.

NORMAL EVIDENCE WORKFLOW
------------------------
1. Start the local companion for the work session.
2. Open the course Portfolio Control Panel.
3. Choose Unit and Grade Evidence.
4. Add only the new student evidence. Evidence label/date/note are optional.
5. Click Build Grading Request.
6. The local companion adds exact current roster, learning map, prior I Can context, and state identity; creates portfolio_grading_request_*.zip in Downloads; and reveals it in Finder.
7. Upload that ZIP to ChatGPT.
8. ChatGPT returns ONE file: Portfolio_Grading_Result.json.
9. Download it to Downloads.
10. Double-click Apply Portfolio Grading Result.command.
11. Local Python validates the exact parent state; updates evidence history, I Can/MG status, intervention routing, state/version chain; builds canonical HTML reports and PowerSchool MG CSVs; runs identity/template QA; archives results/state; and refreshes folders 03-05.
12. Google Drive is not used.

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
- Students appear down the left; selected I Cans appear across the top.
- Check a cell only when that student directly demonstrates that I Can.
- Blank means not observed, not incorrect.

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
Teacher observations and roster updates already rebuild current reports automatically. View Reports also includes a manual Refresh Reports from Current State button. This is a report-only rebuild and never adds evidence, changes grades, or increments the state version.

The View Reports button opens the private local report hub for the selected course/Unit. It includes:
- Student Reports: 03 Student Packets
- Teacher Report: 04 Class & Intervention Summaries
- PowerSchool Exports: 05 PowerSchool Exports

Canonical student and teacher reports are HTML. A PDF visible immediately after migration is a legacy seeded artifact from the old Drive-era results, not the normal new report format.

If canonical HTML reports are missing but a valid current local Portfolio state exists, the companion rebuilds the current HTML reports from that state automatically. This is a report-only refresh: it does not add evidence, change grades, or increment the state version. This also lets email preparation work without requiring a fake grading run just to create HTML.

PowerSchool CSVs are already local. The report hub reminds the teacher to import from:
  _portfolio_data/<Course>/unit N/05 PowerSchool Exports
and provides a Reveal PowerSchool folder in Finder link. There is no need to download the CSVs from the local web page first.

EMAIL PREPARATION
-----------------
The Email Reports button opens the local email control panel.
- Email Reports reuses the established Portfolio email-review layout: course/unit/period controls, student rows, MG snapshot, stored recipient columns, readiness, and a sticky review bar.
- Current active students are shown with Prepare checkboxes. Period filtering plus Select All / Deselect All / Select Visible / Deselect Visible are provided.
- Leave checked only the students whose current reports you want prepared, including individual make-up-work follow-up.
- If current individual HTML reports are missing, they are rebuilt from the installed local state first without changing evidence or grades.
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

CONTROL STABILITY
-----------------
The course control panels use a lightweight 15-second companion heartbeat that updates only connection/state status. It does not redraw hour/student/I Can controls. Roster/I Can lists load initially, on Unit change, or after a true roster/state-structure change. Direct observations preserve hour/student/date/note and clear only the I Can checks that were submitted.
