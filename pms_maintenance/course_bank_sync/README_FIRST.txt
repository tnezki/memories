COURSE BANK SYNC PM

Teacher-facing use:
  Upload this ZIP + current course-site ZIP + current Framework + one finalized Unit Bank.
  Prompt: Carefully read PM and Run.

This package is self-contained for the Bank-driven sync workflow.
The embedded Notes and Downstream Bundle PMs are internal authorities; they do not
need to be uploaded separately.

v1.1 change:
- Bank equality no longer short-circuits downstream refresh.
- Always regenerate allowed Bank-driven descendants, compare, and replace only
  child folders whose bytes differ.
- Byte-identical Bank/child folders remain untouched.
- Deliver a changes-only ZIP in addition to the updated full course ZIP.
