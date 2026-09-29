STUDENT DATA TOOLS v1.1
=======================

NORMAL USE
----------
Open Student Data Tools from the Dock.

The app:
1. starts a fresh Portfolio Local Companion in Terminal without opening the raw localhost home tab;
2. waits for the localhost health check to pass;
3. checks the saved Portfolio Email Delivery web-app URL;
4. opens the small local Student Data Tools landing page.

The Portfolio runtime Terminal window may be minimized while you work. Stop it with Control-C when finished. Opening Student Data Tools again safely stops stale Portfolio companion processes before starting a fresh runtime.

EMAIL WORKFLOW
--------------
Current Portfolio data stays local.

1. Open Portfolio Tools from Student Data Tools.
2. Open the course/unit Email control panel.
3. Select the students for this send and enter any optional weekly/student notes.
4. Click Prepare Selected PDFs.
5. The local runtime creates the PDFs, local delivery manifest, and:
     06 Email Delivery/Current/Portfolio_Email_Sender_Package.zip
   The Current folder opens in Finder.
6. Open Portfolio Email Sender from Student Data Tools.
7. Load Portfolio_Email_Sender_Package.zip.
8. Review the rows and recipients. Recheck after any Send/support-staff selection change.
9. Optionally Send Test to Me.
10. Use LIVE SEND only after the review is correct.

The sender does not read old Portfolio data from Google Drive. Its private Drive use is limited to transiently staging the package you explicitly upload and maintaining its send log.

EMAIL URL
---------
The sender URL is stored only in:
  _portfolio_data/_student_data_tools/email_sender_url.txt

It is not committed to GitHub. To set/change it later, double-click:
  Set Email Sender URL.command

That command uses a visible Terminal prompt so failure cannot disappear silently.

HEALTH MEANING
--------------
Portfolio READY means the localhost runtime returned PASS from /api/runtime-version.

Email REACHABLE means the configured web-app URL responded over HTTPS. The sender still performs the real teacher-account, package, attachment, quota, duplicate-send, recipient, and preview checks after it is opened.

PRIVACY
-------
The app landing page contains no student records. All canonical Portfolio state stays under _portfolio_data. Email sending is always explicit and teacher-authorized.
