PORTFOLIO LOCAL RUNTIME v1
==========================

PURPOSE
-------
Move deterministic Portfolio work onto the teacher's Mac while keeping ChatGPT focused on evidence interpretation and feedback.

NORMAL EVIDENCE WORKFLOW
------------------------
1. Double-click: Build Portfolio Grading Request.command
2. Choose the course/Unit, new evidence, optional teacher supporting files, evidence label/date.
3. The command creates a small portfolio_grading_request_*.zip in Downloads and reveals it in Finder.
4. Upload that request ZIP to ChatGPT.
5. ChatGPT returns ONE file: Portfolio_Grading_Result.json.
6. Download it normally to Downloads.
7. Double-click: Apply Portfolio Grading Result.command
8. The local processor validates the exact parent state, appends evidence, updates I Can/MG status, builds canonical HTML reports, builds current PowerSchool MG CSVs, validates report templates, archives/install state/results, and refreshes folders 03-05.
9. Google Drive is not used.

EMAIL PREPARATION
-----------------
Double-click: Prepare Portfolio Emails.command
- Select course/Unit.
- The command reads current local HTML reports.
- It creates one PDF per active student locally with Chrome/Edge/Chromium.
- It matches stored student/guardian/support recipients by durable student ID.
- It creates 06 Email Delivery/Current with PDFs + email_delivery_manifest.csv.
- It DOES NOT send any email.

SAFETY
------
- Apply refuses a result built from a different state SHA/version/id.
- State/results are built in a temporary transaction and installed only after QA passes.
- Previous state/results remain archived.
- Student data stays under _portfolio_data or in the teacher's private grading request/result downloads. Never commit _portfolio_data or grading request/result files to GitHub.
- ChatGPT does not calculate longitudinal state or render reports in the normal fast-grading path; local Python does.

CURRENT UNIT SUPPORT
--------------------
Algebra 1 Unit 1 and Physics Unit 1 are supported from their migrated local state.
AP Calculus AB Unit 1 is ready to use this runtime after its first local Portfolio state exists.
