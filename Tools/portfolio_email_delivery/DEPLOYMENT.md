# Portfolio Email Delivery - Google Apps Script deployment

This web app sends the already-prepared individual Portfolio PDFs from the private Portfolio Drive. It does not generate reports and it does not import student evidence.

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

## Normal use

1. Portfolio first writes/refreshes the private contact recipient file, individual two-page PDFs, and delivery manifest.
2. Open the email web app.
3. Select Course -> Unit -> Period (or All periods).
4. Click **Run Preflight** and review every row.
5. Optionally choose a student and click **Send Test to Me**. The test goes only to the teacher.
6. Check the confirmation box and click **Send Reports**.

The sender uses one message per student: the student is in **To** and that student's guardian addresses are in **BCC**. It never combines multiple students/families into one message.

## Fail-closed behavior

Live sending is blocked for unresolved contact records, invalid student addresses, missing/duplicate reports, attachment hash mismatches, changed state after preview, insufficient MailApp recipient quota, or an unverified active Google account. A missing guardian address is shown as a warning and allows student-only delivery after teacher review.

A successful live send is logged privately. The same `student_key + report_sha256` is not sent again on a later click.
