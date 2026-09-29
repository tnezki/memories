# Portfolio Email Delivery - Google Apps Script v3.2

This web app is the **transport-only** sender for Student Data Tools. It no longer reads Portfolio rosters, Mastery Goal grades, recipients, notes, or reports from the old Google Drive Portfolio archive.

The current data source is the private local package created by Student Data Tools:

`_portfolio_data/<Course>/unit N/06 Email Delivery/Current/Portfolio_Email_Sender_Package.zip`

## Update the existing deployment

Use the existing standalone Google Apps Script project and existing deployment URL.

1. Replace the project `Code.gs` with the current repository `Tools/portfolio_email_delivery/Code.gs`.
2. Replace `Index.html` with the current repository `Tools/portfolio_email_delivery/Index.html`.
3. Save the Apps Script project.
4. Open **Deploy -> Manage deployments**.
5. Edit the current Web app deployment.
6. Choose **New version** and deploy it.
7. Refresh the web app and confirm the visible badge says **v3.2**.

The existing sender URL can remain unchanged, so Student Data Tools does not need a new URL.

## Script Properties

Required:

- `TEACHER_EMAIL` = the teacher's school Google account
- `TEACHER_DISPLAY_NAME` = the name/signature placed at the bottom of messages

`PORTFOLIO_ROOT_FOLDER_ID` is no longer required by v3.2. It may remain as an unused old property until you choose to remove it.

Run `verifySetup()` once after the update if you want to verify account authorization and MailApp quota. It performs no email send.

## Normal use

1. Open **Student Data Tools**.
2. Open Portfolio Tools and the course/unit Email control panel.
3. Select the students for this send and enter any optional class/student notes.
4. Click **Prepare Selected PDFs**.
5. The local runtime creates `Portfolio_Email_Sender_Package.zip` and reveals `06 Email Delivery/Current` in Finder. No email has been sent.
6. Open **Portfolio Email Sender** from Student Data Tools.
7. Choose the current `Portfolio_Email_Sender_Package.zip` and click **Load Local Package**.
8. Review every row. The sender shows the local MG1-MG4 values, student/guardian/support recipients, notes, and readiness state carried by that package.
9. If you uncheck a student or change the support-staff toggle, click **Recheck**.
10. Optionally choose one student and click **Send Test to Me**. The test goes only to the teacher.
11. When satisfied, use the red **LIVE SEND — EMAIL N STUDENTS NOW** button and confirm the message/recipient counts.

## Private sender storage

The Apps Script sender creates one teacher-private My Drive folder:

`_Student Data Tools Email Sender`

It may contain:

- `Current Package/` — transient staged PDFs/manifest from the package you explicitly uploaded
- `email_send_log.csv` — persistent send audit and duplicate-send guard

This folder is **not** Portfolio state. It must never be used to rebuild, correct, or override `_portfolio_data`.

Loading a new local package replaces the prior `Current Package` staging folder. The persistent send log remains so the same `student_key + report_sha256` is not live-sent twice by accident.

## Privacy and fail-closed behavior

- The sender is restricted to the configured teacher account.
- One student is sent per message; the student is in **To** and guardians/support staff are in **BCC**.
- Missing/invalid student email, missing attachment, identity verification failure, or PDF hash mismatch blocks that included row.
- Missing guardian email is shown as a warning and may allow student-only delivery after teacher review.
- Any send-selection/support-staff change invalidates the preview digest until Recheck.
- A teacher-only test remains available before live send.
- Live send always requires the explicit red button and confirmation stating that it is not a test.
- The sender never falls back to old Drive Portfolio data.

## Message wording

The v3.2 body is intentionally shorter and lower-reading-level. It tells the student that the attached report shows current Mastery Goal progress and next steps, explains that PowerSchool uses one current grade per Mastery Goal after enough evidence, and explains that `I` means In Progress and can change with more evidence. Only teacher-reviewed package notes are appended.


## v3.2 upload repair

The package upload now follows the Google Apps Script HTML-service form-upload pattern directly: the HTML form is the sole parameter to the exposed `uploadPackage(formObject)` server function. The ZIP-processing implementation remains private in `loadLocalSenderPackage_()`. This avoids the v3.0 client error `loadLocalSenderPackage is not a function` while preserving the same package validation and send safeguards.

## v3.2 local ZIP upload repair

The sender now uses the exact Apps Script HTML-service form-submit pattern for file inputs: the HTML `form` element is passed directly as the sole `google.script.run` parameter, so the selected ZIP arrives server-side as an Apps Script Blob. The server validates the ZIP by attempting `Utilities.unzip()` directly instead of rejecting valid native Blob objects with a JavaScript method-type check.

