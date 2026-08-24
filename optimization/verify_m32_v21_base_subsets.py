#!/usr/bin/env python3
"""Exact certificate for every subset of six candidate v=21 position bases.

Universe checked:

* all 1,864 safe-superset trace profiles for the three smallest degrees;
* six fixed unordered position bases, with all six label assignments per base;
* all 2^6=64 base subsets (the empty subset is recorded as having no
  certificate; all 63 nonempty subsets receive an exact worst profile).

Every comparison uses ``fractions.Fraction`` or exact compiled integer
polynomials.  No proof-critical acceptance guard is an ``assert``.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction
from itertools import permutations
from pathlib import Path

from compiled_locked import best_compiled, compile_kernels
from general_locked import locked_bound, low_degree_options, three_lock_profiles


BASES = (
    (10, 11, 12),
    (1, 2, 3),
    (11, 12, 13),
    (1, 11, 13),
    (1, 2, 12),
    (1, 12, 14),
)
EXPECTED_PROFILE_COUNT = 1864
TARGET = Fraction(9599, 9724)
EXPECTED_PROFILE_BASE_SHA256 = "647cf59a810ec84dd036cad482e3b9c219c62ca9591adb37de79157ca8f54e9f"
EXPECTED_BEST_THREE = Fraction(4805, 4862)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def fraction_record(value: Fraction) -> dict[str, int]:
    return {"numerator": value.numerator, "denominator": value.denominator}


def build() -> tuple[list[dict[str, object]], dict[str, object]]:
    base_kernels = []
    for base in BASES:
        assignments = tuple(permutations(base))
        require(len(assignments) == 6, f"base {base} does not have six assignments")
        base_kernels.append(compile_kernels(21, 32, assignments))

    # For every nonempty mask, store (worst value, exact witness record).
    subset_worst: dict[int, tuple[Fraction, dict[str, object]]] = {}
    records: list[dict[str, object]] = []
    digest = hashlib.sha256()
    profile_index = 0
    for degrees in low_degree_options(21, 32, 3):
        for counts in three_lock_profiles(32, degrees):
            base_rows = []
            exact_candidates = []
            for base_index, kernels in enumerate(base_kernels):
                value, positions = best_compiled(counts, kernels)
                base_rows.append(
                    {
                        "base_index": base_index,
                        "bound": fraction_record(value),
                        "positions_by_label": list(positions),
                    }
                )
                exact_candidates.append((value, positions, base_index))

            record = {
                "profile_index": profile_index,
                "degrees": list(degrees),
                "counts_by_mask": list(counts),
                "best_by_base": base_rows,
            }
            records.append(record)
            canonical_line = json.dumps(record, sort_keys=True, separators=(",", ":")) + "\n"
            digest.update(canonical_line.encode("utf-8"))

            for mask in range(1, 1 << len(BASES)):
                selected = min(
                    candidate
                    for candidate in exact_candidates
                    if mask >> candidate[2] & 1
                )
                value, positions, base_index = selected
                old = subset_worst.get(mask)
                if old is None or value > old[0]:
                    witness = {
                        "profile_index": profile_index,
                        "degrees": list(degrees),
                        "counts_by_mask": list(counts),
                        "selected_base_index": base_index,
                        "positions_by_label": list(positions),
                    }
                    subset_worst[mask] = (value, witness)
            profile_index += 1

    require(profile_index == EXPECTED_PROFILE_COUNT, f"got {profile_index} profiles")
    require(len(subset_worst) == 63, f"got {len(subset_worst)} nonempty subsets")
    row_hash = digest.hexdigest()
    if EXPECTED_PROFILE_BASE_SHA256 != "TO_BE_PINNED":
        require(
            row_hash == EXPECTED_PROFILE_BASE_SHA256,
            f"profile/base row hash changed to {row_hash}",
        )

    subset_rows: list[dict[str, object]] = [
        {
            "mask": 0,
            "base_indices": [],
            "cardinality": 0,
            "worst_bound": None,
            "attains_target_or_better": False,
            "reason": "empty subset has no position certificate",
        }
    ]
    for mask in range(1, 1 << len(BASES)):
        value, witness = subset_worst[mask]
        # A separately implemented direct evaluation checks each extremal row.
        direct = locked_bound(
            21,
            32,
            tuple(witness["counts_by_mask"]),
            tuple(witness["positions_by_label"]),
        )
        require(direct == value, f"mask {mask}: direct value {direct} != {value}")
        indices = [i for i in range(len(BASES)) if mask >> i & 1]
        subset_rows.append(
            {
                "mask": mask,
                "base_indices": indices,
                "bases": [list(BASES[i]) for i in indices],
                "cardinality": len(indices),
                "worst_bound": fraction_record(value),
                "attains_target_or_better": value <= TARGET,
                "worst_witness": witness,
                "direct_evaluator_match_at_witness": True,
            }
        )

    nonempty = subset_rows[1:]
    full = next(row for row in nonempty if row["mask"] == 63)
    full_value = Fraction(**full["worst_bound"])
    require(full_value == TARGET, f"full six-base worst is {full_value}")
    best_three_row = min(
        (row for row in nonempty if row["cardinality"] == 3),
        key=lambda row: Fraction(**row["worst_bound"]),
    )
    best_three = Fraction(**best_three_row["worst_bound"])
    if EXPECTED_BEST_THREE is not None:
        require(best_three == EXPECTED_BEST_THREE, f"best three-base value is {best_three}")
    require(best_three > TARGET, "a three-base subset attains the four-base target")
    attaining = [row for row in nonempty if row["attains_target_or_better"]]
    minimum_cardinality = min(row["cardinality"] for row in attaining)
    require(minimum_cardinality == 4, f"minimum attaining cardinality is {minimum_cardinality}")
    selected_mask = (1 << 0) | (1 << 1) | (1 << 2) | (1 << 4)
    selected = next(row for row in nonempty if row["mask"] == selected_mask)
    require(
        Fraction(**selected["worst_bound"]) == TARGET,
        "published four-base subset does not attain target",
    )

    summary_without_hash = {
        "schema": "property-b-m5-m32-v21-six-base-subsets-v1",
        "arithmetic": "Fraction and exact integer-polynomial kernels only",
        "python_optimized_mode_safe": True,
        "vertices": 21,
        "edges": 32,
        "candidate_bases": [list(base) for base in BASES],
        "base_count": len(BASES),
        "subset_count_including_empty": len(subset_rows),
        "nonempty_subset_count": len(nonempty),
        "profile_count": profile_index,
        "label_assignments_per_base": 6,
        "profile_base_certificate_count": profile_index * len(BASES),
        "profile_assignment_evaluations": profile_index * len(BASES) * 6,
        "target": fraction_record(TARGET),
        "best_three_base_worst": fraction_record(best_three),
        "best_three_base_subsets": [
            row["base_indices"]
            for row in nonempty
            if row["cardinality"] == 3
            and Fraction(**row["worst_bound"]) == best_three
        ],
        "no_three_base_subset_attains_target": True,
        "minimum_cardinality_attaining_target": minimum_cardinality,
        "subsets_attaining_target_or_better": [
            row["base_indices"] for row in attaining
        ],
        "published_four_base_indices": [0, 1, 2, 4],
        "published_four_base_worst": selected["worst_bound"],
        "profile_base_rows_sha256": row_hash,
        "all_subsets": subset_rows,
    }
    summary_hash = hashlib.sha256(
        json.dumps(summary_without_hash, sort_keys=True, separators=(",", ":")).encode(
            "utf-8"
        )
    ).hexdigest()
    summary_without_hash["content_sha256_without_this_field"] = summary_hash
    return records, summary_without_hash


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--records", type=Path)
    parser.add_argument("--summary", type=Path)
    args = parser.parse_args()
    records, summary = build()
    if args.records:
        args.records.write_text(
            "".join(
                json.dumps(record, sort_keys=True, separators=(",", ":")) + "\n"
                for record in records
            ),
            encoding="utf-8",
        )
    payload = json.dumps(summary, indent=2, sort_keys=True) + "\n"
    if args.summary:
        args.summary.write_text(payload, encoding="utf-8")
    print(payload, end="")


if __name__ == "__main__":
    main()
