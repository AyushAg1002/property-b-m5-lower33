# Exact Property B at uniformity 5: literature and novelty audit

**Audit date:** 2026-08-23  
**Problem:** Let \(m(k)\) be the least number of edges in a \(k\)-uniform hypergraph that is not 2-colorable (does not have Property B). Determine or improve the bounds on \(m(5)\).

## Bottom line

The presently supported numerical interval is

\[
32 \le m(5) \le 51.
\]

The lower endpoint is **32**, not the older value 29. Grill and Linzmayer proved \(m(5)\ge 32\) in a June 2024 revision of *Improved Lower Bounds for Property B*. The classical Abbott--Hanson construction still supplies the upper bound 51.

An exact or improved computational result would be novel, but there is a serious collision risk: a 2026 survey cites an otherwise unpublished 2024 item by Daniel Linzmayer and Karl Grill titled *Some upper bounds for property B for small values of n by heuristic search*. A public 2024 conference abstract confirms heuristic searches for small uniformities and vertex counts, but this audit found no public manuscript, tables, code, or witness list. The authors should be contacted before claiming novelty for a fixed-vertex upper bound or heuristic construction.

The cleanest rigorous finite reduction for an exact search is:

* repeatedly identify any pair of vertices that never occurs together in an edge;
* the resulting non-2-colorable core covers every vertex pair;
* the 2026 La Jolla covering data give \(C(32,5,2)=52\), so a counterexample with at most 50 edges has a pair-covering core on at most 31 vertices;
* the exact small-vertex results \(m(5,9)=m(5,10)=126\) and \(m(5,11)=m(5,12)=66\) exclude smaller cores.

Consequently an exact proof of \(m(5)=51\) can be organized as a finite exclusion over pair-covering 5-uniform hypergraphs with

\[
13 \le v \le 31, \qquad 32 \le e \le 50.
\]

This reduction is rigorous; it does **not** mean the resulting enumeration is currently practical.

## 1. Current bounds

### Lower bound: \(m(5)\ge 32\)

Karl Grill and Daniel Linzmayer, *Improved Lower Bounds for Property B*, arXiv:2403.05674v3 (20 June 2024), prove \(m(5)\ge 32\). Their method is probabilistic but its numerical inequalities are evaluated exactly:

1. choose a random ordering of the vertices;
2. greedily color in that order, changing color when an edge would become monochromatic;
3. bound failure using critical vertices and pairs of intersecting edges;
4. discretize the argument in terms of permutations rather than continuous random weights;
5. improve the bound by fixing one, two, and then three low-degree vertices into central positions of the random order;
6. evaluate the finite rational expressions with small C programs using GMP.

The progression in the paper is \(m(5)\ge 30\) from the discrete greedy estimate, \(m(5)\ge 31\) with one locked vertex, and \(m(5)\ge 32\) after analyzing three locked vertices. The authors also report improved fixed-vertex lower bounds for \(17\le v\le25\). No public code repository or attached computational artifact was found on the arXiv record.

Primary source: [Grill--Linzmayer arXiv record](https://arxiv.org/abs/2403.05674), [full HTML](https://arxiv.org/html/2403.05674).

### Upper bound: \(m(5)\le 51\)

Abbott and Hanson construct non-Property-B hypergraphs satisfying

\[
m(n) \le n\,m(n-2)+2^{n-1}+2^{n-2}((n-1)\bmod 2).
\]

For \(n=5\), using \(m(3)=7\), this gives

\[
m(5)\le 5\cdot 7+16=51.
\]

Primary source: H. L. Abbott and D. Hanson, *On a Combinatorial Problem of Erdös*, Canadian Mathematical Bulletin 12(6) (1969), 823--829, [DOI and article page](https://doi.org/10.4153/CMB-1969-107-x), [publisher PDF](https://www.cambridge.org/core/services/aop-cambridge-core/content/view/C9C0468CBBACD4DE4EE3946F5F3DE047/S0008439500054394a.pdf/on-a-combinatorial-problem-of-erdos.pdf).

Aglave, Amarnath, Shannigrahi, and Singh restate the recurrence, explicitly calculate 51 for \(n=5\), and supply the prior lower bound 29. Their paper is useful for structural lemmas, but its 29 lower bound has been superseded by Grill--Linzmayer.

Primary source: Sachin Aglave et al., *Improved Bounds for Uniform Hypergraphs without Property B*, Australasian Journal of Combinatorics 76(1) (2020), 73--86, [arXiv](https://arxiv.org/abs/1602.00218), [journal PDF](https://ajc.maths.uq.edu.au/pdf/76/ajc_v76_p073.pdf).

### Status in the current survey and Erdős problem database

The most recent authoritative survey found is Grill and Linzmayer, *An Overview of Property B*, in *Sum(m)it280*, Bolyai Society Mathematical Studies 32, 173--181, published online 28 May 2026. Its bibliography includes both the 2024 lower-bound preprint and the unpublished 2024 heuristic-search work.

Survey page: [Springer chapter](https://link.springer.com/chapter/10.1007/978-3-032-18810-6_9).

The Erdős Problems database lists the asymptotic Property B question as open, problem 901. Exact \(m(5)\) is a finite small-parameter subproblem, not a resolution of the asymptotic question itself.

Database entry: [Erdős problem 901](https://www.erdosproblems.com/901), [edit history](https://www.erdosproblems.com/history/901).

## 2. Prior computational and heuristic work

### Linzmayer's 2018 thesis

Daniel Linzmayer's TU Wien diploma thesis, *Die probabilistische Methode in der Kombinatorik* (2018), contains the clearest public prior computational attack located in this audit. Chapter 10 defines a fixed-vertex variant \(m(k,N)\), develops a simulated-annealing search, includes the C source, reports runtimes, and lists witnesses.

For \(k=5\), it records counting lower bounds and matches them by heuristic constructions at \(N=11,12\):

| vertex count \(N\) | counting lower bound reported | computational result |
|---:|---:|---:|
| 11 | 66 | 66-edge non-2-colorable witness |
| 12 | 66 | 66-edge non-2-colorable witness |
| 13, 14 | 48 | no exact value established in the public thesis |
| 15, 16 | 39 | no exact value established |
| 17, 18 | 34 | no exact value established |
| 19, 20 | 31 | no exact value established |

Thus the public record supports \(m(5,11)=m(5,12)=66\) in the thesis's fixed-vertex sense. Searches at larger vertex counts are explicitly heuristic and do not certify nonexistence.

Primary source: [TU Wien repository record](https://repositum.tuwien.at/handle/20.500.12708/3487), [full thesis PDF](https://repositum.tuwien.at/bitstream/20.500.12708/3487/2/Linzmayer%20Daniel%20-%202018%20-%20Die%20probabilistische%20Methode%20in%20der%20Kombinatorik.pdf), especially Chapter 10 and its appended C code/witnesses.

### Unpublished 2024 Grill--Linzmayer search

The 2026 survey cites:

> Daniel Linzmayer and Karl Grill, *Some upper bounds for property B for small values of n by heuristic search* (2024), unpublished.

A Sum(m)it280 conference abstract, *Some Upper Bounds for Property B* (Karl Grill, joint work with Daniel Linzmayer), says that various heuristic algorithms were used to find upper bounds when both the uniformity and number of vertices are small.

Primary/authoritative sources: [2026 survey bibliography](https://link.springer.com/chapter/10.1007/978-3-032-18810-6_9), [Sum(m)it280 abstract booklet](https://conferences.renyi.hu/uploads/Abstract_Booklet_Summit280_%289%29.pdf).

**Novelty consequence:** before publishing a fixed-\(v\) witness or a heuristic upper bound, request the unpublished tables and witnesses from Grill and Linzmayer. The absence of a public paper is not evidence that a particular parameter value was not already found.

## 3. Structural reductions relevant to an exact search

### Pair-merging / pair-covering core

Suppose two vertices \(x,y\) never occur together in an edge. Identify them, replacing \(y\) by \(x\) in every edge containing \(y\). No edge loses uniformity because no edge contained both vertices. If the merged hypergraph had a valid 2-coloring, assigning the same color to \(x\) and \(y\) would give a valid coloring of the original hypergraph. Hence non-2-colorability is preserved.

Repeating this operation yields a vertex-minimal representative in which every pair of vertices lies in an edge: a \((v,5,2)\) covering. This reduction appears in the exact \(m(4)\) line of work and is stated explicitly in the modern Property B papers.

For a pair-covered \(k\)-uniform hypergraph with \(e\) edges, basic counting gives

\[
e \ge C(v,k,2) \ge
\left\lceil \frac{v}{k}
  \left\lceil\frac{v-1}{k-1}\right\rceil
\right\rceil,
\]

where \(C(v,k,2)\) is the covering number. Grill--Linzmayer also exploit the resulting minimum-degree constraint

\[
\frac{v-1}{k-1}\le \delta(H)\le \frac{ek}{v}.
\]

### Exact finite vertex bound from covering data

The frozen April 2026 La Jolla Covering Repository data give the following relevant entries for \(C(v,5,2)\):

| \(v\) | current LJCR status for \(C(v,5,2)\) |
|---:|---:|
| 28 | 40 |
| 29 | 42--43 |
| 30 | 48 |
| 31 | 50 |
| 32 | 52 |

Therefore a pair-covered 5-uniform hypergraph with at most 50 edges has \(v\le31\). Together with the exact low-vertex results, only \(13\le v\le31\) need be considered in a proof excluding all 32--50 edge counterexamples.

This is a finite-scope theorem, not a claim that the repository enumerates all designs. The repositories store best known covers and covering bounds; they are excellent seeds and bound sources, but they are **not** complete isomorphism classifications of every pair cover with a given block count.

Authoritative data sources:

* Daniel M. Gordon, *La Jolla Coverings Repository* frozen dataset, updated 24 April 2026, [Zenodo record and DOI](https://zenodo.org/records/19735294).
* [LJCR tables](https://ljcr.dmgordon.org/cover/table.html), last updated 21 April 2026.
* [LJCR source repository](https://github.com/dmgordo/LJCR).
* [Current Covering Repository](https://www.coveringrepository.com/default.aspx), which imported the LJCR history through March 2026 and continues tracking improvements.

## 4. The exact \(m(4)=23\) precedent

Patric R. J. Östergård proved \(m(4)=23\) by exhaustive computer search. The published abstract states the exhaustive result; the standard reduction restricts a vertex-minimal counterexample to a \((v,4,2)\) pair covering, after which the finite cases are generated/tested computationally.

Primary bibliographic source: Patric R. J. Östergård, *On the minimum size of 4-uniform hypergraphs without property B*, Discrete Applied Mathematics 163 (2014), 199--204, [DOI](https://doi.org/10.1016/j.dam.2011.11.035), [Aalto publication record](https://research.aalto.fi/en/publications/on-the-minimum-size-of-4-uniform-hypergraphs-without-property-b/).

The 2008 announcement is documented on Jensen and Toft's official problem page, which also notes that uniqueness of the 23-edge Seymour/Toft construction was still open at that time: [Problem 15.1](https://www.imada.sdu.dk/Research/Graphcol/15.1.html).

### Reproducibility caveat

No public source-code archive, complete enumeration log, or machine-checkable certificate specifically associated with the 2014 \(m(4)\) paper was found in this audit. The accessible publisher abstract proves only that an exhaustive search was reported; it does not expose enough implementation detail to reconstruct the full algorithm from the abstract alone. Any modern \(m(5)\) computation should exceed that reproducibility standard rather than treating the 2014 paper as a ready-made code base.

There is a particularly relevant modern method: Kirchweger, Peitl, and Szeider's **SAT Modulo Symmetries with Co-Certificate Learning** (SMS+CCL). It generates only canonical candidate graphs and, whenever a candidate has an unwanted coloring, turns that coloring into a learned blocking clause. The authors explicitly name “computing small non-2-colorable \(n\)-uniform hypergraphs” as a target application.

Primary source: Markus Kirchweger, Tomáš Peitl, and Stefan Szeider, *Co-Certificate Learning with SAT Modulo Symmetries*, IJCAI 2023, [paper PDF](https://www.ijcai.org/proceedings/2023/0216.pdf).

For Property B the co-certificate is especially simple: a red/blue coloring. This makes CCL/CEGAR a much better conceptual fit than enumerating all hypergraphs and only then invoking a separate coloring test.

## 5. What would be publishable?

### Clearly publishable global results

1. **Any explicit non-2-colorable 5-uniform hypergraph with at most 50 edges.** This improves the Abbott--Hanson upper bound, which has stood since 1969. A 50-edge witness already matters; fewer is stronger.
2. **A rigorous proof that all 5-uniform hypergraphs with at most 32 edges are 2-colorable**, i.e. \(m(5)\ge33\). The current lower bound is already 32, so proofs only reaching 29--32 are not new globally.
3. **The exact value \(m(5)=51\)** by exhaustive exclusion of 32--50 edges (or an exact smaller value combining a witness and exclusion below it).

### Potentially publishable intermediate results

1. A new exact value of the fixed-vertex function \(m(5,v)\) for an unresolved \(v\ge13\).
2. A substantial certified exclusion for a range of vertices/edge counts, such as no counterexample with \(v\le V\) and \(e\le E\).
3. A new structural theorem that sharply narrows degree sequences, intersection profiles, or covering types of a minimum obstruction.
4. A reusable proof-producing SAT/QBF/SMS+CCL framework for non-2-colorable uniform hypergraphs, if accompanied by a nontrivial new mathematical bound or complete classification.

The fixed-vertex items require a collision check against the unpublished 2024 Grill--Linzmayer work and the tables behind their 2026 survey.

### Not enough by itself

* failure of simulated annealing, local search, ILP, or SAT under a timeout;
* an UNSAT proof that only shows one *fixed* candidate hypergraph is non-2-colorable;
* an unverified program claim that “all cases” were searched;
* reproducing \(m(5)\ge29\), 31, or 32;
* a repository cover that happens to be 2-colorable, without a completeness argument over all possible covers.

## 6. Required certificates and verification

### For an upper-bound witness

Deliver at minimum:

1. a normalized edge list on vertices \(0,\dots,v-1\), with every edge sorted and all edges distinct;
2. metadata: \(v\), \(e\), degree sequence, pair-coverage status, canonical-label hash, and file checksum;
3. a tiny independent checker for 5-uniformity, distinctness, and non-2-colorability;
4. a machine-checkable SAT refutation.

For a fixed hypergraph \(H=(V,E)\), 2-colorability is the monotone NAE-5-SAT formula

\[
\Phi_H=\bigwedge_{e\in E}
\left(\bigvee_{v\in e}x_v\right)
\wedge
\left(\bigvee_{v\in e}\neg x_v\right).
\]

An upper-bound witness is valid exactly when \(\Phi_H\) is UNSAT. Publish the DIMACS encoding plus a DRAT/LRAT/FRAT proof and verify it with a separately maintained proof checker. A transparent hand proof exploiting symmetry is desirable if the construction has structure, but it should supplement rather than replace the raw edge list.

### For a lower bound / nonexistence result

The hard part is certifying **completeness of generation**, not merely certifying each tested object's colorability. A credible package should include:

1. a proved finite reduction (here, pair merging plus \(13\le v\le31\));
2. a precise encoding of all candidate hypergraphs for each \((v,e)\) slice;
3. proof that cardinality, pair coverage, simplicity, and any degree/intersection restrictions are encoded without losing solutions;
4. rigorous symmetry handling: canonical augmentation/SAT modulo symmetries, or independently checked static symmetry breaking;
5. deterministic counts and hashes for every completed slice;
6. proof logs for UNSAT terminal slices, or a proof-producing QBF formulation;
7. source code, exact build environment/container, solver versions, seeds, command lines, and raw logs;
8. an independent verifier, preferably using a different SAT solver and a separate canonical-label implementation (for example nauty/Traces versus the search's internal symmetry code);
9. cube-and-conquer coverage evidence if the search is partitioned: the cubes must be shown to cover the original formula, and every cube's proof must check.

Dynamic symmetry clauses and CCL clauses are logically valid only with their respective canonicity/coloring justifications. If the solver cannot emit a standard end-to-end proof, retain independently checkable advice records and validate the final result with a second enumeration path. “The code finished” is not a mathematical certificate.

### Natural quantified formulation

The existence of a counterexample with prescribed \(v,e\) has the form

\[
\exists\,\text{edge-selection variables}\quad
\forall\,\text{vertex colorings}\quad
\exists\,\text{a monochromatic selected edge}.
\]

This is naturally expressible as QBF. In practice, CEGAR/co-certificate learning avoids materializing all \(2^{v-1}\) complementary coloring classes at once: the master solver proposes a hypergraph, the coloring solver returns a valid 2-coloring if one exists, and the master learns a clause requiring a future hypergraph to contain at least one edge monochromatic under that coloring.

## 7. Recommended novelty-safe research sequence

1. Contact Grill and Linzmayer for the unpublished 2024 tables, source, and witnesses.
2. Reproduce the public fixed-vertex cases \(v=11,12\) from Linzmayer's thesis as a validation benchmark.
3. Implement a canonical, pair-covering CCL/CEGAR search and cross-check it on \(m(4)=23\).
4. Search for an upper-bound witness first. A 50-edge witness is far easier to certify and already publishable.
5. In parallel, complete small \((v,e)\) exclusion slices with proof logs and publish the slice manifest even if the global exact computation remains unfinished.
6. Only claim a global lower bound after the completeness and symmetry machinery has an independent audit.

## 8. Bibliography and source ledger

* H. L. Abbott and D. Hanson, “On a Combinatorial Problem of Erdös,” *Canadian Mathematical Bulletin* 12(6) (1969), 823--829. [DOI](https://doi.org/10.4153/CMB-1969-107-x).
* Sachin Aglave, V. A. Amarnath, Saswata Shannigrahi, and Shwetank Singh, “Improved Bounds for Uniform Hypergraphs without Property B,” *Australasian Journal of Combinatorics* 76(1) (2020), 73--86. [Journal PDF](https://ajc.maths.uq.edu.au/pdf/76/ajc_v76_p073.pdf), [arXiv](https://arxiv.org/abs/1602.00218).
* Karl Grill and Daniel Linzmayer, “Improved Lower Bounds for Property B,” arXiv:2403.05674v3 (2024). [arXiv](https://arxiv.org/abs/2403.05674).
* Karl Grill and Daniel Linzmayer, “An Overview of Property B,” in *Sum(m)it280*, Bolyai Society Mathematical Studies 32 (2026), 173--181. [Springer](https://link.springer.com/chapter/10.1007/978-3-032-18810-6_9).
* Daniel Linzmayer and Karl Grill, “Some upper bounds for property B for small values of n by heuristic search” (2024), unpublished; cited in the 2026 survey. Related [conference abstract booklet](https://conferences.renyi.hu/uploads/Abstract_Booklet_Summit280_%289%29.pdf).
* Daniel Linzmayer, *Die probabilistische Methode in der Kombinatorik*, diploma thesis, TU Wien (2018). [Repository](https://repositum.tuwien.at/handle/20.500.12708/3487), [PDF](https://repositum.tuwien.at/bitstream/20.500.12708/3487/2/Linzmayer%20Daniel%20-%202018%20-%20Die%20probabilistische%20Methode%20in%20der%20Kombinatorik.pdf).
* Patric R. J. Östergård, “On the minimum size of 4-uniform hypergraphs without property B,” *Discrete Applied Mathematics* 163 (2014), 199--204. [DOI](https://doi.org/10.1016/j.dam.2011.11.035), [Aalto metadata](https://research.aalto.fi/en/publications/on-the-minimum-size-of-4-uniform-hypergraphs-without-property-b/).
* Markus Kirchweger, Tomáš Peitl, and Stefan Szeider, “Co-Certificate Learning with SAT Modulo Symmetries,” *IJCAI 2023*, 1944--1953. [PDF](https://www.ijcai.org/proceedings/2023/0216.pdf).
* Daniel M. Gordon, *La Jolla Coverings Repository* dataset (updated 2026-04-24). [Zenodo](https://zenodo.org/records/19735294), [source](https://github.com/dmgordo/LJCR), [tables](https://ljcr.dmgordon.org/cover/table.html).

## Audit limitations

This audit used the official Erdős Problems database, primary papers/preprints, institutional repositories, author/publisher pages, conference material, and the official covering repositories. The paywalled/full-text presentation of the 2014 Östergård article did not expose a public code/certificate artifact, and the 2024 Grill--Linzmayer heuristic manuscript is not publicly available. Those two gaps should be resolved by author contact before a definitive “no prior computation” statement is made.
