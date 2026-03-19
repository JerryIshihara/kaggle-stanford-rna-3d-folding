# SUB003 Post-Mortem Analysis

**Kernel**: jerryishihara/stanford-rna-3d-template-neural-refinement-v3
**Status**: COMPLETE (execution finished, but no valid submission generated)
**Runtime**: ~14 seconds on NVIDIA GPU
**Leaderboard score**: None (no predictions generated)

## Execution Summary

| Stage | Result | Time |
|-------|--------|------|
| Data loading | **FAILED** — 0 CSVs found | 0.3s |
| Template DB loading | **FAILED** — 0 chains loaded | instant |
| Training data construction | SKIPPED (no data) | - |
| Refinement training | SKIPPED (no data) | - |
| Test predictions | SKIPPED (no test sequences) | - |
| Submission CSV | NOT GENERATED | - |

## Root Causes

### Issue 1: Template DB Empty (0 chains)

The dataset `jerryishihara/rna-pdb-template-db` contained 499 individual JSON files
but **NO `template_index.pkl`** file. The `PDBRNADatabase.__init__` method only loads
from `template_index.pkl`, so with it missing, 0 chains were loaded.

With `enable_internet: false`, the fallback `build_database()` could not download from
RCSB, resulting in an empty template library.

**Fix applied**: Rebuilt `template_index.pkl` (1081 chains) from JSON files and uploaded
to the dataset as a new version.

### Issue 2: Competition Data Files Not Found

```
WARNING: test_sequences not found at /kaggle/input/stanford-rna-3d-folding-2/test_sequences.csv
WARNING: sample_submission not found at /kaggle/input/stanford-rna-3d-folding-2/sample_submission.csv
WARNING: validation_sequences not found at /kaggle/input/stanford-rna-3d-folding-2/validation_sequences.csv
WARNING: validation_labels not found at /kaggle/input/stanford-rna-3d-folding-2/validation_labels.csv
```

The kernel metadata correctly specifies `competition_sources: ["stanford-rna-3d-folding-2"]`,
and the Kaggle API can download these files. The root cause is unclear — possibly
a dataset versioning delay, kernel metadata processing issue, or competition data
mount timing issue.

### Issue 3: Wrong Template Strategy

Even if both issues above were fixed, the approach has a fundamental flaw: using an
external PDB template DB (1081 chains) instead of the competition's **train data**
(5716 sequences with ground-truth 3D coordinates). The competition provides
`train_sequences.csv` + `train_labels.csv` with real RNA structures that are far
more relevant templates.

Public notebooks achieving TM-score 0.2-0.4+ all use the competition's own training
data as their template library.

## Comparison with Successful Public Notebooks

| Feature | Our SUB003 | Public Template Notebook |
|---------|-----------|------------------------|
| Template source | External PDB (broken) | Competition train data (5716 seqs) |
| Alignment | Custom NW (Python, slow) | BioPython PairwiseAligner (C, fast) |
| Prefilter | k-mer Jaccard | Length ratio + k-mer Jaccard |
| Coordinate transfer | NW-based | Alignment block transfer |
| Chain awareness | None | Stoichiometry-aware segments |
| Diversity | MC-dropout + noise | Hinge/jitter/wiggle transforms |
| Structural constraints | None | Bond distance + steric constraints |
| Internet required | No (but DB was empty) | No |

## Critical Fixes for SUB004

1. **Use competition train data as template library** — 5716 sequences vs 1081 PDB chains
2. **Add diagnostic file listing** — print contents of `/kaggle/input/` to debug data access
3. **Add chain-aware prediction** — handle multi-chain RNA complexes
4. **Add structural constraints** — enforce realistic C1' bond distances (~5.95Å)
5. **Better diversity generation** — hinge, jitter, wiggle transforms instead of just noise
6. **Remove dependency on external dataset** — no `rna-pdb-template-db` needed
7. **Add robust error handling** — fallback strategies at every stage
