# Plan — IT003: Sentinel Value Fix and Submission Pipeline

## Iteration ID
IT003

## Title
Fix sentinel value handling, improve training robustness, submit to competition

## Target Module(s)
- `submissions/` — New SUB003 notebook
- `optimizer/` — Training data quality

## Hypothesis
The refinement model fails because sentinel values (-1e18) in validation_labels.csv are treated as valid coordinates. Filtering these out and adding per-residue masking will allow the model to train successfully (loss < 100) and produce coordinate corrections that improve upon pure template predictions. Combined with a valid competition submission, this should yield our first competition score.

## Files to Create/Modify

| File | Action | Description |
|------|--------|-------------|
| `submissions/submission_SUB003.ipynb` | CREATE | New notebook with sentinel fix and robust paths |
| `submissions/submission_SUB003.md` | CREATE | Submission metadata |
| `submissions/kernel-metadata.json` | MODIFY | Point to SUB003 notebook |

## Exact Changes

### 1. Sentinel Value Filter (build_training_data)
- Add check: `if np.any(vals < -1e15): continue` when reading validation label coordinates
- This skips residues with sentinel values instead of treating them as valid

### 2. Per-Residue Loss Masking (train_refinement)
- Create binary mask for valid residues (non-zero, non-sentinel ground truth)
- Apply mask to MSE loss so only valid residues contribute to gradient
- Formula: `loss = ((pred - gt) ** 2 * mask).sum() / mask.sum()`

### 3. Robust Data Path Detection
- Try multiple paths: `/kaggle/input/competitions/stanford-rna-3d-folding-2`, `/kaggle/input/stanford-rna-3d-folding-2`, `data/raw`
- Use first path that exists

### 4. Training Improvements
- Focus training on structure 1 (highest coverage at 90.3%)
- Use structures 2-5 only when available and valid, as augmentation
- Add gradient clipping and loss clamping for extra safety
- Increase epochs from 25 to 40 since data is now clean

### 5. Build template DB from cache or fresh
- Try loading from Kaggle dataset first, fall back to building from RCSB API
- Save template DB to Kaggle output for future reuse

## Expected Metric Impact
- Training loss: from ~10^34 → < 10 (normalized MSE)
- Prediction quality: moderate improvement over pure template (TM-score +0.01-0.05)
- First competition submission with actual score

## Evaluation Plan
1. Local test: Run training data construction with downloaded competition data, verify no sentinel values in training tensors
2. Local test: Run 5-epoch training, verify loss decreases normally
3. Push notebook to Kaggle and run
4. Submit to competition and check score

## Rollback Plan
If refinement still fails, the notebook falls back to pure template predictions (same as SUB002 output).

## Linked Research
[research/research_IT003_sentinel_fix.md](../research/research_IT003_sentinel_fix.md)
