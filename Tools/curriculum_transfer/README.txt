CURRICULUM TRANSFER
===================

PURPOSE
-------
Canonical source for the local Curriculum Transfer installer and Dock launcher.

DOCK APP
--------
Drag `Curriculum Transfer.app` from this folder to the macOS Dock.

When opened, the app launches Terminal and runs:
  Apply Curriculum Transfers.command

The Terminal window stays visible so the teacher can watch the run. Every run ends with a repeated all-caps SUCCESS or FAILURE banner.

WRITABLE RUNTIME
----------------
The launcher creates and uses the sibling workspace folder:
  _curriculum_transfers/

with:
  downloads/
  _processed/
  _failed/
  _backups/
  _logs/
  approved_roots.json

The canonical approved-roots seed lives in this source folder and is copied into the writable runtime on each launch.

INBOX BOUNDARY
--------------
The Dock app reads only:
  _curriculum_transfers/downloads/

It does not scan `_github_transfers/`. The older helper remains separate for any still-unconverted legacy workflow. A legacy github_transfer/2 package can still be processed by Curriculum Transfer only when it is deliberately placed in the new Curriculum Transfer downloads folder.

NO GIT ACTIONS
--------------
Curriculum Transfer installs local files only. It never commits, pushes, pulls, branches, merges, or creates pull requests.
