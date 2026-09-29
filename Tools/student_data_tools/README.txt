STUDENT DATA TOOLS v1.2
=======================

NORMAL USE
----------
Open Student Data Tools from the Dock.

The app:
1. stops the old Portfolio runtime and closes only stale Student Data Tools / Portfolio Terminal windows;
2. starts one fresh Portfolio Local Companion Terminal session;
3. waits for the localhost health check to pass;
4. checks the saved Portfolio Email Delivery web-app URL;
5. opens the numbered Student Data Tools landing page;
6. minimizes the fresh runtime Terminal window after Portfolio is READY.

The runtime Terminal must remain running because macOS Documents-folder privacy is most reliable when the Portfolio server runs from Terminal. Opening Student Data Tools again replaces the old runtime/window instead of accumulating stale Terminal windows.

NORMAL WORKFLOW
---------------
1. NEW EVIDENCE
   Open Portfolio Tools when you are grading/adding evidence, entering teacher observations, or updating a roster.

2. JUST PRINT / VIEW REPORTS
   Use current reports when you do not want to change evidence or grades.

3. PREPARE EMAIL REPORTS
   In Portfolio, choose the students, review notes, and prepare the current email batch.
   Student Data Tools builds:
     06 Email Delivery/Current/Portfolio_Email_Sender_Package.zip
   Finder then highlights that exact ZIP and the configured sender page opens.

4. SEND REPORTS
   In Portfolio Email Sender, choose the highlighted ZIP, Load Local Package, review recipients/status, optionally Send Test to Me, then use LIVE SEND only when correct.

Nothing sends automatically.

EMAIL URL
---------
The sender URL is stored only in:
  _portfolio_data/_student_data_tools/email_sender_url.txt

It is not committed to GitHub. To set/change it later, double-click:
  Set Email Sender URL.command

HEALTH MEANING
--------------
Portfolio READY means the localhost runtime returned PASS from /api/runtime-version.

Email REACHABLE means the configured web-app URL responded over HTTPS. The sender still performs the real teacher-account, package, attachment, quota, duplicate-send, recipient, and preview checks after it is opened.

PRIVACY
-------
The app landing page contains no student records. All canonical Portfolio state stays under _portfolio_data. Email sending is always explicit and teacher-authorized.

