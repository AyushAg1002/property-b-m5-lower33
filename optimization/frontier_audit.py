#!/usr/bin/env python3
"""Regenerate exact all-placement frontier data for 32 and 33 edges.

This program is an optimization audit, not a proof of m(5)>=34.  It records
where the locked-permutation machinery succeeds and, crucially, where the
complete position space still has bound at least one.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction
from itertools import permutations
from math import ceil, comb, factorial
from pathlib import Path
from typing import Sequence

from general_locked import locked_bound, self_test as general_self_test, zero_lock_bound
from state_optimizer import StateCostModel, relabel_counts
from trace_partitions import clique_partitions, edge_profile, trace_size_type


EXPECTED = {
    # M=33 complete three-lock position ceilings.
    "m33_three_v20": Fraction(2287, 2210),
    "m33_three_v21": Fraction(119365, 116688),
    "m33_three_v22": Fraction(387055, 369512),
    "m33_three_v23": Fraction(10671, 9880),
    "m33_three_v24": Fraction(89966, 88179),
    "m33_three_v25": Fraction(25888, 24871),
    # M=32 v23 allowed degree-(6,6,7,7) four-lock rows.
    "m32_v23_allowed_0": Fraction(8315, 8398),
    "m32_v23_allowed_1": Fraction(4152, 4199),
    "m32_v23_allowed_2": Fraction(4152, 4199),
    # K4 orbit order: 6K2, K3+3K2, K4.
    "m32_v24_k4_(2, 2, 2, 2, 2, 2)": Fraction(243, 247),
    "m32_v24_k4_(2, 2, 2, 3)": Fraction(16671, 16796),
    "m32_v24_k4_(4,)": Fraction(8323, 8398),
    "m33_v23_k4_(2, 2, 2, 2, 2, 2)": Fraction(4227, 4199),
    "m33_v23_k4_(2, 2, 2, 3)": Fraction(4221, 4199),
    "m33_v23_k4_(4,)": Fraction(4263, 4199),
    "m33_v24_k4_(2, 2, 2, 2, 2, 2)": Fraction(8535, 8398),
    "m33_v24_k4_(2, 2, 2, 3)": Fraction(17217, 16796),
    "m33_v24_k4_(4,)": Fraction(4298, 4199),
    "m33_v25_k4_(2, 2, 2, 2, 2, 2)": Fraction(9441, 9044),
    "m33_v25_k4_(2, 2, 2, 3)": Fraction(4715, 4522),
    "m33_v25_k4_(4,)": Fraction(92290, 88179),
    # K5 orbit order is keyed directly by its trace-size multiset.
    "m32_v25_k5_(2, 2, 2, 2, 2, 2, 2, 2, 2, 2)": Fraction(4188, 4199),
    "m32_v25_k5_(2, 2, 2, 2, 2, 2, 2, 3)": Fraction(16827, 16796),
    "m32_v25_k5_(2, 2, 2, 2, 4)": Fraction(37, 38),
    "m32_v25_k5_(2, 2, 2, 2, 3, 3)": Fraction(20953, 20995),
    "m32_v25_k5_(5,)": Fraction(3899, 4199),
    "m33_v23_k5_(2, 2, 2, 2, 2, 2, 2, 2, 2, 2)": Fraction(1863, 1870),
    "m33_v23_k5_(2, 2, 2, 2, 2, 2, 2, 3)": Fraction(12081, 12155),
    "m33_v23_k5_(2, 2, 2, 2, 4)": Fraction(11758, 12155),
    "m33_v23_k5_(2, 2, 2, 2, 3, 3)": Fraction(4831, 4862),
    "m33_v23_k5_(5,)": Fraction(4515, 4862),
    "m33_v24_k5_(2, 2, 2, 2, 2, 2, 2, 2, 2, 2)": Fraction(8535, 8398),
    "m33_v24_k5_(2, 2, 2, 2, 2, 2, 2, 3)": Fraction(8511, 8398),
    "m33_v24_k5_(2, 2, 2, 2, 4)": Fraction(4213, 4199),
    "m33_v24_k5_(2, 2, 2, 2, 3, 3)": Fraction(8511, 8398),
    "m33_v24_k5_(5,)": Fraction(8071, 8398),
    "m33_v25_k5_(2, 2, 2, 2, 2, 2, 2, 2, 2, 2)": Fraction(8649, 8398),
    "m33_v25_k5_(2, 2, 2, 2, 2, 2, 2, 3)": Fraction(17373, 16796),
    "m33_v25_k5_(2, 2, 2, 2, 4)": Fraction(325, 323),
    "m33_v25_k5_(2, 2, 2, 2, 3, 3)": Fraction(17343, 16796),
    "m33_v25_k5_(5,)": Fraction(8071, 8398),
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def fraction_record(value: Fraction) -> dict[str, int]:
    return {"numerator": value.numerator, "denominator": value.denominator}


def global_record(
    key: str,
    v: int,
    edge_count: int,
    counts: Sequence[int],
    trace_type: tuple[int, ...] | None = None,
) -> dict[str, object]:
    counts = tuple(counts)
    model = StateCostModel.build(v, counts)
    result = model.global_minimum()
    expected = EXPECTED[key]
    require(result.bound == expected, f"{key}: {result.bound} != {expected}")
    direct = locked_bound(v, edge_count, counts, result.positions)
    require(direct == result.bound, f"{key}: direct evaluator mismatch")
    full_count = factorial(v) // factorial(v - model.lock_count)
    require(
        result.placements_covered == full_count,
        f"{key}: covered {result.placements_covered} of {full_count}",
    )
    return {
        "key": key,
        "vertices": v,
        "edges": edge_count,
        "lock_count": model.lock_count,
        "trace_type": list(trace_type) if trace_type is not None else None,
        "counts_by_mask": list(counts),
        "global_minimum": fraction_record(result.bound),
        "one_minimizing_labelled_assignment": list(result.positions),
        "quotient_placements_checked": result.placements_checked,
        "labelled_placements_covered": result.placements_covered,
        "trace_automorphism_count": result.automorphism_count,
        "direct_evaluator_match": True,
        "strictly_below_one": result.bound < 1,
        "strictly_above_one": result.bound > 1,
    }


def orbit_representatives(
    lock_count: int, degrees: tuple[int, ...], edge_count: int
) -> tuple[tuple[tuple[int, ...], tuple[int, ...]], ...]:
    """One canonical trace table for each S_lock_count relabelling orbit."""
    groups: dict[tuple[int, ...], tuple[int, ...]] = {}
    label_permutations = tuple(permutations(range(lock_count)))
    for partition in clique_partitions(lock_count):
        counts = edge_profile(partition, degrees, edge_count)
        canonical = min(relabel_counts(counts, p) for p in label_permutations)
        groups.setdefault(canonical, trace_size_type(partition))
    expected_orbits = {4: 3, 5: 5}[lock_count]
    require(len(groups) == expected_orbits, f"K{lock_count}: got {len(groups)} orbits")
    return tuple(sorted((trace_type, counts) for counts, trace_type in groups.items()))


def build_report() -> dict[str, object]:
    general_self_test()
    pair_surplus = 10 * 33 - comb(19, 2)
    gamma = 33 * 32 - 2 * ceil(pair_surplus / 6)
    zero = zero_lock_bound(19, 33, gamma)
    require(pair_surplus == 159 and gamma == 1002, "v19 surplus calculation changed")
    require(zero == Fraction(228291, 230945) < 1, "v19 certificate changed")
    require(26 * ceil(25 / 4) == 182 > 165, "v26 degree contradiction changed")

    three_cases = (
        ("m33_three_v20", 20, (15, 4, 4, 2, 4, 2, 2, 0)),
        ("m33_three_v21", 21, (15, 5, 5, 1, 5, 1, 1, 0)),
        ("m33_three_v22", 22, (15, 5, 5, 1, 5, 1, 1, 0)),
        ("m33_three_v23", 23, (15, 5, 5, 1, 5, 1, 1, 0)),
        ("m33_three_v24", 24, (19, 4, 4, 0, 4, 0, 0, 2)),
        ("m33_three_v25", 25, (19, 4, 4, 0, 4, 0, 0, 2)),
    )
    three_rows = [global_record(key, v, 33, counts) for key, v, counts in three_cases]

    # Three structurally allowed v23 rows from the existing m=32 proof.
    allowed_rows = []
    allowed_index = 0
    for partition in clique_partitions(4):
        trace_on_low_pair = next(trace for trace in partition if trace & 3 == 3)
        if trace_on_low_pair != 3:
            continue
        counts = edge_profile(partition, (6, 6, 7, 7), 32)
        key = f"m32_v23_allowed_{allowed_index}"
        allowed_rows.append(global_record(key, 23, 32, counts, trace_size_type(partition)))
        allowed_index += 1
    require(len(allowed_rows) == 3, "v23 allowed family no longer has three rows")

    orbit_rows = []
    orbit_specs = (
        (32, 24, 4, (6, 6, 6, 6)),
        (33, 23, 4, (6, 6, 6, 6)),
        (33, 24, 4, (6, 6, 6, 6)),
        (33, 25, 4, (6, 6, 6, 6)),
        (32, 25, 5, (6, 6, 6, 6, 6)),
        (33, 23, 5, (6, 6, 6, 6, 6)),
        (33, 24, 5, (6, 6, 6, 6, 6)),
        (33, 25, 5, (6, 6, 6, 6, 6)),
    )
    for edge_count, v, lock_count, degrees in orbit_specs:
        for trace_type, counts in orbit_representatives(lock_count, degrees, edge_count):
            key = f"m{edge_count}_v{v}_k{lock_count}_{trace_type}"
            orbit_rows.append(global_record(key, v, edge_count, counts, trace_type))

    report = {
        "schema": "property-b-m5-locked-frontier-audit-v1",
        "arithmetic": "Python fractions.Fraction; no floating-point acceptance",
        "python_optimized_mode_note": (
            "All acceptance checks in this driver use explicit RuntimeError guards."
        ),
        "m33_normal_form": {
            "pair_covered_vertex_range_before_greedy": [19, 26],
            "v19_pair_surplus": pair_surplus,
            "v19_ordered_unique_intersection_cap": gamma,
            "v19_zero_lock_bound": fraction_record(zero),
            "v26_minimum_degree": 7,
            "v26_minimum_degree_sum": 182,
            "actual_degree_sum": 165,
            "remaining_vertex_counts": [20, 21, 22, 23, 24, 25],
        },
        "m33_three_lock_global_ceiling_rows": three_rows,
        "m32_v23_allowed_four_lock_rows": allowed_rows,
        "clique_partition_orbit_rows": orbit_rows,
        "conclusion": (
            "The exact locked-permutation method with complete position optimization "
            "does not by itself exclude 33-edge cores.  In particular the v=25 "
            "degree-six 10K2 profile has global minimum 8649/8398>1."
        ),
    }
    payload = json.dumps(report, sort_keys=True, separators=(",", ":")).encode("utf-8")
    report["content_sha256_without_this_field"] = hashlib.sha256(payload).hexdigest()
    return report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = build_report()
    payload = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(payload, encoding="utf-8")
    print(payload, end="")


if __name__ == "__main__":
    main()
