#!/usr/bin/env python3
"""Build the whitelisted lower-bound release directory without search debris."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
from pathlib import Path, PurePosixPath

from package_lower33_release import load_release_manifest
from verify_sha256 import contains_symlink


REPOSITORY = Path(__file__).resolve().parent.parent


def fail(message: str) -> None:
    raise ValueError(message)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "output",
        nargs="?",
        type=Path,
        default=REPOSITORY / "dist" / "property_b_m5_lower33_artifact",
    )
    args = parser.parse_args()
    output = args.output.resolve()
    if output.exists():
        fail(f"refusing to overwrite existing path: {output}")

    _, files = load_release_manifest(REPOSITORY)
    repository = REPOSITORY.resolve()

    for name in files:
        path = PurePosixPath(name)
        if contains_symlink(repository, name):
            fail(f"symlinked release input: {name}")
        source = repository.joinpath(*path.parts)
        try:
            resolved = source.resolve(strict=True)
        except FileNotFoundError:
            fail(f"missing release input: {name}")
        if repository not in resolved.parents or not resolved.is_file():
            fail(f"unsafe release input: {name}")

    output.mkdir(parents=True)
    try:
        for name in files:
            parts = PurePosixPath(name).parts
            source = REPOSITORY.joinpath(*parts)
            destination = output.joinpath(*parts)
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, destination)
            os.chmod(destination, 0o644)
    except BaseException:
        try:
            shutil.rmtree(output)
        except OSError:
            pass
        raise

    print(
        json.dumps(
            {
                "status": "LOWER33_RELEASE_BUILT",
                "file_count": len(files),
                "output": str(output),
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError) as error:
        print(f"RELEASE BUILD FAILED: {error}", file=sys.stderr)
        raise SystemExit(1) from error
