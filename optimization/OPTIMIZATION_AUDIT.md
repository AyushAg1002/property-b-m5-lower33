# Locked-permutation optimization audit at 32 and 33 edges

## Scope and verdict

This directory asks a deliberately narrower question than the main proof:
after optimizing **every allowed locked position**, can the exact
locked-permutation certificate exclude a pair-covered 33-edge obstruction,
or materially strengthen the narrowest 32-edge certificates?

The result is two-sided.

1. The 32-edge proof can be made less numerically brittle.  A four-base menu
   improves the complete `v=21` profile sweep from `12148/12155` to
   `9599/9724`, and one added four-lock base improves the relevant `v=23`
   maximum from `4194/4199` to `8315/8398`.
2. Position optimization alone cannot promote the existing argument to 33
   edges.  Complete all-placement searches leave a three-lock residual at
   every `v=20,...,25`.  More decisively, the two non-`K5` outcomes forced by
   the existing `v=25` selection argument have exact global minima

   ```text
   10K2:       8649/8398 > 1,
   K4 + 4K2:    325/323  > 1.
   ```

Thus the defensible theorem remains `m(5) >= 33`.  This audit does **not**
show that `m(5)=33`, that a 33-edge obstruction exists, or that every possible
five-lock selection rule fails.  It gives a precise ceiling for the current
trace-product bound and the current `v=25` structural selection lemma.

All acceptance comparisons below use `fractions.Fraction`.  Floating point
was used once for a preliminary screen of subsets of a proposed `v=21`
position menu.  That screen has now been superseded by an archived exact
check of all 64 subsets, with pinned profile/base rows and direct-evaluator
checks at every subset extremum.

## 1. Independent implementation and search-space identity

The optimization code is isolated from the canonical proof code.

- `general_locked.py` reimplements the locked-permutation formulas with the
  edge count as an explicit parameter.  Its self-test reproduces five pinned
  fractions from the canonical evaluator, including both zero-lock values.
- `compiled_locked.py` compiles the linear last/first events and quadratic
  paired event to common-denominator integer polynomials.  It is cross-checked
  against `general_locked.py` for one, three, and four locks.
- `state_optimizer.py` uses the exact state identity described next to search
  every labelled placement efficiently.
- `trace_partitions.py` independently regenerates the six labelled clique
  partitions of `K4` and the 32 labelled clique partitions of `K5`.

For fixed trace counts, the contribution at a free position depends only on

```text
(the mask of locks already passed, the number of free positions already passed),
```

and at a locked position it additionally depends on the current lock label.
Consequently a labelled position assignment is represented uniquely by

```text
(an order of the s lock labels, a weak composition of v-s into s+1 gaps).
```

There are

```text
s! * C(v,s) = v!/(v-s)!
```

such representations, exactly the number of labelled injections into the
`v` positions.  `state_optimizer.py` computes each exact state cost once,
scales all state costs to a common integer denominator, and enumerates these
orders and gap vectors.  It quotients lock orders only by automorphisms of the
complete trace table and records both the quotient count and the unquotiented
number covered.

The complete labelled position spaces used here are:

| locks | `v=20` | `v=21` | `v=22` | `v=23` | `v=24` | `v=25` |
|---:|---:|---:|---:|---:|---:|---:|
| 3 | 6,840 | 7,980 | 9,240 | 10,626 | 12,144 | 13,800 |
| 4 | — | — | — | 212,520 | 255,024 | 303,600 |
| 5 | — | — | — | 4,037,880 | 5,100,480 | 6,375,600 |

## 2. What 33 edges can still exclude immediately

Padding and pair compression work with 33 in place of 32.  A pair-covered
33-edge core has `v <= 26`.  Balanced-colouring counting excludes `v <= 18`.

At `v=19`, total pair-incidence surplus is

```text
R = 10*33 - C(19,2) = 159.
```

At least `ceil(159/6)=27` unordered edge pairs meet in at least two vertices,
so the number `gamma` of ordered edge pairs with intersection exactly one is
at most

```text
33*32 - 2*27 = 1002.
```

The exact zero-lock evaluation is

```text
U0(19,1002) = 228291/230945 < 1.
```

At `v=26`, pair coverage forces minimum degree seven, but

```text
26*7 = 182 > 5*33 = 165.
```

Hence a 33-edge proof needs to handle exactly `v=20,...,25`.

## 3. Complete three-lock ceilings for 33 edges

The safe-superset enumeration for the three smallest degrees contains 4,799,
3,151, 1,000, 1,000, 192, and 192 profiles for `v=20,...,25`, respectively.
For each `v`, the following row is a member of that complete superset and was
minimized over **every** labelled three-lock placement.

Counts are in mask order `000,001,010,011,100,101,110,111`.

| `v` | selected degrees | trace counts | global minimum | one minimizer |
|---:|---|---|---:|---|
| 20 | `(8,8,8)` | `(15,4,4,2,4,2,2,0)` | `2287/2210` | `(1,2,12)` |
| 21 | `(7,7,7)` | `(15,5,5,1,5,1,1,0)` | `119365/116688` | `(1,2,3)` |
| 22 | `(7,7,7)` | `(15,5,5,1,5,1,1,0)` | `387055/369512` | `(1,2,3)` |
| 23 | `(7,7,7)` | `(15,5,5,1,5,1,1,0)` | `10671/9880` | `(1,2,3)` |
| 24 | `(6,6,6)` | `(19,4,4,0,4,0,0,2)` | `89966/88179` | `(1,12,14)` |
| 25 | `(6,6,6)` | `(19,4,4,0,4,0,0,2)` | `25888/24871` | `(1,13,15)` |

Every displayed fraction exceeds one.  Therefore no finite menu of
three-lock positions can close the complete safe-superset enumeration at any
remaining vertex count.  These rows are not asserted to be globally
realisable hypergraphs; they establish the ceiling of the three-lock profile
relaxation.  Further progress requires structural selection beyond these
profiles, sharper compatible-pair counts, or another colouring argument.

## 4. Four- and five-lock trace orbits at 33 edges

If every selected pair has codegree one, non-singleton traces form a clique
partition.  Up to relabelling, the six labelled `K4` partitions have three
types and the 32 labelled `K5` partitions have five types.

### 4.1 Four degree-six locks

Each entry is the exact minimum over every labelled placement for a canonical
representative; relabelling gives the same value throughout its orbit.

| `v` | `6K2` | `K3+3K2` | `K4` |
|---:|---:|---:|---:|
| 23 | `4227/4199` | `4221/4199` | `4263/4199` |
| 24 | `8535/8398` | `17217/16796` | `4298/4199` |
| 25 | `9441/9044` | `4715/4522` | `92290/88179` |

All nine exact minima exceed one.  Thus four pair-codegree-one degree-six
locks do not close any of these 33-edge trace orbits at `v=23,24,25`.

### 4.2 Five degree-six locks

The five `K5` trace orbits have sizes 1, 10, 5, 15, and 1 among the 32
labelled partitions.

| trace type | orbit size | `v=23` | `v=24` | `v=25` |
|---|---:|---:|---:|---:|
| `10K2` | 1 | `1863/1870` | `8535/8398` | `8649/8398` |
| `K3+7K2` | 10 | `12081/12155` | `8511/8398` | `17373/16796` |
| `K4+4K2` | 5 | `11758/12155` | `4213/4199` | `325/323` |
| `2K3+4K2` | 15 | `4831/4862` | `8511/8398` | `17343/16796` |
| `K5` | 1 | `4515/4862` | `8071/8398` | `8071/8398` |

An unexpected positive result is that all five orbits close at `v=23`; the
worst is `1863/1870`.  This does not exclude `v=23`, because the 33-edge
degree sum does not force five degree-six vertices.  At `v=24` and `v=25`,
only the single-`K5` orbit closes; all other orbits remain above one.

At `v=25`, the degree-six set has size at least ten and every pair incident
with it has codegree one.  The existing 32-edge selection argument forces
either `10K2`, `K4+4K2`, or `K5`.  At 33 edges its two non-`K5` branches have
global minima above one.  Hence **no enlargement of the locked-position menu
can upgrade that selection argument**.

This last statement is independently checked by
`verify_v25_selection_ceiling.py`.  For `10K2`, full `S5` symmetry reduces the
search to 53,130 unordered position sets, representing all 6,375,600 labelled
placements.  Its exact row hash is

```text
1ad597008faafc801ebda73698880b6bd4a390e2a3b62341743321f5de236850
```

For a representative `K4+4K2` table, automorphism group 24 reduces the search
to 265,650 order/gap rows, again representing all 6,375,600 placements.  The
five labelled tables are one relabelling orbit.  Its exact row hash is

```text
33724380a6ebb4691f8e50f7a362031edbf69ab7a2c3706aa55c893709d9fd05
```

Both minima are independently re-evaluated by the direct generalized
evaluator at their reported assignments.  Every proof-critical guard in
this verifier is an explicit exception check and remains active under
`python -O`.

## 5. Exact robustness improvements for the 32-edge proof

### 5.1 `v=21`: four bases suffice

The original two position bases are

```text
(10,11,12), (1,2,3).
```

The exact candidate universe is the following six bases:

```text
B0=(10,11,12), B1=(1,2,3),     B2=(11,12,13),
B3=(1,11,13),  B4=(1,2,12),    B5=(1,12,14).
```

`verify_m32_v21_base_subsets.py` checks all `2^6=64` subsets, including an
explicit no-certificate record for the empty subset.  For each nonempty
subset it examines all 1,864 safe profiles and all six label assignments to
every included base, using exact compiled integer-polynomial kernels.  The
underlying table contains 11,184 exact profile/base certificates obtained
from 67,104 profile/assignment evaluations.  A direct independently written
evaluator agrees at the worst profile of every one of the 63 nonempty
subsets.

The best exact worst value among all three-base subsets is

```text
4805/4862 = 0.988276...
```

attained by base-index sets `{0,1,2}` and `{1,2,3}`.  Since
`4805/4862 > 9599/9724`, no three-base subset attains the four-base target.
The minimum attaining cardinality in this six-base family is therefore
exactly four.  The selected four-base set is

```text
(10,11,12), (1,2,3), (11,12,13), (1,2,12).
```

All six label assignments to every base are allowed.  The exact worst value
improves from

```text
12148/12155 = 0.999424...
```

to

```text
9599/9724 = 0.987145...
```

at degrees `(7,7,7)`, trace counts `(15,5,4,1,4,1,2,0)`, and assignment
`(1,2,12)`.  The complete 1,864-row hash is

```text
dd41903f21f585c7dd2cf83b33f8035763a8b47586339e33b5457408e8dd2b4d
```

The selected unordered-base counts were 1,066, 2, 3, and 793 in the order
displayed.  The two rarely selected bases are nevertheless necessary to
retain this exact worst value within the exact candidate-family audit.

The pinned SHA-256 of the 11,184 canonical profile/base rows is

```text
647cf59a810ec84dd036cad482e3b9c219c62ca9591adb37de79157ca8f54e9f
```

and the exact 64-subset summary, before adding its self-hash field, has

```text
5f80b112a2679d9fbfd9cb0a7012fddd0c7fc71c83048b2eaee782ef014f9c91.
```

### 5.2 `v=23`: one shifted four-lock base helps

For the three allowed `(6,6,7,7)` clique-partition rows whose low pair has a
separate `K2` trace, complete all-placement optimization gives

| trace type | global minimum | one minimizing assignment |
|---|---:|---|
| `6K2` | `8315/8398` | `(12,13,14,15)` |
| first `K3+3K2` labelling | `4152/4199` | `(11,12,13,14)` |
| second `K3+3K2` labelling | `4152/4199` | `(12,11,13,14)` |

Adding base `(12,13,14,15)` to the existing central base therefore reduces
the family maximum from `4194/4199` to `8315/8398`.

### 5.3 The later bottlenecks are already position-optimal

At `v=24`, the global minima of the three degree-six `K4` orbits are

```text
6K2: 243/247,  K3+3K2: 16671/16796,  K4: 8323/8398.
```

Thus the existing worst value `16671/16796` is globally position-optimal.

At `v=25`, the three favourable five-lock rows used by the proof have global
minima

```text
10K2: 4188/4199,  K4+4K2: 37/38,  K5: 3899/4199.
```

Again the existing bottleneck `4188/4199` is globally position-optimal.  Of
the two unused `K5` trace orbits, `2K3+4K2` closes at `20953/20995`, while
`K3+7K2` remains above one even at 32 edges, with exact global minimum
`16827/16796`.  This confirms that the favourable-set selection step is
structurally essential, not merely a shortcut around a poor position menu.

## 6. Reproduction commands and observed runtimes

Run from `property_b_m5/optimization`:

```sh
python3 -O general_locked.py
python3 -O compiled_locked.py
python3 -O state_optimizer.py
python3 -O trace_partitions.py
PYTHONPATH=. python3 -O verify_v25_selection_ceiling.py \
  --output v25_selection_ceiling_verification.json
PYTHONPATH=. python3 -O sweep_m32_v21_menu.py \
  --summary m32_v21_menu_summary.json \
  --records m32_v21_menu_records.jsonl
PYTHONPATH=. python3 -O verify_m32_v21_base_subsets.py \
  --summary m32_v21_base_subsets_summary.json \
  --records m32_v21_six_base_profiles.jsonl
```

On the audit machine, the independent two-branch `v=25` verifier used 8.50
CPU seconds (139.27 elapsed under the managed runner), while the complete
`v=21` four-base sweep used 10.20 CPU seconds (154.75 elapsed).  The unusual
elapsed/CPU ratio is scheduler time, not computation hidden from the report.
The final optimized-mode all-subset rerun used 14.26 CPU seconds (100.26
elapsed), checked its pinned row hash, and reproduced `4805/4862` as the best
three-base worst value.

`frontier_audit.py` is the slower full-orbit regeneration driver for all
tables in Sections 3--5.  It uses explicit `RuntimeError` acceptance guards,
checks every reported minimizer against `general_locked.locked_bound`, and
checks that the automorphism quotient covers the full labelled placement
count.  It can be run as

```sh
PYTHONPATH=. python3 -O frontier_audit.py --output optimization_results.json
```

The three smaller proof-critical verifiers above are preferred for release CI.

## 7. Precise ceiling statement for a paper

The following wording is supported by the exhaustive data:

> Complete optimization over the locked positions does not extend our
> `v=25` selection argument from 32 to 33 edges.  For the 33-edge trace table
> consisting of ten separate pair traces, the minimum of the exact
> locked-permutation bound over all labelled placements is `8649/8398`.
> For each of the five labelled `K4+4K2` trace tables, the corresponding
> minimum is `325/323`.  Hence neither of the two non-`K5` outcomes forced by
> the 32-edge selection lemma yields a strict certificate at 33 edges,
> regardless of the position menu.

It is important to append:

> This is a limitation of the present trace-product bound and selection
> lemma.  It does not preclude a sharper compatible-edge-pair count, a
> different selected set, six or more locks, or another colouring method.
