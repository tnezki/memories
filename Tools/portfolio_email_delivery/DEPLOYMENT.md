# Portfolio Email Delivery - Google Apps Script deployment








This web app sends already-prepared individual Portfolio PDFs from the private Portfolio Drive. It does not generate reports and it does not import student evidence. The same teacher-owned sender is course-generic: Algebra 1, Physics, AP Calculus, STEM, and future courses appear when their private Portfolio course/unit state exists.








## One-time setup








1. Create a **standalone Google Apps Script project** while signed into the teacher's school Google Workspace account.
2. Copy these repository files into the Apps Script project:
   - `Code.gs`
   - `Index.html`
   - `appsscript.json` (Project Settings -> Show `appsscript.json` manifest file)
3. In **Project Settings -> Script Properties**, add:
   - `PORTFOLIO_ROOT_FOLDER_ID` = the canonical Portfolio root folder ID declared by `SYSTEM_RUNTIME_PORTFOLIO_AMENDMENT.txt`
   - `TEACHER_EMAIL` = the teacher's school Google account
   - `TEACHER_DISPLAY_NAME` = the name/signature to place at the bottom of messages
4. Run `verifySetup()` once from the Apps Script editor and authorize Drive + Send Mail access. It performs no email send.
5. Deploy as a **Web app**. Use the teacher as the executing account and the most restrictive access setting available. Prefer **Only myself**. If the district only offers domain access, the code still requires the active account to exactly equal `TEACHER_EMAIL`.
6. Open the web-app URL while signed into the teacher school account.








No additional OAuth scope or Script Property is needed for weekly/student message notes. Those notes are stored only in the private Unit Portfolio data folder.








## Updating an existing deployment


**Important:** applying the GitHub Transfer ZIP does not update the already-deployed Google Apps Script web app. After copying the new `Code.gs` and `Index.html`, deploy a **New version**. The current UI visibly shows **v2.4**. If the page does not show v2.4, do not send reports.








After replacing `Code.gs` and `Index.html` in the existing Apps Script project:








1. Save the project.
2. Open **Deploy -> Manage deployments**.
3. Edit the existing Web app deployment.
4. Choose **New version** and deploy it.
5. Refresh the Web app.








The existing deployment URL and Script Properties can remain unchanged.








## Normal weekly use








1. Portfolio first refreshes the private results ZIP and recipient state. In the email app, click **Refresh Reports & Load Class**. This prepares current PDFs from `Latest Portfolio Results.zip`, loads saved notes, reads the four current Mastery Goal grades, and runs preflight in one sequence. A full refresh may take a few minutes; leave the tab open while the spinner is showing.
2. Open the email web app directly or from a course Teacher Dashboard.
3. Select Course -> Unit -> Period (or All periods).
4. In **Message notes**:
   - optionally enter a weekly/Unit note for the class, such as an upcoming assessment or help reminder;
   - optionally enter persistent student-specific notes and check **Include this week** only for the students who should receive them.
5. After editing Send checkboxes or notes, click **Save Changes & Recheck**. Review every row, including MG1-MG4, recipients, and the exact notes that will be sent.
6. Optionally choose a student and click **Send Test to Me**. The test goes only to the teacher and uses the exact attachment and message that student would receive.
7. When satisfied, use the red **LIVE SEND — EMAIL N STUDENTS NOW** button. The confirmation states the student-email count and total recipient count and explicitly says that this is not a test. Live send may take a few minutes; leave the tab open until it finishes.








A successful live send automatically unchecks **Include this week** for each successfully sent student note while preserving the note text in the private note bank. The weekly note stays in place until the teacher edits or clears it. Failed/unsent students keep their active student-note state.








Weekly is a communication cadence, **not an unattended automation**. The system never performs a live weekly send on its own; each send still requires teacher review/recheck and the explicit red **LIVE SEND — EMAIL N STUDENTS NOW** action.








## Family-facing message model








The standard body is centralized in `buildBody_()` so wording can be revised without changing recipient/safety logic. It explains:








- reports are expected about weekly as evidence is collected;
- the Portfolio represents growth over time rather than an average of assignment scores;
- PowerSchool shows one current grade for each Mastery Goal once that goal has been assessed;
- the five fixed `Next` labels are next steps rather than grades;
- optional weekly and student-specific teacher notes appear as clearly labeled blocks.








A temporary statement such as "At this point in the unit, there is not yet enough evidence to fairly assign a letter grade" belongs in the weekly note when it is currently true, rather than being permanently hard-coded into every future message.








## Course Teacher Dashboard links








A Teacher Dashboard can link to the same sender and pass a non-sensitive course hint:








`WEB_APP_URL?course=Algebra%201`








`WEB_APP_URL?course=Physics`








The hint only preselects a course that already exists in the private Portfolio root. If a dashboard hints at a course that has not been initialized in private Portfolio state yet, the app displays that condition and does **not** silently fall back to a different course.








## Support-staff routing source




The sender reads one course-agnostic private file at `____Portfolio_Data / 00 Contact Directory / student_support_contacts_current.csv`. Its exact columns are:




`student_id,student_name,staff_name,staff_email,role,support_class,active`




A student may have multiple rows. Roles are free text and may include Case Manager, Special Education Teacher, Study Skills Teacher, Academic Support Teacher, Resource Room Teacher, or future support roles. `support_class` may be any support/resource/study-skills course and may be blank. Only active rows with a valid staff email are eligible recipients. The sender matches this file to the selected course roster by student ID; the file does not contain disability, diagnosis, or accommodation narrative.




## Privacy and fail-closed behavior








The sender uses one message per student: the student is in **To** and that student's guardian addresses are in **BCC**. It never combines multiple students/families in one message.








Student-specific message notes are private communication state. They are keyed by `student_key` in `02 Portfolio Data/email_message_notes.csv` and are never stored in GitHub, public dashboard URLs, QR codes, or public curriculum files.








Live sending is blocked for unresolved contact records, invalid student addresses, missing/duplicate reports, attachment hash mismatches, malformed note state, changed recipient/report/note state after preview, insufficient MailApp recipient quota, or an unverified active Google account. A missing guardian address is shown as a warning and allows student-only delivery after teacher review.








A successful live send is logged privately. The same `student_key + report_sha256` is not sent again on a later click.


## Identity safety and current roster behavior

- The sender blocks legacy/unverified delivery manifests. Click **Refresh Reports & Load Class** before sending.
- Preflight has a **Send** checkbox to omit a student for the current send only.
- The email tool does not change roster membership. Use the Portfolio roster-update workflow for permanent roster changes.
- Custom notes are cleaned before send. A fragment such as `hasn't been coming for help in crewtime` becomes `Chase hasn't been coming for help in Crewtime.` The tool uses the student's first name rather than guessing a gendered pronoun.
- The family message explicitly states that **I = In Progress and is not permanent**.


## v2.4 review-table cleanup

- The email screen no longer contains **Remove from class**. Roster changes belong to the Portfolio roster workflow; uncheck **Send** for a temporary omission.
- The preflight table shows four read-only current Mastery Goal grade columns: **MG1, MG2, MG3, MG4**. Values come from `02 Portfolio Data/mastery_goal_status_current.csv`; the email tool does not calculate or alter grades.
- Long operations keep the spinner visible and state that the refresh/live send may take a few minutes. Keep the tab open until the status changes from working to complete.
- Student custom notes remain private saved notes. Test sends do not clear them.
