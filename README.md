# Exact artifact for a new lower bound on the fifth Property-B number

This repository is the complete computational artifact for the theorem

\[
m(5) \ge 33.
\]

Here `m(5)` is the minimum number of edges in a non-2-colourable
5-uniform hypergraph.  The published interval before this work was
`32 <= m(5) <= 51`; the theorem narrows it to `33 <= m(5) <= 51`.
The result is new research and has not yet completed journal peer review.

## Start here

- `output/pdf/property_b_m5_lower33.pdf` — submission-style manuscript.
- `paper/main.tex` — manuscript source.
- `theory/m32_to_m33_proof.md` — expanded proof with implementation details.
- `theory/README.md` — map of the exact certificate.
- `solver_alt/LOWER33_INDEPENDENT_AUDIT.md` — line-by-line structural audit.
- `optimization/OPTIMIZATION_AUDIT.md` — exact robustness and method-ceiling audit.
- `literature/novelty_audit_2026-08-23.md` — dated primary-source novelty review.

The proof is self-contained.  A padding-and-compression lemma reduces every
hypothetical obstruction with at most 32 edges to an exactly 32-edge,
pair-covered obstruction on 19 through 25 vertices.  Balanced random
colourings close orders through 18.  A zero-lock greedy bound, strengthened by
pair surplus at order 20, closes orders 19 and 20.  Exact locked-permutation
bounds and small selection lemmas close orders 21 through 25.

The finite part uses exact integers and rational arithmetic.  It does not
enumerate all hypergraphs and it does not rely on floating-point acceptance
tests.  The checked-in certificate contains 3,081 rows for orders 21 and 22;
the remaining orders are regenerated from compact trace partitions.

## Reproduce the lower bound

Run one command from the repository root:

```sh
python3 verify_lower33_artifact.py
```

This needs CPython 3.10 or newer and no third-party packages or network
access.  It verifies portable SHA-256 checksums, regenerates the compact
manifest, and runs both independent evaluators over every archived row.  Add
`--full` to also regenerate all 3,081 canonical witness choices in a temporary
directory and demand byte equality.  See `REPRODUCIBILITY.md` for the exact
protocol and expected rational endpoints.  Every canonical lower-bound
program that uses validation assertions rejects Python `-O/-OO`, because
those modes would remove the checks.  The separate optimization verifiers use
explicit exception guards and are deliberately rerun under `-O` as a safety
test.

The independent verifiers do not import the canonical evaluator.  They
rederive the probability coefficients, enumerate profiles through separate
code paths, reconstruct clique partitions, and compare all canonical row
hashes.  Their persisted JSON reports contain no timestamps, durations, host
names, absolute paths, or unordered serialization.

## Clean release artifact

The release whitelist is `release/lower33_manifest.json`.  Build it into a
new directory with:

```sh
python3 tools/build_lower33_release.py /path/to/new/release-directory
```

The clean layout is self-verifying and excludes all upper-bound searches,
obsolete lower-bound experiments, caches, binaries, and the 280 MB
interrupted radius-two SAT data.  After building, run the one-command verifier
again from inside the new directory.  `SHA256SUMS` uses a repository-relative
format checked by the portable standard-library program
`tools/verify_sha256.py`; GNU or BSD checksum utilities are not required.

The canonical archival object is the deterministic
`property_b_m5_lower33_artifact-v1.0.0.zip`, not GitHub's automatically
generated source archives.  The companion arXiv source tarball and the
external archive-checksum sidecar are also deterministic; exact names and
commands are recorded in `REPRODUCIBILITY.md`.  Journal-specific files under
`submission/ejc/` are operational handoff material and are deliberately not
part of the DOI-bearing proof artifact.

## Upper-bound search

The companion search under `solver_alt/` reconstructs and exhaustively
verifies the 51-edge Abbott--Hanson obstruction.  It also proves that none of
the 7,824,675 radius-one 50-edge repairs is an obstruction.  The bounded
radius-two runs ended `UNKNOWN`; their interrupted DRAT prefix is explicitly
not claimed as a proof.  No improvement of the upper bound is claimed.

## Release and submission status

The release metadata are recorded in `CITATION.cff`.  The public repository is
<https://github.com/AyushAg1002/property-b-m5-lower33>; release tag `v1.0.0`
and Zenodo DOI <https://doi.org/10.5281/zenodo.22070117> identify the archival
release.  Source code is licensed under MIT; the manuscript source, proof
notes, documentation, certificates, manifests and reports are licensed under
CC BY 4.0.  See `LICENSES/README.md`.

The author has recorded human verification of the mathematical and
computational claims and an independent combinatorics review.  Journal peer
review remains essential, especially for the normalization lemma and the
finite-case interface.

The E-JC-oriented initial-submission materials are under `submission/ejc/`.
They include the standalone HTML abstract, final author metadata and editor
note, a human-verification-record template, and a fail-closed readiness
checker.  Run `python3 submission/ejc/check_readiness.py` only after the
responsible author completes the final human record and the release archives
and checksums are frozen.  A passing mechanical check does not certify the
truth of the human attestations.
