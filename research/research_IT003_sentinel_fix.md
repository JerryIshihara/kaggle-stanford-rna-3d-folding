# Research — IT003: Sentinel Value Fix and Submission Pipeline

## Iteration ID
IT003

## Title
Fix sentinel value handling in training data and establish working competition submission pipeline

## Target Module(s)
- `submissions/` — Fixed notebook with sentinel filtering and robust data paths
- `optimizer/` — Training data quality improvements

## Research Question
Why does the SUB002 refinement training still produce astronomical loss values (~10^34) despite the normalization fix, and why did the v3 kernel fail to load any data?

## Background / Context
SUB001 had training loss = inf due to raw PDB coordinates overflowing Conv1d and BatchNorm instability. SUB002 attempted to fix this with coordinate normalization and InstanceNorm1d. While loss changed from inf to ~10^34, it's still completely unusable. The refinement model never converged, and predictions fell back to pure template coordinates. Additionally, no submission was ever made to the competition.

Three kernels exist on Kaggle:
- v1 (`stanford-rna-3d-template-neural-refinement`): loss=inf, never submitted
- v2 (`stanford-rna-3d-template-neural-refinement-v2`): loss=~10^34, never submitted
- v3 (`stanford-rna-3d-template-neural-refinement-v3`): failed to load data, no output

## Findings

### Bug 1: Sentinel Values in validation_labels.csv (CRITICAL)

**Root cause identified**: `validation_labels.csv` uses `-1e18` as a sentinel value for missing/invalid coordinates. The training data builder checks for `np.isnan()` but `-1e18` is **not NaN** — it's a finite float. Result: sentinel values pass all quality checks and enter the training loop.

**Data analysis**:
| Structure | Valid rows | Sentinel rows | Coverage |
|-----------|-----------|---------------|----------|
| 1 (x_1..z_1) | 8,815 | 947 | 90.3% |
| 2 (x_2..z_2) | 2,275 | 7,487 | 23.3% |
| 3 (x_3..z_3) | 256 | 9,506 | 2.6% |
| 4 (x_4..z_4) | 71 | 9,691 | 0.7% |
| 5 (x_5..z_5) | 71 | 9,691 | 0.7% |

Some targets are particularly affected: `9MME` has 472 sentinel values in structure 1 out of 4,640 rows (10.2%). After centroid subtraction and scale division, the normalized sentinel becomes `(-1e18 - centroid) / scale ≈ -1e16`, causing MSE loss ≈ 10^32 per residue.

**Fix**: Filter out residues where any coordinate component < -1e15 before including in ground truth. Apply per-residue masking so loss is only computed on valid residues.

### Bug 2: V3 Kernel Data Path Failure

**Root cause**: The v3 notebook uses `BASE = "/kaggle/input/stanford-rna-3d-folding-2"` but competition data when linked via `competition_sources` in kernel-metadata.json may be mounted at `/kaggle/input/competitions/stanford-rna-3d-folding-2` (a different path than v2 which correctly used the `/competitions/` prefix). Additionally, v3 attempted to load a pre-built template DB from `/kaggle/input/rna-pdb-template-db` which didn't exist.

**Fix**: Implement robust path detection that tries multiple known Kaggle mount points.

### Bug 3: No Competition Submission

`kaggle kernels push` runs the notebook as a standalone kernel but does NOT submit output to the competition. The output CSV must be explicitly submitted.

**Fix**: The notebook must be linked to the competition on Kaggle and submitted through the Kaggle UI or API.

### Insight: Validation Data Has 40 Structures

The validation_labels.csv has columns for 40 structures (x_1..x_40), not just 5. However, only structures 1-2 have meaningful coverage. Structure 1 alone covers 90.3% of residues and should be the primary training target.

## Candidate Ideas

1. **Filter sentinel values with threshold < -1e15** — Immediate fix for loss explosion
2. **Per-residue masking** — Only compute loss on valid residues
3. **Focus on structure 1** — Highest coverage (90.3%), most reliable ground truth
4. **Robust Kaggle path detection** — Try multiple paths to handle Kaggle mount variations
5. **Use all 40 structures for training data augmentation** — More diverse training signal where available

## Expected Impact
- Training loss drops from ~10^34 to a reasonable value (< 100)
- Refinement model actually learns, improving upon pure template predictions
- First actual competition submission with a real score

## Risks / Assumptions
- Coordinate normalization approach may still need tuning even after sentinel fix
- Template predictions alone (without refinement) may already be competitive
- 28 training samples is very small; refinement may overfit

## Source Links
- SUB001 post-mortem: `analysis/SUB001_postmortem.md`
- SUB002 metadata: `submissions/submission_SUB002.md`
- Kaggle v2 kernel log: analyzed from `kaggle kernels output`
- Kaggle v3 kernel log: analyzed from `kaggle kernels output`
- Competition data: `kaggle competitions files stanford-rna-3d-folding-2`

## Recommended Next Action
Implement the sentinel fix, per-residue masking, and robust path detection in a new SUB003 notebook. Test locally with downloaded competition data, then push to Kaggle and submit.
