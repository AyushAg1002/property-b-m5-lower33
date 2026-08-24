#!/usr/bin/env python3
"""Exact certificates excluding 32-edge cores on 21 and 22 vertices.

This module is deliberately small and deterministic.  It imports the generic
locked-permutation evaluator from ``locked_greedy_32.py``, enumerates a safe
superset of the possible trace profiles of the three lowest-degree vertices,
and records one strict rational certificate for every closed profile.

For v=22 exactly three initial profiles survive the fixed position menu.  In
all three, the chosen vertices have degree seven and their pair-codegrees are
1,1,2.  This forces minimum degree seven.  At least 16 vertices then have
degree seven.  Ramsey's R(3,3)=6 theorem supplies three degree-seven vertices
whose repeated-pair graph is either independent (all pair-codegrees one) or a
triangle (all pair-codegrees at least two).  The second enumeration certifies
every profile in both Ramsey classes.
"""

from __future__ import annotations

if not __debug__:
    raise RuntimeError(
        "close_v21_v22.py is a proof checker and must be run without "
        "Python -O/-OO, which would remove validation assertions"
    )

import argparse
import hashlib
import json
from fractions import Fraction
from itertools import permutations
from pathlib import Path
from typing import Iterable, Sequence

from locked_greedy_32 import (
    category_profiles,
    locked_bound,
    three_smallest_degree_options,
)


V21_POSITION_BASES = (
    (10, 11, 12),
    (1, 2, 3),
    (11, 12, 13),
    (1, 2, 12),
)
V22_POSITION_BASES = (
    (10, 11, 12),
    (1, 2, 3),
    (1, 2, 11),
    (1, 2, 13),
    (1, 11, 13),
)


EXPECTED_RECORD_HASHES = {
    "v21": "c622bed337a8fb1682f765020a2504542c89c77383559909095d05b98e040ee2",
    "v22_ramsey": "80274adc462f71be34906175b470324bedd6480f2fad452278aad0a36720700c",
    "all": "feb165603b8eda25a3dfd55f842783810b015a5f1d4be510ce347a6dfac2ab7a",
}


def fraction_record(value: Fraction) -> dict[str, int]:
    return {"numerator": value.numerator, "denominator": value.denominator}


def position_assignments(bases: Sequence[Sequence[int]]) -> Iterable[tuple[int, ...]]:
    """Yield distinct label-to-position assignments in deterministic order."""
    seen: set[tuple[int, ...]] = set()
    for base in bases:
        for assignment in permutations(base):
            if assignment not in seen:
                seen.add(assignment)
                yield assignment


def best_certificate(
    v: int, counts: tuple[int, ...], bases: Sequence[Sequence[int]]
) -> tuple[Fraction, tuple[int, ...]]:
    return min((locked_bound(v, counts, p), p) for p in position_assignments(bases))


def profile_record(
    v: int,
    degrees: tuple[int, int, int],
    counts: tuple[int, ...],
    bound: Fraction,
    positions: tuple[int, ...],
    family: str,
) -> dict[str, object]:
    codegrees = (
        counts[3] + counts[7],
        counts[5] + counts[7],
        counts[6] + counts[7],
    )
    return {
        "family": family,
        "vertices": v,
        "degrees": list(degrees),
        "counts_by_mask_000_to_111": list(counts),
        "selected_codegrees": list(codegrees),
        "positions_by_selected_label": list(positions),
        "bound": fraction_record(bound),
        "strictly_below_one": bound < 1,
    }


def records_hash(records: Sequence[dict[str, object]]) -> str:
    digest = hashlib.sha256()
    for record in records:
        digest.update(
            json.dumps(record, sort_keys=True, separators=(",", ":")).encode("utf-8")
        )
        digest.update(b"\n")
    return digest.hexdigest()


def close_v21() -> tuple[list[dict[str, object]], dict[str, object]]:
    records: list[dict[str, object]] = []
    for degrees in three_smallest_degree_options(21):
        for counts in category_profiles(degrees):
            bound, positions = best_certificate(21, counts, V21_POSITION_BASES)
            assert bound < 1, (degrees, counts, bound, positions)
            records.append(
                profile_record(21, degrees, counts, bound, positions, "v21_all")
            )
    assert len(records) == 1864
    worst = max(records, key=lambda r: Fraction(**r["bound"]))
    worst_value = Fraction(**worst["bound"])
    assert worst_value == Fraction(9599, 9724)
    return records, {
        "profile_count": len(records),
        "certificate_sha256": records_hash(records),
        "worst_bound": fraction_record(worst_value),
        "worst_profile": worst,
        "position_bases": [list(x) for x in V21_POSITION_BASES],
    }


def initial_v22_records() -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    closed: list[dict[str, object]] = []
    residual: list[dict[str, object]] = []
    for degrees in three_smallest_degree_options(22):
        for counts in category_profiles(degrees):
            bound, positions = best_certificate(22, counts, V22_POSITION_BASES)
            record = profile_record(
                22, degrees, counts, bound, positions, "v22_initial_three_lowest"
            )
            (closed if bound < 1 else residual).append(record)
    assert len(closed) + len(residual) == 1000
    assert len(closed) == 997
    assert len(residual) == 3
    for record in residual:
        assert record["degrees"] == [7, 7, 7]
        assert sorted(record["selected_codegrees"]) == [1, 1, 2]
        assert record["counts_by_mask_000_to_111"][7] == 0
    return closed, residual


def ramsey_v22_records() -> tuple[list[dict[str, object]], dict[str, object]]:
    records: list[dict[str, object]] = []
    family_counts = {"v22_ramsey_independent": 0, "v22_ramsey_triangle": 0}
    for counts in category_profiles((7, 7, 7)):
        codegrees = (counts[3] + counts[7], counts[5] + counts[7], counts[6] + counts[7])
        if all(value == 1 for value in codegrees):
            family = "v22_ramsey_independent"
        elif all(value >= 2 for value in codegrees):
            family = "v22_ramsey_triangle"
        else:
            continue
        bound, positions = best_certificate(22, counts, V22_POSITION_BASES)
        assert bound < 1, (family, counts, bound, positions)
        family_counts[family] += 1
        records.append(profile_record(22, (7, 7, 7), counts, bound, positions, family))

    assert family_counts == {
        "v22_ramsey_independent": 2,
        "v22_ramsey_triangle": 215,
    }
    worst_by_family: dict[str, dict[str, object]] = {}
    for family in family_counts:
        family_records = [r for r in records if r["family"] == family]
        worst = max(family_records, key=lambda r: Fraction(**r["bound"]))
        worst_by_family[family] = worst
    assert Fraction(**worst_by_family["v22_ramsey_independent"]["bound"]) == Fraction(
        91231, 92378
    )
    assert Fraction(**worst_by_family["v22_ramsey_triangle"]["bound"]) == Fraction(
        456463, 461890
    )
    return records, {
        "family_counts": family_counts,
        "certificate_sha256": records_hash(records),
        "worst_by_family": worst_by_family,
    }


def build_artifact() -> tuple[list[dict[str, object]], dict[str, object]]:
    v21, v21_summary = close_v21()
    v22_closed, v22_residual = initial_v22_records()
    v22_ramsey, ramsey_summary = ramsey_v22_records()
    all_records = v21 + v22_closed + v22_residual + v22_ramsey
    manifest = {
        "schema": "property-b-m5-locked-certificate-v1",
        "arithmetic": "Python Fraction; no floating-point comparisons",
        "v21": v21_summary,
        "v22": {
            "initial_profile_count": len(v22_closed) + len(v22_residual),
            "initial_directly_closed": len(v22_closed),
            "initial_residual_count": len(v22_residual),
            "initial_residual_profiles": v22_residual,
            "ramsey_step": (
                "Residual profiles force minimum degree 7.  Since total degree is 160, "
                "at least 16 vertices have degree 7.  R(3,3)=6 applied to the graph "
                "xy iff codegree(x,y)>=2 supplies an independent triple or a triangle."
            ),
            "ramsey": ramsey_summary,
            "position_bases": [list(x) for x in V22_POSITION_BASES],
        },
        "all_records_sha256": records_hash(all_records),
        "all_record_count": len(all_records),
    }
    assert v21_summary["certificate_sha256"] == EXPECTED_RECORD_HASHES["v21"]
    assert (
        ramsey_summary["certificate_sha256"]
        == EXPECTED_RECORD_HASHES["v22_ramsey"]
    )
    assert manifest["all_records_sha256"] == EXPECTED_RECORD_HASHES["all"]
    assert manifest["all_record_count"] == 3081
    return all_records, manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output-dir", type=Path, default=Path(__file__).resolve().parent / "certificates"
    )
    args = parser.parse_args()
    records, manifest = build_artifact()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    records_path = args.output_dir / "v21_v22_locked_certificates.jsonl"
    manifest_path = args.output_dir / "v21_v22_manifest.json"
    records_path.write_text(
        "".join(json.dumps(r, sort_keys=True) + "\n" for r in records),
        encoding="utf-8",
    )
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
