#!/usr/bin/env python3
"""Create deterministic artifact ZIP and arXiv-source tarball."""

from __future__ import annotations

import argparse
import errno
import gzip
import hashlib
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
import zipfile
from pathlib import Path, PurePosixPath


REPOSITORY = Path(__file__).resolve().parent.parent
ZIP_TIME = (1980, 1, 1, 0, 0, 0)
RELEASE_SCHEMA = "property-b-m5-lower33-release-v2"
EXPECTED_VERSION = "1.0.0"
EXPECTED_TAG = "v1.0.0"
EXPECTED_REPOSITORY = "https://github.com/AyushAg1002/property-b-m5-lower33"
EXPECTED_DOI = "10.5281/zenodo.22070117"
EXPECTED_CFF_VERSION = "1.2.0"
GZIP_HEADER = b"\x1f\x8b\x08\x00\x00\x00\x00\x00\x02\xff"
WINDOWS_DEVICES = {
    "CON",
    "PRN",
    "AUX",
    "NUL",
    *(f"COM{index}" for index in range(1, 10)),
    *(f"LPT{index}" for index in range(1, 10)),
}
ARXIV_INPUTS = {
    "main.tex": PurePosixPath("paper/main.tex"),
    "references.bib": PurePosixPath("paper/references.bib"),
}
PLACEHOLDERS = (
    "[REPOSITORY URL]",
    "[FULL COMMIT HASH]",
    "[ZENODO OR EQUIVALENT DOI]",
    "[ARTIFACT LICENSE]",
    "RESERVED_ID",
    "example.invalid",
    "REPLACE WITH",
)
METADATA_FILES = ("README.md", "CITATION.cff", "paper/main.tex")


def fail(message: str) -> None:
    raise ValueError(message)


def safe_release_name(value: object, context: str) -> str:
    if not isinstance(value, str):
        fail(f"{context}: release paths must be strings")
    if (
        not value
        or not value.isascii()
        or value != value.strip()
        or "\\" in value
        or any(ord(character) < 32 or ord(character) == 127 for character in value)
    ):
        fail(f"{context}: non-portable release path {value!r}")
    path = PurePosixPath(value)
    if (
        path.is_absolute()
        or ".." in path.parts
        or not path.parts
        or any(part in {"", "."} for part in path.parts)
        or path.as_posix() != value
    ):
        fail(f"{context}: unsafe or non-canonical path {value!r}")
    for part in path.parts:
        device_base = part.rstrip(" .").split(".", 1)[0].upper()
        if (
            any(character in '<>:"|?*' for character in part)
            or part.endswith((" ", "."))
            or device_base in WINDOWS_DEVICES
        ):
            fail(f"{context}: Windows-incompatible release path {value!r}")
    return value


def load_release_manifest(root: Path) -> tuple[dict[str, object], list[str]]:
    manifest = root / "release" / "lower33_manifest.json"
    data = json.loads(manifest.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        fail("release manifest top-level JSON value must be an object")
    if data.get("schema") != RELEASE_SCHEMA:
        fail(f"unsupported release schema: {data.get('schema')!r}")
    version = data.get("artifact_version")
    if version != EXPECTED_VERSION:
        fail(f"invalid artifact_version: {version!r}")
    if data.get("release_tag") != EXPECTED_TAG:
        fail(f"release_tag must be the immutable tag {EXPECTED_TAG!r}")
    repository = data.get("repository")
    if repository != EXPECTED_REPOSITORY:
        fail(f"invalid repository URL: {repository!r}")
    doi = data.get("archive_doi")
    if doi != EXPECTED_DOI:
        fail(f"invalid archive DOI: {doi!r}")
    policy = data.get("license_policy")
    if not isinstance(policy, dict) or policy != {
        "source_code": "MIT",
        "manuscript_documentation_certificates_and_reports": "CC-BY-4.0",
        "mapping": "LICENSES/README.md",
    }:
        fail("release manifest has an unexpected license_policy")

    raw_names = data.get("included_files")
    if not isinstance(raw_names, list) or not raw_names:
        fail("release manifest has no included_files list")
    names: list[str] = []
    seen: set[str] = set()
    seen_casefold: set[str] = set()
    for index, value in enumerate(raw_names):
        name = safe_release_name(value, f"included_files[{index}]")
        if name in seen:
            fail(f"duplicate release path: {name!r}")
        if name.casefold() in seen_casefold:
            fail(f"case-colliding release path: {name!r}")
        seen.add(name)
        seen_casefold.add(name.casefold())
        names.append(name)

    required = {
        "README.md",
        "REPRODUCIBILITY.md",
        "SUBMISSION_CHECKLIST.md",
        "CITATION.cff",
        "LICENSES/README.md",
        "LICENSES/MIT.txt",
        "LICENSES/CC-BY-4.0.txt",
        "SHA256SUMS",
        "release/lower33_manifest.json",
        "tools/verify_sha256.py",
        "tools/build_lower33_release.py",
        "tools/package_lower33_release.py",
        "paper/main.tex",
        "paper/references.bib",
        "output/pdf/property_b_m5_lower33.pdf",
    }
    missing = sorted(required - seen)
    if missing:
        fail(f"release manifest omits required public-release files: {missing!r}")
    if "CITATION.cff.template" in seen:
        fail("public release must contain CITATION.cff, not its template")
    forbidden = []
    for name in names:
        lowered = name.casefold()
        suffixes = PurePosixPath(lowered).suffixes
        if (
            name.startswith("submission/")
            or "__pycache__" in PurePosixPath(name).parts
            or PurePosixPath(lowered).suffix
            in {".pyc", ".pyo", ".cnf", ".drat", ".aux", ".log"}
            or suffixes[-2:] == [".tar", ".gz"]
            or PurePosixPath(lowered).suffix in {".zip", ".tgz"}
            or any(
                marker in lowered
                for marker in (
                    "unknown",
                    "search_upper",
                    "upper_bound_search",
                    "radius_q2",
                    "obsolete_m29",
                )
            )
        ):
            forbidden.append(name)
    if forbidden:
        fail(f"release manifest contains excluded material: {forbidden!r}")
    return data, names


def validate_embedded_metadata(root: Path, data: dict[str, object]) -> None:
    texts = {
        name: (root / name).read_text(encoding="utf-8")
        for name in METADATA_FILES
    }
    for name, content in texts.items():
        for placeholder in PLACEHOLDERS:
            if placeholder in content:
                fail(f"unresolved public-release placeholder {placeholder!r} in {name}")

    required_values = {
        "README.md": (
            data["repository"],
            data["release_tag"],
            data["archive_doi"],
        ),
        "CITATION.cff": (
            data["repository"],
            data["artifact_version"],
            data["release_tag"],
            data["archive_doi"],
        ),
        "paper/main.tex": (
            data["repository"],
            data["release_tag"],
            data["archive_doi"],
        ),
    }
    for name, values in required_values.items():
        for value in values:
            if not isinstance(value, str) or value not in texts[name]:
                fail(f"{name} does not record release value {value!r}")
    citation = texts["CITATION.cff"]
    exact_cff_fields = {
        "cff-version": EXPECTED_CFF_VERSION,
        "type": "software",
        "version": EXPECTED_VERSION,
        "doi": EXPECTED_DOI,
        "repository-code": EXPECTED_REPOSITORY,
        "repository-artifact": f"https://doi.org/{EXPECTED_DOI}",
        "url": f"https://doi.org/{EXPECTED_DOI}",
    }
    for field, expected in exact_cff_fields.items():
        encoded = re.escape(expected)
        pattern = rf"(?m)^{re.escape(field)}:\s*(?:\"{encoded}\"|'{encoded}'|{encoded})\s*$"
        if re.search(pattern, citation) is None:
            fail(f"CITATION.cff does not have exact {field}: {expected!r}")
    tag_url = f"{EXPECTED_REPOSITORY}/releases/tag/{EXPECTED_TAG}"
    if re.search(
        rf"(?m)^\s+value:\s*(?:\"{re.escape(tag_url)}\"|'{re.escape(tag_url)}'|{re.escape(tag_url)})\s*$",
        citation,
    ) is None:
        fail("CITATION.cff does not record the exact immutable-tag URL")
    if re.search(r"(?m)^license\s*:", citation):
        fail("CITATION.cff must not collapse the mixed-license mapping into license:")


def refuse_existing(path: Path) -> None:
    if path.exists():
        raise FileExistsError(f"refusing to overwrite existing archive: {path}")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def normalized_zip(
    source_root: Path, names: list[str], output: Path, prefix: str
) -> None:
    with zipfile.ZipFile(
        output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9
    ) as archive:
        for name in sorted(names):
            source = source_root.joinpath(*PurePosixPath(name).parts)
            info = zipfile.ZipInfo(f"{prefix}/{name}", ZIP_TIME)
            info.create_system = 3
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, source.read_bytes(), compresslevel=9)


def normalized_arxiv_tar(source_root: Path, output: Path) -> None:
    with output.open("wb") as raw:
        with gzip.GzipFile(
            filename="", mode="wb", fileobj=raw, compresslevel=9, mtime=0
        ) as compressed:
            with tarfile.open(
                fileobj=compressed, mode="w", format=tarfile.USTAR_FORMAT
            ) as archive:
                for name, relative in sorted(ARXIV_INPUTS.items()):
                    source = source_root.joinpath(*relative.parts)
                    payload = source.read_bytes()
                    info = tarfile.TarInfo(name)
                    info.size = len(payload)
                    info.mode = 0o644
                    info.mtime = 0
                    info.uid = info.gid = 0
                    info.uname = info.gname = ""
                    archive.addfile(info, io.BytesIO(payload))


def run_release_verifier(root: Path) -> None:
    subprocess.run(
        [
            sys.executable,
            str(root / "tools" / "verify_sha256.py"),
            str(root / "SHA256SUMS"),
            "--root",
            str(root),
            "--release-manifest",
            str(root / "release" / "lower33_manifest.json"),
        ],
        cwd=root,
        check=True,
    )


def git_output(root: Path, *arguments: str) -> bytes:
    """Run Git without a shell and return its exact standard output."""
    completed = subprocess.run(
        ["git", "-C", str(root), *arguments],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if completed.returncode != 0:
        detail = completed.stderr.decode("utf-8", errors="replace").strip()
        fail(f"git {' '.join(arguments)} failed: {detail or completed.returncode}")
    return completed.stdout


def validate_tagged_payload(
    git_root: Path, content_root: Path, names: list[str]
) -> None:
    """Require content_root bytes to equal every whitelisted tagged blob."""
    for name in names:
        tagged_payload = git_output(git_root, "show", f"{EXPECTED_TAG}:{name}")
        payload = content_root.joinpath(*PurePosixPath(name).parts).read_bytes()
        if payload != tagged_payload:
            fail(f"release bytes differ from {EXPECTED_TAG}:{name}")


def validate_git_tag(root: Path, names: list[str]) -> None:
    """Bind a clean release worktree byte-for-byte to the immutable Git tag."""
    top_level = Path(
        git_output(root, "rev-parse", "--show-toplevel")
        .decode("utf-8")
        .strip()
    ).resolve()
    if top_level != root.resolve():
        fail(f"Git top-level {top_level} is not release root {root.resolve()}")

    tagged = (
        git_output(root, "rev-parse", "--verify", f"refs/tags/{EXPECTED_TAG}^{{commit}}")
        .decode("ascii")
        .strip()
    )
    head = (
        git_output(root, "rev-parse", "--verify", "HEAD^{commit}")
        .decode("ascii")
        .strip()
    )
    if tagged != head:
        fail(f"HEAD {head} is not immutable tag {EXPECTED_TAG} ({tagged})")

    git_output(root, "ls-files", "--error-unmatch", "--", *names)
    status = git_output(
        root, "status", "--porcelain=v1", "--untracked-files=all", "--", *names
    )
    if status:
        fail(
            "release-whitelist files are not clean at the tagged commit:\n"
            + status.decode("utf-8", errors="replace").rstrip()
        )

    validate_tagged_payload(root, root, names)


def require_exact_staged_files(staged: Path, names: list[str]) -> None:
    actual = sorted(
        path.relative_to(staged).as_posix()
        for path in staged.rglob("*")
        if path.is_file()
    )
    expected = sorted(names)
    if actual != expected:
        missing = [name for name in expected if name not in actual]
        extra = [name for name in actual if name not in expected]
        fail(f"staged release differs from whitelist: missing={missing!r}; extra={extra!r}")


def validate_zip(
    path: Path, source_root: Path, names: list[str], prefix: str
) -> None:
    expected = [f"{prefix}/{name}" for name in sorted(names)]
    with zipfile.ZipFile(path, "r") as archive:
        if archive.namelist() != expected:
            fail("ZIP member list or order differs from the release whitelist")
        if archive.comment:
            fail("ZIP archive has a non-normalized comment")
        bad = archive.testzip()
        if bad is not None:
            fail(f"ZIP integrity check failed at {bad!r}")
        for info in archive.infolist():
            if info.date_time != ZIP_TIME:
                fail(f"ZIP member has a non-normalized timestamp: {info.filename}")
            if info.create_system != 3 or info.external_attr != 0o100644 << 16:
                fail(f"ZIP member has non-normalized mode metadata: {info.filename}")
            if info.compress_type != zipfile.ZIP_DEFLATED:
                fail(f"ZIP member has unexpected compression: {info.filename}")
            if info.extra or info.comment:
                fail(f"ZIP member has non-normalized extra metadata: {info.filename}")
            name = info.filename.removeprefix(f"{prefix}/")
            source = source_root.joinpath(*PurePosixPath(name).parts)
            if archive.read(info) != source.read_bytes():
                fail(f"ZIP member differs from staged source: {info.filename}")


def validate_arxiv_tar(path: Path, source_root: Path) -> None:
    payload = path.read_bytes()
    if len(payload) < 10 or payload[:10] != GZIP_HEADER:
        fail("arXiv archive has a non-normalized gzip header")
    with tarfile.open(path, "r:gz") as archive:
        members = archive.getmembers()
        expected_names = sorted(ARXIV_INPUTS)
        if [member.name for member in members] != expected_names:
            fail("arXiv archive must contain exactly main.tex and references.bib")
        for member in members:
            if (
                not member.isfile()
                or member.mode != 0o644
                or member.mtime != 0
                or member.uid != 0
                or member.gid != 0
                or member.uname != ""
                or member.gname != ""
            ):
                fail(f"arXiv member has non-normalized metadata: {member.name}")
            stream = archive.extractfile(member)
            if stream is None:
                fail(f"cannot read arXiv member: {member.name}")
            relative = ARXIV_INPUTS[member.name]
            expected = source_root.joinpath(*relative.parts).read_bytes()
            if stream.read() != expected:
                fail(f"arXiv member differs from staged source: {member.name}")


def checksum_payload(artifact_zip: Path, arxiv_tar: Path) -> bytes:
    return (
        f"{sha256(artifact_zip)}  {artifact_zip.name}\n"
        f"{sha256(arxiv_tar)}  {arxiv_tar.name}\n"
    ).encode("ascii")


def validate_checksum_sidecar(
    path: Path, artifact_zip: Path, arxiv_tar: Path
) -> None:
    if path.read_bytes() != checksum_payload(artifact_zip, arxiv_tar):
        fail("archive checksum sidecar is malformed or stale")


def normalize_output_file(path: Path) -> None:
    """Normalize permissions and make a completed temporary file durable."""
    os.chmod(path, 0o644)
    with path.open("rb") as stream:
        os.fsync(stream.fileno())


def install_no_replace(source: Path, destination: Path) -> None:
    """Atomically install one file without an overwrite race."""
    try:
        os.link(source, destination)
    except OSError as error:
        if error.errno not in {
            errno.EPERM,
            errno.EACCES,
            errno.EXDEV,
            errno.ENOSYS,
            getattr(errno, "EOPNOTSUPP", errno.ENOSYS),
        }:
            raise
        descriptor = os.open(
            destination, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644
        )
        try:
            with os.fdopen(descriptor, "wb") as output:
                descriptor = -1
                with source.open("rb") as input_stream:
                    shutil.copyfileobj(input_stream, output, 1024 * 1024)
                output.flush()
                os.fsync(output.fileno())
            if sha256(destination) != sha256(source):
                fail(f"installed output differs from temporary file: {destination}")
            os.chmod(destination, 0o644)
        except BaseException:
            if descriptor >= 0:
                os.close(descriptor)
            try:
                destination.unlink()
            except OSError:
                pass
            raise
    try:
        source.unlink()
    except BaseException:
        try:
            destination.unlink()
        except OSError:
            pass
        raise


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument(
        "--preflight-only",
        action="store_true",
        help="validate metadata, whitelist membership, and checksums without packaging",
    )
    parser.add_argument(
        "--require-git-tag",
        action="store_true",
        help=(
            "also require this exact 48-file tree to be tracked, clean, and at "
            f"immutable Git tag {EXPECTED_TAG}"
        ),
    )
    args = parser.parse_args()
    data, names = load_release_manifest(REPOSITORY)
    validate_embedded_metadata(REPOSITORY, data)
    run_release_verifier(REPOSITORY)
    if args.require_git_tag:
        validate_git_tag(REPOSITORY, names)

    version = data["artifact_version"]
    if not isinstance(version, str):
        fail("artifact_version must be a string")
    if args.preflight_only:
        print(
            json.dumps(
                {
                    "status": "LOWER33_RELEASE_PREFLIGHT_PASSED",
                    "artifact_version": version,
                    "file_count": len(names),
                    "git_tag_binding": (
                        "verified" if args.require_git_tag else "not requested"
                    ),
                },
                indent=2,
                sort_keys=True,
            )
        )
        return 0

    default_output_dir = (REPOSITORY / "release").resolve()
    if args.output_dir is None:
        if not args.require_git_tag:
            fail(
                "untagged release-candidate packaging requires an explicit "
                "non-default --output-dir"
            )
        output_dir = default_output_dir
    else:
        output_dir = args.output_dir.resolve()
        if not args.require_git_tag and output_dir == default_output_dir:
            fail(
                "untagged release-candidate output must not be the repository's "
                "release directory"
            )
    output_dir.mkdir(parents=True, exist_ok=True)
    artifact_zip = output_dir / f"property_b_m5_lower33_artifact-v{version}.zip"
    arxiv_tar = output_dir / f"property_b_m5_lower33_arxiv-v{version}.tar.gz"
    archive_sums = output_dir / f"property_b_m5_lower33_archives-v{version}.sha256"
    refuse_existing(artifact_zip)
    refuse_existing(arxiv_tar)
    refuse_existing(archive_sums)

    prefix = f"property_b_m5_lower33_artifact-v{version}"
    installed: list[Path] = []
    try:
        with tempfile.TemporaryDirectory(prefix="property_b_m5_release_") as directory:
            staged = Path(directory) / "artifact"
            subprocess.run(
                [sys.executable, "tools/build_lower33_release.py", str(staged)],
                cwd=REPOSITORY,
                check=True,
            )
            require_exact_staged_files(staged, names)
            validate_embedded_metadata(staged, data)
            run_release_verifier(staged)
            if args.require_git_tag:
                validate_tagged_payload(REPOSITORY, staged, names)

            with tempfile.TemporaryDirectory(
                prefix=".property_b_m5_archives_", dir=output_dir
            ) as archive_directory:
                temporary_dir = Path(archive_directory)
                temporary_zip = temporary_dir / artifact_zip.name
                temporary_tar = temporary_dir / arxiv_tar.name
                temporary_sums = temporary_dir / archive_sums.name
                repeated_zip = temporary_dir / f"repeat-{artifact_zip.name}"
                repeated_tar = temporary_dir / f"repeat-{arxiv_tar.name}"

                normalized_zip(staged, names, temporary_zip, prefix)
                normalized_arxiv_tar(staged, temporary_tar)
                normalized_zip(staged, names, repeated_zip, prefix)
                normalized_arxiv_tar(staged, repeated_tar)
                if temporary_zip.read_bytes() != repeated_zip.read_bytes():
                    fail("independent ZIP constructions are not byte-identical")
                if temporary_tar.read_bytes() != repeated_tar.read_bytes():
                    fail("independent arXiv constructions are not byte-identical")
                validate_zip(temporary_zip, staged, names, prefix)
                validate_arxiv_tar(temporary_tar, staged)
                temporary_sums.write_bytes(
                    checksum_payload(temporary_zip, temporary_tar)
                )
                validate_checksum_sidecar(
                    temporary_sums, temporary_zip, temporary_tar
                )
                for path in (temporary_zip, temporary_tar, temporary_sums):
                    normalize_output_file(path)

                for temporary, final in (
                    (temporary_zip, artifact_zip),
                    (temporary_tar, arxiv_tar),
                    (temporary_sums, archive_sums),
                ):
                    install_no_replace(temporary, final)
                    installed.append(final)
    except BaseException:
        for path in reversed(installed):
            try:
                path.unlink(missing_ok=True)
            except OSError:
                pass
        raise

    print(
        json.dumps(
            {
                "status": "DETERMINISTIC_RELEASE_ARCHIVES_CREATED",
                "artifact_version": version,
                "artifact_zip": str(artifact_zip),
                "arxiv_source": str(arxiv_tar),
                "checksums": str(archive_sums),
                "git_tag_binding": (
                    "verified" if args.require_git_tag else "not requested"
                ),
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (
        OSError,
        KeyError,
        ValueError,
        tarfile.TarError,
        subprocess.CalledProcessError,
    ) as error:
        print(f"PACKAGING FAILED: {error}", file=sys.stderr)
        raise SystemExit(1) from error
