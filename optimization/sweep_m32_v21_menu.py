#!/usr/bin/env python3
"""Exact four-base robustness sweep for the m=32, v=21 proof family."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from fractions import Fraction
from pathlib import Path

from compiled_locked import best_compiled, compile_kernels
from general_locked import (
    assignments_from_bases,
    locked_bound,
    low_degree_options,
    three_lock_profiles,
)


BASES = ((10, 11, 12), (1, 2, 3), (11, 12, 13), (1, 2, 12))
EXPECTED_PROFILE_COUNT = 1864
EXPECTED_WORST = Fraction(9599, 9724)
EXPECTED_WORST_COUNTS = (15, 5, 4, 1, 4, 1, 2, 0)
EXPECTED_WORST_DEGREES = (7, 7, 7)
EXPECTED_WORST_POSITIONS = (1, 2, 12)
EXPECTED_RECORD_SHA256 = "dd41903f21f585c7dd2cf83b33f8035763a8b47586339e33b5457408e8dd2b4d"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def run() -> tuple[list[dict[str, object]], dict[str, object]]:
    assignments = assignments_from_bases(BASES)
    require(len(assignments) == 24, f"expected 24 assignments, got {len(assignments)}")
    kernels = compile_kernels(21, 32, assignments)
    records = []
    selected_bases: Counter[tuple[int, ...]] = Counter()
    digest = hashlib.sha256()
    for degrees in low_degree_options(21, 32, 3):
        for counts in three_lock_profiles(32, degrees):
            value, positions = best_compiled(counts, kernels)
            require(value < 1, f"unclosed profile {degrees}, {counts}: {value}")
            selected_bases[tuple(sorted(positions))] += 1
            record = {
                "degrees": list(degrees),
                "counts_by_mask": list(counts),
                "positions_by_label": list(positions),
                "bound": {"numerator": value.numerator, "denominator": value.denominator},
            }
            records.append(record)
            digest.update(
                (json.dumps(record, sort_keys=True, separators=(",", ":")) + "\n").encode(
                    "utf-8"
                )
            )
    require(len(records) == EXPECTED_PROFILE_COUNT, f"got {len(records)} profiles")
    worst = max(
        records,
        key=lambda r: Fraction(r["bound"]["numerator"], r["bound"]["denominator"]),
    )
    worst_value = Fraction(worst["bound"]["numerator"], worst["bound"]["denominator"])
    require(worst_value == EXPECTED_WORST, f"worst value changed to {worst_value}")
    require(tuple(worst["degrees"]) == EXPECTED_WORST_DEGREES, "worst degrees changed")
    require(tuple(worst["counts_by_mask"]) == EXPECTED_WORST_COUNTS, "worst counts changed")
    require(
        tuple(worst["positions_by_label"]) == EXPECTED_WORST_POSITIONS,
        "worst positions changed",
    )
    direct = locked_bound(21, 32, EXPECTED_WORST_COUNTS, EXPECTED_WORST_POSITIONS)
    require(direct == worst_value, f"direct evaluator gives {direct}")
    row_hash = digest.hexdigest()
    if EXPECTED_RECORD_SHA256 != "TO_BE_PINNED":
        require(row_hash == EXPECTED_RECORD_SHA256, f"row hash changed to {row_hash}")
    summary = {
        "schema": "property-b-m5-m32-v21-four-base-menu-v1",
        "arithmetic": "fractions.Fraction; compiled integer-polynomial kernels",
        "python_optimized_mode_safe": True,
        "position_bases": [list(base) for base in BASES],
        "labelled_assignments": len(assignments),
        "profile_count": len(records),
        "worst_bound": {"numerator": worst_value.numerator, "denominator": worst_value.denominator},
        "worst_profile": worst,
        "selected_base_counts": {
            str(base): count for base, count in sorted(selected_bases.items())
        },
        "record_sha256": row_hash,
        "direct_evaluator_match_at_worst": True,
    }
    return records, summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--summary", type=Path)
    parser.add_argument("--records", type=Path)
    args = parser.parse_args()
    records, summary = run()
    if args.records:
        args.records.write_text(
            "".join(json.dumps(row, sort_keys=True) + "\n" for row in records),
            encoding="utf-8",
        )
    payload = json.dumps(summary, indent=2, sort_keys=True) + "\n"
    if args.summary:
        args.summary.write_text(payload, encoding="utf-8")
    print(payload, end="")


if __name__ == "__main__":
    main()
