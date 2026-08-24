#!/usr/bin/env python3
"""Independently verify every emitted v=21/v=22 locked certificate row."""

from __future__ import annotations

if not __debug__:
    raise RuntimeError(
        "verify_v21_v22.py is a proof checker and must be run without "
        "Python -O/-OO, which would remove validation assertions"
    )

import argparse
import hashlib
import itertools
import json
import time
from fractions import Fraction
from math import ceil
from pathlib import Path

from verify_lower33 import independent_locked_bound, independent_three_profiles


def degree_options(v: int) -> tuple[tuple[int, int, int], ...]:
    minimum = ceil((v - 1) / 4)
    return tuple(
        (first, second, third)
        for first in range(minimum, 33)
        for second in range(first, 33)
        for third in range(second, 33)
        if first + second + (v - 2) * third <= 160
    )


def assignments(bases: tuple[tuple[int, int, int], ...]) -> set[tuple[int, int, int]]:
    return {assignment for base in bases for assignment in itertools.permutations(base)}


def fraction(record: dict) -> Fraction:
    return Fraction(record["bound"]["numerator"], record["bound"]["denominator"])


def records_hash(records: list[dict]) -> str:
    digest = hashlib.sha256()
    for record in records:
        digest.update(
            json.dumps(record, sort_keys=True, separators=(",", ":")).encode("utf-8")
        )
        digest.update(b"\n")
    return digest.hexdigest()


def profile_key(record: dict) -> tuple[tuple[int, ...], tuple[int, ...]]:
    return tuple(record["degrees"]), tuple(record["counts_by_mask_000_to_111"])


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--artifact-dir",
        type=Path,
        default=Path(__file__).resolve().parent.parent / "theory" / "certificates",
    )
    parser.add_argument(
        "--report",
        type=Path,
        default=Path(__file__).resolve().parent
        / "logs"
        / "v21_v22_independent_verification.json",
        help="write the deterministic JSON report here",
    )
    args = parser.parse_args()
    started = time.monotonic()
    records_path = args.artifact_dir / "v21_v22_locked_certificates.jsonl"
    manifest_path = args.artifact_dir / "v21_v22_manifest.json"
    records = [
        json.loads(line)
        for line in records_path.read_text(encoding="utf-8").splitlines()
    ]
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert len(records) == manifest["all_record_count"]
    assert records_hash(records) == manifest["all_records_sha256"]
    assert manifest["all_records_sha256"] == (
        "feb165603b8eda25a3dfd55f842783810b015a5f1d4be510ce347a6dfac2ab7a"
    )

    bases21 = ((10, 11, 12), (1, 2, 3), (11, 12, 13), (1, 2, 12))
    bases22 = ((10, 11, 12), (1, 2, 3), (1, 2, 11), (1, 2, 13), (1, 11, 13))
    allowed21 = assignments(bases21)
    allowed22 = assignments(bases22)

    expected21 = {
        (degrees, counts)
        for degrees in degree_options(21)
        for counts in independent_three_profiles(degrees)
    }
    rows21 = [record for record in records if record["family"] == "v21_all"]
    assert len(rows21) == 1864
    assert records_hash(rows21) == manifest["v21"]["certificate_sha256"]
    assert manifest["v21"]["certificate_sha256"] == (
        "c622bed337a8fb1682f765020a2504542c89c77383559909095d05b98e040ee2"
    )
    assert {profile_key(record) for record in rows21} == expected21
    for record in rows21:
        counts = tuple(record["counts_by_mask_000_to_111"])
        positions = tuple(record["positions_by_selected_label"])
        assert positions in allowed21
        value = independent_locked_bound(21, counts, positions)
        assert value == fraction(record) and value < 1
        assert tuple(record["selected_codegrees"]) == (
            counts[3] + counts[7],
            counts[5] + counts[7],
            counts[6] + counts[7],
        )
    assert max(map(fraction, rows21)) == Fraction(9599, 9724)

    initial22 = [
        record
        for record in records
        if record["family"] == "v22_initial_three_lowest"
    ]
    expected22 = {
        (degrees, counts)
        for degrees in degree_options(22)
        for counts in independent_three_profiles(degrees)
    }
    assert len(initial22) == 1000
    assert {profile_key(record) for record in initial22} == expected22
    residual22 = []
    for record in initial22:
        counts = tuple(record["counts_by_mask_000_to_111"])
        positions = tuple(record["positions_by_selected_label"])
        assert positions in allowed22
        value = independent_locked_bound(22, counts, positions)
        assert value == fraction(record)
        if value >= 1:
            # Only three rows need a full minimization check; this verifies
            # that the chosen witness did not merely overlook a closing menu
            # assignment.
            menu_minimum = min(
                independent_locked_bound(22, counts, assignment)
                for assignment in allowed22
            )
            assert menu_minimum == value
            residual22.append(record)
        else:
            assert record["strictly_below_one"]
    assert len(residual22) == 3
    for record in residual22:
        assert record["degrees"] == [7, 7, 7]
        assert sorted(record["selected_codegrees"]) == [1, 1, 2]
        assert record["counts_by_mask_000_to_111"][7] == 0

    ramsey_rows = [record for record in records if record["family"].startswith("v22_ramsey_")]
    assert records_hash(ramsey_rows) == manifest["v22"]["ramsey"]["certificate_sha256"]
    assert manifest["v22"]["ramsey"]["certificate_sha256"] == (
        "80274adc462f71be34906175b470324bedd6480f2fad452278aad0a36720700c"
    )
    expected_ramsey: dict[str, set[tuple[tuple[int, ...], tuple[int, ...]]]] = {
        "v22_ramsey_independent": set(),
        "v22_ramsey_triangle": set(),
    }
    for counts in independent_three_profiles((7, 7, 7)):
        codegrees = (counts[3] + counts[7], counts[5] + counts[7], counts[6] + counts[7])
        if all(value == 1 for value in codegrees):
            expected_ramsey["v22_ramsey_independent"].add(((7, 7, 7), counts))
        elif all(value >= 2 for value in codegrees):
            expected_ramsey["v22_ramsey_triangle"].add(((7, 7, 7), counts))
    actual_by_family = {
        family: {profile_key(record) for record in ramsey_rows if record["family"] == family}
        for family in expected_ramsey
    }
    assert actual_by_family == expected_ramsey
    assert {family: len(rows) for family, rows in expected_ramsey.items()} == {
        "v22_ramsey_independent": 2,
        "v22_ramsey_triangle": 215,
    }
    for record in ramsey_rows:
        counts = tuple(record["counts_by_mask_000_to_111"])
        positions = tuple(record["positions_by_selected_label"])
        assert positions in allowed22
        value = independent_locked_bound(22, counts, positions)
        assert value == fraction(record) and value < 1
    worst_independent = max(
        fraction(record)
        for record in ramsey_rows
        if record["family"] == "v22_ramsey_independent"
    )
    worst_triangle = max(
        fraction(record)
        for record in ramsey_rows
        if record["family"] == "v22_ramsey_triangle"
    )
    assert worst_independent == Fraction(91231, 92378)
    assert worst_triangle == Fraction(456463, 461890)

    # Structural Ramsey arithmetic, independent of the profile files.
    assert 160 - 7 * 22 == 6
    assert 22 - 6 == 16  # at least sixteen degree-seven vertices

    report = {
        "status": "ALL_V21_V22_ROWS_INDEPENDENTLY_VERIFIED",
        "artifact_record_count": len(records),
        "artifact_sha256": records_hash(records),
        "v21_profile_count": len(expected21),
        "v21_worst": str(max(map(fraction, rows21))),
        "v22_initial_profile_count": len(expected22),
        "v22_closed_directly": len(initial22) - len(residual22),
        "v22_residual_count": len(residual22),
        "v22_ramsey_independent_count": len(expected_ramsey["v22_ramsey_independent"]),
        "v22_ramsey_triangle_count": len(expected_ramsey["v22_ramsey_triangle"]),
        "v22_ramsey_independent_worst": str(worst_independent),
        "v22_ramsey_triangle_worst": str(worst_triangle),
    }
    output = args.report
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    # Keep the pinned report byte-for-byte reproducible. Runtime is useful to
    # the person launching the check, but must not enter a checksummed file.
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
