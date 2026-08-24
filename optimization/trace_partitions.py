#!/usr/bin/env python3
"""Independent clique-partition generator for pair-codegree-one lock sets."""

from __future__ import annotations

from itertools import combinations


def clique_partitions(order: int) -> tuple[tuple[int, ...], ...]:
    """All labelled partitions of E(K_order) into nontrivial cliques."""
    pairs = tuple(combinations(range(order), 2))
    pair_index = {pair: i for i, pair in enumerate(pairs)}
    target = (1 << len(pairs)) - 1
    cliques = []
    for size in range(2, order + 1):
        for vertices in combinations(range(order), size):
            vertex_mask = sum(1 << x for x in vertices)
            pair_mask = sum(
                1 << pair_index[pair] for pair in combinations(vertices, 2)
            )
            cliques.append((vertex_mask, pair_mask))
    by_first_pair = {i: [] for i in range(len(pairs))}
    for clique_index, (_, pair_mask) in enumerate(cliques):
        for pair_number in range(len(pairs)):
            if pair_mask >> pair_number & 1:
                by_first_pair[pair_number].append(clique_index)

    answers: set[tuple[int, ...]] = set()

    def visit(covered: int, selected: tuple[int, ...]) -> None:
        if covered == target:
            answers.add(tuple(sorted(selected)))
            return
        first = next(i for i in range(len(pairs)) if not covered >> i & 1)
        for clique_index in by_first_pair[first]:
            vertex_mask, pair_mask = cliques[clique_index]
            if not pair_mask & covered:
                visit(covered | pair_mask, selected + (vertex_mask,))

    visit(0, ())
    return tuple(sorted(answers))


def edge_profile(
    partition: tuple[int, ...],
    degrees: tuple[int, ...],
    edge_count: int,
) -> tuple[int, ...]:
    """Complete a clique partition by forced singleton and empty traces."""
    counts = [0] * (1 << len(degrees))
    for trace in partition:
        counts[trace] += 1
    for vertex, degree in enumerate(degrees):
        used = sum(
            number for mask, number in enumerate(counts) if mask >> vertex & 1
        )
        counts[1 << vertex] = degree - used
    counts[0] = edge_count - sum(counts)
    if min(counts) < 0:
        raise ValueError("partition and degrees force a negative trace count")
    return tuple(counts)


def trace_size_type(partition: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(sorted(mask.bit_count() for mask in partition))


def self_test() -> None:
    expected = {3: 2, 4: 6, 5: 32}
    for order, wanted in expected.items():
        got = len(clique_partitions(order))
        if got != wanted:
            raise RuntimeError(
                f"K_{order} clique-partition count changed: {got} != {wanted}"
            )


if __name__ == "__main__":
    self_test()
    print("trace-partition generator self-test passed")
