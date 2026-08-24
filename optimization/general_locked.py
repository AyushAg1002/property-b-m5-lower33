#!/usr/bin/env python3
"""Exact locked-permutation bounds for arbitrary 5-uniform edge count.

This is an independent optimization sandbox.  It intentionally does not
import the canonical m=32 evaluator: the edge count is an explicit argument
and all comparisons use ``fractions.Fraction``.
"""

from __future__ import annotations

from fractions import Fraction
from itertools import permutations
from math import ceil, comb
from typing import Iterable, Iterator, Sequence


RANK = 5


def C(n: int, k: int) -> int:
    """Binomial coefficient, extended by zero outside its natural range."""
    return comb(n, k) if n >= 0 and 0 <= k <= n else 0


def locked_bound(
    v: int,
    edge_count: int,
    counts: Sequence[int],
    positions: Sequence[int],
) -> Fraction:
    """Return the exact locked-permutation union bound.

    ``counts[mask]`` is the number of edges with precisely that trace on the
    labelled locked set.  ``positions[i]`` is the 1-based position of lock i.
    Products of category sizes are safe upper bounds on compatible ordered
    edge-pair counts, exactly as in the general locked-permutation lemma.
    """
    positions = tuple(positions)
    counts = tuple(counts)
    s = len(positions)
    if len(counts) != 1 << s:
        raise ValueError("trace table has the wrong size")
    if len(set(positions)) != s or any(not 1 <= p <= v for p in positions):
        raise ValueError("locked positions must be distinct and lie in [1,v]")
    if sum(counts) != edge_count or min(counts, default=0) < 0:
        raise ValueError("trace counts must be nonnegative and sum to edge_count")

    locked_at = {position: i for i, position in enumerate(positions)}
    free = v - s
    total = Fraction(0)

    def locks_before(mask: int, k: int) -> bool:
        return all(positions[i] < k for i in range(s) if mask >> i & 1)

    def locks_after(mask: int, k: int) -> bool:
        return all(positions[i] > k for i in range(s) if mask >> i & 1)

    for k in range(1, v + 1):
        before = sum(position not in locked_at for position in range(1, k))
        after = sum(position not in locked_at for position in range(k + 1, v + 1))
        last = Fraction(0)
        first = Fraction(0)
        both = Fraction(0)

        if k not in locked_at:
            for mask, number in enumerate(counts):
                random_in_edge = RANK - mask.bit_count()
                if random_in_edge >= 1 and locks_before(mask, k):
                    last += number * Fraction(random_in_edge, free) * Fraction(
                        C(before, random_in_edge - 1),
                        C(free - 1, random_in_edge - 1),
                    )
                if random_in_edge >= 1 and locks_after(mask, k):
                    first += number * Fraction(random_in_edge, free) * Fraction(
                        C(after, random_in_edge - 1),
                        C(free - 1, random_in_edge - 1),
                    )

            for left_mask, left_number in enumerate(counts):
                if not left_number or not locks_before(left_mask, k):
                    continue
                left_other = RANK - left_mask.bit_count() - 1
                if left_other < 0:
                    continue
                for right_mask, right_number in enumerate(counts):
                    if (
                        not right_number
                        or left_mask & right_mask
                        or not locks_after(right_mask, k)
                    ):
                        continue
                    right_other = RANK - right_mask.bit_count() - 1
                    if right_other < 0:
                        continue
                    ordered = left_number * (
                        right_number - int(left_mask == right_mask)
                    )
                    denominator = (
                        free
                        * C(free - 1, left_other)
                        * C(free - 1 - left_other, right_other)
                    )
                    if ordered and denominator:
                        both += Fraction(
                            ordered
                            * C(before, left_other)
                            * C(after, right_other),
                            denominator,
                        )
        else:
            locked_vertex = locked_at[k]
            bit = 1 << locked_vertex
            for mask, number in enumerate(counts):
                if not number or not mask & bit:
                    continue
                other_locks = mask ^ bit
                random_in_edge = RANK - mask.bit_count()
                if locks_before(other_locks, k):
                    last += number * Fraction(
                        C(before, random_in_edge), C(free, random_in_edge)
                    )
                if locks_after(other_locks, k):
                    first += number * Fraction(
                        C(after, random_in_edge), C(free, random_in_edge)
                    )

            for left_mask, left_number in enumerate(counts):
                if (
                    not left_number
                    or not left_mask & bit
                    or not locks_before(left_mask ^ bit, k)
                ):
                    continue
                left_random = RANK - left_mask.bit_count()
                for right_mask, right_number in enumerate(counts):
                    if (
                        not right_number
                        or not right_mask & bit
                        or left_mask & right_mask != bit
                        or not locks_after(right_mask ^ bit, k)
                    ):
                        continue
                    right_random = RANK - right_mask.bit_count()
                    ordered = left_number * (
                        right_number - int(left_mask == right_mask)
                    )
                    denominator = C(free, left_random) * C(
                        free - left_random, right_random
                    )
                    if ordered and denominator:
                        both += Fraction(
                            ordered
                            * C(before, left_random)
                            * C(after, right_random),
                            denominator,
                        )

        total += min(last, first, both)
    return total


def zero_lock_bound(v: int, edge_count: int, gamma: int | None = None) -> Fraction:
    """Exact unconditioned greedy bound with an optional ordered-pair cap."""
    if gamma is None:
        gamma = edge_count * (edge_count - 1)
    denominator4 = C(v - 1, 4)
    denominator8 = denominator4 * C(v - 5, 4)
    answer = Fraction(0)
    for k in range(1, v + 1):
        last = Fraction(RANK * edge_count * C(k - 1, 4), v * denominator4)
        first = Fraction(RANK * edge_count * C(v - k, 4), v * denominator4)
        both = Fraction(
            gamma * C(k - 1, 4) * C(v - k, 4), v * denominator8
        )
        answer += min(last, first, both)
    return answer


def low_degree_options(
    v: int, edge_count: int, lock_count: int
) -> Iterator[tuple[int, ...]]:
    """Safe options for the ``lock_count`` smallest degrees in a pair cover."""
    minimum = ceil((v - 1) / 4)

    def visit(prefix: tuple[int, ...]) -> Iterator[tuple[int, ...]]:
        if len(prefix) == lock_count:
            # Selected degrees plus all unselected degrees at least the last.
            if sum(prefix) + (v - lock_count) * prefix[-1] <= RANK * edge_count:
                yield prefix
            return
        lower = prefix[-1] if prefix else minimum
        for degree in range(lower, edge_count + 1):
            candidate = prefix + (degree,)
            optimistic = sum(candidate)
            remaining_selected = lock_count - len(candidate)
            optimistic += (remaining_selected + v - lock_count) * degree
            if optimistic > RANK * edge_count:
                break
            yield from visit(candidate)

    yield from visit(())


def three_lock_profiles(
    edge_count: int, degrees: tuple[int, int, int]
) -> Iterator[tuple[int, ...]]:
    """Enumerate the safe-superset trace tables for three pair-covered locks."""
    d1, d2, d3 = degrees
    for triple in range(min(degrees) + 1):
        for pair12 in range(min(d1, d2) - triple + 1):
            for pair13 in range(min(d1, d3) - triple + 1):
                only1 = d1 - triple - pair12 - pair13
                if only1 < 0:
                    continue
                for pair23 in range(min(d2, d3) - triple + 1):
                    only2 = d2 - triple - pair12 - pair23
                    only3 = d3 - triple - pair13 - pair23
                    if min(only2, only3) < 0:
                        continue
                    if min(pair12 + triple, pair13 + triple, pair23 + triple) < 1:
                        continue
                    counts = [0, only1, only2, pair12, only3, pair13, pair23, triple]
                    counts[0] = edge_count - sum(counts)
                    if counts[0] >= 0:
                        yield tuple(counts)


def assignments_from_bases(
    bases: Iterable[Sequence[int]],
) -> tuple[tuple[int, ...], ...]:
    """All distinct label assignments generated from position bases."""
    return tuple(sorted({p for base in bases for p in permutations(base)}))


def best_bound(
    v: int,
    edge_count: int,
    counts: Sequence[int],
    assignments: Iterable[Sequence[int]],
) -> tuple[Fraction, tuple[int, ...]]:
    """Best exact bound and deterministic placement witness."""
    return min(
        (locked_bound(v, edge_count, counts, positions), tuple(positions))
        for positions in assignments
    )


def self_test() -> None:
    """Pin canonical m=32 values and direct zero-lock computations."""
    expected_one_lock = {
        (20, 5): Fraction(22953, 24310),
        (21, 6): Fraction(4179, 4199),
        (25, 6): Fraction(223777, 208012),
    }
    for (v, degree), wanted in expected_one_lock.items():
        got = locked_bound(v, 32, (32 - degree, degree), ((v + 1) // 2,))
        if got != wanted:
            raise RuntimeError(
                f"one-lock regression changed: {(v, degree, got, wanted)!r}"
            )
    expected_zero_lock = {
        (19, 992): Fraction(222656, 230945),
        (20, 948): Fraction(20874, 20995),
    }
    for (v, gamma), wanted in expected_zero_lock.items():
        got = zero_lock_bound(v, 32, gamma)
        if got != wanted:
            raise RuntimeError(
                f"zero-lock regression changed: {(v, gamma, got, wanted)!r}"
            )


if __name__ == "__main__":
    self_test()
    print("general exact evaluator self-test passed")
