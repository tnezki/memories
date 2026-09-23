PORTFOLIO LOCAL STATE
=====================

Purpose
-------
Keep private Portfolio data in a local `_portfolio_data` folder beside the Git repositories, and manually copy that folder to/from a USB drive between computers. GitHub remains curriculum/code only.

Setup
-----
Run `Create Portfolio Local Folders.command` once on each computer. It creates the private sibling folder under the detected GitHub root.

Normal run
----------
1. Keep new evidence privately in `_portfolio_data/<Course>/unit N/01 Evidence Inbox/`.
2. In the course Portfolio Control Panel, select `02 Portfolio Data/Portfolio_State_CURRENT.zip` plus only the new evidence for this run.
3. Upload the generated request ZIP to a fresh ChatGPT run.
4. The run returns `Portfolio_State_UPDATED.zip` and, when reports were requested, `Portfolio_Results.zip`.
5. Run `Install Portfolio Update.command` to archive the prior state, install the new current state, and optionally archive/update Latest results.
6. At the end of the day, copy the whole `_portfolio_data` folder to the USB drive. Copy that folder onto the other computer before doing Portfolio work there.

One-time migration
------------------
Until a course/unit has a portable current-state ZIP, use the Control Panel checkbox `One-time migration from existing Google Drive state`. That migration may read Drive once and must return the first portable state. After that, normal runs do not use Drive.

Privacy
-------
`_portfolio_data` must never be initialized as a Git repository, added to a Git repository, committed, pushed, or packaged in a GitHub Transfer ZIP.
