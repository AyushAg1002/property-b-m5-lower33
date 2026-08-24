#!/usr/bin/env python3
"""Independent adversarial checker for the m(5)>=33 finite certificates.

Independence choices:

* clique partitions are generated as set partitions of E(K_s), then filtered
  by a clique predicate (the source generator instead recursively covers the
  first uncovered pair with a precomputed clique);
* the locked-position probabilities are re-derived using direct counts of
  placements of the random vertices, rather than importing ``locked_bound``;
* three-lock profiles are enumerated from the four multi-lock category counts
  and linear degree equations, without importing ``category_profiles``.

All arithmetic is ``fractions.Fraction`` and every asserted maximum is exact.
"""

from __future__ import annotations

if not __debug__:
    raise RuntimeError(
        "verify_lower33.py is a proof checker and must be run without "
        "Python -O/-OO, which would remove validation assertions"
    )

import argparse
import itertools
import json
import sys
import time
from fractions import Fraction
from functools import lru_cache
from hashlib import sha256
from math import comb
from pathlib import Path


UNIFORMITY = 5
EDGE_COUNT = 32


def C(n: int, k: int) -> int:
    return comb(n, k) if n >= 0 and 0 <= k <= n else 0


def digest(rows) -> str:
    payload = "\n".join(
        ",".join(map(str, row)) if isinstance(row, tuple) else str(row)
        for row in sorted(rows)
    ).encode()
    return sha256(payload).hexdigest()


def canonical_json_digest(rows) -> str:
    """Match the source artifact's documented JSON hash encoding.

    This is intentionally implemented here rather than imported from the
    certificate generator so equality tests cover both serialization and the
    independently generated finite objects.
    """
    payload = json.dumps(
        sorted(rows), separators=(",", ":"), ensure_ascii=True
    ).encode("ascii")
    return sha256(payload).hexdigest()


def is_clique_block(edge_ids: tuple[int, ...], pairs: list[tuple[int, int]]) -> bool:
    vertices = set()
    actual = set()
    for edge_id in edge_ids:
        pair = pairs[edge_id]
        actual.add(pair)
        vertices.update(pair)
    return actual == set(itertools.combinations(sorted(vertices), 2))


def independent_clique_partitions(order: int) -> tuple[tuple[int, ...], ...]:
    """Partition E(K_order) arbitrarily, retaining only clique blocks."""
    pairs = list(itertools.combinations(range(order), 2))
    answers: set[tuple[int, ...]] = set()

    def visit(next_edge: int, blocks: list[list[int]]) -> None:
        if next_edge == len(pairs):
            frozen = [tuple(block) for block in blocks]
            if all(is_clique_block(block, pairs) for block in frozen):
                traces = []
                for block in frozen:
                    vertices = set()
                    for edge_id in block:
                        vertices.update(pairs[edge_id])
                    traces.append(sum(1 << vertex for vertex in vertices))
                answers.add(tuple(sorted(traces)))
            return
        for block in blocks:
            block.append(next_edge)
            visit(next_edge + 1, blocks)
            block.pop()
        blocks.append([next_edge])
        visit(next_edge + 1, blocks)
        blocks.pop()

    visit(0, [])
    return tuple(sorted(answers))


@lru_cache(maxsize=None)
def independent_locked_bound(
    v: int, counts: tuple[int, ...], positions: tuple[int, ...]
) -> Fraction:
    """Exact union/min bound from direct random-position counts."""
    selected = len(positions)
    if len(counts) != 1 << selected or sum(counts) != EDGE_COUNT:
        raise ValueError("invalid trace profile")
    if len(set(positions)) != selected:
        raise ValueError("locked positions must be distinct")
    locked_at = {position: vertex for vertex, position in enumerate(positions)}
    random_vertices = v - selected
    total = Fraction(0)

    def all_locked_before(trace: int, position: int, omit: int = 0) -> bool:
        trace &= ~omit
        return all(
            positions[vertex] < position
            for vertex in range(selected)
            if trace & (1 << vertex)
        )

    def all_locked_after(trace: int, position: int, omit: int = 0) -> bool:
        trace &= ~omit
        return all(
            positions[vertex] > position
            for vertex in range(selected)
            if trace & (1 << vertex)
        )

    for position in range(1, v + 1):
        before = sum(p not in locked_at for p in range(1, position))
        after = sum(p not in locked_at for p in range(position + 1, v + 1))
        last = Fraction(0)
        first = Fraction(0)
        both = Fraction(0)

        if position not in locked_at:
            for trace, number in enumerate(counts):
                q = UNIFORMITY - trace.bit_count()
                denominator = C(random_vertices, q)
                if q >= 1 and denominator and all_locked_before(trace, position):
                    last += number * Fraction(C(before, q - 1), denominator)
                if q >= 1 and denominator and all_locked_after(trace, position):
                    first += number * Fraction(C(after, q - 1), denominator)

            for left_trace, left_number in enumerate(counts):
                if not left_number or not all_locked_before(left_trace, position):
                    continue
                left_other = UNIFORMITY - left_trace.bit_count() - 1
                if left_other < 0:
                    continue
                for right_trace, right_number in enumerate(counts):
                    if (
                        not right_number
                        or left_trace & right_trace
                        or not all_locked_after(right_trace, position)
                    ):
                        continue
                    right_other = UNIFORMITY - right_trace.bit_count() - 1
                    if right_other < 0:
                        continue
                    ordered_pairs = left_number * (
                        right_number - int(left_trace == right_trace)
                    )
                    denominator = (
                        random_vertices
                        * C(random_vertices - 1, left_other)
                        * C(random_vertices - 1 - left_other, right_other)
                    )
                    if ordered_pairs and denominator:
                        both += ordered_pairs * Fraction(
                            C(before, left_other) * C(after, right_other), denominator
                        )
        else:
            vertex = locked_at[position]
            bit = 1 << vertex
            for trace, number in enumerate(counts):
                if not trace & bit:
                    continue
                q = UNIFORMITY - trace.bit_count()
                denominator = C(random_vertices, q)
                if denominator and all_locked_before(trace, position, bit):
                    last += number * Fraction(C(before, q), denominator)
                if denominator and all_locked_after(trace, position, bit):
                    first += number * Fraction(C(after, q), denominator)

            for left_trace, left_number in enumerate(counts):
                if (
                    not left_number
                    or not left_trace & bit
                    or not all_locked_before(left_trace, position, bit)
                ):
                    continue
                left_random = UNIFORMITY - left_trace.bit_count()
                for right_trace, right_number in enumerate(counts):
                    if (
                        not right_number
                        or not right_trace & bit
                        or left_trace & right_trace != bit
                        or not all_locked_after(right_trace, position, bit)
                    ):
                        continue
                    right_random = UNIFORMITY - right_trace.bit_count()
                    ordered_pairs = left_number * (
                        right_number - int(left_trace == right_trace)
                    )
                    denominator = C(random_vertices, left_random) * C(
                        random_vertices - left_random, right_random
                    )
                    if ordered_pairs and denominator:
                        both += ordered_pairs * Fraction(
                            C(before, left_random) * C(after, right_random), denominator
                        )

        total += min(last, first, both)
    return total


def independent_three_profiles(degrees: tuple[int, int, int]):
    """Enumerate trace counts from multi-lock counts and degree equations."""
    d0, d1, d2 = degrees
    for all_three in range(min(degrees) + 1):
        for pair01 in range(min(d0, d1) - all_three + 1):
            for pair02 in range(min(d0, d2) - all_three + 1):
                for pair12 in range(min(d1, d2) - all_three + 1):
                    if min(pair01 + all_three, pair02 + all_three, pair12 + all_three) < 1:
                        continue
                    single0 = d0 - pair01 - pair02 - all_three
                    single1 = d1 - pair01 - pair12 - all_three
                    single2 = d2 - pair02 - pair12 - all_three
                    if min(single0, single1, single2) < 0:
                        continue
                    nonempty = (
                        single0
                        + single1
                        + single2
                        + pair01
                        + pair02
                        + pair12
                        + all_three
                    )
                    empty = EDGE_COUNT - nonempty
                    if empty >= 0:
                        yield (
                            empty,
                            single0,
                            single1,
                            pair01,
                            single2,
                            pair02,
                            pair12,
                            all_three,
                        )


def independent_edge_profile(
    partition: tuple[int, ...], degrees: tuple[int, ...]
) -> tuple[int, ...]:
    counts = [0] * (1 << len(degrees))
    for trace in partition:
        counts[trace] += 1
    for vertex, degree in enumerate(degrees):
        used = sum(n for trace, n in enumerate(counts) if trace & (1 << vertex))
        if counts[1 << vertex]:
            raise AssertionError("clique partition unexpectedly contains a singleton")
        counts[1 << vertex] = degree - used
    counts[0] = EDGE_COUNT - sum(counts)
    if min(counts) < 0:
        raise AssertionError("negative trace count")
    return tuple(counts)


def best(v: int, counts: tuple[int, ...], positions: tuple[int, ...]) -> Fraction:
    return min(
        independent_locked_bound(v, counts, assignment)
        for assignment in itertools.permutations(positions)
    )


def best_certificate(
    v: int,
    counts: tuple[int, ...],
    assignments: tuple[tuple[int, ...], ...],
) -> tuple[Fraction, tuple[int, ...]]:
    """Return the exact minimum and lexicographically first minimizer."""
    return min(
        (independent_locked_bound(v, counts, assignment), assignment)
        for assignment in assignments
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--report",
        type=Path,
        default=Path(__file__).resolve().parent
        / "logs"
        / "lower33_independent_verification.json",
        help="write the deterministic JSON report here",
    )
    args = parser.parse_args()
    started = time.monotonic()
    source_manifest_path = (
        Path(__file__).resolve().parent.parent / "theory" / "SELECTION_MANIFEST.json"
    )
    source_manifest = json.loads(source_manifest_path.read_text(encoding="utf-8"))
    p4 = independent_clique_partitions(4)
    p5 = independent_clique_partitions(5)
    expected_p4_hash = "c9162cf0f0291c4586b3737979262be64d296df4018a8a711c697cb340294f24"
    expected_p5_hash = "67959c2e215517af54d33e1459fbd477e9bfc70755332a4f08b5362dc0e8a817"
    assert len(p4) == 6 and digest(p4) == expected_p4_hash
    assert len(p5) == 32 and digest(p5) == expected_p5_hash

    profile_sets = []
    residual_sets = []
    expected_residual = {
        (6, 6, 6): (0, "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"),
        (6, 6, 7): (2, "5be5c92be6730f3be9df111a518afe159cfc52eb6036765a3b59a98574493163"),
        (6, 7, 7): (17, "3d2bf36f9899db74567037847bfb92b3d65a0b7402f48b3237fdd59d4c283421"),
    }
    for degrees, (expected_count, expected_hash) in expected_residual.items():
        profiles = tuple(sorted(independent_three_profiles(degrees)))
        profile_sets.append(profiles)
        residual = tuple(
            sorted(
                counts
                for counts in profiles
                if best(23, counts, (11, 12, 13)) >= 1
            )
        )
        assert len(residual) == expected_count
        assert digest(residual) == expected_hash
        residual_sets.append(residual)

    allowed4 = []
    for partition in p4:
        low_pair_traces = [trace for trace in partition if trace & 3 == 3]
        assert len(low_pair_traces) == 1
        if low_pair_traces[0] == 3:
            allowed4.append(partition)
    assignments4 = tuple(
        dict.fromkeys(
            assignment
            for base in ((10, 11, 12, 13), (12, 13, 14, 15))
            for assignment in itertools.permutations(base)
        )
    )
    rows_case_b = []
    for partition in allowed4:
        value, assignment = best_certificate(
            23,
            independent_edge_profile(partition, (6, 6, 7, 7)),
            assignments4,
        )
        rows_case_b.append((partition, assignment, value.numerator, value.denominator))
    rows_case_b = tuple(sorted(rows_case_b))
    values_case_b = [Fraction(row[2], row[3]) for row in rows_case_b]
    assert len(allowed4) == 3
    assert max(values_case_b) == Fraction(8315, 8398) < 1

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
    values_case_a = []
    rows_case_a = []
    assignment_wins = [0] * len(assignments)
    for partition in p5:
        counts = independent_edge_profile(partition, (6, 7, 7, 7, 7))
        values = [independent_locked_bound(23, counts, p) for p in assignments]
        winning_value, winning_assignment = min(zip(values, assignments))
        winner = assignments.index(winning_assignment)
        assignment_wins[winner] += 1
        values_case_a.append(winning_value)
        rows_case_a.append(
            (
                partition,
                winning_assignment,
                winning_value.numerator,
                winning_value.denominator,
            )
        )
    rows_case_a = tuple(sorted(rows_case_a))
    assert len(values_case_a) == 32
    assert sum(assignment_wins) == 32 and all(value < 1 for value in values_case_a)
    assert max(values_case_a) == Fraction(45784, 51051) < 1

    assignments24 = tuple(itertools.permutations((11, 12, 13, 14)))
    rows24 = []
    for partition in p4:
        value, assignment = best_certificate(
            24,
            independent_edge_profile(partition, (6, 6, 6, 6)),
            assignments24,
        )
        rows24.append((partition, assignment, value.numerator, value.denominator))
    rows24 = tuple(sorted(rows24))
    values24 = [Fraction(row[2], row[3]) for row in rows24]
    assert max(values24) == Fraction(16671, 16796) < 1

    favourable = []
    for partition in p5:
        sizes = tuple(sorted(trace.bit_count() for trace in partition))
        if sizes in {
            (2, 2, 2, 2, 2, 2, 2, 2, 2, 2),
            (2, 2, 2, 2, 4),
            (5,),
        }:
            favourable.append(partition)
    assignments25 = tuple(itertools.permutations((11, 12, 13, 14, 15)))
    rows25 = []
    for partition in favourable:
        value, assignment = best_certificate(
            25,
            independent_edge_profile(partition, (6, 6, 6, 6, 6)),
            assignments25,
        )
        rows25.append((partition, assignment, value.numerator, value.denominator))
    rows25 = tuple(sorted(rows25))
    values25 = [Fraction(row[2], row[3]) for row in rows25]
    assert len(favourable) == 7
    assert max(values25) == Fraction(4188, 4199) < 1

    # Compare every independently generated finite set and certificate row to
    # the canonical source manifest.  These hashes include chosen placements
    # and exact numerators/denominators, not merely the reported maxima.
    canonical = {
        "pbd_k4": (len(p4), canonical_json_digest(p4)),
        "pbd_k5": (len(p5), canonical_json_digest(p5)),
        "profiles_666": (len(profile_sets[0]), canonical_json_digest(profile_sets[0])),
        "profiles_667": (len(profile_sets[1]), canonical_json_digest(profile_sets[1])),
        "profiles_677": (len(profile_sets[2]), canonical_json_digest(profile_sets[2])),
        "residual_666": (len(residual_sets[0]), canonical_json_digest(residual_sets[0])),
        "residual_667": (len(residual_sets[1]), canonical_json_digest(residual_sets[1])),
        "residual_677": (len(residual_sets[2]), canonical_json_digest(residual_sets[2])),
        "rows_v23_6677": (len(rows_case_b), canonical_json_digest(rows_case_b)),
        "assignments_v23_6677": (
            len(assignments4),
            canonical_json_digest(assignments4),
        ),
        "rows_v23_67777": (len(rows_case_a), canonical_json_digest(rows_case_a)),
        "assignments_v23_67777": (len(assignments), canonical_json_digest(assignments)),
        "rows_v24": (len(rows24), canonical_json_digest(rows24)),
        "rows_v25": (len(rows25), canonical_json_digest(rows25)),
    }
    canonical_expected = {
        "pbd_k4": (
            source_manifest["pbd"]["K4"]["count"],
            source_manifest["pbd"]["K4"]["sha256"],
        ),
        "pbd_k5": (
            source_manifest["pbd"]["K5"]["count"],
            source_manifest["pbd"]["K5"]["sha256"],
        ),
        "profiles_666": (
            source_manifest["v23_three_lock"]["(6, 6, 6)"]["all_profile_count"],
            source_manifest["v23_three_lock"]["(6, 6, 6)"]["all_profiles_sha256"],
        ),
        "profiles_667": (
            source_manifest["v23_three_lock"]["(6, 6, 7)"]["all_profile_count"],
            source_manifest["v23_three_lock"]["(6, 6, 7)"]["all_profiles_sha256"],
        ),
        "profiles_677": (
            source_manifest["v23_three_lock"]["(6, 7, 7)"]["all_profile_count"],
            source_manifest["v23_three_lock"]["(6, 7, 7)"]["all_profiles_sha256"],
        ),
        "residual_666": (
            source_manifest["v23_three_lock"]["(6, 6, 6)"]["residual_count"],
            source_manifest["v23_three_lock"]["(6, 6, 6)"]["residual_profiles_sha256"],
        ),
        "residual_667": (
            source_manifest["v23_three_lock"]["(6, 6, 7)"]["residual_count"],
            source_manifest["v23_three_lock"]["(6, 6, 7)"]["residual_profiles_sha256"],
        ),
        "residual_677": (
            source_manifest["v23_three_lock"]["(6, 7, 7)"]["residual_count"],
            source_manifest["v23_three_lock"]["(6, 7, 7)"]["residual_profiles_sha256"],
        ),
        "rows_v23_6677": (
            source_manifest["v23_degree_6_6_7_7_four_lock"]["row_count"],
            source_manifest["v23_degree_6_6_7_7_four_lock"]["rows_sha256"],
        ),
        "assignments_v23_6677": (
            source_manifest["v23_degree_6_6_7_7_four_lock"]["allowed_assignment_count"],
            source_manifest["v23_degree_6_6_7_7_four_lock"]["allowed_assignments_sha256"],
        ),
        "rows_v23_67777": (
            source_manifest["v23_degree_6_7_7_7_7_five_lock"]["row_count"],
            source_manifest["v23_degree_6_7_7_7_7_five_lock"]["rows_sha256"],
        ),
        "assignments_v23_67777": (
            source_manifest["v23_degree_6_7_7_7_7_five_lock"]["allowed_assignment_count"],
            source_manifest["v23_degree_6_7_7_7_7_five_lock"]["allowed_assignments_sha256"],
        ),
        "rows_v24": (
            source_manifest["v24_degree_6_6_6_6_four_lock"]["row_count"],
            source_manifest["v24_degree_6_6_6_6_four_lock"]["rows_sha256"],
        ),
        "rows_v25": (
            source_manifest["v25_favourable_five_lock"]["row_count"],
            source_manifest["v25_favourable_five_lock"]["rows_sha256"],
        ),
    }
    assert canonical == canonical_expected

    report = {
        "status": "ALL_INDEPENDENT_EXACT_CHECKS_PASSED",
        "arithmetic": "fractions.Fraction only",
        "k4_partition_count": len(p4),
        "k4_sha256": digest(p4),
        "k5_partition_count": len(p5),
        "k5_sha256": digest(p5),
        "v23_residual_counts": [len(rows) for rows in residual_sets],
        "v23_residual_hashes": [digest(rows) for rows in residual_sets],
        "v23_case_b_max": str(max(values_case_b)),
        "v23_case_a_max": str(max(values_case_a)),
        "v23_case_a_assignment_wins": assignment_wins,
        "v24_max": str(max(values24)),
        "v25_favourable_count": len(favourable),
        "v25_favourable_max": str(max(values25)),
        # This string is intentionally repository-relative.  An absolute path
        # made earlier checksummed reports differ after cloning or relocating
        # the artifact even though every mathematical result was identical.
        "canonical_manifest": "theory/SELECTION_MANIFEST.json",
        "canonical_all_row_hashes_match": canonical == canonical_expected,
        "canonical_fingerprints": {
            key: {"count": count, "sha256": fingerprint}
            for key, (count, fingerprint) in canonical.items()
        },
        "bound_cache": independent_locked_bound.cache_info()._asdict(),
    }
    output = args.report
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    # Wall-clock time is intentionally printed but not persisted: the report
    # is part of a checksum manifest and must be stable across clean replays.
    print(
        json.dumps(
            {
                "output": str(output),
                "elapsed_seconds": time.monotonic() - started,
                **report,
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
