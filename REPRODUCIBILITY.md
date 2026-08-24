# Reproducibility protocol

## Environment

The lower-bound artifact uses only the Python standard library.  It requires
CPython 3.10 or newer and no network access, compiler, SAT solver, or
third-party package.  It was release-tested with CPython 3.13.1 on macOS.
All paths are resolved relative to the repository, and all mathematical
comparisons use integers or `fractions.Fraction`.

Do not invoke the canonical lower-bound programs with `python -O` or
`python -OO`.  The five programs containing validation assertions explicitly
reject those modes so optimization cannot silently remove a check.  Programs
under `optimization/` instead use explicit exception guards for every
proof-critical condition; the release driver intentionally reruns their
critical paths under `python -O`.

## One-command verification

From the artifact root, run:

```sh
python3 verify_lower33_artifact.py
```

The default independent-replay run performs the following checks:

1. validates every whitelisted file against `SHA256SUMS`;
2. runs the exact one-lock regression checks;
3. regenerates the compact `v=23,24,25` manifest;
4. independently evaluates every row in the 3,081-row `v=21,22` certificate;
5. runs the structurally separate `v=23,24,25` evaluator into a temporary
   report;
6. reruns the exact `v=21` menu/subset audits and both forced `v=25` ceiling
   branches under optimized Python; and
7. requires every regenerated manifest, record file, and report to equal the
   pinned files.

The optimization audit checks all 64 subsets of the six candidate `v=21`
bases.  Its best three-base worst value is `4805/4862`, strictly above the
four-base target `9599/9724`; hence cardinality four is minimal within that
candidate family.  It also certifies the forced 33-edge `v=25` ceiling values
`8649/8398` for `10K2` and `325/323` for `K4+4K2`.  These are scoped method
ceilings, not counterexamples and not a proof that `m(5)=33`.

The one-command driver covers the lower-bound theorem and every
proof-critical optimization claim used by the manuscript.  It does not
regenerate the broader optional orbit tables in `OPTIMIZATION_AUDIT.md`;
their pinned source driver can be run separately with
`python3 -O optimization/frontier_audit.py --output /tmp/optimization_results.json`.
That broader table is diagnostic and is not needed for the theorem or the two
forced `v=25` ceiling branches.

For the archival full-provenance pass, which additionally regenerates all
canonical witness choices into a temporary directory and requires both files
to be byte-identical to the archive, run:

```sh
python3 verify_lower33_artifact.py --full
```

The command exits nonzero on the first failed computation.  A successful run
ends with `ALL_LOWER33_ARTIFACT_CHECKS_PASSED`.  Wall-clock time is reported
to the terminal but is never stored in a checksummed artifact.

Runtime is hardware-dependent.  The independent-replay mode is intended for
referees and clean-clone tests.  Full mode is substantially slower because it
searches every allowed position menu to reconstruct the canonical witness for
each profile; it is intended for archival provenance, not a partial timeout.

## Expected exact endpoints

```text
v=21: 1,864 profiles; maximum 9599/9724
v=22: 1,000 profiles; 997 direct, 3 residual
      independent class maximum 91231/92378
      triangle class maximum 456463/461890
v=23: maxima 8315/8398 and 45784/51051
v=24: maximum 16671/16796
v=25: maximum 4188/4199
```

## Build a clean release

The command below copies only files whitelisted by
`release/lower33_manifest.json`:

```sh
python3 tools/build_lower33_release.py /path/to/new/release-directory
```

The output deliberately excludes compiled binaries, Python caches, obsolete
`m(5)>=29` experiments, all upper-bound searches, and the 280 MB interrupted
radius-two CNF/DRAT files.  Run `python3 verify_lower33_artifact.py` again from
inside the resulting directory before archiving it or minting a DOI.

After the manuscript and metadata are frozen, create deterministic reviewer
and arXiv archives with:

```sh
python3 tools/verify_sha256.py SHA256SUMS \
  --write-from-release-manifest release/lower33_manifest.json
python3 tools/package_lower33_release.py \
  --output-dir tmp/release_candidate_v1
```

The checksum write is atomic, follows the release-whitelist order, and then
verifies all 47 hashed members.  Packaging refuses to overwrite an existing
versioned archive, validates `SHA256SUMS` before and after clean staging,
normalizes archive order, timestamps, ownership, and permissions, constructs
each archive twice and requires byte equality.  The candidate command writes
`tmp/release_candidate_v1/property_b_m5_lower33_artifact-v1.0.0.zip` plus
`tmp/release_candidate_v1/property_b_m5_lower33_arxiv-v1.0.0.tar.gz`, with both
hashes recorded in
`tmp/release_candidate_v1/property_b_m5_lower33_archives-v1.0.0.sha256`.
After the remote tag exists, a strict tag-bound build from a standalone clean
checkout may instead use the default `release/` directory together with
`--require-git-tag`.

The deterministic artifact ZIP is the canonical DOI-bearing proof object.
GitHub's automatically generated tag archives are convenient mirrors but are
not substitutes for that ZIP.  Journal-specific files under `submission/ejc/`
are intentionally outside the proof whitelist.
