#!/usr/bin/env python3
"""Independent exact verifier for both v=25 branches of the m=32 selection lemma.

At 33 edges the old selection lemma can force either a 10K2 trace table or
one of five labelled K4+4K2 tables.  This verifier proves that complete
position optimization leaves both branches above one.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction
from itertools import combinations, permutations
from math import factorial
from pathlib import Path
from typing import Sequence

from general_locked import locked_bound
from verify_v25_10k2 import (
    EDGE_COUNT,
    FREE,
    LOCKS,
    V,
    free_cost,
    locked_cost,
    relabel_mask,
    require,
    verify as verify_10k2,
)


EXPECTED_K4_MINIMUM = Fraction(325, 323)
EXPECTED_K4_POSITIONS = (12, 1, 13, 14, 15)
EXPECTED_K4_QUOTIENT_ROWS = 265650
EXPECTED_K4_ROW_SHA256 = "33724380a6ebb4691f8e50f7a362031edbf69ab7a2c3706aa55c893709d9fd05"


def k4_plus_pairs_counts() -> tuple[int, ...]:
    """K4 on labels 1..4 plus the four pairs from label 0."""
    counts = [0] * (1 << LOCKS)
    block = sum(1 << i for i in range(1, LOCKS))
    counts[block] = 1
    for i in range(1, LOCKS):
        counts[1 | (1 << i)] = 1
    for i in range(LOCKS):
        used = sum(number for mask, number in enumerate(counts) if mask >> i & 1)
        counts[1 << i] = 6 - used
    counts[0] = EDGE_COUNT - sum(counts)
    require(min(counts) >= 0 and sum(counts) == EDGE_COUNT, "invalid K4 profile")
    return tuple(counts)


def relabel_counts(counts: Sequence[int], permutation: Sequence[int]) -> tuple[int, ...]:
    answer = [0] * len(counts)
    for mask, number in enumerate(counts):
        answer[relabel_mask(mask, permutation)] = number
    return tuple(answer)


def automorphisms_and_orbit(counts: Sequence[int]) -> tuple[int, int]:
    relabelled = {
        relabel_counts(counts, permutation)
        for permutation in permutations(range(LOCKS))
    }
    orbit_size = len(relabelled)
    automorphisms = factorial(LOCKS) // orbit_size
    require(orbit_size == 5, f"expected five labelled K4 profiles, got {orbit_size}")
    require(automorphisms == 24, f"expected automorphism group 24, got {automorphisms}")
    return automorphisms, orbit_size


def order_tables(counts: Sequence[int], order: tuple[int, ...]):
    prefixes = []
    locks = []
    left = 0
    for stage in range(LOCKS + 1):
        row = [Fraction(0)]
        for b in range(FREE):
            row.append(row[-1] + free_cost(counts, left, b))
        prefixes.append(tuple(row))
        if stage < LOCKS:
            current = order[stage]
            locks.append(
                tuple(locked_cost(counts, current, left, b) for b in range(FREE + 1))
            )
            left |= 1 << current
    return tuple(prefixes), tuple(locks)


def value_for_positions(
    positions: tuple[int, ...],
    prefixes: Sequence[Sequence[Fraction]],
    locks: Sequence[Sequence[Fraction]],
) -> Fraction:
    free_used = 0
    previous = 0
    answer = Fraction(0)
    for stage, position in enumerate(positions):
        gap = position - previous - 1
        answer += prefixes[stage][free_used + gap] - prefixes[stage][free_used]
        free_used += gap
        answer += locks[stage][free_used]
        previous = position
    answer += prefixes[LOCKS][FREE] - prefixes[LOCKS][free_used]
    return answer


def verify_k4_branch() -> dict[str, object]:
    counts = k4_plus_pairs_counts()
    automorphisms, orbit_size = automorphisms_and_orbit(counts)
    # Quotient label orders: label 0 is distinguished; labels 1..4 are symmetric.
    orders = []
    for distinguished_rank in range(LOCKS):
        others = iter(range(1, LOCKS))
        order = []
        for rank in range(LOCKS):
            order.append(0 if rank == distinguished_rank else next(others))
        orders.append(tuple(order))
    require(len(set(orders)) == 5, "order quotient is not of size five")

    digest = hashlib.sha256()
    minimum: Fraction | None = None
    minimizing_assignment: tuple[int, ...] | None = None
    checked = 0
    for order in orders:
        prefixes, locks = order_tables(counts, order)
        for position_set in combinations(range(1, V + 1), LOCKS):
            value = value_for_positions(position_set, prefixes, locks)
            labelled_positions = [0] * LOCKS
            for rank, label in enumerate(order):
                labelled_positions[label] = position_set[rank]
            labelled_positions_tuple = tuple(labelled_positions)
            digest.update(
                (
                    ",".join(map(str, order))
                    + ":"
                    + ",".join(map(str, position_set))
                    + f":{value.numerator}/{value.denominator}\n"
                ).encode("ascii")
            )
            checked += 1
            if minimum is None or value < minimum:
                minimum = value
                minimizing_assignment = labelled_positions_tuple
    require(checked == EXPECTED_K4_QUOTIENT_ROWS, f"checked {checked} rows")
    require(minimum == EXPECTED_K4_MINIMUM, f"minimum changed to {minimum}")
    require(
        minimizing_assignment == EXPECTED_K4_POSITIONS,
        f"minimizer changed to {minimizing_assignment}",
    )
    row_hash = digest.hexdigest()
    if EXPECTED_K4_ROW_SHA256 != "TO_BE_PINNED":
        require(row_hash == EXPECTED_K4_ROW_SHA256, f"row hash changed to {row_hash}")
    direct = locked_bound(V, EDGE_COUNT, counts, EXPECTED_K4_POSITIONS)
    require(direct == minimum, f"direct evaluator gives {direct}")
    representative_labelled_placements = checked * automorphisms
    require(
        representative_labelled_placements == factorial(V) // factorial(V - LOCKS),
        "quotient does not cover all representative assignments",
    )
    return {
        "trace_type": "K4+4K2",
        "labelled_trace_profiles_in_orbit": orbit_size,
        "representative_trace_counts": list(counts),
        "trace_automorphism_count": automorphisms,
        "quotient_rows_checked": checked,
        "representative_labelled_placements_covered": representative_labelled_placements,
        "minimum": {"numerator": minimum.numerator, "denominator": minimum.denominator},
        "one_minimizing_assignment_by_label": list(EXPECTED_K4_POSITIONS),
        "direct_evaluator_match": True,
        "row_sha256": row_hash,
        "strictly_above_one": minimum > 1,
    }


def verify() -> dict[str, object]:
    ten_pairs = verify_10k2()
    k4_branch = verify_k4_branch()
    return {
        "schema": "property-b-m5-v25-old-selection-global-ceiling-v1",
        "arithmetic": "fractions.Fraction only",
        "python_optimized_mode_safe": True,
        "ten_separate_pairs_branch": ten_pairs,
        "k4_plus_four_pairs_branch": k4_branch,
        "conclusion": (
            "Both non-K5 outcomes forced by the m=32 v25 selection argument "
            "remain strictly above one at 33 edges under every placement."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = verify()
    payload = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(payload, encoding="utf-8")
    print(payload, end="")


if __name__ == "__main__":
    main()
