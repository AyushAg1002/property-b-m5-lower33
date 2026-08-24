# Submission checklist

Complete every item below before calling the manuscript or artifact submitted.
Unchecked boxes identify the remaining archive and journal handoff steps.

## Responsible authorship and mathematical verification

- [x] Add every human author's full name, affiliation, email, and ORCID.
- [x] Remove `Anonymous draft for review` unless the chosen journal explicitly
      requires an anonymous review file; keep a separate identified source.
- [x] A responsible human author has personally read and verified every proof
      step, program claim, certificate interface, and reported computation.
- [x] At least one independent combinatorics expert has reviewed the
      normalization lemma, locked-permutation lemma, and all five finite cases.
- [x] Record and disclose the AI assistance accurately under the
      target journal's current authorship and research-integrity policies.
- [x] Do not list an AI system as an author or imply that human verification
      has occurred when it has not.

The Electronic Journal of Combinatorics policy was rechecked on 2026-08-24.
Its author-responsibility requirements are reflected in the manuscript and
the separate human-verification record.

## Novelty and citations

- [x] Repeat the primary-source novelty search immediately before submission
      and record its cutoff date in the manuscript and novelty audit.
- [ ] Contact the authors of the previous `m(5)>=32` result to ask about
      overlapping unpublished work.
- [x] Verify every bibliography field, theorem attribution, URL, DOI, and
      claimed historical bound against the primary source.
- [x] Confirm that no newer preprint or publication already proves
      `m(5)>=33` or a stronger result.

## Frozen artifact and metadata

- [x] Choose and install the licenses described in `LICENSES/README.md`.
- [x] Create and validate `CITATION.cff`.
- [x] Fix the public repository, immutable release tag `v1.0.0`, and reserved
      Zenodo DOI `10.5281/zenodo.22070117` in the manuscript and citation
      metadata.
- [ ] Publish the exact `v1.0.0` archive at the reserved Zenodo DOI and verify
      that the DOI resolves to that release.
- [x] Rebuild `SHA256SUMS` and both distributable archives after the final
      metadata and manuscript changes.
- [x] Confirm that E-JC's initial submission is identified rather than
      double-blind.

## Final mechanical checks

- [x] Compile the identified manuscript from the arXiv/source archive in a
      clean TeX environment; inspect every rendered page visually.
- [x] Run `python3 verify_lower33_artifact.py` and
      `python3 verify_lower33_artifact.py --full` and retain complete transcripts.
- [ ] Have a second person independently rerun the exact verifier on a
      different machine and record OS, Python version, wall time, and archive
      SHA-256.
- [x] Check that all displayed fractions, row counts, and hashes in the paper
      match the final reports and manifests.
- [ ] Upload the source archive, computational artifact, and availability
      statement required by the chosen venue.

## E-JC initial-submission handoff

The current target is The Electronic Journal of Combinatorics.  Its public
instructions require an initial identified PDF, author metadata entered in
the web system, and a standalone HTML abstract; source files are requested
only after acceptance.  The current official instructions and AI policy must
be rechecked on the actual submission date.

- [x] Prepare an E-JC-compatible standalone HTML abstract.
- [x] Prepare author-metadata, editor-note, and human-attestation templates.
- [x] Add a fail-closed mechanical readiness checker.
- [x] Create final `submission/ejc/AUTHOR_METADATA.md` from the template.
- [x] Create final `submission/ejc/COMMENTS_FOR_EDITOR.txt` from the template.
- [x] Create final `submission/ejc/HUMAN_VERIFICATION_RECORD.md` from the
      template, completed personally by the responsible author.
- [x] Run `python3 submission/ejc/check_readiness.py` and retain its PASS
      output.
- [ ] Enter every author's name, affiliation and email using literal Unicode
      accents and the agreed author order in E-JC's web form.
- [ ] Paste `submission/ejc/HTML_ABSTRACT.txt` into the HTML abstract field.
- [ ] Upload only the final identified manuscript PDF as the initial article,
      unless the authenticated workflow explicitly requests another file.
