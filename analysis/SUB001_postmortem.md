# SUB001 Post-Mortem Analysis

**Kernel**: jerryishihara/stanford-rna-3d-template-neural-refinement (v1)
**Status**: COMPLETE (ran to finish, but refinement training failed)
**Runtime**: ~85 minutes on NVIDIA T4 GPU
**Leaderboard score**: None (not submitted to competition)

## Execution Summary

| Stage | Result | Time |
|-------|--------|------|
| Data loading | OK -- 28 test, 28 val targets, 9762 residues | 0.3s |
| Template DB build | OK -- 2000 entries queried, 3721 chains indexed | ~14 min |
| Val template predictions | OK -- 28/28 targets predicted | ~12 min |
| Training data construction | OK -- 28 samples built, 0 skipped | instant |
| Refinement training | **FAILED** -- loss = inf all 25 epochs | ~6s |
| Test template predictions | OK -- 28/28 targets predicted (x5 diverse) | ~58 min |
| Submission CSV | OK -- 9762 rows, 0 NaN | ~3s |

Total: ~85 min (within Kaggle 12-hour GPU limit)

## Bug 1: Training Loss = inf (CRITICAL)

### Symptom

All 25 training epochs produced `loss=inf`:
```
Epoch   1/25  loss=inf  best=inf  lr=2.99e-04
Epoch   5/25  loss=inf  best=inf  lr=2.71e-04
Epoch  10/25  loss=inf  best=inf  lr=1.96e-04
Epoch  15/25  loss=inf  best=inf  lr=1.04e-04
Epoch  20/25  loss=inf  best=inf  lr=2.86e-05
Epoch  25/25  loss=inf  best=inf  lr=0.00e+00
Training complete. Best loss: inf
```

### Root Cause Analysis

The refinement model receives 9 input features per residue:
- template_xyz (3): Raw PDB coordinates, range approximately -100 to +100 Angstroms
- onehot_ACGU (4): Values 0 or 1
- relative_position (1): Range 0 to 1
- confidence (1): Range 0 to 1

The coordinate features dominate by 2 orders of magnitude. When passed through `Conv1d(9, 128, 1)` with random initialization (weights ~ N(0, 0.01)), outputs can be in the range of hundreds. After 6 residual blocks with BatchNorm1d, the signal either:
1. Overflows to inf due to accumulated large activations
2. BatchNorm1d variance estimation is unstable with effective batch size = 1 (each training sample is processed individually)

### Fix

1. **Normalize coordinates**: Subtract centroid, divide by standard deviation before feeding to the model. Denormalize deltas after prediction.
2. **Replace BatchNorm1d with InstanceNorm1d**: InstanceNorm computes statistics per-sample per-channel, so it works correctly with batch_size=1.
3. **Clamp features**: Add `torch.clamp()` to prevent inf propagation.

### Impact

Because training loss was inf, the refinement model had random weights. All predictions were effectively `template_coords + random_noise`, making the refinement useless. The submission was pure template predictions corrupted by random deltas from an untrained model.

## Bug 2: No Competition Submission

### Symptom

`kaggle competitions submissions stanford-rna-3d-folding-2` returns "No submissions found".

### Root Cause

`kaggle kernels push` executes the notebook as a standalone kernel, but does NOT submit it to the competition. For code competitions, the notebook must be explicitly submitted through:
1. The Kaggle web UI (Competitions > Submit > Select Notebook)
2. Or the notebook must be linked to the competition and submitted via the competition's submission mechanism

### Fix

After the kernel finishes running, submit it via:
```bash
kaggle competitions submit -c stanford-rna-3d-folding-2 \
  -f /tmp/kaggle_output/submission.csv \
  -m "SUB001: Template + refinement pipeline"
```
Or directly submit the output from the kernel page.

## Issue 3: Slow Inference (58 min for 28 targets)

### Symptom

Test predictions took 58 minutes for only 28 targets. Estimated 125 seconds per target.

### Root Cause

Each call to `generate_5_structures(sequence)` calls `predict_refined()` 5 times. Each `predict_refined()` calls `template_model.predict(sequence)` which runs the full template search (k-mer pre-filter + Needleman-Wunsch alignment) against 3721 chains.

For a long sequence (e.g., 500 nt), Needleman-Wunsch against a 500 nt template takes O(250,000) operations. Multiplied by ~100 candidates * 5 predictions = 500 full alignments per target.

The 4th target took ~7 minutes alone (likely a long sequence like ribosomal RNA), causing the huge time estimate spikes in the progress bar.

### Fix

1. **Cache template predictions per target**: Run `template_model.predict()` once per target, then reuse the coordinates for all 5 diverse predictions.
2. **Limit alignment length**: Cap the Needleman-Wunsch DP matrix size (e.g., max 500x500). For longer sequences, use banded alignment.
3. **Reduce candidate count**: Tighten the k-mer pre-filter threshold or reduce `top_k * 5` candidate limit.

Expected speedup: 5x from caching alone (58 min -> ~12 min).

## Data Format Discovery

From the kernel log, the actual competition data format:

**test_sequences.csv** (28 rows, 8 columns):
- `target_id`, `sequence`, `temporal_cutoff`, `description`, `stoichiometry`, `all_sequences`, `ligand_ids`, `ligand_SMILES`

**sample_submission.csv** (9762 rows, 18 columns):
- `ID`, `resname`, `resid`, `x_1`, `y_1`, `z_1`, `x_2`, `y_2`, `z_2`, `x_3`, `y_3`, `z_3`, `x_4`, `y_4`, `z_4`, `x_5`, `y_5`, `z_5`

**validation_labels.csv** (9762 rows, 126 columns):
- `ID`, `resname`, `resid`, + 123 coordinate columns (likely more structure variants or additional annotations)

Key insight: val_labels has 126 columns vs sample_submission's 18. The extra columns likely contain multiple experimental structure conformations or additional metadata.

## Recommendations for SUB002

1. **Fix normalization**: Center + scale template coordinates before model input
2. **Fix BatchNorm**: Switch to InstanceNorm1d or GroupNorm
3. **Cache predictions**: Run template search once per target
4. **Submit to competition**: Use `kaggle competitions submit` or web UI
5. **Explore val_labels columns**: 126 columns suggests richer training signal than the 5 structures we assumed
6. **Consider**: If refinement still struggles, submit pure template predictions (which are already reasonable)

## Appendix: Key Log Lines

```
Device: cuda
Loaded test_sequences: (28, 8)
Loaded sample_submission: (9762, 18)
Loaded validation_sequences: (28, 8)
Loaded validation_labels: (9762, 126)
Found 2000 RNA entries.
Database built: 3721 chains total
Built 28 training samples, skipped 0.
Training complete. Best loss: inf
Submission saved to /kaggle/working/submission.csv
Shape: (9762, 18)
NaN values: 0
```
