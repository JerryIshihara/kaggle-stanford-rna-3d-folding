# Report — IT003: Sentinel Value Fix and Submission Pipeline

## Iteration ID
IT003

## Title
Fix sentinel value handling in training data and establish working competition submission pipeline

## Target Module(s)
- `submissions/` — SUB003 notebook
- `optimizer/` — Training data quality

## Files Changed

| File | Action | Description |
|------|--------|-------------|
| `submissions/submission_SUB003.ipynb` | CREATED | New notebook with sentinel fix, masked loss, robust paths |
| `submissions/submission_SUB003.md` | CREATED | Submission metadata and traceability |
| `submissions/kernel-metadata.json` | MODIFIED | Updated to point to SUB003 notebook |
| `research/research_IT003_sentinel_fix.md` | CREATED | Root cause analysis of loss explosion |
| `plans/plan_IT003_sentinel_fix.md` | CREATED | Implementation plan |

## Functions/Features Changed

| Function | Change |
|----------|--------|
| `build_training_data()` | Added sentinel filter: skip residues where any coord < -1e15 |
| `build_training_data()` | Returns `valid_mask_list` alongside `gt_coords_list` |
| `build_training_data()` | Lowered coverage threshold from 50% to 30% |
| `train_refinement()` | Per-residue masked loss: `(sq_err * mask).sum() / (mask.sum() * 3)` |
| `train_refinement()` | Added loss clamping: skip batches with loss > 1e6 |
| Cell 1 (config) | Robust path detection for competition data (tries 2 mount points) |
| Cell 1 (config) | Template DB path detection (tries pre-built dataset, falls back to fresh build) |
| Cell 1 (config) | Reduced LR from 3e-4 to 1e-4, increased epochs from 25 to 40 |

## Experiment Setup

### Local Validation
- Downloaded competition data (`test_sequences.csv`, `sample_submission.csv`, `validation_sequences.csv`, `validation_labels.csv`)
- Tested sentinel filtering on all 28 targets
- Tested training loop with mock template predictions on 10 targets for 5 epochs

### Kaggle Run
- Pushed SUB003 notebook via `kaggle kernels push`
- Kernel: `jerryishihara/stanford-rna-3d-template-refinement`

## Metrics

### Local Test Results

| Metric | SUB002 (before fix) | IT003 local (after fix) |
|--------|--------------------|--------------------|
| Training loss epoch 1 | ~2.2 × 10^34 | ~23.8 |
| Training loss epoch 5 | ~1.8 × 10^34 | ~22.6 |
| Loss finite? | No (falls back) | Yes |
| Refinement model usable | False | True |
| Sentinel residues filtered | 0 | 21,224 |

### Kaggle Kernel Results (SUB003)

| Metric | Value |
|--------|-------|
| Device | NVIDIA T4 GPU (cuda) |
| Template DB | 3,721 chains from 2,000 PDB entries |
| Training samples | 28 |
| Sentinel residues filtered | 37,322 |
| **Training loss epoch 1** | **63.37** |
| **Training loss epoch 40** | **41.94** |
| **Best training loss** | **40.57** |
| **Refinement model usable** | **True** |
| Submission rows | 9,762 |
| NaN values | 0 |
| Total runtime | ~40 minutes |

### Training Convergence (Kaggle Run)

```
Epoch   1/40  loss=63.37  best=63.37
Epoch   5/40  loss=60.05  best=59.44
Epoch  10/40  loss=52.18  best=52.18
Epoch  15/40  loss=49.53  best=48.41
Epoch  20/40  loss=46.61  best=44.46
Epoch  25/40  loss=43.57  best=42.69
Epoch  30/40  loss=41.26  best=41.26
Epoch  35/40  loss=42.02  best=40.67
Epoch  40/40  loss=41.94  best=40.57
```

Loss decreased steadily from 63.4 to 40.6 over 40 epochs — the model actually converged.

### Validation Data Analysis

| Metric | Value |
|--------|-------|
| Total residues | 9,762 |
| Sentinel in struct 1 | 947 (9.7%) |
| Targets with sentinel in struct 1 | 12/28 (42.9%) |
| Worst target (9J09) | 46.7% sentinel in struct 1 |

## Comparison vs Previous

| Aspect | SUB001 | SUB002 | SUB003 |
|--------|--------|--------|--------|
| Training loss | inf | ~10^34 | **40.57** |
| Normalization | None | Centroid + scale | Centroid + scale |
| Norm layer | BatchNorm | InstanceNorm | InstanceNorm |
| Sentinel handling | None | None | **Filtered + masked** |
| Refinement usable | No | No | **Yes** |
| Competition submission | None | None | Notebook pushed; needs UI submission |

## Outcome Classification
**PROMOTED** — The sentinel fix completely resolves the training loss explosion. The refinement model converges on Kaggle with loss decreasing from 63.4 to 40.6. The notebook is ready for competition submission through the Kaggle UI.

## Decision and Follow-up

### Immediate
1. **Submit notebook to competition through Kaggle UI** — the notebook (`stanford-rna-3d-template-refinement`) has completed successfully and needs to be submitted via the competition's submission interface
2. Record first competition score

### Future Iterations
1. **IT004**: Explore using all 40 validation structures for data augmentation (currently only struct 1 has >30% coverage)
2. **IT005**: Investigate MSA features for template-free predictions
3. **IT006**: Evaluate whether refinement actually improves TM-score over pure template baseline
4. Consider uploading template DB as a Kaggle dataset to speed up future kernel runs (~14 min saved)
5. Lower the validation mask threshold or implement Kabsch alignment between predicted and ground truth before computing loss
