# An exact locked-permutation exclusion of a 32-edge Property-B obstruction

## Status and scope

Let \(m(5)\) be the least number of edges in a simple 5-uniform hypergraph
with no proper two-colouring.  Grill and Linzmayer state the previously best
lower bound

\[
m(5)\ge 32
\]

as Theorem 1 of arXiv:2403.05674v3.  The argument and exact finite
certificates below exclude every obstruction with at most 32 edges and hence
give

\[
\boxed{m(5)\ge 33}.
\]

This proof is self-contained with respect to the earlier numerical lower
bound: its padding-and-compression reduction converts any counterexample
with at most 32 edges to an exactly-32-edge pair-covered core.  It therefore
does **not** rely on the undocumented three-locked-vertex computation behind
the paper's 31-edge exclusion.  The paper remains the primary source for the
greedy method and for the previous state of the art.  Its reproducibility
gap is relevant historical context, not a hypothesis of the theorem below.

Primary source: [Grill--Linzmayer, *Improved Lower Bounds for Property B*,
arXiv:2403.05674v3](https://arxiv.org/abs/2403.05674), with the displayed
greedy formulae available in the [HTML version](https://arxiv.org/html/2403.05674).

All finite comparisons in the attached programs use Python integers and
`fractions.Fraction`.  There is no floating-point acceptance test.

## 1. Normal form for a hypothetical obstruction

Assume for contradiction that \(H\) is a non-two-colourable simple
5-uniform hypergraph with at most 32 edges.

### 1.1 Pair-cover reduction

Every 5-uniform hypergraph on at most eight vertices is two-colourable:
split its vertices into two classes of size at most four.  Thus \(v(H)\ge9\).
Since \(\binom95=126>32\), add distinct 5-edges until \(H\) has exactly 32
edges.  Adding constraints preserves non-two-colourability.

Now, after this padding, suppose vertices \(x,y\) occur together in no edge.
Identify \(x\) and \(y\), and discard duplicate edge images.

* No image edge loses a vertex, because no original edge contains both
  \(x\) and \(y\); every image edge still has size five.
* A two-colouring of the simple quotient pulls back to a two-colouring of
  \(H\), assigning the quotient colour to both \(x\) and \(y\).  Thus the
  quotient remains non-two-colourable.
* The simple quotient has at most 32 edges.  If it has at most eight
  vertices, the preceding balanced split is a contradiction.  Otherwise it
  has at least nine vertices, so it can again be padded with distinct
  5-edges to exactly 32 while remaining non-two-colourable.

After every padding step, either the new hypergraph is already pair-covered
or choose a noncoincident pair in that padded hypergraph and merge it.  Each
merge decreases the vertex count.  Iteration must therefore give a 32-edge
simple non-two-colourable core in which every vertex pair occurs in an edge;
termination at eight vertices would already be a contradiction.  We replace
\(H\) by this padded core.  If \(v\) is its vertex count and
\(\lambda_{xy}\) its pair codegrees, then

\[
\lambda_{xy}\ge1,\qquad
\binom v2\le32\binom52=320,
\]

so \(v\le25\).

Balanced-colouring counting excludes \(v\le18\):

\[
m(5,v)\ge
\frac{\binom v5}
{\binom{\lfloor v/2\rfloor}5+\binom{\lceil v/2\rceil}5}.
\]

For \(10\le v\le18\), the rounded-up values are respectively
\(126,66,66,48,48,39,39,34,34\); for \(v\le9\) the same balanced-colour
argument is immediate.  Hence initially \(19\le v\le25\).

### 1.2 The unconditioned greedy exclusions at 19 and 20 vertices

Let \(\gamma\) be the number of **ordered** pairs of distinct edges whose
intersection has size exactly one.  The discrete greedy bound, the
zero-lock special case of the locked-permutation lemma below, is

\[
U_0(v,\gamma)=\sum_{k=1}^{v}\frac1v\min\!\left\{
160\frac{\binom{k-1}4}{\binom{v-1}4},
160\frac{\binom{v-k}4}{\binom{v-1}4},
\gamma\frac{\binom{k-1}4\binom{v-k}4}
{\binom{v-1}4\binom{v-5}4}
\right\}.
\]

At \(v=19\), using \(\gamma\le32\cdot31=992\), exact evaluation gives

\[
U_0(19,992)=\frac{222656}{230945}<1.
\]

For \(v=20\), define the total pair-incidence surplus

\[
R=\sum_{x<y}(\lambda_{xy}-1)=320-\binom{20}{2}=130
\]

and

\[
Q=\sum_{x<y}\binom{\lambda_{xy}}2.
\]

Because \(\binom t2\ge t-1\) for \(t\ge1\), \(Q\ge R\).  Also

\[
Q=\sum_{\{e,f\}}\binom{|e\cap f|}{2}.
\]

Two distinct 5-edges meet in at most four points, so each unordered edge
pair meeting in at least two points contributes at most six to \(Q\).
There are therefore at least \(\lceil130/6\rceil=22\) such unordered pairs,
and

\[
\gamma\le992-2\cdot22=948.
\]

Substitution gives the strict exact certificate

\[
U_0(20,948)=\frac{20874}{20995}<1.
\]

Thus only

\[
21\le v\le25
\tag{1}
\]

remains.

### 1.3 Degree and local-excess identities

For every vertex \(x\), pair coverage and incidence counting give

\[
d(x)\ge\left\lceil\frac{v-1}{4}\right\rceil,
\qquad
\sum_xd(x)=5\cdot32=160,
\]

and

\[
\sum_{y\ne x}\lambda_{xy}=4d(x).
\]

It is useful to record the exact local pair excess

\[
\rho_x:=\sum_{y\ne x}(\lambda_{xy}-1)
=4d(x)-(v-1).
\tag{2}
\]

As an ancillary fact, an edge-minimum counterexample to any Property-B lower
bound is edge-critical: deleting any edge leaves a two-colourable
hypergraph, and in every proper colouring after that deletion the restored
edge is the unique monochromatic edge.  The padded core need not inherit
edge-criticality, and no later step assumes that it does.

## 2. The general locked-permutation lemma

This section derives every coefficient used by the exact evaluator.

Choose an ordered set of locked vertices
\(S=(s_1,\ldots,s_s)\), where \(0\le s\le5\) and \(f:=v-s\ge9\), and
distinct positions \(p_1,\ldots,p_s\in\{1,\ldots,v\}\).  The other \(f\)
vertices are assigned uniformly at random to the free positions.  For
\(A\subseteq[s]\), let

\[
l_A=|\{e\in E(H):e\cap S=\{s_i:i\in A\}\}|.
\]

For a position \(k\), let \(b=b(k)\) and \(a=a(k)\) be the numbers of free
positions before and after \(k\).  Write \(A\prec k\) when every lock in
\(A\) is before \(k\), and \(A\succ k\) when every lock in \(A\) is after
\(k\).  Binomial coefficients outside their natural range are zero, and an
impossible term is omitted.

Run Pluhár's greedy procedure: initially colour every vertex red; process
the permutation, and turn the current vertex blue if it is the last vertex
of an otherwise-red edge.  A red edge cannot remain at the end.  If a blue
edge remains, take its earliest vertex \(x\).  Vertex \(x\) was turned blue
because it was last in a red witness edge, while all other points of the
blue edge occur after \(x\).  Consequently the two witness edges intersect
exactly in \(x\).  Call such an \(x\) critical.

### 2.1 A free position

Suppose \(k\) is free.  For an edge of type \(A\), there are
\(5-|A|\) free edge vertices.  If \(A\prec k\), the probability that the
occupant of \(k\) is one of them and all the other free edge vertices are
before \(k\) is

\[
\frac{5-|A|}{f}
\frac{\binom b{4-|A|}}{\binom{f-1}{4-|A|}}.
\]

The first factor chooses the occupant; conditional on it, the second puts
the other \(4-|A|\) free vertices among the \(b\) earlier free slots.
A union bound over edges therefore gives

\[
L_k=\sum_{\substack{A\prec k\\|A|\le4}}l_A\frac{5-|A|}{f}
\frac{\binom b{4-|A|}}{\binom{f-1}{4-|A|}}.
\tag{3}
\]

Reversing the order gives

\[
F_k=\sum_{\substack{A\succ k\\|A|\le4}}l_A\frac{5-|A|}{f}
\frac{\binom a{4-|A|}}{\binom{f-1}{4-|A|}}.
\tag{4}
\]

For a simultaneous last-edge of type \(A\) and first-edge of type \(B\),
the locked types must be disjoint.  Put
\(r_A=4-|A|\), \(r_B=4-|B|\).  A fixed compatible ordered edge pair has
probability

\[
\frac1f
\frac{\binom b{r_A}}{\binom{f-1}{r_A}}
\frac{\binom a{r_B}}{\binom{f-1-r_A}{r_B}}.
\]

There are at most
\(l_Al_B-\mathbf1_{A=B}l_A\) distinct ordered edge pairs of the two types.
This product also counts pairs that do not intersect exactly once; treating
each of those as if it were compatible only increases the union bound.
Thus

\[
B_k=\sum_{\substack{A\cap B=\varnothing\\A\prec k,\ B\succ k\\
|A|,|B|\le4}}
\left(l_Al_B-\mathbf1_{A=B}l_A\right)
\frac{\binom b{4-|A|}\binom a{4-|B|}}
{f\binom{f-1}{4-|A|}\binom{f-1-(4-|A|)}{4-|B|}}.
\tag{5}
\]

Trace classes of size five have no free vertex and hence are absent from
all three free-position sums.

The diagonal subtraction excludes using the same edge twice.  Under the
disjointness condition it is nonzero only for \(A=B=\varnothing\), but the
uniform formula is convenient.

### 2.2 A locked position

Now let \(k=p_i\).  Only types \(A\ni i\) can use \(s_i\) as critical
vertex.  An edge of type \(A\) has \(5-|A|\) free points.  Therefore

\[
L_k=\sum_{\substack{i\in A\\A\setminus\{i\}\prec k}}
l_A\frac{\binom b{5-|A|}}{\binom f{5-|A|}},
\qquad
F_k=\sum_{\substack{i\in A\\A\setminus\{i\}\succ k}}
l_A\frac{\binom a{5-|A|}}{\binom f{5-|A|}}.
\tag{6}
\]

For the paired event the locked intersections must meet exactly at \(i\).
The red and blue free vertices are disjoint, so

\[
B_k=\sum_{\substack{A\cap B=\{i\}\\
A\setminus\{i\}\prec k,\ B\setminus\{i\}\succ k}}
\left(l_Al_B-\mathbf1_{A=B}l_A\right)
\frac{\binom b{5-|A|}\binom a{5-|B|}}
{\binom f{5-|A|}\binom{f-(5-|A|)}{5-|B|}}.
\tag{7}
\]

Again the category product is a safe upper bound on the number of actual
ordered pairs whose unique intersection is \(s_i\).

### 2.3 Conclusion and adaptivity

Criticality at position \(k\) is contained in each of the last-edge,
first-edge and paired events.  Hence

\[
\Pr(k\text{ is critical})\le\min\{L_k,F_k,B_k\}.
\]

A final union bound gives

\[
\Pr(\text{greedy failure})\le
Q(H,S,p):=\sum_{k=1}^v\min\{L_k,F_k,B_k\}.
\tag{8}
\]

Therefore \(Q<1\) proves that \(H\) is two-colourable.

The selection may be adaptive in the following precise sense.  After
inspecting the fixed hypergraph and its trace profile, choose \(S\) and its
position assignment deterministically; only then randomise the remaining
vertices.  A different profile may use a different assignment.  No union
bound over the possible selections or assignments is required.

Equations (3)--(7) are implemented literally by
`locked_greedy_32.py`.  As one-lock regression checks it returns

\[
(v,d)=(20,5):\frac{22953}{24310},\quad
(21,6):\frac{4179}{4199},\quad
(25,6):\frac{223777}{208012}.
\]

## 3. The finite profile and trace enumerations

For three selected vertices, counts are stored in mask order

\[
(l_{000},l_{001},l_{010},l_{011},l_{100},l_{101},l_{110},l_{111}).
\]

Given degrees \((d_1,d_2,d_3)\), `category_profiles` loops over the triple
count and three pair-only counts, derives the singleton counts from the
three degree equations, derives \(l_{000}\) from the total of 32 edges, and
keeps all nonnegative solutions with each selected pair covered.  It imposes
no unproved realisability assumption, so it is a safe superset of profiles
arising from a pair-covered hypergraph.

We also use the following trace observation.  If every pair in a selected
set \(S\) has codegree exactly one, then the traces \(e\cap S\) of size at
least two partition \(E(K_S)\) into clique edge sets.  Indeed, a trace
\(T\) contributes precisely the pairs in \(\binom T2\); every selected pair
occurs once, so these clique edge sets are disjoint and exhaustive.
Conversely, once such a clique partition and the selected degrees are
fixed, the singleton trace counts and then the empty trace count are forced.

`clique_partitions` is a complete recursive generator: it takes the first
uncovered pair and branches over every clique containing that pair and no
already-covered pair.  It generates six labelled partitions of \(K_4\)
and 32 labelled partitions of \(K_5\).  The \(K_4\) partitions have exactly
the three types

\[
K_4,\qquad K_3+3K_2,\qquad 6K_2.
\]

If a \(K_4\) block is absent but a triangle is present, no remaining pair
can join another remaining pair into a triangle without reusing an edge of
the first triangle; hence its other three blocks are single pairs.  This
also proves the displayed classification directly.

## 4. Excluding \(v=21\)

Let \(d_1\le d_2\le d_3\) be the three smallest degrees.  Pair coverage and
the degree sum imply

\[
d_1\ge5,\qquad d_1+d_2+19d_3\le160.
\]

The complete integer list is

\[
\begin{split}
&(5,5,5),(5,5,6),(5,5,7),(5,6,6),(5,6,7),\\
&(5,7,7),(6,6,6),(6,6,7),(6,7,7),(7,7,7).
\end{split}
\]

These give 1,864 safe-superset category profiles.  For every profile the
certificate checks all label assignments to one of the four position bases

\[
(10,11,12),\quad(1,2,3),\quad(11,12,13),\quad(1,2,12).
\]

All 1,864 profiles have \(Q<1\); the largest chosen bound is

\[
\frac{9599}{9724}<1.
\]

For orientation, the two profiles not closed by central positions alone are

\[
(13,6,6,0,6,0,0,1),\quad
(14,5,5,1,5,1,1,0).
\]

The first-three-position assignment closes them with bounds
\(4351/4488\) and \(113351/116688\), respectively.  The full record for
every profile, including its selected placement and exact fraction, is
emitted by `close_v21_v22.py`.

## 5. Excluding \(v=22\)

Now

\[
d_1\ge6,\qquad d_1+d_2+20d_3\le160,
\]

so the complete degree-triple list is

\[
(6,6,6),(6,6,7),(6,7,7),(7,7,7).
\]

The resulting safe superset has 1,000 profiles.  All label assignments to
the following five position bases are allowed:

\[
(10,11,12),(1,2,3),(1,2,11),(1,2,13),(1,11,13).
\]

Exactly 997 profiles have a direct strict certificate.  The only three
residual profiles are the three labelings

\[
\begin{split}
&(15,4,4,2,5,1,1,0),\\
&(15,4,5,1,4,2,1,0),\\
&(15,5,4,1,4,1,2,0).
\end{split}
\]

In each, the selected degrees are \((7,7,7)\), the pair-codegree multiset is
\((1,1,2)\), and \(l_{111}=0\).  Because these vertices were chosen as the
three smallest, any residual obstruction has minimum degree seven.

The total excess above degree seven is \(160-22\cdot7=6\).  Hence at least
16 vertices have degree exactly seven.  On those vertices form a graph
\(G\) by

\[
xy\in E(G)\iff\lambda_{xy}\ge2.
\]

The theorem \(R(3,3)=6\) supplies either an independent triple or a triangle
among the degree-seven vertices.  In the independent case all three
pair-codegrees are exactly one; in the triangle case all are at least two.

A second safe-superset enumeration over degree profile \((7,7,7)\) has two
independent-class profiles and 215 triangle-class profiles.  The same fixed
position menu closes all of them.  The respective worst exact bounds are

\[
\frac{91231}{92378}<1,
\qquad
\frac{456463}{461890}<1.
\]

Thus \(v=22\) is impossible.

## 6. Excluding \(v=23\)

The degree constraints leave only

\[
(d_1,d_2,d_3)=(6,6,6),(6,6,7),(6,7,7).
\]

With all assignments to positions \((11,12,13)\), the exact enumeration is

| degrees | all profiles | residual profiles | residual consequence |
|---|---:|---:|---|
| \((6,6,6)\) | 192 | 0 | no three degree-six vertices |
| \((6,6,7)\) | 220 | 2 | all three selected pair-codegrees are 1 |
| \((6,7,7)\) | 263 | 17 | all three selected pair-codegrees are at most 2 |

Because there cannot be three degree-six vertices and the total degree is
160, exactly one of the following degree sequences holds:

\[
(6^2,7^{20},8),\qquad(6,7^{22}).
\tag{9}
\]

The residual consequences quantify over every arbitrary choice of the
degree-seven vertex or pair, since such a choice could have been made before
running the three-lock bound.

### 6.1 Degree sequence \((6^2,7^{20},8)\)

Let \(u,v\) be the degree-six vertices.  Applying the \((6,6,7)\) residual
statement with any degree-seven vertex \(y\) gives

\[
\lambda_{uv}=\lambda_{uy}=\lambda_{vy}=1.
\]

Let \(e\) be the unique edge containing \(u,v\).  At least 17 of the 20
degree-seven vertices lie outside \(e\).  Among these there are two,
say \(y,z\), with \(\lambda_{yz}=1\): otherwise each of those vertices
would have local excess at least 16, contrary to
\(\rho_y=4\cdot7-22=6\).

Thus \(S=\{u,v,y,z\}\) is pairwise codegree one, and the trace containing
\(u,v\) is exactly \(\{u,v\}\), since \(y,z\notin e\).  Of the six labelled
\(K_4\) clique partitions, only three remain: \(6K_2\), or one of the two
labelings of \(K_3+3K_2\) whose triangle does not contain both \(u,v\).
All assignments to either position base \((10,11,12,13)\) or
\((12,13,14,15)\) give the exact type maxima

\[
6K_2:\frac{8315}{8398},\qquad
K_3+3K_2:\frac{4152}{4199}.
\]

Both are strict.

### 6.2 Degree sequence \((6,7^{22})\)

Let \(u\) be the degree-six vertex.  Applying the \((6,7,7)\) residual
statement with every pair of degree-seven vertices shows that every pair
codegree in \(H\) is at most two.  Form the repeated-pair graph

\[
xy\in E(G)\iff\lambda_{xy}=2.
\]

By (2), its degree sequence is \((2,6^{22})\), so \(|E(G)|=67\).  Put
\(A=N_G(u)\) and \(B=V(H)\setminus(\{u\}\cup A)\); then \(|A|=2\) and
\(|B|=20\).  For \(R=\{u\}\cup A\),
\(e(G[R])\in\{2,3\}\), and the number of graph edges incident with \(R\) is

\[
\sum_{x\in R}d_G(x)-e(G[R])=14-e(G[R]).
\]

Consequently

\[
e(G[B])=67-(14-e(G[R]))\in\{55,56\}.
\]

Caro--Wei followed by Cauchy--Schwarz yields

\[
\alpha(G[B])\ge\sum_{x\in B}\frac1{d_B(x)+1}
\ge\frac{|B|^2}{2e(G[B])+|B|}
\ge\frac{400}{132}=\frac{100}{33}>3.
\]

Choose four independent vertices in \(B\).  Together with \(u\) they form
a five-set with every pair codegree one, hence one of the 32 labelled
clique partitions of \(K_5\), with selected degrees \((6,7,7,7,7)\).

The artifact lists an explicit menu of 11 ordered position assignments.  For
each of the 32 partitions at least one assignment gives \(Q<1\); the largest
chosen value is

\[
\frac{45784}{51051}<1.
\]

This excludes the second sequence and hence all of \(v=23\).

## 7. Excluding \(v=24\)

Every degree is at least six.  Writing the degree multiset as six plus
nonnegative excesses, the excesses sum to

\[
160-24\cdot6=16.
\]

Thus the complete degree-sequence condition is: a partition of 16 into at
most 16 positive integer excesses, padded by zeros to 24 vertices.  In
particular the set \(D\) of degree-six vertices has size at least eight.

For \(x\in D\), (2) gives \(\rho_x=1\).  Hence exactly one pair incident
with \(x\) has codegree two and every other incident pair has codegree one.
The graph on \(D\) joining repeated pairs has maximum degree one.  It
therefore has an independent four-set \(S\).

All pairs in \(S\) have codegree one, so its traces give one of the six
labelled \(K_4\) partitions.  The degrees \((6,6,6,6)\) force all singleton
and empty trace counts.  Over all assignments to positions
\((11,12,13,14)\), the exact bound by partition type is

\[
K_4:\frac{8323}{8398},\qquad
K_3+3K_2:\frac{16671}{16796},\qquad
6K_2:\frac{243}{247}.
\]

All are below one, so \(v=24\) is impossible.

## 8. Excluding \(v=25\)

Again every degree is at least six.  Now the nonnegative degree excesses
sum to

\[
160-25\cdot6=10.
\]

Equivalently, the complete degree-sequence condition is a partition of ten
into at most ten positive excesses, padded by zeros to 25 vertices.  Thus
the degree-six set \(D\) has size at least 15.

For \(x\in D\), equation (2) gives \(\rho_x=0\).  Hence every pair incident
with \(D\) has codegree exactly one.  We need only the following seven of
the 32 labelled \(K_5\) trace partitions:

| trace type | labelled profiles | best exact bound |
|---|---:|---:|
| \(10K_2\) | 1 | \(4188/4199\) |
| \(K_4+4K_2\) | 5 | \(37/38\) |
| \(K_5\) | 1 | \(3899/4199\) |

All assignments to positions \((11,12,13,14,15)\) are allowed.

It remains to show that a favourable five-set exists; this is what handles
the other 25 trace profiles.  If some hyperedge \(e\) contains at least four
points of \(D\), choose four of those points and a fifth point
\(z\in D\setminus e\), possible because \(|D|\ge15\).  The trace of \(e\)
is a \(K_4\) block.  Each of the four pairs from \(z\) to that block must be
a separate \(K_2\) block: combining two would reuse their internal
\(K_4\) pair.  Thus the trace type is exactly \(K_4+4K_2\).

Otherwise every hyperedge contains at most three points of \(D\), so each
edge covers at most one triple of \(D\).  There are at most 32 covered
triples.  If some five-set in \(D\) contains no covered triple, every trace
has size at most two and its partition is \(10K_2\), as desired.

If no such five-set existed, double-counting pairs \((T,S)\), where \(T\)
is a covered triple and \(S\) a five-set containing it, would give

\[
\binom{|D|}{5}\le32\binom{|D|-3}{2}.
\]

But

\[
\frac{\binom{|D|}{5}}{\binom{|D|-3}{2}}
=\frac{\binom{|D|}{3}}{10}
\ge\frac{\binom{15}{3}}{10}=\frac{91}{2}>32,
\]

a contradiction.  Therefore a favourable five-set always exists, and
\(v=25\) is impossible.

Together with (1), all vertex counts are excluded.

## 9. Exact artifacts and deterministic verification

The proof package is intentionally solver-free and standard-library-only.

* `locked_greedy_32.py` implements equations (3)--(8) with exact fractions.
* `close_v21_v22.py` emits one JSONL record for every enumerated \(v=21,22\)
  profile, including the chosen positions and exact bound, plus a manifest.
* `selection_certificates.py` regenerates the \(v=23,24,25\) profile and
  clique-partition sets, asserts their counts and SHA-256 fingerprints, and
  emits `SELECTION_MANIFEST.json`.
* `../solver_alt/verify_lower33.py` independently rederives the placement
  probabilities, generates clique partitions as arbitrary set partitions
  filtered by a clique predicate, and regenerates the three-lock profiles
  from the degree equations.  It imports none of the primary evaluator or
  generators.
* `../solver_alt/verify_v21_v22.py` independently regenerates the complete
  \(v=21,22\) profile sets and replays every emitted chosen placement using
  that second evaluator.

The pinned \(v=23,24,25\) set counts and hashes are:

| set | count | SHA-256 of canonical sorted JSON |
|---|---:|---|
| labelled \(K_4\) partitions | 6 | `35d71c1bd523dd2dd334603c79c6fcba62973f36ea518d22ed52940e5c76f312` |
| labelled \(K_5\) partitions | 32 | `e3a72027cd5955883eb6c56ff848a95a974e3e9d2c517ec5e3fd9d49505ca12b` |
| \(v=23,(6,6,6)\) profiles | 192 | `7cf883eaa09767ef80cf11a726df495b3b44efca99308bb98ea80fd2dfaf15ae` |
| \(v=23,(6,6,7)\) profiles | 220 | `4cb7b1bf3d375c04ad35ed98b482f66308781d19485211ce8744940d5338cc9e` |
| \(v=23,(6,7,7)\) profiles | 263 | `6272e1e5873fa83ecce0a7de46da04a01f62fd94e0a6a632df309cd367e37121` |
| residual \((6,6,6)\) | 0 | `4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945` |
| residual \((6,6,7)\) | 2 | `7ec468f5c51527ee1cadb66dda086e52abc2b4eb26aec72ed2b2841e7cdb9c69` |
| residual \((6,7,7)\) | 17 | `b3eb95aa6bd1adddd17a5abf7624e24d3213e3c97e43a4ebc84e5e4ca55a748e` |

The certificate-row hashes, which include the selected position assignment
and reduced exact fraction for every row, are pinned in
`SELECTION_MANIFEST.json` and as constants in `selection_certificates.py`.
The \(v=21,22\) artifact contains 3,081 records and has canonical internal
record hash
`feb165603b8eda25a3dfd55f842783810b015a5f1d4be510ce347a6dfac2ab7a`.
Its \(v=21\) and Ramsey-step subhashes are respectively
`c622bed337a8fb1682f765020a2504542c89c77383559909095d05b98e040ee2`
and
`80274adc462f71be34906175b470324bedd6480f2fad452278aad0a36720700c`.
All three are asserted as constants by `close_v21_v22.py`.  The checked-in
JSONL file itself has SHA-256
`228c32cada31ef82c49acc421bc4a842c01dc723d80e79555857b6364b946263`.

Recomputation commands from this directory are:

```sh
python3 locked_greedy_32.py --self-test
python3 close_v21_v22.py --output-dir certificates
python3 selection_certificates.py
python3 ../solver_alt/verify_lower33.py
python3 ../solver_alt/verify_v21_v22.py --artifact-dir certificates
```

The generators assert every count, residual structural condition and quoted
maximum before emitting their manifests.  Selection is always performed
before the random free permutation, exactly as required by Section 2.3.
The checked-in independent reports are
`../solver_alt/logs/lower33_independent_verification.json` and
`../solver_alt/logs/v21_v22_independent_verification.json`; both report that
all exact assertions and canonical row hashes match.
The separate line-by-line mathematical review, including an independently
derived version of every probability coefficient, is recorded in
`../solver_alt/LOWER33_INDEPENDENT_AUDIT.md`.  It found no omitted structural
case or finite-computation mismatch; external peer review is still
appropriate for a new extremal bound.
