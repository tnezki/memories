#!/usr/bin/env python3
"""Deterministically rebalance selected-response answer positions in a staged Bank JSON.

Curriculum Build tool. Intended for build-time use on a TEMPORARY COPY of
unitN_bank_data.json immediately before Summative rendering. It never needs to
modify the canonical deployed Bank.

Behavior:
- Finds Summative selected-response items with a choices array.
- Preserves every choice's content exactly, but reorders the choices.
- Moves the correct answer to a deterministic, balanced display position per form.
- Reorders distractors deterministically.
- Updates correct_choice and leading answer/solution letter prefixes when present.
- Emits a JSON report and fails closed on ambiguous/malformed items.

For a 16-question, four-choice form, the required result is exactly 4 A / 4 B /
4 C / 4 D, with the target sequence shuffled to avoid a visible ABCD pattern.
For other counts, letter counts differ by at most one when mathematically possible.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import random
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

TOOL_VERSION = "1.0"
LETTER_POOL = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def stable_seed_int(text: str) -> int:
    return int.from_bytes(hashlib.sha256(text.encode("utf-8")).digest()[:8], "big")


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path: Path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
        f.write("\n")


def get_items_container(data):
    if isinstance(data, dict) and isinstance(data.get("items"), list):
        return data["items"], "list"
    if isinstance(data, dict) and isinstance(data.get("items"), dict):
        return list(data["items"].values()), "dict"
    if isinstance(data, list):
        return data, "root_list"
    raise ValueError("Input JSON must be a list or contain an 'items' list/dict.")


def is_summative_sr(item: dict) -> bool:
    choices = item.get("choices")
    if not isinstance(choices, list) or len(choices) < 2:
        return False
    item_type = str(item.get("item_type", "")).strip().lower().replace("_", " ")
    dest_group = str(item.get("destination_group", "")).strip().lower()
    dest = str(item.get("destination", "")).strip().lower()
    security = str(item.get("security_level", "")).strip().lower()
    return (
        ("selected response" in item_type or item_type in {"mc", "multiple choice"})
        and (dest_group == "summative" or dest.startswith("summative") or "summative" in security)
    )


def form_id(item: dict) -> str:
    return str(
        item.get("destination_form_set_version")
        or item.get("summative_version")
        or item.get("form_id")
        or "UNSPECIFIED"
    )


def question_sort_key(item: dict):
    bid = str(item.get("bank_id", ""))
    m = re.search(r"(?:Q|q)(\d+)(?:\D|$)", bid)
    return (int(m.group(1)) if m else 10**9, bid)


def choice_text(choice):
    if isinstance(choice, str):
        return choice
    if isinstance(choice, dict):
        for k in ("text", "html", "label", "choice_text", "student_text"):
            if k in choice:
                return choice[k]
    return choice


def normalize_correct_index(item: dict) -> int:
    choices = item["choices"]
    cc = item.get("correct_choice")
    if isinstance(cc, int):
        if 0 <= cc < len(choices):
            return cc
        if 1 <= cc <= len(choices):
            return cc - 1
    if isinstance(cc, str):
        s = cc.strip().upper()
        if len(s) == 1 and s in LETTER_POOL[: len(choices)]:
            return LETTER_POOL.index(s)
        if s.isdigit():
            v = int(s)
            if 1 <= v <= len(choices):
                return v - 1
    # Support dict choices that mark the correct option.
    marked = []
    for i, c in enumerate(choices):
        if isinstance(c, dict) and (c.get("correct") is True or c.get("is_correct") is True):
            marked.append(i)
    if len(marked) == 1:
        return marked[0]
    raise ValueError(f"{item.get('bank_id','<unknown>')}: cannot resolve exactly one correct choice")


def balanced_targets(n: int, m: int, seed_text: str) -> list[int]:
    base, rem = divmod(n, m)
    targets = []
    for idx in range(m):
        targets.extend([idx] * (base + (1 if idx < rem else 0)))
    rng = random.Random(stable_seed_int(seed_text))

    def acceptable(seq):
        # Avoid three identical letters in a row and obvious repeated ABCD-style cycles.
        if any(seq[i] == seq[i+1] == seq[i+2] for i in range(len(seq)-2)):
            return False
        if len(seq) >= 8:
            for p in range(2, min(m + 1, 6)):
                if len(seq) >= 2*p and seq[:p] == seq[p:2*p]:
                    return False
        return True

    for _ in range(5000):
        candidate = targets[:]
        rng.shuffle(candidate)
        if acceptable(candidate):
            return candidate
    # Deterministic fallback still preserves exact balance.
    rng.shuffle(targets)
    return targets


def update_letter_prefix(text: str, old_letter: str, new_letter: str) -> str:
    if not isinstance(text, str) or old_letter == new_letter:
        return text
    # Plain text: leading "C." / "C)" / "C:" only.
    text2 = re.sub(
        rf"^(\s*){re.escape(old_letter)}([\.:\)])(\s+)",
        rf"\1{new_letter}\2\3",
        text,
        count=1,
    )
    if text2 != text:
        return text2
    # HTML solution wrapper: replace the first visible letter immediately after opening tags.
    return re.sub(
        rf"^(\s*(?:<[^>]+>\s*)*){re.escape(old_letter)}([\.:\)])(\s+)",
        rf"\1{new_letter}\2\3",
        text,
        count=1,
        flags=re.IGNORECASE,
    )


def scramble_item(item: dict, target_correct_idx: int, seed_text: str) -> dict:
    choices = item["choices"]
    m = len(choices)
    if target_correct_idx >= m:
        raise ValueError(f"{item.get('bank_id')}: target index {target_correct_idx} invalid for {m} choices")
    old_correct_idx = normalize_correct_index(item)
    old_letter = LETTER_POOL[old_correct_idx]
    new_letter = LETTER_POOL[target_correct_idx]

    correct_obj = choices[old_correct_idx]
    distractors = [c for i, c in enumerate(choices) if i != old_correct_idx]
    rng = random.Random(stable_seed_int(seed_text + "|distractors"))
    rng.shuffle(distractors)

    new_choices = [None] * m
    new_choices[target_correct_idx] = correct_obj
    it = iter(distractors)
    for i in range(m):
        if i != target_correct_idx:
            new_choices[i] = next(it)

    before_multiset = sorted(json.dumps(c, sort_keys=True, ensure_ascii=False) for c in choices)
    after_multiset = sorted(json.dumps(c, sort_keys=True, ensure_ascii=False) for c in new_choices)
    if before_multiset != after_multiset:
        raise AssertionError(f"{item.get('bank_id')}: choice content changed during scramble")

    item["choices"] = new_choices
    item["correct_choice"] = new_letter
    if "answer_text" in item:
        item["answer_text"] = update_letter_prefix(item["answer_text"], old_letter, new_letter)
    if "solution_html" in item:
        item["solution_html"] = update_letter_prefix(item["solution_html"], old_letter, new_letter)

    # Keep dict-level correct flags synchronized when present.
    for idx, c in enumerate(new_choices):
        if isinstance(c, dict):
            if "correct" in c:
                c["correct"] = idx == target_correct_idx
            if "is_correct" in c:
                c["is_correct"] = idx == target_correct_idx

    item["choice_scramble"] = {
        "tool": "scramble_selected_response.py",
        "tool_version": TOOL_VERSION,
        "original_correct_choice": old_letter,
        "final_correct_choice": new_letter,
        "content_preserved": True,
    }
    return {
        "bank_id": item.get("bank_id"),
        "form": form_id(item),
        "original_correct_choice": old_letter,
        "final_correct_choice": new_letter,
        "choice_count": m,
    }


def run(data, seed: str, strict_16x4: bool = False):
    items, _ = get_items_container(data)
    groups = defaultdict(list)
    for item in items:
        if isinstance(item, dict) and is_summative_sr(item):
            groups[form_id(item)].append(item)

    if not groups:
        return {"status": "PASS_NOOP", "tool_version": TOOL_VERSION, "forms": {}, "items_changed": 0}

    report_forms = {}
    total = 0
    for fid in sorted(groups):
        form_items = sorted(groups[fid], key=question_sort_key)
        choice_counts = {len(it["choices"]) for it in form_items}
        if len(choice_counts) != 1:
            raise ValueError(f"{fid}: selected-response items have mixed choice counts {sorted(choice_counts)}")
        m = next(iter(choice_counts))
        n = len(form_items)
        if strict_16x4 and (n != 16 or m != 4):
            raise ValueError(f"{fid}: expected exactly 16 selected-response items with 4 choices; found {n} x {m}")

        targets = balanced_targets(n, m, f"{seed}|{fid}|targets|v{TOOL_VERSION}")
        item_reports = []
        for item, target in zip(form_items, targets):
            bid = str(item.get("bank_id", ""))
            item_reports.append(scramble_item(item, target, f"{seed}|{fid}|{bid}|v{TOOL_VERSION}"))
            total += 1

        final_letters = [r["final_correct_choice"] for r in item_reports]
        dist = Counter(final_letters)
        counts = [dist.get(LETTER_POOL[i], 0) for i in range(m)]
        if max(counts) - min(counts) > 1:
            raise AssertionError(f"{fid}: final answer distribution is not balanced: {dict(dist)}")
        if strict_16x4 and counts != [4, 4, 4, 4]:
            raise AssertionError(f"{fid}: expected 4/4/4/4 distribution, got {counts}")
        if any(final_letters[i] == final_letters[i+1] == final_letters[i+2] for i in range(len(final_letters)-2)):
            raise AssertionError(f"{fid}: contains a run of 3 identical correct letters")

        report_forms[fid] = {
            "selected_response_count": n,
            "choice_count": m,
            "final_distribution": {LETTER_POOL[i]: counts[i] for i in range(m)},
            "final_sequence": final_letters,
            "items": item_reports,
        }

    return {"status": "PASS", "tool_version": TOOL_VERSION, "seed": seed, "forms": report_forms, "items_changed": total}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("input_json", type=Path, help="staged unitN_bank_data.json or equivalent item JSON")
    ap.add_argument("output_json", nargs="?", type=Path, help="output JSON; omit only with --in-place")
    ap.add_argument("--in-place", action="store_true", help="rewrite input_json in place (use only on a staging copy)")
    ap.add_argument("--seed", default="curriculum-build-selected-response-v1", help="stable deterministic seed string")
    ap.add_argument("--report", type=Path, help="write scramble report JSON")
    ap.add_argument("--strict-16x4", action="store_true", help="require each form to contain exactly 16 SR items with 4 choices")
    args = ap.parse_args()

    if args.in_place and args.output_json:
        ap.error("do not pass output_json with --in-place")
    if not args.in_place and not args.output_json:
        ap.error("output_json is required unless --in-place is used")

    src = args.input_json
    dst = src if args.in_place else args.output_json
    try:
        data = load_json(src)
        out = copy.deepcopy(data)
        report = run(out, args.seed, strict_16x4=args.strict_16x4)
        save_json(dst, out)
        if args.report:
            save_json(args.report, report)
        print(json.dumps({k: v for k, v in report.items() if k != "forms"}, ensure_ascii=False))
        for fid, info in report.get("forms", {}).items():
            print(f"{fid}: {info['final_distribution']} sequence={''.join(info['final_sequence'])}")
        return 0
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
