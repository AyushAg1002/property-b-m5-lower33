#!/usr/bin/env python3
"""Portable, strict SHA-256 manifest verifier for the lower-bound artifact."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import tempfile
from pathlib import Path, PurePosixPath


LINE = re.compile(r"^([0-9a-f]{64})  (.+)$")
RELEASE_SCHEMA = "property-b-m5-lower33-release-v2"
WINDOWS_DEVICES = {
    "CON",
    "PRN",
    "AUX",
    "NUL",
    *(f"COM{index}" for index in range(1, 10)),
    *(f"LPT{index}" for index in range(1, 10)),
}


class ManifestError(ValueError):
    """The checksum manifest is malformed or unsafe."""


def validate_relative_name(name: object, context: str) -> str:
    """Return one canonical, safe POSIX path from release metadata."""
    if not isinstance(name, str):
        raise ManifestError(f"{context}: paths must be strings")
    if (
        not name
        or not name.isascii()
        or name != name.strip()
        or "\\" in name
        or any(ord(character) < 32 or ord(character) == 127 for character in name)
    ):
        raise ManifestError(f"{context}: non-portable path {name!r}")
    posix = PurePosixPath(name)
    if posix.is_absolute() or ".." in posix.parts:
        raise ManifestError(f"{context}: unsafe path {name!r}")
    if not posix.parts or any(part in {"", "."} for part in posix.parts):
        raise ManifestError(f"{context}: non-canonical path {name!r}")
    if posix.as_posix() != name:
        raise ManifestError(f"{context}: non-POSIX path {name!r}")
    for part in posix.parts:
        device_base = part.rstrip(" .").split(".", 1)[0].upper()
        if (
            any(character in '<>:"|?*' for character in part)
            or part.endswith((" ", "."))
            or device_base in WINDOWS_DEVICES
        ):
            raise ManifestError(f"{context}: Windows-incompatible path {name!r}")
    return name


def hash_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def parse_manifest(path: Path) -> list[tuple[str, str]]:
    entries: list[tuple[str, str]] = []
    seen: set[str] = set()
    seen_casefold: set[str] = set()
    for line_number, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not raw or raw.startswith("#"):
            continue
        match = LINE.fullmatch(raw)
        if match is None:
            raise ManifestError(
                f"{path}:{line_number}: expected '<64 lowercase hex>  <relative path>'"
            )
        expected, name = match.groups()
        validate_relative_name(name, f"{path}:{line_number}")
        if name in seen:
            raise ManifestError(f"{path}:{line_number}: duplicate path {name!r}")
        if name.casefold() in seen_casefold:
            raise ManifestError(
                f"{path}:{line_number}: case-colliding path {name!r}"
            )
        seen.add(name)
        seen_casefold.add(name.casefold())
        entries.append((expected, name))
    if not entries:
        raise ManifestError(f"{path}: contains no checksum entries")
    return entries


def parse_release_manifest(path: Path) -> list[str]:
    """Read and strictly validate the release whitelist."""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise ManifestError(f"{path}: invalid JSON: {error}") from error
    if not isinstance(data, dict):
        raise ManifestError(f"{path}: top-level JSON value must be an object")
    if data.get("schema") != RELEASE_SCHEMA:
        raise ManifestError(
            f"{path}: expected release schema {RELEASE_SCHEMA!r}, "
            f"got {data.get('schema')!r}"
        )
    names = data.get("included_files")
    if not isinstance(names, list) or not names:
        raise ManifestError(f"{path}: included_files must be a nonempty list")
    answer: list[str] = []
    seen: set[str] = set()
    seen_casefold: set[str] = set()
    for index, value in enumerate(names):
        name = validate_relative_name(value, f"{path}:included_files[{index}]")
        if name in seen:
            raise ManifestError(f"{path}: duplicate release path {name!r}")
        if name.casefold() in seen_casefold:
            raise ManifestError(f"{path}: case-colliding release path {name!r}")
        seen.add(name)
        seen_casefold.add(name.casefold())
        answer.append(name)
    return answer


def path_name_within_root(path: Path, root: Path, context: str) -> str:
    root = root.resolve()
    resolved = path.resolve()
    try:
        relative = resolved.relative_to(root)
    except ValueError as error:
        raise ManifestError(f"{context}: {resolved} is outside root {root}") from error
    name = PurePosixPath(*relative.parts).as_posix()
    return validate_relative_name(name, context)


def contains_symlink(root: Path, name: str) -> bool:
    """Return whether any manifest path component below root is a symlink."""
    candidate = root
    for part in PurePosixPath(name).parts:
        candidate /= part
        if candidate.is_symlink():
            return True
    return False


def checksum_names_for_release(
    release_manifest: Path, checksum_manifest: Path, root: Path
) -> list[str]:
    """Return the exact checksum order implied by a release whitelist."""
    names = parse_release_manifest(release_manifest)
    release_name = path_name_within_root(
        release_manifest, root, "release manifest"
    )
    checksum_name = path_name_within_root(
        checksum_manifest, root, "checksum manifest"
    )
    if names.count(release_name) != 1:
        raise ManifestError(
            f"{release_manifest}: must include itself as {release_name!r} exactly once"
        )
    if names.count(checksum_name) != 1:
        raise ManifestError(
            f"{release_manifest}: must include checksum manifest "
            f"{checksum_name!r} exactly once"
        )
    if release_name == checksum_name:
        raise ManifestError("release and checksum manifests must be distinct files")
    return [name for name in names if name != checksum_name]


def require_release_membership(
    checksum_manifest: Path, release_manifest: Path, root: Path
) -> None:
    """Require checksum entries to equal the release whitelist and its order."""
    expected = checksum_names_for_release(release_manifest, checksum_manifest, root)
    actual = [name for _, name in parse_manifest(checksum_manifest)]
    if actual == expected:
        return
    missing = [name for name in expected if name not in actual]
    extra = [name for name in actual if name not in expected]
    details = []
    if missing:
        details.append(f"missing={missing!r}")
    if extra:
        details.append(f"extra={extra!r}")
    if not missing and not extra:
        details.append("entries are not in release-manifest order")
    raise ManifestError(
        f"{checksum_manifest}: checksum/release membership mismatch: "
        + "; ".join(details)
    )


def write_release_checksums(
    checksum_manifest: Path, release_manifest: Path, root: Path
) -> int:
    """Atomically regenerate checksums in release-whitelist order."""
    root = root.resolve()
    names = checksum_names_for_release(release_manifest, checksum_manifest, root)
    entries: list[tuple[str, str]] = []
    for name in names:
        candidate = root.joinpath(*PurePosixPath(name).parts)
        if contains_symlink(root, name):
            raise ManifestError(f"symlinked release input {name!r}")
        try:
            resolved = candidate.resolve(strict=True)
        except FileNotFoundError as error:
            raise ManifestError(f"missing release input {name!r}") from error
        if root not in resolved.parents or not resolved.is_file():
            raise ManifestError(f"unsafe release input {name!r}")
        entries.append((hash_file(resolved), name))

    destination = checksum_manifest.resolve()
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary_name: str | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="wb",
            dir=destination.parent,
            prefix=f".{destination.name}.",
            delete=False,
        ) as stream:
            temporary_name = stream.name
            stream.write(
                "".join(
                    f"{expected}  {name}\n" for expected, name in entries
                ).encode("ascii")
            )
            stream.flush()
            os.fsync(stream.fileno())
        os.chmod(temporary_name, 0o644)
        temporary_path = Path(temporary_name)
        if parse_manifest(temporary_path) != entries:
            raise ManifestError("temporary checksum manifest failed round-trip parsing")
        for expected, name in entries:
            if contains_symlink(root, name):
                raise ManifestError(f"release input changed to a symlink: {name!r}")
            candidate = root.joinpath(*PurePosixPath(name).parts)
            try:
                resolved = candidate.resolve(strict=True)
            except FileNotFoundError as error:
                raise ManifestError(f"release input disappeared: {name!r}") from error
            if root not in resolved.parents or not resolved.is_file():
                raise ManifestError(f"unsafe release input {name!r}")
            if hash_file(resolved) != expected:
                raise ManifestError(
                    f"release input changed during checksum generation: {name!r}"
                )
        os.replace(temporary_name, destination)
        temporary_name = None
        if hasattr(os, "O_DIRECTORY"):
            directory_descriptor = os.open(
                destination.parent, os.O_RDONLY | os.O_DIRECTORY
            )
            try:
                os.fsync(directory_descriptor)
            finally:
                os.close(directory_descriptor)
    finally:
        if temporary_name is not None:
            Path(temporary_name).unlink(missing_ok=True)
    return len(entries)


def verify(manifest: Path, root: Path) -> list[str]:
    failures: list[str] = []
    root = root.resolve()
    for expected, name in parse_manifest(manifest):
        candidate = root.joinpath(*PurePosixPath(name).parts)
        if contains_symlink(root, name):
            failures.append(f"UNSAFE   {name}: symlinks are not allowed")
            continue
        try:
            resolved = candidate.resolve(strict=True)
        except FileNotFoundError:
            failures.append(f"MISSING  {name}")
            continue
        if root not in resolved.parents or not resolved.is_file():
            failures.append(f"UNSAFE   {name}")
            continue
        actual = hash_file(resolved)
        if actual != expected:
            failures.append(f"FAILED   {name}: expected {expected}, got {actual}")
        else:
            print(f"OK       {name}")
    return failures


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    repository = Path(__file__).resolve().parent.parent
    parser.add_argument(
        "manifest",
        nargs="?",
        type=Path,
        default=repository / "SHA256SUMS",
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=repository,
        help="directory against which manifest paths are resolved",
    )
    release_mode = parser.add_mutually_exclusive_group()
    release_mode.add_argument(
        "--release-manifest",
        type=Path,
        help="also require checksum membership/order to match this release JSON",
    )
    release_mode.add_argument(
        "--write-from-release-manifest",
        type=Path,
        help="atomically rewrite the checksum manifest from this release JSON",
    )
    args = parser.parse_args()
    try:
        if args.write_from_release_manifest is not None:
            count = write_release_checksums(
                args.manifest, args.write_from_release_manifest, args.root
            )
            failures = verify(args.manifest, args.root)
            require_release_membership(
                args.manifest, args.write_from_release_manifest, args.root
            )
            if failures:
                print("\n".join(failures), file=sys.stderr)
                return 1
            print(f"wrote and verified {count} SHA-256 entries")
            return 0
        if args.release_manifest is not None:
            require_release_membership(args.manifest, args.release_manifest, args.root)
        failures = verify(args.manifest, args.root)
    except (OSError, ManifestError) as error:
        print(f"MANIFEST ERROR: {error}", file=sys.stderr)
        return 2
    if failures:
        print("\n".join(failures), file=sys.stderr)
        return 1
    print(f"verified {len(parse_manifest(args.manifest))} SHA-256 entries")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
