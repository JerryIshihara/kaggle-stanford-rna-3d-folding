# SUB004 -- Train-Data Template-Based Prediction

**Submission ID**: SUB004
**Kernel**: jerryishihara/stanford-rna-3d-template-refinement
**Lineage**: IT001 → IT002 → SUB001-SUB003 (all failed) → SUB004

## Key Changes from SUB003

| Change | Why |
|--------|-----|
| Use competition train data as templates (2671+ seqs) | External PDB DB was empty (0 chains) |
| No external dataset dependency | `rna-pdb-template-db` was broken |
| No neural refinement | Pure template matching, simpler and more robust |
| Chain-aware prediction via stoichiometry parsing | Handles multi-chain RNA complexes |
| Structural constraints (bond distances, steric) | Enforce realistic C1' geometry |
| Diversity via hinge/jitter/wiggle transforms | Better best-of-5 TM-score coverage |
| Diagnostic file listing on startup | Debug data access issues |
| Robust path detection | Search multiple candidate paths |

## Method

1. Load `train_sequences.csv` + `train_labels.csv` as template library (~2671 seqs)
2. K-mer prefilter (5-mers, Jaccard similarity) for fast candidate retrieval
3. Optional NW alignment scoring for short sequences (< 5M cells)
4. Full NW alignment + coordinate transfer for top template(s)
5. Gap interpolation for unaligned residues
6. RNA structural constraints (C1' bond distance ~5.95Å, steric repulsion)
7. 5 diverse structures: best match, noise, hinge, jitter, wiggle

## Artifacts

- `submission_SUB004.ipynb` -- the submission notebook
- `kernel-metadata.json` -- points to SUB004, no internet, no external datasets
- `analysis/SUB003_postmortem.md` -- documents SUB003 failure analysis
- `research/research_IT004_train_template.md` -- research notes
- `plans/plan_IT004_train_template.md` -- implementation plan
