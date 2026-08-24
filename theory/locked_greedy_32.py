#!/usr/bin/env python3
"""Exact reconstruction of the locked-vertex greedy bound for m=32, n=5.

The paper Grill--Linzmayer (arXiv:2403.05674v3) describes, but does not
publish code or formulas for, its s=2 and s=3 computations.  This file
implements the general counting rule behind the displayed s=1 formulas.
All probabilities use fractions.Fraction and exact binomial coefficients.

This is an exploratory verifier, not by itself a proof of m(5) >= 33: the
selection rule for the locked vertices and every residual profile still have
to be justified/closed.
"""

from __future__ import annotations

if not __debug__:
    raise RuntimeError(
        "locked_greedy_32.py is a proof checker and must be run without "
        "Python -O/-OO, which would remove validation assertions"
    )

import argparse
from fractions import Fraction
from itertools import permutations
from math import ceil, comb


N_UNIFORM = 5
M_EDGES = 32


def C(n: int, k: int) -> int:
    return comb(n, k) if n >= 0 and 0 <= k <= n else 0


def locked_bound(v: int, counts: tuple[int, ...], positions: tuple[int, ...]) -> Fraction:
    """Union/min bound for criticality with selected vertices locked in place.

    counts[mask] is the number of edges whose intersection with the selected
    locked vertices is exactly mask.  positions[i] is the 1-based position
    of locked vertex i.  Products of category sizes upper-bound the number
    of ordered edge pairs having the required unique intersection.
    """
    s = len(positions)
    assert len(counts) == 1 << s
    assert len(positions) == s and len(set(positions)) == s
    assert sum(counts) == M_EDGES and min(counts) >= 0
    locked_at = {position: i for i, position in enumerate(positions)}
    random_vertices = v - s
    total = Fraction(0)

    def locks_before(mask: int, k: int) -> bool:
        return all(positions[i] < k for i in range(s) if mask >> i & 1)

    def locks_after(mask: int, k: int) -> bool:
        return all(positions[i] > k for i in range(s) if mask >> i & 1)

    for k in range(1, v + 1):
        before_slots = sum(position not in locked_at for position in range(1, k))
        after_slots = sum(position not in locked_at for position in range(k + 1, v + 1))

        if k not in locked_at:
            last = Fraction(0)
            first = Fraction(0)
            both = Fraction(0)

            for mask, number in enumerate(counts):
                random_in_edge = N_UNIFORM - mask.bit_count()
                if random_in_edge >= 1 and locks_before(mask, k):
                    last += (
                        number
                        * Fraction(random_in_edge, random_vertices)
                        * Fraction(
                            C(before_slots, random_in_edge - 1),
                            C(random_vertices - 1, random_in_edge - 1),
                        )
                    )
                if random_in_edge >= 1 and locks_after(mask, k):
                    first += (
                        number
                        * Fraction(random_in_edge, random_vertices)
                        * Fraction(
                            C(after_slots, random_in_edge - 1),
                            C(random_vertices - 1, random_in_edge - 1),
                        )
                    )

            for left_mask, left_number in enumerate(counts):
                if not locks_before(left_mask, k):
                    continue
                left_other = N_UNIFORM - left_mask.bit_count() - 1
                if left_other < 0:
                    continue
                for right_mask, right_number in enumerate(counts):
                    if left_mask & right_mask or not locks_after(right_mask, k):
                        continue
                    right_other = N_UNIFORM - right_mask.bit_count() - 1
                    if right_other < 0:
                        continue
                    ordered_pairs = left_number * (
                        right_number - int(left_mask == right_mask)
                    )
                    denominator = (
                        random_vertices
                        * C(random_vertices - 1, left_other)
                        * C(random_vertices - 1 - left_other, right_other)
                    )
                    if ordered_pairs and denominator:
                        both += Fraction(
                            ordered_pairs
                            * C(before_slots, left_other)
                            * C(after_slots, right_other),
                            denominator,
                        )
        else:
            locked_vertex = locked_at[k]
            bit = 1 << locked_vertex
            last = Fraction(0)
            first = Fraction(0)
            both = Fraction(0)

            for mask, number in enumerate(counts):
                if not mask & bit:
                    continue
                other_locks = mask ^ bit
                random_in_edge = N_UNIFORM - mask.bit_count()
                if locks_before(other_locks, k):
                    last += number * Fraction(
                        C(before_slots, random_in_edge),
                        C(random_vertices, random_in_edge),
                    )
                if locks_after(other_locks, k):
                    first += number * Fraction(
                        C(after_slots, random_in_edge),
                        C(random_vertices, random_in_edge),
                    )

            for left_mask, left_number in enumerate(counts):
                if not left_mask & bit or not locks_before(left_mask ^ bit, k):
                    continue
                left_random = N_UNIFORM - left_mask.bit_count()
                for right_mask, right_number in enumerate(counts):
                    if (
                        not right_mask & bit
                        or left_mask & right_mask != bit
                        or not locks_after(right_mask ^ bit, k)
                    ):
                        continue
                    right_random = N_UNIFORM - right_mask.bit_count()
                    ordered_pairs = left_number * (
                        right_number - int(left_mask == right_mask)
                    )
                    denominator = C(random_vertices, left_random) * C(
                        random_vertices - left_random, right_random
                    )
                    if ordered_pairs and denominator:
                        both += Fraction(
                            ordered_pairs
                            * C(before_slots, left_random)
                            * C(after_slots, right_random),
                            denominator,
                        )

        total += min(last, first, both)

    return total


def three_smallest_degree_options(v: int) -> list[tuple[int, int, int]]:
    """Necessary options for the three smallest degrees in a pair cover."""
    minimum = ceil((v - 1) / 4)
    options = []
    for d1 in range(minimum, M_EDGES + 1):
        for d2 in range(d1, M_EDGES + 1):
            for d3 in range(d2, M_EDGES + 1):
                # The other v-3 points have degree at least d3.
                if d1 + d2 + (v - 2) * d3 <= N_UNIFORM * M_EDGES:
                    options.append((d1, d2, d3))
    return options


def category_profiles(degrees: tuple[int, int, int]):
    """Enumerate all eight edge-category counts with these three degrees.

    Pair coverage among the locked vertices is imposed.  Counts are ordered
    by masks 000,001,010,011,100,101,110,111.
    """
    d1, d2, d3 = degrees
    for triple in range(min(degrees) + 1):
        for pair12_only in range(min(d1, d2) - triple + 1):
            for pair13_only in range(min(d1, d3) - triple + 1):
                only1 = d1 - triple - pair12_only - pair13_only
                if only1 < 0:
                    continue
                for pair23_only in range(min(d2, d3) - triple + 1):
                    only2 = d2 - triple - pair12_only - pair23_only
                    only3 = d3 - triple - pair13_only - pair23_only
                    if min(only2, only3) < 0:
                        continue
                    if min(
                        pair12_only + triple,
                        pair13_only + triple,
                        pair23_only + triple,
                    ) < 1:
                        continue
                    values = [
                        0,
                        only1,
                        only2,
                        pair12_only,
                        only3,
                        pair13_only,
                        pair23_only,
                        triple,
                    ]
                    values[0] = M_EDGES - sum(values)
                    if values[0] >= 0:
                        yield tuple(values)


def analyze_vertex_count(v: int) -> None:
    center = ceil(v / 2)
    central_positions = (center - 1, center, center + 1)
    options = three_smallest_degree_options(v)
    profile_count = 0
    residual = []
    worst = (Fraction(0), None)

    for degrees in options:
        for counts in category_profiles(degrees):
            profile_count += 1
            best_placement = min(
                locked_bound(v, counts, positions)
                for positions in permutations(central_positions)
            )
            if best_placement > worst[0]:
                worst = (best_placement, (degrees, counts))
            if best_placement >= 1:
                residual.append((best_placement, degrees, counts))

    print(f"v={v}")
    print(f"  degree triples: {options}")
    print(f"  category profiles checked: {profile_count}")
    print(f"  worst best-placement bound: {worst[0]} = {float(worst[0]):.12f}")
    print(f"  worst profile: {worst[1]}")
    print(f"  residual profiles with bound >= 1: {len(residual)}")
    for value, degrees, counts in sorted(residual, reverse=True)[:20]:
        print(f"    {value} ({float(value):.12f}) d={degrees} l={counts}")


def regression_tests() -> None:
    """Pin three independently recomputed one-lock special cases."""
    expected = {
        (20, 5): Fraction(22953, 24310),
        (21, 6): Fraction(4179, 4199),
        (25, 6): Fraction(223777, 208012),
    }
    for (v, degree), wanted in expected.items():
        got = locked_bound(v, (M_EDGES - degree, degree), ((v + 1) // 2,))
        assert got == wanted, (v, degree, got, wanted)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("v", type=int, choices=range(19, 26), nargs="?")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        regression_tests()
        print("exact one-lock regression checks passed")
    if args.v is not None:
        analyze_vertex_count(args.v)
    elif not args.self_test:
        parser.error("supply v or --self-test")


if __name__ == "__main__":
    main()
