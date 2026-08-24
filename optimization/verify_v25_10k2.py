#!/usr/bin/env python3
"""Independent exhaustive verifier for the M=33, v=25, 10K2 ceiling.

Five labelled degree-six vertices with pair-codegree one and ten separate
pair traces have the fully symmetric trace table

    l_empty=13, l_singleton=2, l_pair=1, all other l_A=0.

The verifier derives every state contribution directly from the binomial
probabilities, fixes one label order using the explicitly checked S5
symmetry, and enumerates all C(25,5)=53,130 unordered position sets.  These
represent all 25P5=6,375,600 labelled placements.  It imports the generalized
evaluator only for a final equality check at the reported minimizer.

No proof-critical check uses ``assert``; running Python with ``-O`` leaves
all acceptance checks active.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction
from itertools import combinations, permutations
from math import comb, factorial
from pathlib import Path
from typing import Sequence


V = 25
LOCKS = 5
FREE = V - LOCKS
EDGE_COUNT = 33
EXPECTED_MINIMUM = Fraction(8649, 8398)
EXPECTED_POSITIONS = (11, 12, 13, 14, 15)
EXPECTED_QUOTIENT_COUNT = 53130
EXPECTED_LABELLED_COUNT = 6375600
EXPECTED_ROW_SHA256 = "1ad597008faafc801ebda73698880b6bd4a390e2a3b62341743321f5de236850"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def C(n: int, k: int) -> int:
    return comb(n, k) if n >= 0 and 0 <= k <= n else 0


def trace_counts() -> tuple[int, ...]:
    counts = [0] * (1 << LOCKS)
    counts[0] = 13
    for i in range(LOCKS):
        counts[1 << i] = 2
    for i, j in combinations(range(LOCKS), 2):
        counts[(1 << i) | (1 << j)] = 1
    require(sum(counts) == EDGE_COUNT, "trace counts do not sum to 33")
    return tuple(counts)


def relabel_mask(mask: int, permutation: Sequence[int]) -> int:
    answer = 0
    for old in range(LOCKS):
        if mask >> old & 1:
            answer |= 1 << permutation[old]
    return answer


def check_full_symmetry(counts: Sequence[int]) -> int:
    automorphisms = 0
    for permutation in permutations(range(LOCKS)):
        relabelled = [0] * len(counts)
        for mask, number in enumerate(counts):
            relabelled[relabel_mask(mask, permutation)] = number
        if tuple(relabelled) == tuple(counts):
            automorphisms += 1
    require(automorphisms == factorial(LOCKS), "trace profile is not S5-invariant")
    return automorphisms


def free_cost(counts: Sequence[int], left: int, b: int) -> Fraction:
    """Derive min(last,first,paired) for a free vertex state."""
    right = ((1 << LOCKS) - 1) ^ left
    a = FREE - 1 - b
    last = Fraction(0)
    first = Fraction(0)
    paired = Fraction(0)
    nonzero = tuple((mask, number) for mask, number in enumerate(counts) if number)

    for mask, number in nonzero:
        random_points = 5 - mask.bit_count()
        if random_points >= 1 and mask & ~left == 0:
            last += number * Fraction(random_points, FREE) * Fraction(
                C(b, random_points - 1), C(FREE - 1, random_points - 1)
            )
        if random_points >= 1 and mask & ~right == 0:
            first += number * Fraction(random_points, FREE) * Fraction(
                C(a, random_points - 1), C(FREE - 1, random_points - 1)
            )

    for left_mask, left_number in nonzero:
        if left_mask & ~left:
            continue
        red_other = 4 - left_mask.bit_count()
        if red_other < 0:
            continue
        for right_mask, right_number in nonzero:
            if left_mask & right_mask or right_mask & ~right:
                continue
            blue_other = 4 - right_mask.bit_count()
            if blue_other < 0:
                continue
            ordered_pairs = left_number * (
                right_number - int(left_mask == right_mask)
            )
            denominator = (
                FREE
                * C(FREE - 1, red_other)
                * C(FREE - 1 - red_other, blue_other)
            )
            if ordered_pairs and denominator:
                paired += Fraction(
                    ordered_pairs * C(b, red_other) * C(a, blue_other),
                    denominator,
                )
    return min(last, first, paired)


def locked_cost(counts: Sequence[int], current: int, left: int, b: int) -> Fraction:
    """Derive min(last,first,paired) for the next lock in fixed label order."""
    current_bit = 1 << current
    right = ((1 << LOCKS) - 1) ^ left ^ current_bit
    a = FREE - b
    last = Fraction(0)
    first = Fraction(0)
    paired = Fraction(0)
    nonzero = tuple((mask, number) for mask, number in enumerate(counts) if number)

    for mask, number in nonzero:
        if not mask & current_bit:
            continue
        other_locks = mask ^ current_bit
        random_points = 5 - mask.bit_count()
        if other_locks & ~left == 0:
            last += number * Fraction(C(b, random_points), C(FREE, random_points))
        if other_locks & ~right == 0:
            first += number * Fraction(C(a, random_points), C(FREE, random_points))

    for left_mask, left_number in nonzero:
        if not left_mask & current_bit or (left_mask ^ current_bit) & ~left:
            continue
        red_random = 5 - left_mask.bit_count()
        for right_mask, right_number in nonzero:
            if (
                not right_mask & current_bit
                or left_mask & right_mask != current_bit
                or (right_mask ^ current_bit) & ~right
            ):
                continue
            blue_random = 5 - right_mask.bit_count()
            ordered_pairs = left_number * (
                right_number - int(left_mask == right_mask)
            )
            denominator = C(FREE, red_random) * C(FREE - red_random, blue_random)
            if ordered_pairs and denominator:
                paired += Fraction(
                    ordered_pairs * C(b, red_random) * C(a, blue_random),
                    denominator,
                )
    return min(last, first, paired)


def build_prefix_tables(counts: Sequence[int]):
    """Precompute exact state costs for fixed order 0,1,2,3,4."""
    prefixes = []
    locks = []
    left = 0
    for current in range(LOCKS + 1):
        row = [Fraction(0)]
        for b in range(FREE):
            row.append(row[-1] + free_cost(counts, left, b))
        prefixes.append(tuple(row))
        if current < LOCKS:
            locks.append(
                tuple(locked_cost(counts, current, left, b) for b in range(FREE + 1))
            )
            left |= 1 << current
    return tuple(prefixes), tuple(locks)


def bound_for_positions(
    positions: tuple[int, ...],
    prefixes: Sequence[Sequence[Fraction]],
    locks: Sequence[Sequence[Fraction]],
) -> Fraction:
    free_used = 0
    previous_position = 0
    answer = Fraction(0)
    for stage, position in enumerate(positions):
        gap = position - previous_position - 1
        answer += prefixes[stage][free_used + gap] - prefixes[stage][free_used]
        free_used += gap
        answer += locks[stage][free_used]
        previous_position = position
    answer += prefixes[LOCKS][FREE] - prefixes[LOCKS][free_used]
    return answer


def verify() -> dict[str, object]:
    counts = trace_counts()
    automorphisms = check_full_symmetry(counts)
    prefixes, locks = build_prefix_tables(counts)
    digest = hashlib.sha256()
    minimum: Fraction | None = None
    minimizers: list[tuple[int, ...]] = []
    checked = 0
    for positions in combinations(range(1, V + 1), LOCKS):
        value = bound_for_positions(positions, prefixes, locks)
        digest.update(
            (",".join(map(str, positions)) + f":{value.numerator}/{value.denominator}\n").encode(
                "ascii"
            )
        )
        checked += 1
        if minimum is None or value < minimum:
            minimum = value
            minimizers = [positions]
        elif value == minimum:
            minimizers.append(positions)

    require(checked == EXPECTED_QUOTIENT_COUNT, f"checked {checked} quotient rows")
    require(minimum == EXPECTED_MINIMUM, f"minimum changed to {minimum}")
    require(EXPECTED_POSITIONS in minimizers, "central minimizer missing")
    labelled = checked * automorphisms
    require(labelled == EXPECTED_LABELLED_COUNT, f"labelled count is {labelled}")
    row_hash = digest.hexdigest()
    if EXPECTED_ROW_SHA256 != "TO_BE_PINNED":
        require(row_hash == EXPECTED_ROW_SHA256, f"row hash changed to {row_hash}")

    # Cross-check one decisive row against the separately implemented general evaluator.
    from general_locked import locked_bound

    direct = locked_bound(V, EDGE_COUNT, counts, EXPECTED_POSITIONS)
    require(direct == minimum, f"direct evaluator gives {direct}, state sweep gives {minimum}")
    return {
        "schema": "property-b-m5-v25-10k2-global-ceiling-v1",
        "arithmetic": "fractions.Fraction only",
        "python_optimized_mode_safe": True,
        "vertices": V,
        "edges": EDGE_COUNT,
        "trace_profile": list(counts),
        "automorphism_count": automorphisms,
        "quotient_position_sets_checked": checked,
        "labelled_placements_covered": labelled,
        "minimum": {"numerator": minimum.numerator, "denominator": minimum.denominator},
        "one_minimizer": list(EXPECTED_POSITIONS),
        "minimizer_count_in_quotient": len(minimizers),
        "direct_evaluator_match": True,
        "row_sha256": row_hash,
        "strictly_above_one": minimum > 1,
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
