#!/usr/bin/env python3
"""Exhaustive exact optimization over every locked-position assignment.

The event contribution at a position depends only on (i) the set of locks
already passed and (ii) the number of free positions already passed.  For a
fixed trace profile we compute each such state once, scale all state costs to
one integer denominator, and enumerate a lock order plus a weak composition
of the free gaps.  This is exactly the same set as all labelled injections of
the locks into the ``v`` positions, but needs only O(s) integer work per
placement.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from itertools import permutations
from math import lcm
from typing import Iterator, Sequence

from general_locked import C, RANK, locked_bound


def compositions(total: int, parts: int) -> Iterator[tuple[int, ...]]:
    """All weak compositions in deterministic lexicographic order."""
    if parts == 1:
        yield (total,)
        return
    for first in range(total + 1):
        for rest in compositions(total - first, parts - 1):
            yield (first,) + rest


def free_state_cost(
    v: int,
    counts: Sequence[int],
    left_locks: int,
    free_before: int,
) -> Fraction:
    """Exact criticality bound at one free-position state."""
    s = (len(counts) - 1).bit_length()
    full = (1 << s) - 1
    right_locks = full ^ left_locks
    free = v - s
    free_after = free - 1 - free_before
    last = Fraction(0)
    first = Fraction(0)
    paired = Fraction(0)

    for mask, number in enumerate(counts):
        random_in_edge = RANK - mask.bit_count()
        if random_in_edge < 1:
            continue
        if mask & ~left_locks == 0:
            last += number * Fraction(random_in_edge, free) * Fraction(
                C(free_before, random_in_edge - 1),
                C(free - 1, random_in_edge - 1),
            )
        if mask & ~right_locks == 0:
            first += number * Fraction(random_in_edge, free) * Fraction(
                C(free_after, random_in_edge - 1),
                C(free - 1, random_in_edge - 1),
            )

    for left_mask, left_number in enumerate(counts):
        if not left_number or left_mask & ~left_locks:
            continue
        left_other = RANK - left_mask.bit_count() - 1
        if left_other < 0:
            continue
        for right_mask, right_number in enumerate(counts):
            if (
                not right_number
                or left_mask & right_mask
                or right_mask & ~right_locks
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
                paired += Fraction(
                    ordered
                    * C(free_before, left_other)
                    * C(free_after, right_other),
                    denominator,
                )
    return min(last, first, paired)


def locked_state_cost(
    v: int,
    counts: Sequence[int],
    current: int,
    left_locks: int,
    free_before: int,
) -> Fraction:
    """Exact criticality bound at one locked-position state."""
    s = (len(counts) - 1).bit_length()
    full = (1 << s) - 1
    bit = 1 << current
    if left_locks & bit:
        raise ValueError("current lock already lies in left_locks")
    right_locks = full ^ left_locks ^ bit
    free = v - s
    free_after = free - free_before
    last = Fraction(0)
    first = Fraction(0)
    paired = Fraction(0)

    for mask, number in enumerate(counts):
        if not number or not mask & bit:
            continue
        other_locks = mask ^ bit
        random_in_edge = RANK - mask.bit_count()
        if other_locks & ~left_locks == 0:
            last += number * Fraction(
                C(free_before, random_in_edge), C(free, random_in_edge)
            )
        if other_locks & ~right_locks == 0:
            first += number * Fraction(
                C(free_after, random_in_edge), C(free, random_in_edge)
            )

    for left_mask, left_number in enumerate(counts):
        if (
            not left_number
            or not left_mask & bit
            or (left_mask ^ bit) & ~left_locks
        ):
            continue
        left_random = RANK - left_mask.bit_count()
        for right_mask, right_number in enumerate(counts):
            if (
                not right_number
                or not right_mask & bit
                or left_mask & right_mask != bit
                or (right_mask ^ bit) & ~right_locks
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
                paired += Fraction(
                    ordered
                    * C(free_before, left_random)
                    * C(free_after, right_random),
                    denominator,
                )
    return min(last, first, paired)


@dataclass(frozen=True)
class GlobalMinimum:
    bound: Fraction
    positions: tuple[int, ...]
    lock_order: tuple[int, ...]
    gaps: tuple[int, ...]
    placements_checked: int
    placements_covered: int
    automorphism_count: int


@dataclass(frozen=True)
class StateCostModel:
    v: int
    counts: tuple[int, ...]
    denominator: int
    # prefix[mask][b] is the scaled sum of free-state costs for ranks < b.
    free_prefix: tuple[tuple[int, ...], ...]
    locked_weights: dict[tuple[int, int, int], int]

    @classmethod
    def build(cls, v: int, counts: Sequence[int]) -> "StateCostModel":
        counts = tuple(counts)
        s = (len(counts) - 1).bit_length()
        if len(counts) != 1 << s:
            raise ValueError("trace table length is not a power of two")
        free = v - s
        free_costs = {
            (mask, b): free_state_cost(v, counts, mask, b)
            for mask in range(1 << s)
            for b in range(free)
        }
        locked_costs = {
            (current, left, b): locked_state_cost(v, counts, current, left, b)
            for current in range(s)
            for left in range(1 << s)
            if not left >> current & 1
            for b in range(free + 1)
        }
        denominator = 1
        for value in (*free_costs.values(), *locked_costs.values()):
            denominator = lcm(denominator, value.denominator)

        scaled_free = {
            state: value.numerator * (denominator // value.denominator)
            for state, value in free_costs.items()
        }
        scaled_locked = {
            state: value.numerator * (denominator // value.denominator)
            for state, value in locked_costs.items()
        }
        prefixes = []
        for mask in range(1 << s):
            row = [0]
            for b in range(free):
                row.append(row[-1] + scaled_free[(mask, b)])
            prefixes.append(tuple(row))
        return cls(v, counts, denominator, tuple(prefixes), scaled_locked)

    @property
    def lock_count(self) -> int:
        return (len(self.counts) - 1).bit_length()

    def scaled_value(self, order: Sequence[int], gaps: Sequence[int]) -> int:
        s = self.lock_count
        free = self.v - s
        if tuple(sorted(order)) != tuple(range(s)):
            raise ValueError("order must permute lock labels")
        if len(gaps) != s + 1 or sum(gaps) != free or min(gaps) < 0:
            raise ValueError("gaps must weakly compose the free positions")
        left = 0
        free_used = 0
        total = 0
        for j, gap in enumerate(gaps):
            total += self.free_prefix[left][free_used + gap] - self.free_prefix[left][free_used]
            free_used += gap
            if j < s:
                current = order[j]
                total += self.locked_weights[(current, left, free_used)]
                left |= 1 << current
        return total

    def positions(self, order: Sequence[int], gaps: Sequence[int]) -> tuple[int, ...]:
        answer = [0] * self.lock_count
        cursor = 0
        for j, current in enumerate(order):
            cursor += gaps[j]
            answer[current] = cursor + 1
            cursor += 1
        return tuple(answer)

    def evaluate_positions(self, positions: Sequence[int]) -> Fraction:
        labelled = sorted((position, label) for label, position in enumerate(positions))
        order = tuple(label for _, label in labelled)
        gaps = []
        previous = 0
        for position, _ in labelled:
            gaps.append(position - previous - 1)
            previous = position
        gaps.append(self.v - previous)
        return Fraction(self.scaled_value(order, gaps), self.denominator)

    def global_minimum(self) -> GlobalMinimum:
        """Exhaustively minimize over all labelled injections into [1,v].

        Lock orders equivalent under an automorphism of the trace table are
        represented once.  Since such relabelling leaves the objective
        invariant, the quotient is exact; ``placements_covered`` records the
        size of the unquotiented labelled assignment space.
        """
        s = self.lock_count
        free = self.v - s
        gap_vectors = tuple(compositions(free, s + 1))
        all_orders = tuple(permutations(range(s)))
        automorphisms = tuple(
            permutation
            for permutation in all_orders
            if relabel_counts(self.counts, permutation) == self.counts
        )
        order_representatives = tuple(
            order
            for order in all_orders
            if order
            == min(
                tuple(permutation[label] for label in order)
                for permutation in automorphisms
            )
        )
        if len(order_representatives) * len(automorphisms) != len(all_orders):
            raise RuntimeError("automorphism quotient does not cover every lock order")
        best_value: int | None = None
        best_order: tuple[int, ...] | None = None
        best_gaps: tuple[int, ...] | None = None
        checked = 0
        for order in order_representatives:
            for gaps in gap_vectors:
                value = self.scaled_value(order, gaps)
                checked += 1
                if best_value is None or value < best_value:
                    best_value = value
                    best_order = order
                    best_gaps = gaps
        if best_value is None or best_order is None or best_gaps is None:
            raise RuntimeError("global position search evaluated no placement")
        positions = self.positions(best_order, best_gaps)
        return GlobalMinimum(
            Fraction(best_value, self.denominator),
            positions,
            best_order,
            best_gaps,
            checked,
            checked * len(automorphisms),
            len(automorphisms),
        )


def relabel_counts(counts: Sequence[int], permutation: Sequence[int]) -> tuple[int, ...]:
    """Relabel trace-table coordinates by ``old_label -> permutation[label]``."""
    s = (len(counts) - 1).bit_length()
    if tuple(sorted(permutation)) != tuple(range(s)):
        raise ValueError("permutation has the wrong labels")
    answer = [0] * len(counts)
    for old_mask, number in enumerate(counts):
        new_mask = 0
        for old_label in range(s):
            if old_mask >> old_label & 1:
                new_mask |= 1 << permutation[old_label]
        answer[new_mask] = number
    return tuple(answer)


def self_test() -> None:
    fixtures = (
        (20, (15, 4, 4, 2, 4, 2, 2, 0), (1, 2, 12)),
        (21, (14, 5, 5, 1, 5, 1, 1, 0), (1, 2, 3)),
        (
            23,
            (10, 4, 4, 1, 4, 1, 1, 0, 4, 1, 1, 0, 1, 0, 0, 0),
            (10, 11, 12, 13),
        ),
    )
    for v, counts, positions in fixtures:
        model = StateCostModel.build(v, counts)
        got = model.evaluate_positions(positions)
        wanted = locked_bound(v, sum(counts), counts, positions)
        if got != wanted:
            raise RuntimeError(
                f"state/direct mismatch: {(v, positions, got, wanted)!r}"
            )


if __name__ == "__main__":
    self_test()
    print("state optimizer exact cross-check passed")
