# Selected-Response Choice Scrambler

`tools/~scramble_selected_response.py` is the build-time answer-position tool used by the Summative renderer.

## Ownership
- Canonical Bank owns prompt, choice content, correct content, I-can/evidence metadata, and representations.
- Summative renderer owns final displayed choice order.
- The scrambler runs on a **temporary staging copy** only. Never rewrite the deployed Bank.

## Detection contract
A Summative selected-response item is recognized from the current canonical Bank schema when it has a Summative destination/security signal, a non-empty choices array, and `question_design.response_mode = selected_response`. Legacy `item_type` values remain supported; `item_type` is not required. Under `--strict-16x4`, Summative choice records that are not recognized cause a hard failure rather than PASS_NOOP.

## Current Physics contract
For each active Physics form with 16 selected-response questions and four choices, run with `--strict-16x4`. The output must be exactly 4 A / 4 B / 4 C / 4 D, while preserving every choice's content exactly.

## Example
```bash
python3 tools/~scramble_selected_response.py staged_unit_bank_data.json --in-place \
  --seed "Physics|unit1|practice-to-summative-v1" \
  --report summative_choice_scramble_report.json --strict-16x4
```

The scramble is deterministic for the same seed/source. After this step, no later build step may reorder choices.
