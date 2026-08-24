#!/usr/bin/env python3
"""One-command deterministic verification of the m(5) >= 33 artifact."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
import time
from pathlib import Path


REPOSITORY = Path(__file__).resolve().parent


class VerificationError(RuntimeError):
    """A required computation or byte-for-byte comparison failed."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise VerificationError(message)


def run(
    *arguments: str, capture: bool = False, optimized: bool = False
) -> subprocess.CompletedProcess[str]:
    command = [sys.executable]
    if optimized:
        command.append("-O")
    command.extend(arguments)
    print("+", " ".join(command), flush=True)
    return subprocess.run(
        command,
        cwd=REPOSITORY,
        check=True,
        text=True,
        capture_output=capture,
    )


def same_bytes(generated: Path, pinned: Path) -> None:
    require(generated.read_bytes() == pinned.read_bytes(), f"byte mismatch: {pinned}")
    print(f"BYTE-IDENTICAL {pinned.relative_to(REPOSITORY)}")


def same_json(generated_text: str, pinned: Path) -> None:
    generated = json.loads(generated_text)
    expected = json.loads(pinned.read_text(encoding="utf-8"))
    require(generated == expected, f"JSON mismatch: {pinned}")
    print(f"JSON-IDENTICAL {pinned.relative_to(REPOSITORY)}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--full",
        action="store_true",
        help="also regenerate the 3,081-row canonical witness certificate",
    )
    args = parser.parse_args()
    require(sys.version_info >= (3, 10), "CPython 3.10 or newer is required")
    require(__debug__, "run without Python -O/-OO; proof checks must remain enabled")
    started = time.monotonic()

    run("tools/verify_sha256.py")
    run(
        "tools/verify_sha256.py",
        "optimization/ARTIFACTS.sha256",
        "--root",
        "optimization",
    )
    run("theory/locked_greedy_32.py", "--self-test")

    selection = run("theory/selection_certificates.py", "--compact", capture=True)
    same_json(selection.stdout, REPOSITORY / "theory" / "SELECTION_MANIFEST.json")

    with tempfile.TemporaryDirectory(prefix="property_b_m5_lower33_") as directory:
        temporary = Path(directory)
        if args.full:
            regenerated = temporary / "certificates"
            run(
                "theory/close_v21_v22.py",
                "--output-dir",
                str(regenerated),
                capture=True,
            )
            for filename in (
                "v21_v22_locked_certificates.jsonl",
                "v21_v22_manifest.json",
            ):
                same_bytes(
                    regenerated / filename,
                    REPOSITORY / "theory" / "certificates" / filename,
                )

        v21_report = temporary / "v21_v22_independent_verification.json"
        run(
            "solver_alt/verify_v21_v22.py",
            "--artifact-dir",
            "theory/certificates",
            "--report",
            str(v21_report),
            capture=True,
        )
        same_bytes(
            v21_report,
            REPOSITORY
            / "solver_alt"
            / "logs"
            / "v21_v22_independent_verification.json",
        )

        lower_report = temporary / "lower33_independent_verification.json"
        run(
            "solver_alt/verify_lower33.py",
            "--report",
            str(lower_report),
            capture=True,
        )
        same_bytes(
            lower_report,
            REPOSITORY
            / "solver_alt"
            / "logs"
            / "lower33_independent_verification.json",
        )

        # The optimization programs use explicit guards rather than assert,
        # and are deliberately exercised under -O to prove those checks stay
        # active.  Their output paths are temporary, then compared bytewise.
        for program in (
            "optimization/general_locked.py",
            "optimization/compiled_locked.py",
            "optimization/state_optimizer.py",
            "optimization/trace_partitions.py",
        ):
            run(program, optimized=True, capture=True)

        v25_10k2 = temporary / "v25_10k2_verification.json"
        run(
            "optimization/verify_v25_10k2.py",
            "--output",
            str(v25_10k2),
            optimized=True,
            capture=True,
        )
        same_bytes(
            v25_10k2,
            REPOSITORY / "optimization" / "v25_10k2_verification.json",
        )

        v25_selection = temporary / "v25_selection_ceiling_verification.json"
        run(
            "optimization/verify_v25_selection_ceiling.py",
            "--output",
            str(v25_selection),
            optimized=True,
            capture=True,
        )
        same_bytes(
            v25_selection,
            REPOSITORY
            / "optimization"
            / "v25_selection_ceiling_verification.json",
        )

        menu_summary = temporary / "m32_v21_menu_summary.json"
        menu_records = temporary / "m32_v21_menu_records.jsonl"
        run(
            "optimization/sweep_m32_v21_menu.py",
            "--summary",
            str(menu_summary),
            "--records",
            str(menu_records),
            optimized=True,
            capture=True,
        )
        same_bytes(
            menu_summary,
            REPOSITORY / "optimization" / "m32_v21_menu_summary.json",
        )
        same_bytes(
            menu_records,
            REPOSITORY / "optimization" / "m32_v21_menu_records.jsonl",
        )

        subset_summary = temporary / "m32_v21_base_subsets_summary.json"
        subset_records = temporary / "m32_v21_six_base_profiles.jsonl"
        run(
            "optimization/verify_m32_v21_base_subsets.py",
            "--summary",
            str(subset_summary),
            "--records",
            str(subset_records),
            optimized=True,
            capture=True,
        )
        same_bytes(
            subset_summary,
            REPOSITORY
            / "optimization"
            / "m32_v21_base_subsets_summary.json",
        )
        same_bytes(
            subset_records,
            REPOSITORY / "optimization" / "m32_v21_six_base_profiles.jsonl",
        )

    result = {
        "status": "ALL_LOWER33_ARTIFACT_CHECKS_PASSED",
        "mode": "full" if args.full else "independent-replay",
        "python": ".".join(map(str, sys.version_info[:3])),
        "elapsed_seconds": round(time.monotonic() - started, 3),
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, subprocess.CalledProcessError, VerificationError) as error:
        print(f"VERIFICATION FAILED: {error}", file=sys.stderr)
        raise SystemExit(1) from error
