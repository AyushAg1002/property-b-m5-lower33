# Independent audit of the exact `m(5) >= 33` certificate

## Result

Both independent replay programs pass with exact rational arithmetic:

- `verify_v21_v22.py` checks all 3,081 emitted certificate records.  It
  independently regenerates the complete profile universes, evaluates every
  listed witness assignment, and checks the v=22 residual and Ramsey classes.
- `verify_lower33.py` independently regenerates the K4/K5 clique partitions
  and the v=23 profile universes.  It recomputes every v=23--25 certificate
  row, including the chosen assignment and reduced fraction, and matches all
  canonical JSON SHA-256 fingerprints in `theory/SELECTION_MANIFEST.json`.

No finite-computation mismatch was found.

## Release reproducibility controls

The independent reports are deterministic and repository-location neutral.
They omit timing and host data; the `canonical_manifest` field is the stable
relative path `theory/SELECTION_MANIFEST.json`.  Both verifiers accept a
`--report` destination, allowing the publication driver to write into a
temporary directory and compare the result byte-for-byte with the archived
report.  Both explicitly reject Python `-O/-OO`, so optimization cannot
discard their validation assertions.  The clean-release test relocates the
whitelisted artifact before replaying these checks.

## Independent coefficient derivation

Let `S` contain `s` locked vertices and let `f=v-s` vertices be randomly
permuted over the free slots.  If an edge has locked trace `A`, put
`q_A=5-|A|`.  For a free slot `k`, with `b` free slots before it and `a`
after it, direct counting gives

```text
P(k is the last point of an A-edge)
  = q_A/f * C(b,q_A-1)/C(f-1,q_A-1)
  = C(b,q_A-1)/C(f,q_A).
```

The reverse-order first-point coefficient replaces `b` by `a`.  For a
compatible ordered pair of edge types `A,B` whose common vertex occupies the
free slot, direct sequential placement gives

```text
1/f * C(b,q_A-1)/C(f-1,q_A-1)
    * C(a,q_B-1)/C(f-q_A,q_B-1).
```

At a locked slot belonging to selected vertex `i`, an `A`-edge with `i in A`
has all `q_A` random points before the lock with probability

```text
C(b,q_A)/C(f,q_A),
```

and the compatible ordered-pair coefficient is

```text
C(b,q_A) C(a,q_B) / (C(f,q_A) C(f-q_A,q_B)).
```

Multiplying the pair coefficient by
`l_A*l_B - 1[A=B]*l_A` is safe: it counts all distinct category pairs and may
include incompatible pairs, so it only enlarges the union bound.  Summing, at
each position, the minimum of the last-edge, first-edge, and paired-event
upper bounds yields the checked failure bound.  `verify_lower33.py` implements
these placement counts directly and does not import the canonical
`locked_bound` implementation.

## Exact replay results

```text
v=21: 1,864 profiles; maximum 9599/9724
v=22: 1,000 initial profiles; 997 closed; 3 residual
      Ramsey independent class: 2 profiles; maximum 91231/92378
      Ramsey triangle class: 215 profiles; maximum 456463/461890
v=23: residual counts 0,2,17; higher-lock maxima 8315/8398 and 45784/51051
v=24: six K4 trace partitions; maximum 16671/16796
v=25: seven favourable K5 trace partitions; maximum 4188/4199
```

The independent reports are:

- `logs/v21_v22_independent_verification.json`
- `logs/lower33_independent_verification.json`

## Structural adversarial audit

The non-computational selections in `theory/m32_to_m33_proof.md` were checked
separately:

- Padding and repeated noncoincident-pair identification preserve
  non-2-colourability and 5-uniformity, and terminate in a pair-covered core.
- The v=19 and v=20 zero-lock fractions recompute exactly as
  `222656/230945` and `20874/20995`.
- For v=22, the three residual rows force minimum degree seven; degree-sum
  arithmetic gives at least 16 degree-seven vertices, so `R(3,3)=6` supplies
  one of the two exhaustively checked classes.
- For v=23 with degree sequence `(6^2,7^20,8)`, the universal residual
  consequence gives all required codegrees one.  At least 17 degree-seven
  vertices lie outside the unique low-pair edge, and local excess six forces
  a codegree-one pair among them.
- For v=23 with degree sequence `(6,7^22)`, the residual consequence makes
  every codegree at most two.  The repeated-pair graph has degree sequence
  `(2,6^22)`; the stated Caro--Wei calculation gives an independent four-set
  outside the low vertex's two neighbours.
- For v=24, at least eight degree-six vertices induce a graph of maximum
  degree one, hence contain an independent four-set.
- For v=25, at least 15 degree-six vertices have all incident codegrees one.
  The K4 case and the covered-triple double count do force one of the seven
  checked favourable five-set traces.

No structural contradiction or missing case was found in this audit.  This
is an independent computational and adversarial check of the supplied proof,
not a substitute for external peer review.
