#!/usr/bin/env python3
"""Compiled exact kernels for fast locked-profile sweeps.

For fixed ``(v, positions)`` each last/first event is linear in the trace
counts and each paired event is quadratic.  This module compiles their
rational coefficients to common-denominator integer polynomials.  Profile
evaluation then uses integers except for the final sum of at most ``v``
selected minima.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from math import lcm
from typing import Iterable, Sequence

from general_locked import C, RANK, locked_bound


Monomial = tuple[int, ...]


@dataclass(frozen=True)
class IntPolynomial:
    denominator: int
    terms: tuple[tuple[int, Monomial], ...]

    @classmethod
    def compile(cls, coefficients: dict[Monomial, Fraction]) -> "IntPolynomial":
        coefficients = {m: c for m, c in coefficients.items() if c}
        denominator = 1
        for coefficient in coefficients.values():
            denominator = lcm(denominator, coefficient.denominator)
        terms = tuple(
            sorted(
                (
                    coefficient.numerator
                    * (denominator // coefficient.denominator),
                    monomial,
                )
                for monomial, coefficient in coefficients.items()
            )
        )
        return cls(denominator, terms)

    def evaluate(self, counts: Sequence[int]) -> tuple[int, int]:
        numerator = 0
        for coefficient, monomial in self.terms:
            product = 1
            for index in monomial:
                product *= counts[index]
            numerator += coefficient * product
        return numerator, self.denominator


@dataclass(frozen=True)
class PositionEvents:
    last: IntPolynomial
    first: IntPolynomial
    paired: IntPolynomial


@dataclass(frozen=True)
class LockedKernel:
    v: int
    edge_count: int
    positions: tuple[int, ...]
    events: tuple[PositionEvents, ...]

    def evaluate(self, counts: Sequence[int]) -> Fraction:
        if len(counts) != 1 << len(self.positions):
            raise ValueError("trace table has the wrong size")
        if sum(counts) != self.edge_count or min(counts) < 0:
            raise ValueError("invalid trace counts")
        total = Fraction(0)
        for event in self.events:
            values = (
                event.last.evaluate(counts),
                event.first.evaluate(counts),
                event.paired.evaluate(counts),
            )
            numerator, denominator = min(
                values, key=lambda x: Fraction(x[0], x[1])
            )
            total += Fraction(numerator, denominator)
        return total


def add(
    coefficients: dict[Monomial, Fraction],
    monomial: Monomial,
    coefficient: Fraction,
) -> None:
    if coefficient:
        coefficients[monomial] = coefficients.get(monomial, Fraction(0)) + coefficient


def compile_kernel(v: int, edge_count: int, positions: Sequence[int]) -> LockedKernel:
    """Compile the exact evaluator for one labelled position assignment."""
    positions = tuple(positions)
    s = len(positions)
    if len(set(positions)) != s or any(not 1 <= p <= v for p in positions):
        raise ValueError("invalid locked positions")
    locked_at = {position: i for i, position in enumerate(positions)}
    free = v - s
    mask_count = 1 << s

    def locks_before(mask: int, k: int) -> bool:
        return all(positions[i] < k for i in range(s) if mask >> i & 1)

    def locks_after(mask: int, k: int) -> bool:
        return all(positions[i] > k for i in range(s) if mask >> i & 1)

    compiled = []
    for k in range(1, v + 1):
        before = sum(position not in locked_at for position in range(1, k))
        after = sum(position not in locked_at for position in range(k + 1, v + 1))
        last: dict[Monomial, Fraction] = {}
        first: dict[Monomial, Fraction] = {}
        paired: dict[Monomial, Fraction] = {}

        if k not in locked_at:
            for mask in range(mask_count):
                random_in_edge = RANK - mask.bit_count()
                if random_in_edge >= 1 and locks_before(mask, k):
                    add(
                        last,
                        (mask,),
                        Fraction(random_in_edge, free)
                        * Fraction(
                            C(before, random_in_edge - 1),
                            C(free - 1, random_in_edge - 1),
                        ),
                    )
                if random_in_edge >= 1 and locks_after(mask, k):
                    add(
                        first,
                        (mask,),
                        Fraction(random_in_edge, free)
                        * Fraction(
                            C(after, random_in_edge - 1),
                            C(free - 1, random_in_edge - 1),
                        ),
                    )

            for left_mask in range(mask_count):
                if not locks_before(left_mask, k):
                    continue
                left_other = RANK - left_mask.bit_count() - 1
                if left_other < 0:
                    continue
                for right_mask in range(mask_count):
                    if left_mask & right_mask or not locks_after(right_mask, k):
                        continue
                    right_other = RANK - right_mask.bit_count() - 1
                    if right_other < 0:
                        continue
                    denominator = (
                        free
                        * C(free - 1, left_other)
                        * C(free - 1 - left_other, right_other)
                    )
                    if not denominator:
                        continue
                    coefficient = Fraction(
                        C(before, left_other) * C(after, right_other), denominator
                    )
                    add(paired, (left_mask, right_mask), coefficient)
                    if left_mask == right_mask:
                        add(paired, (left_mask,), -coefficient)
        else:
            locked_vertex = locked_at[k]
            bit = 1 << locked_vertex
            for mask in range(mask_count):
                if not mask & bit:
                    continue
                other_locks = mask ^ bit
                random_in_edge = RANK - mask.bit_count()
                if locks_before(other_locks, k):
                    add(
                        last,
                        (mask,),
                        Fraction(C(before, random_in_edge), C(free, random_in_edge)),
                    )
                if locks_after(other_locks, k):
                    add(
                        first,
                        (mask,),
                        Fraction(C(after, random_in_edge), C(free, random_in_edge)),
                    )

            for left_mask in range(mask_count):
                if not left_mask & bit or not locks_before(left_mask ^ bit, k):
                    continue
                left_random = RANK - left_mask.bit_count()
                for right_mask in range(mask_count):
                    if (
                        not right_mask & bit
                        or left_mask & right_mask != bit
                        or not locks_after(right_mask ^ bit, k)
                    ):
                        continue
                    right_random = RANK - right_mask.bit_count()
                    denominator = C(free, left_random) * C(
                        free - left_random, right_random
                    )
                    if not denominator:
                        continue
                    coefficient = Fraction(
                        C(before, left_random) * C(after, right_random), denominator
                    )
                    add(paired, (left_mask, right_mask), coefficient)
                    if left_mask == right_mask:
                        add(paired, (left_mask,), -coefficient)

        compiled.append(
            PositionEvents(
                IntPolynomial.compile(last),
                IntPolynomial.compile(first),
                IntPolynomial.compile(paired),
            )
        )
    return LockedKernel(v, edge_count, positions, tuple(compiled))


def compile_kernels(
    v: int, edge_count: int, assignments: Iterable[Sequence[int]]
) -> tuple[LockedKernel, ...]:
    return tuple(compile_kernel(v, edge_count, p) for p in assignments)


def best_compiled(
    counts: Sequence[int], kernels: Iterable[LockedKernel]
) -> tuple[Fraction, tuple[int, ...]]:
    return min((kernel.evaluate(counts), kernel.positions) for kernel in kernels)


def self_test() -> None:
    """Cross-check compiled and direct evaluation on varied lock counts."""
    fixtures = (
        (20, 32, (27, 5), (10,)),
        (21, 32, (14, 5, 5, 1, 5, 1, 1, 0), (1, 2, 3)),
        (
            23,
            32,
            (10, 4, 4, 1, 4, 1, 1, 0, 4, 1, 1, 0, 1, 0, 0, 0),
            (10, 11, 12, 13),
        ),
    )
    for v, edge_count, counts, positions in fixtures:
        direct = locked_bound(v, edge_count, counts, positions)
        compiled = compile_kernel(v, edge_count, positions).evaluate(counts)
        if compiled != direct:
            raise RuntimeError(
                f"compiled/direct mismatch: {(v, positions, compiled, direct)!r}"
            )


if __name__ == "__main__":
    self_test()
    print("compiled exact evaluator self-test passed")
