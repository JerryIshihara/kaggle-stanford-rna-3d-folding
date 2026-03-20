# SUB002 Post-Mortem Analysis

**Kernel**: jerryishihara/stanford-rna-3d-template-neural-refinement-v2
**Status**: COMPLETE (ran to finish, but refinement training had astronomical loss)
**Runtime**: ~85 minutes on NVIDIA T4 GPU
**Leaderboard score**: None (never submitted to competition)

## Execution Summary

| Stage | Result | Details |
|-------|--------|---------|
| Data loading | OK | 28 test, 28 val targets, 9762 residues |
| Template DB build | OK | 2000 entries queried, 3721 chains indexed |
| Val template predictions | OK | 28/28 targets predicted |
| Training data construction | OK (but buggy) | 28 samples built, 0 skipped, sentinel values included |
| Refinement training | **FAILED** | loss ~10^34 all 25 epochs |
| Test template predictions | OK | 28/28 targets predicted |
| Submission CSV | OK | 9762 rows, 0 NaN |

## Root Cause: Sentinel Values in Training Data

The normalization fix from SUB001 (centroid subtraction + scale division) was necessary but not sufficient. The real problem was **sentinel values (-1e18) in validation_labels.csv** being treated as valid coordinates.

### Data Analysis

| Metric | Value |
|--------|-------|
| Total residues in val_labels | 9,762 |
| Sentinel values in structure 1 | 947 (9.7%) |
| Targets with sentinel in struct 1 | 12/28 (42.9%) |
| Worst target (9J09) | 46.7% sentinel |
| Sentinel value | exactly -1e18 |
| Is NaN? | No (finite float) |
| Is finite? | Yes |

### Why the Code Missed It

```python
vals = row[cols].values.astype(np.float64)
if not np.any(np.isnan(vals)):  # sentinel passes this check!
    gt[idx] = vals
```

The `-1e18` value is not NaN, so it passes the NaN check. After centroid subtraction (centroid ≈ ~100) and scale division (scale ≈ ~50), the normalized sentinel becomes `(-1e18 - 100) / 50 ≈ -2e16`. The MSE loss on this single residue is `(pred - (-2e16))^2 ≈ 4e32`, which dominates the entire batch.

### Additional Contributing Factors

The model's randomly initialized head produces large deltas. After 6 residual blocks with ReLU activations and residual connections, activations can grow unboundedly. The `scale` floor in `normalize_coords` was set to `1e-8`, which for short sequences with near-zero variance means enormous normalized values.

The competition also requires `enable_internet: false` for code submission. SUB002 had `enable_internet: true` because `build_database()` downloads from RCSB at runtime. Even if the model worked perfectly, we couldn't submit.

### V2 Training Log

```
Epoch   1/25  loss=21912079152914031805627084811796480.000000
Epoch   5/25  loss=18796263071463117707196506778370048.000000
Epoch  10/25  loss=20353091294961906265704755579846656.000000
Epoch  15/25  loss=7506128419762354635806818802073600.000000
Epoch  25/25  loss=18259238587362543306393142320693248.000000
Training complete. Best loss: 7506128419762354635806818802073600.000000
```

The loss fluctuates because different random structure selections bring different targets (with/without sentinels) into each epoch. The model never converges.

### V2 Output Quality

Despite the failed refinement, the submission CSV was still valid because the fallback path used pure template predictions:
- Shape: (9762, 18), 0 NaN
- Coordinate range: x_1 [-40.6, 151.9], y_1 [-46.4, 240.5], z_1 [-69.1, 1334.8]
- All 28 targets predicted
- **Never submitted to competition**

## V3 Kernel Failure

The v3 kernel (`stanford-rna-3d-template-neural-refinement-v3`) failed completely:
- Used path `/kaggle/input/stanford-rna-3d-folding-2/` (without `competitions/` prefix)
- Tried to load template DB from `/kaggle/input/rna-pdb-template-db` (non-existent dataset)
- Result: 0 templates, 0 test sequences, 0 predictions, empty submission

## Fixes Applied in SUB003

| Issue | Fix |
|-------|-----|
| Sentinel values (-1e18) treated as valid | Filter residues where any coord < -1e15 |
| No masking for missing ground truth | Per-residue binary mask in loss computation |
| Random head init -> huge deltas | Zero-initialize head weights (initial delta = 0) |
| Unbounded delta output | `tanh(raw) * delta_scale` constrains output to [-2, 2] in normalized space |
| MSE sensitive to outliers | Huber loss (`SmoothL1Loss`) for robustness |
| Scale floor too small | `scale = max(np.std(centered), 1.0)` instead of `+ 1e-8` |
| Internet dependency | Pre-built template DB uploaded as Kaggle dataset |
| ReLU accumulation in residuals | GELU activation + Kaiming initialization |
| 6 residual blocks (too deep) | Reduced to 4 blocks |
| Learning rate 3e-4 too high | Reduced to 1e-4 |
| Wrong competition data path | Robust path detection trying multiple mount points |
| `kaggle kernels push` ≠ competition submit | Document proper submission process |

Local test confirms: loss drops from ~10^34 to ~23 (normalized MSE), and decreases over epochs.
