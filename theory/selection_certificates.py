#!/usr/bin/env python3
"""Exact finite certificates used to exclude v=23,24,25 for m=32.

This script is deliberately small and solver-free.  It enumerates clique
partitions of K4 and K5, constructs the corresponding locked edge-type
profiles, and evaluates the rational greedy-failure bound from
``locked_greedy_32.py``.  It also checks the three-lock residual profiles
that drive the v=23 degree/codegree split.
"""

from __future__ import annotations

if not __debug__:
    raise RuntimeError(
        "selection_certificates.py is a proof checker and must be run without "
        "Python -O/-OO, which would remove validation assertions"
    )

import argparse
import json
from fractions import Fraction
from hashlib import sha256
from itertools import combinations, permutations

from locked_greedy_32 import category_profiles, locked_bound


# These constants pin the complete enumerated sets and the rows containing
# each chosen placement and exact rational certificate.  Changing any input,
# enumeration order after sorting, or arithmetic result trips an assertion.
EXPECTED_FINGERPRINTS = {
    "pbd_k4": (6, "35d71c1bd523dd2dd334603c79c6fcba62973f36ea518d22ed52940e5c76f312"),
    "pbd_k5": (32, "e3a72027cd5955883eb6c56ff848a95a974e3e9d2c517ec5e3fd9d49505ca12b"),
    "profiles_666": (192, "7cf883eaa09767ef80cf11a726df495b3b44efca99308bb98ea80fd2dfaf15ae"),
    "profiles_667": (220, "4cb7b1bf3d375c04ad35ed98b482f66308781d19485211ce8744940d5338cc9e"),
    "profiles_677": (263, "6272e1e5873fa83ecce0a7de46da04a01f62fd94e0a6a632df309cd367e37121"),
    "residual_666": (0, "4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945"),
    "residual_667": (2, "7ec468f5c51527ee1cadb66dda086e52abc2b4eb26aec72ed2b2841e7cdb9c69"),
    "residual_677": (17, "b3eb95aa6bd1adddd17a5abf7624e24d3213e3c97e43a4ebc84e5e4ca55a748e"),
    "rows_v23_6677": (3, "93a8ebe99ee26910fa6524a99c73148d3c1c9d83bbf86dbfcfd65d74465ab9df"),
    "assignments_v23_6677": (48, "67e374002fa507030105f5ae5e632b5c42a09856e0d895c9a8794d172e0dc713"),
    "rows_v23_67777": (32, "0e1063136d9611768c47870b4e862b102235abe14b921f0251e41dd0b7d4899e"),
    "assignments_v23_67777": (11, "7efdf3fe24c67ab5d45bbb53593fd68061bd2850dabbd512a016907b5a0dc186"),
    "rows_v24": (6, "1cad328201da36b7ee2e88da5df72371c63d1710f6a7c7532896ce7b79f43685"),
    "rows_v25": (7, "18055e130748c9676e3231ca9ea2349152affe1bce6d8038033e9d2ccaa04aba"),
}


def digest(rows) -> str:
    """SHA-256 of a canonical JSON encoding of an enumerated finite set."""
    payload = json.dumps(
        sorted(rows), separators=(",", ":"), ensure_ascii=True
    ).encode("ascii")
    return sha256(payload).hexdigest()


def clique_partitions(order: int) -> tuple[tuple[int, ...], ...]:
    """All labelled partitions of E(K_order) into edge sets of cliques."""
    pairs = list(combinations(range(order), 2))
    pair_index = {pair: i for i, pair in enumerate(pairs)}
    all_pairs = (1 << len(pairs)) - 1
    cliques = []
    for size in range(2, order + 1):
        for vertices in combinations(range(order), size):
            vertex_mask = sum(1 << vertex for vertex in vertices)
            pair_mask = sum(
                1 << pair_index[pair] for pair in combinations(vertices, 2)
            )
            cliques.append((vertex_mask, pair_mask))

    containing = {i: [] for i in range(len(pairs))}
    for index, (_, pair_mask) in enumerate(cliques):
        for i in range(len(pairs)):
            if pair_mask >> i & 1:
                containing[i].append(index)

    answers = set()

    def visit(covered: int, chosen: list[int]) -> None:
        if covered == all_pairs:
            answers.add(tuple(sorted(chosen)))
            return
        first = next(i for i in range(len(pairs)) if not covered >> i & 1)
        for index in containing[first]:
            vertex_mask, pair_mask = cliques[index]
            if not pair_mask & covered:
                visit(covered | pair_mask, chosen + [vertex_mask])

    visit(0, [])
    return tuple(sorted(answers))


def edge_profile(partition: tuple[int, ...], degrees: tuple[int, ...]) -> tuple[int, ...]:
    """Complete a clique partition with singleton and empty edge types."""
    counts = [0] * (1 << len(degrees))
    for trace in partition:
        counts[trace] += 1
    for vertex, degree in enumerate(degrees):
        used = sum(
            number
            for trace, number in enumerate(counts)
            if trace >> vertex & 1
        )
        counts[1 << vertex] = degree - used
    counts[0] = 32 - sum(counts)
    assert min(counts) >= 0
    return tuple(counts)


def best_over_assignments(
    v: int, counts: tuple[int, ...], position_set: tuple[int, ...]
) -> Fraction:
    return min(
        locked_bound(v, counts, assignment)
        for assignment in permutations(position_set)
    )


def best_certificate(
    v: int,
    counts: tuple[int, ...],
    assignments: tuple[tuple[int, ...], ...],
) -> tuple[Fraction, tuple[int, ...]]:
    """Return an exact optimum and a deterministic lexicographic witness."""
    candidates = tuple((locked_bound(v, counts, p), p) for p in assignments)
    return min(candidates)


def three_lock_v23():
    """Return and verify residual profiles for the three possible low triples."""
    profile_sets = []
    residual_sets = []
    expected = {
        (6, 6, 6): 0,
        (6, 6, 7): 2,
        (6, 7, 7): 17,
    }
    for degrees in expected:
        profiles = tuple(category_profiles(degrees))
        profile_sets.append(tuple(sorted(profiles)))
        residual = []
        for counts in profiles:
            value = best_over_assignments(23, counts, (11, 12, 13))
            if value >= 1:
                residual.append(counts)
        residual = tuple(sorted(residual))
        assert len(residual) == expected[degrees]
        residual_sets.append(residual)

    # In both (6,6,7) residuals, all three selected pair-codegrees are one.
    for counts in residual_sets[1]:
        assert (
            counts[3] + counts[7],
            counts[5] + counts[7],
            counts[6] + counts[7],
        ) == (1, 1, 1)

    # In every (6,7,7) residual, all selected pair-codegrees are at most two.
    for counts in residual_sets[2]:
        assert max(
            counts[3] + counts[7],
            counts[5] + counts[7],
            counts[6] + counts[7],
        ) <= 2
    return tuple(profile_sets), tuple(residual_sets)


def v23_higher_lock_certificates(partitions4, partitions5):
    # Degree sequence (6^2,7^20,8): choose u,v,y,z with all codegrees one,
    # where the unique trace containing {u,v} has size exactly two.
    allowed4 = []
    for partition in partitions4:
        trace_on_low_pair = next(trace for trace in partition if trace & 3 == 3)
        if trace_on_low_pair == 3:
            allowed4.append(partition)
    position_bases4 = ((10, 11, 12, 13), (12, 13, 14, 15))
    assignments4 = tuple(
        dict.fromkeys(
            assignment
            for base in position_bases4
            for assignment in permutations(base)
        )
    )
    rows4 = []
    for partition in allowed4:
        value, assignment = best_certificate(
            23, edge_profile(partition, (6, 6, 7, 7)), assignments4
        )
        rows4.append((partition, assignment, value.numerator, value.denominator))
    assert len(allowed4) == 3
    assert max(Fraction(row[2], row[3]) for row in rows4) == Fraction(8315, 8398) < 1

    # Degree sequence (6,7^22): the eleven assignments below are an explicit
    # certificate covering all 32 labelled K5 clique partitions.
    assignments = (
        (13, 16, 17, 18, 14),
        (11, 4, 3, 2, 1),
        (16, 15, 17, 18, 14),
        (10, 4, 3, 1, 2),
        (15, 16, 17, 18, 14),
        (10, 4, 3, 2, 1),
        (12, 15, 16, 17, 14),
        (17, 15, 16, 18, 14),
        (12, 16, 17, 18, 14),
        (10, 15, 16, 17, 14),
        (12, 4, 3, 2, 1),
    )
    rows5 = []
    for partition in partitions5:
        counts = edge_profile(partition, (6, 7, 7, 7, 7))
        value, assignment = best_certificate(23, counts, assignments)
        rows5.append((partition, assignment, value.numerator, value.denominator))
    assert len(rows5) == 32
    assert max(Fraction(row[2], row[3]) for row in rows5) == Fraction(45784, 51051) < 1
    return tuple(sorted(rows4)), tuple(sorted(rows5)), assignments4, assignments


def v24_certificate(partitions4):
    assignments = tuple(permutations((11, 12, 13, 14)))
    rows = []
    for partition in partitions4:
        value, assignment = best_certificate(
            24, edge_profile(partition, (6, 6, 6, 6)), assignments
        )
        rows.append((partition, assignment, value.numerator, value.denominator))
    assert len(rows) == 6
    assert max(Fraction(row[2], row[3]) for row in rows) == Fraction(16671, 16796) < 1
    return tuple(sorted(rows))


def v25_favourable_trace_certificate(partitions5):
    favourable = []
    for partition in partitions5:
        sizes = tuple(sorted(trace.bit_count() for trace in partition))
        if sizes in {
            (2, 2, 2, 2, 2, 2, 2, 2, 2, 2),
            (2, 2, 2, 2, 4),
            (5,),
        }:
            favourable.append(partition)
    assignments = tuple(permutations((11, 12, 13, 14, 15)))
    rows = []
    for partition in favourable:
        value, assignment = best_certificate(
            25, edge_profile(partition, (6, 6, 6, 6, 6)), assignments
        )
        rows.append((partition, assignment, value.numerator, value.denominator))
    assert len(favourable) == 7  # one all-pair, five K4, one K5 profile
    assert max(Fraction(row[2], row[3]) for row in rows) == Fraction(4188, 4199) < 1
    return tuple(sorted(rows))


def rational_text(value: Fraction) -> str:
    return f"{value.numerator}/{value.denominator}"


def make_manifest() -> dict[str, object]:
    """Recompute every finite set and return its deterministic manifest."""
    partitions4 = clique_partitions(4)
    partitions5 = clique_partitions(5)
    assert len(partitions4) == 6
    assert len(partitions5) == 32

    profile_sets, residual_sets = three_lock_v23()
    rows23b, rows23a, assignments23b, assignments23a = v23_higher_lock_certificates(
        partitions4, partitions5
    )
    rows24 = v24_certificate(partitions4)
    rows25 = v25_favourable_trace_certificate(partitions5)

    triples = ((6, 6, 6), (6, 6, 7), (6, 7, 7))
    three_lock = {}
    for degrees, profiles, residual in zip(triples, profile_sets, residual_sets):
        three_lock[str(degrees)] = {
            "all_profile_count": len(profiles),
            "all_profiles_sha256": digest(profiles),
            "residual_count": len(residual),
            "residual_profiles_sha256": digest(residual),
        }

    def row_manifest(rows):
        values = tuple(Fraction(row[2], row[3]) for row in rows)
        return {
            "row_count": len(rows),
            "rows_sha256": digest(rows),
            "maximum_bound": rational_text(max(values)),
        }

    manifest = {
        "schema": "property-b-m5-locked-certificate-v1",
        "arithmetic": "Python fractions.Fraction; binomial coefficients are exact integers",
        "canonical_hash_encoding": "ASCII JSON, sorted rows, separators=(',', ':')",
        "pbd": {
            "K4": {"count": len(partitions4), "sha256": digest(partitions4)},
            "K5": {"count": len(partitions5), "sha256": digest(partitions5)},
        },
        "v23_three_lock": three_lock,
        "v23_degree_6_6_7_7_four_lock": {
            **row_manifest(rows23b),
            "position_bases": [[10, 11, 12, 13], [12, 13, 14, 15]],
            "allowed_assignment_count": len(assignments23b),
            "allowed_assignments_sha256": digest(assignments23b),
        },
        "v23_degree_6_7_7_7_7_five_lock": {
            **row_manifest(rows23a),
            "allowed_assignment_count": len(assignments23a),
            "allowed_assignments_sha256": digest(assignments23a),
        },
        "v24_degree_6_6_6_6_four_lock": row_manifest(rows24),
        "v25_favourable_five_lock": row_manifest(rows25),
    }

    actual_fingerprints = {
        "pbd_k4": (len(partitions4), digest(partitions4)),
        "pbd_k5": (len(partitions5), digest(partitions5)),
        "profiles_666": (len(profile_sets[0]), digest(profile_sets[0])),
        "profiles_667": (len(profile_sets[1]), digest(profile_sets[1])),
        "profiles_677": (len(profile_sets[2]), digest(profile_sets[2])),
        "residual_666": (len(residual_sets[0]), digest(residual_sets[0])),
        "residual_667": (len(residual_sets[1]), digest(residual_sets[1])),
        "residual_677": (len(residual_sets[2]), digest(residual_sets[2])),
        "rows_v23_6677": (len(rows23b), digest(rows23b)),
        "assignments_v23_6677": (len(assignments23b), digest(assignments23b)),
        "rows_v23_67777": (len(rows23a), digest(rows23a)),
        "assignments_v23_67777": (len(assignments23a), digest(assignments23a)),
        "rows_v24": (len(rows24), digest(rows24)),
        "rows_v25": (len(rows25), digest(rows25)),
    }
    assert actual_fingerprints == EXPECTED_FINGERPRINTS
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--compact", action="store_true", help="emit canonical one-line JSON"
    )
    args = parser.parse_args()
    manifest = make_manifest()
    print(
        json.dumps(
            manifest,
            sort_keys=True,
            indent=None if args.compact else 2,
            separators=(",", ":") if args.compact else None,
        )
    )


if __name__ == "__main__":
    main()
