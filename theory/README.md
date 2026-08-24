# Exact lower-bound certificate for `m(5) >= 33`

This directory contains a research-grade exact certificate excluding every
non-2-colourable 5-uniform hypergraph with at most 32 edges.

The mathematical proof is in `m32_to_m33_proof.md`.  Its normalization is
self-contained: pad any at-most-32-edge counterexample to 32 edges, identify
a noncoincident vertex pair, discard duplicate images, repad, and repeat.
This yields an exactly-32-edge pair-covered core without assuming the prior
published lower bound.

Primary artifacts:

* `locked_greedy_32.py` — exact general locked-permutation bound;
* `close_v21_v22.py` and `certificates/` — all `v=21,22` profile records;
* `selection_certificates.py` and `SELECTION_MANIFEST.json` — `v=23,24,25`
  trace/profile certificates;
* `../solver_alt/verify_lower33.py` and `verify_v21_v22.py` — independent
  exact implementations and replays;
* `../solver_alt/LOWER33_INDEPENDENT_AUDIT.md` — structural and coefficient
  audit.

For the publication artifact, run from the repository root:

```sh
python3 verify_lower33_artifact.py
```

This independently evaluates every archived row without rewriting the
certificate or reports.  Add `--full` to regenerate the canonical files in a
temporary directory and require byte equality.  See `../REPRODUCIBILITY.md`
for the decomposed commands and expected results.

All acceptance comparisons use `fractions.Fraction`.  The two independent
replays passed and matched every canonical row hash.  This package is meant
to support, not replace, external mathematical peer review of a new bound.

All lower-bound proof scripts refuse execution under Python `-O/-OO`; their
validation assertions therefore cannot be silently disabled.

The older `enumerate_reductions.py` targeted the superseded value 29 and is
retained only as clearly labelled historical scratch work.
