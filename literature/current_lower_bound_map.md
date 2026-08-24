# Current lower bound map for \(m(5)\)

**Source audited:** Karl Grill and Daniel Linzmayer, *Improved Lower Bounds for Property B*, arXiv:2403.05674v3, dated 20 June 2024.  
**Audit date:** 2026-08-23.  
**Official source:** [abstract/version history](https://arxiv.org/abs/2403.05674), [v3 PDF](https://arxiv.org/pdf/2403.05674), [HTML](https://arxiv.org/html/2403.05674).

## Executive finding

The paper states and labels as Theorem 1 that

\[
m(5)\ge 32.
\]

The analytic/probabilistic dependency chain is clear through the discrete greedy bound and the one-locked-vertex setup. The final step from 31 to 32, however, is **not reproducible from the public paper or its official arXiv source archive**:

* the paper says that three marked vertices require seven edge-category counts \(l_A\);
* it says that exact finite calculations for selected \((n,m,v)\) cases yield \(m(5)\ge32\);
* it prints no three-vertex probability formulas, no list of the checked \((m,v,l_A)\) tuples, no feasible-domain constraints for the seven counts, no maximum probabilities/slack, and no program;
* the v3 arXiv source archive contains one file, `PropB.tex`, and no C/GMP source or output.

Thus the theorem is a published preprint claim resting on an undocumented finite computation. This is not evidence that the result is false, but it is a material reproducibility gap for any project that plans to use 32 as a formally certified baseline.

No post-2024 improvement of the global small-case bound was found in official/primary sources through 23 August 2026. The supported current interval remains \(32\le m(5)\le51\).

## 1. Notation and logical target

The paper defines \(m(n,v)\) as the least number of edges in a non-2-colorable \(n\)-uniform hypergraph on \(v\) vertices, and \(m(n)\) as the unrestricted minimum (p. 1).

To prove \(m(5)\ge32\), it is enough to exclude a non-2-colorable 5-graph with 31 edges. Since smaller edge counts had already been excluded at preceding stages, the genuinely new final slice is \(m=31\).

For a non-2-colorable hypergraph, the greedy algorithm fails for every vertex ordering. Consequently, any valid upper bound \(U\) on its failure probability must satisfy \(U\ge1\). Every strict inequality \(U<1\) is therefore an exclusion certificate.

## 2. The dependency map

### Node A — minimal-vertex pair-cover reduction

For the smallest \(v\) at which a hypergraph with at most \(m\) edges is non-2-colorable, every vertex pair must occur in an edge. Otherwise the two never-coincident vertices can be identified, preserving uniformity and non-2-colorability while reducing \(v\).

This yields Schönheim's covering bound

\[
m\ge
\left\lceil\frac{v}{n}
  \left\lceil\frac{v-1}{n-1}\right\rceil
\right\rceil .
\tag{3}
\]

**Location:** p. 2, equation (3), with the pair-cover explanation immediately before it.

For a pair-covered core, the same observation gives the minimum-degree constraint used later:

\[
\frac{v-1}{n-1}\le \delta(H)\le\frac{mn}{v}.
\tag{D}
\]

**Location:** p. 6, first half of Section 3. This inequality is displayed but unnumbered.

### Node B — balanced-random-coloring bound

Counting balanced colorings gives

\[
m(n,v)\ge
\frac{\binom{v}{n}}
{\binom{\lfloor v/2\rfloor}{n}+
 \binom{\lceil v/2\rceil}{n}}.
\tag{4}
\]

Since \(m(n,v)\) is integral, its numerical use requires a ceiling.

Combining (3) and (4) and minimizing over \(v\) gives equation (5).

**Location:** p. 2, equations (4) and (5).

### Node C — greedy failure implies a critical vertex

The Pluhár greedy procedure begins with all vertices red and processes them in a random order, recoloring a vertex blue when it is last in an otherwise-red edge. It cannot leave a red monochromatic edge. If it produces a blue edge, the first vertex of that blue edge must also have been last in another edge; such a vertex is called *critical*.

Writing \(\gamma\) for the number of **ordered** pairs of distinct edges whose intersection has size exactly one, the continuous bound is

\[
\Pr(\text{failure})\le
\int_0^1\min\{mnx^{n-1},mn(1-x)^{n-1},
\gamma x^{n-1}(1-x)^{n-1}\}\,dx.
\tag{6}
\]

Equation (7) is the corresponding one-parameter expression. A value strictly below 1 proves colorability.

**Location:** pp. 3–4, equations (6) and (7).

### Node D — fixed-\(v\) discrete greedy bound

For a uniformly random permutation, the paper obtains

\[
U_8(n,v,m,\gamma)=
\sum_k\frac1v\min\left\{
mn\frac{\binom{k-1}{n-1}}{\binom{v-1}{n-1}},
mn\frac{\binom{v-k}{n-1}}{\binom{v-1}{n-1}},
\gamma\frac{\binom{k-1}{n-1}\binom{v-k}{n-1}}
{\binom{v-1}{n-1}\binom{v-n}{n-1}}
\right\}.
\tag{8}
\]

The paper writes \(k=0,\ldots,v\), although physical permutation positions are \(1,\ldots,v\). Interpreting out-of-range binomial coefficients as zero makes the extra \(k=0\) term harmless; this convention is not stated.

The baseline is \(\gamma\le m(m-1)\). Two refinements are printed on p. 5:

\[
\gamma\le m(m-1)-r(r-1)
\]

if some vertex pair occurs in \(r\) edges, and

\[
\gamma\le
\sum_{i=1}^v\bigl(d_i(d_i-1)-r_i(r_i-1)\bigr),
\]

where \(d_i\) is a vertex degree and \(r_i\) is the maximum codegree of a pair containing vertex \(i\).

The authors say that small C programs with exact GMP integer arithmetic evaluate these bounds for \(5\le n\le9\) and \(2n+1\le v\le200\).

**Location:** pp. 4–5, equation (8), equation (9), and the two unnumbered \(\gamma\)-bounds; implementation statement on p. 5.

**Published numerical output:** Table 1, p. 6, reports the *global* row

\[
\text{“Discrete greedy eq. (8)” for }n=5: \quad m(5)\ge30.
\]

It does not publish the individual \(v\)-values or the exact GMP output.

### Node E — one locked low-degree vertex

Choose a minimum-degree vertex, of degree \(l\), and fix it at the middle position \(v_1=\lceil v/2\rceil\). The degree interval is (D). For an unmarked position \(k<v_1\), the paper prints three union bounds \(p_1(k),p_2(k),p_3(k)\), corresponding to being last in an edge, first in an edge, or both.

The paper then reports that the calculation improves the global value to

\[
m(5)\ge31.
\]

**Location:** pp. 6–7, Section 3. The formulas are unnumbered; the numerical conclusion is the first paragraph on p. 7.

**Missing details:** formulas for \(k=v_1\) and \(k>v_1\), the finite parameter list, exact maxima, slack, and code are not printed.

For \(n=5,m=30\), the displayed earlier bounds show why the hard slice is narrow: (3), (4), and (8) reduce the unresolved pair-covered case to \(v=25\); (D) then forces \(l=6\). The paper does not spell out this dependency.

### Node F — two locked vertices

For two marked vertices the paper introduces three counts:

* \(l_1\): edges containing only mark 1;
* \(l_2\): edges containing only mark 2;
* \(l_{12}\): edges containing both.

It says all relevant \((n,v)\) combinations were calculated, but the only new global conclusions reported are \(m(7)\ge128\) and \(m(8)\ge262\). No new \(m(5)\) value is claimed here.

**Location:** p. 7, second paragraph of Section 3.

No two-mark formulas, tables, or code are published.

### Node G — three locked vertices, the opaque final step

For three marked vertices the edge set is partitioned into seven counts

\[
l_A,\qquad \varnothing\ne A\subseteq\{1,2,3\},
\]

where \(l_A\) counts edges containing exactly the marked subset \(A\). The paper states:

> “We apply this to selected combinations of \(n,m,v\). This by itself is enough to give us \(m(5)\ge32\).”

**Location:** p. 7, third paragraph of Section 3.

The next detailed paragraph concerns \(n=6\), not \(n=5\). There is no displayed calculation for the \(n=5\) step.

Logically, equations (3), (4), and (8) show that an \(m=31\) proof must initially consider only \(19\le v\le25\), and (8) with the published trivial bound \(\gamma\le930\) already excludes \(v=19,20,21\). Therefore any undocumented final calculation has to dispose of the unresolved slices

\[
(n,m,v)=(5,31,22),(5,31,23),(5,31,24),(5,31,25),
\]

except for any of these that the undocumented one- or two-mark computations may already eliminate. The paper does not say which slices reach the three-mark stage.

### Node H — Theorem 1

Theorem 1 states

\[
m(5)\ge32,\quad m(6)\ge64,\quad m(7)\ge128,\quad
m(8)\ge263,\quad m(9)\ge538.
\]

**Location:** p. 7.

The \(m(5)\) dependency is A → B → C → D → E → G → H. Node F may provide local exclusions but contributes no separately stated global \(m(5)\) improvement.

## 3. The exact \(m=31\) bottleneck visible from printed formulas

With \(n=5,m=31\), equations (3) and (4) restrict a minimal pair-covering core to \(19\le v\le25\). Direct exact evaluation of equation (8) with \(\gamma=31\cdot30=930\) gives:

| \(v\) | \(U_8(5,v,31,930)\) | consequence |
|---:|---:|---|
| 19 | \(42749/46189\approx0.925523\) | excluded |
| 20 | \(16275/16796\approx0.968981\) | excluded |
| 21 | \(4154/4199\approx0.989283\) | excluded |
| 22 | \(24986/24871\approx1.004624\) | unresolved by (8) |
| 23 | \(592968/572033\approx1.036598\) | unresolved by (8) |
| 24 | \(216907/208012\approx1.042762\) | unresolved by (8) |
| 25 | \(274877/260015\approx1.057158\) | unresolved by (8) |

These fractions are exact recomputations of the displayed equation, not a table printed by the authors.

The pair-cover degree bookkeeping in the four unresolved slices is:

| \(v\) | possible \(\delta\) | total degree slack above degree 6 | forced low-degree structure |
|---:|---:|---:|---|
| 22 | 6 or 7 | \(155-6(22)=23\) | if \(\delta=7\), degree multiset is exactly \(8,7^{21}\) |
| 23 | 6 | 17 | at least 6 vertices have degree 6 |
| 24 | 6 | 11 | at least 13 vertices have degree 6 |
| 25 | 6 | 5 | at least 20 vertices have degree 6 |

For a degree-6 vertex \(x\), pair coverage gives

\[
\sum_{y\ne x}(\lambda_{xy}-1)=4\cdot6-(v-1),
\]

so the local pair-incidence excess is respectively 3, 2, 1, and 0 for \(v=22,23,24,25\). In particular, at \(v=25\) every pair containing a degree-6 vertex occurs exactly once. These are the tight structural conditions that the omitted \(l_A\)-enumeration should exploit.

## 4. What the paper actually publishes for \(17\le v\le25\)

The sentence on p. 5 says:

> “For \(n=5\), we get improved lower bounds for \(17\le v\le25\).”

There is **no fixed-\(v\) table** in the PDF, TeX source, or arXiv ancillary material. Table 1 is indexed by uniformity \(n\), not by vertex count \(v\). The exact strengthened-\(\gamma\) values, degree/codegree cases, and GMP outputs are not supplied.

The earlier public fixed-vertex list is in Linzmayer's 2018 TU Wien thesis, Theorem 10.2.2 and equations (10.2.3)–(10.2.5), pp. 73–75. For the requested range it prints

\[
m(5,17)\ge34,\quad m(5,18)\ge34,\quad
m(5,19),m(5,20)\ge\frac{646}{21}\approx30.762,
\]

so integrality gives 31 for \(v=19,20\). It prints no entries for \(21\le v\le25\), explaining that the same generic bound then falls below the global lower bound known at the time. These values are exactly the balanced-coloring calculation later shown as equation (4), not a separate stronger method. [Official TU Wien thesis PDF](https://repositum.tuwien.at/bitstream/20.500.12708/3487/2/Linzmayer%20Daniel%20-%202018%20-%20Die%20probabilistische%20Methode%20in%20der%20Kombinatorik.pdf).

The following are all numerical values that can be recovered transparently from the printed formulas. The “equation (8)” column deliberately uses only the published universal \(\gamma\le m(m-1)\), not an undocumented refinement.

| \(v\) | Schönheim (3) | random coloring (4), rounded up | max of (3),(4) | direct equation (8) lower bound | strongest stated consequence after Theorem 1 |
|---:|---:|---:|---:|---:|---:|
| 17 | 14 | 34 | 34 | 35 | 35 |
| 18 | 18 | 34 | 34 | 34 | 34 |
| 19 | 19 | 31 | 31 | 33 | 33 |
| 20 | 20 | 31 | 31 | 32 | 32 |
| 21 | 21 | 29 | 29 | 32 | 32 |
| 22 | 27 | 29 | 29 | 31 | 32 |
| 23 | 28 | 27 | 28 | 31 | 32 |
| 24 | 29 | 27 | 29 | 31 | 32 |
| 25 | 30 | 26 | 30 | 30 | 32 |

For example, the strict equation-(8) checks at the claimed lower bound minus one are:

\[
\begin{array}{c|ccccccccc}
v&17&18&19&20&21&22&23&24&25\\\hline
m&34&33&32&31&31&30&30&30&29
\end{array}
\]

and the corresponding exact upper probabilities are

\[
\frac{38}{39},\frac{33}{34},\frac{222656}{230945},
\frac{16275}{16796},\frac{4154}{4199},
\frac{23850}{24871},\frac{563280}{572033},
\frac{207435}{208012},\frac{106604}{111435},
\]

all strictly below 1.

The qualitative claim “improved lower bounds” may refer to stronger values produced by the unpublished \(\gamma\)-refinement program, but no exact per-\(v\) values can be responsibly attributed to the authors from v3. The global Theorem 1 implies \(m(5,v)\ge32\) for every \(v\), but that implication inherits the undocumented three-mark computation.

## 5. Necessary equality/slack conditions for a hypothetical 32-edge obstruction

This section records rigorous consequences of the paper's displayed inequalities plus elementary double counting. Items explicitly derived here are not claims made verbatim in the paper.

### 5.1 Vertex count and minimum degree

Let \(H\) be a 32-edge non-2-colorable 5-graph and compress never-coincident vertex pairs until a vertex-minimal pair-covered core is obtained. Because a merge producing at most 31 distinct edges would contradict Theorem 1, a minimum 32-edge obstruction can be taken pair-covered with 32 distinct edges.

Equations (3) and (4) give

\[
19\le v\le25.
\]

Equation (8) with \(\gamma\le32\cdot31=992\) already gives

\[
U_8(5,19,32,992)=\frac{222656}{230945}<1,
\]

so \(v=19\) is impossible without any refined intersection estimate.

The degree interval is

\[
\left\lceil\frac{v-1}{4}\right\rceil
\le\delta(H)\le
\left\lfloor\frac{160}{v}\right\rfloor.
\]

| \(v\) | possible \(\delta(H)\) | surplus \(160-6v\) when \(\delta=6\) | guaranteed degree-6 vertices when \(\delta=6\) |
|---:|---:|---:|---:|
| 20 | 5–8 | — | — |
| 21 | 5–7 | — | — |
| 22 | 6–7 | 28 | no nontrivial guarantee |
| 23 | exactly 6 | 22 | at least 1 |
| 24 | exactly 6 | 16 | at least 8 |
| 25 | exactly 6 | 10 | at least 15 |

At \(v=23,24,25\), a degree-6 vertex has local pair-excess 2, 1, 0 respectively. At \(v=25\), every pair containing such a vertex occurs exactly once.

### 5.2 Required abundance of one-point edge intersections

Let \(\gamma\) be the ordered number of edge pairs with intersection exactly one. Since a non-2-colorable hypergraph makes greedy coloring fail with probability 1, equation (8) forces the following even-integer thresholds:

| \(v\) | minimum even \(\gamma\) required by \(U_8\ge1\) |
|---:|---:|
| 19 | impossible even at \(\gamma=992\) |
| 20 | 960 |
| 21 | 880 |
| 22 | 878 |
| 23 | 848 |
| 24 | 816 |
| 25 | 798 |

Thus, for example, a \(v=20\) obstruction would require at least 480 of the \(\binom{32}{2}=496\) unordered edge pairs to intersect in exactly one vertex.

### 5.3 Pair-cover surplus excludes \(v=20\)

For a pair-covered core write \(\lambda_{xy}\ge1\) for pair codegrees. There are 320 edge-pair incidences, so

\[
R(v):=\sum_{x<y}(\lambda_{xy}-1)
=320-\binom v2.
\]

Also

\[
Q:=\sum_{x<y}\binom{\lambda_{xy}}2
=\sum_{\{e,f\}}\binom{|e\cap f|}{2}\ge R(v).
\]

Two distinct 5-edges intersect in at most four vertices, so each edge pair with intersection at least two contributes at most \(\binom42=6\) to \(Q\). Hence at least \(\lceil R(v)/6\rceil\) unordered edge pairs have intersection at least two, giving

\[
\gamma\le 992-2\left\lceil\frac{R(v)}6\right\rceil.
\tag{S}
\]

| \(v\) | \(R(v)\) | upper bound (S) on \(\gamma\) | required \(\gamma\) | consequence |
|---:|---:|---:|---:|---|
| 19 | 149 | 942 | impossible | excluded |
| 20 | 130 | 948 | at least 960 | excluded |
| 21 | 110 | 954 | at least 880 | survives |
| 22 | 89 | 962 | at least 878 | survives |
| 23 | 67 | 968 | at least 848 | survives |
| 24 | 44 | 976 | at least 816 | survives |
| 25 | 20 | 984 | at least 798 | survives |

At \(v=20\), substituting \(\gamma=948\) into equation (8) gives the explicit strict slack

\[
U_8(5,20,32,948)=\frac{20874}{20995}
=1-\frac{121}{20995}<1.
\]

Therefore a 32-edge obstruction, if one exists, has a pair-covered core with

\[
21\le v\le25.
\]

This \(v=20\) exclusion is a new transparent consequence recorded by this audit; it is not stated as a lemma in arXiv:2403.05674v3.

### 5.4 Edge-critical equality

Because 31 edges are asserted insufficient, every 32-edge obstruction is edge-critical: for every edge \(e\), \(H-e\) is 2-colorable. In any proper coloring of \(H-e\), the removed edge \(e\) must be the unique monochromatic edge when restored. Hence a certifying dataset for a 32-edge obstruction can include 32 witness colorings, one for each edge deletion, in addition to the UNSAT certificate for the full hypergraph.

## 6. Search for a post-2024 improvement

Only primary or official sources were used for the status check.

1. **Official arXiv API.** A query for `"property B" AND hypergraph`, sorted by submission date, returned arXiv:2403.05674 as the newest relevant extremal Property B paper; the next results were from 2023 and earlier. [Official API query](https://export.arxiv.org/api/query?search_query=all:%22property%20B%22%20AND%20all:hypergraph&start=0&max_results=100&sortBy=submittedDate&sortOrder=descending).
2. **2026 author survey.** Grill and Linzmayer's *An Overview of Property B*, published online 28 May 2026, cites the 2024 lower-bound preprint as its recent lower-bound source. Its bibliography contains no later lower improvement. It also cites the unpublished 2024 heuristic upper-bound work. [Official Springer chapter page](https://link.springer.com/chapter/10.1007/978-3-032-18810-6_9).
3. **Official Crossref metadata.** A title/subject search over publications dated 2024-06-21 through 2026-08-23 found the 2026 survey but no later paper improving \(m(5)\). This is a discovery check, not a proof of nonexistence.
4. **Erdős Problems database.** Problem 901 remained open at its 28 December 2025 update, although the page tracks the asymptotic problem rather than the exact small value \(m(5)\). [Official problem page](https://www.erdosproblems.com/901).

**Conclusion as of 2026-08-23:** no post-2024 primary source was found that improves \(m(5)\ge32\) or \(m(5)\le51\). The 2026 survey is the strongest contemporaneous confirmation, but its chapter text is subscription-only and its bibliography alone cannot certify that no unpublished result exists.

## 7. Verification implications

Before treating 32 as a proof-checked computational baseline, request from Grill and Linzmayer:

* the C/GMP programs used for equations (8) and the locked-vertex cases;
* the complete tuple list for \((n,m,v,l_A)\);
* exact rational maxima and slack for every \(n=5,m=31\) slice;
* the rule used to select the one, two, or three marked vertices;
* the feasibility constraints imposed on the seven \(l_A\) values;
* compiler/GMP versions and deterministic output logs.

Absent those artifacts, an independent project should reprove the four \(m=31\), \(v=22,23,24,25\) slices with a proof-producing method rather than assume that the omitted finite calculation can be reproduced from the article.
