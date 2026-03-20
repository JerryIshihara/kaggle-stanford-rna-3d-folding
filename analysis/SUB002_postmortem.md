# SUB002 Post-Mortem Analysis

**Kernel**: jerryishihara/stanford-rna-3d-template-neural-refinement-v2
**Status**: COMPLETE (ran to finish, refinement failed, fallback used)
**Runtime**: ~45 minutes on NVIDIA P100 GPU
**Leaderboard score**: None (cannot submit: internet was enabled)

## Execution Summary

| Stage | Result | Time |
|-------|--------|------|
| Data loading | OK | 0.3s |
| Template DB build | OK -- 3721 chains | ~14 min |
| Val template predictions | OK -- 28/28 | ~12 min |
| Training data construction | OK -- 28 samples | instant |
| Refinement training | **FAILED** -- loss ~7.5e33 | ~8s |
| Test predictions (cached) | OK -- 28/28 targets | ~12 min |
| Submission CSV | OK -- 9762 rows, 0 NaN | ~3s |

## What Changed from SUB001

| Fix | Result |
|-----|--------|
| `normalize_coords()` | Loss went from inf to ~7.5e33 (finite but still pathological) |
| `InstanceNorm1d` replacing `BatchNorm1d` | No more NaN from batch stats, but didn't fix root cause |
| Cached template predictions | Test inference ~12 min vs 58 min (5x speedup) |
| Convergence guard | Correctly detected failure, fell back to pure template |

## Bug: Training Loss ~7.5e33

### Symptom

```
Epoch   1/25  loss=21912079152914031805627084811796480.000000
Epoch   5/25  loss=18796263071463117707196506778370048.000000
Epoch  10/25  loss=20353091294961906265704755579846656.000000
Epoch  15/25  loss=7506128419762354635806818802073600.000000
Epoch  20/25  loss=12057296429843558384947343426322432.000000
Epoch  25/25  loss=18259238587362543306393142320693248.000000
```

### Root Cause

The normalization fixed infinity but the model's randomly initialized head produces large deltas. After 6 residual blocks with ReLU activations and residual connections, activations can grow unboundedly. The head layer with random weights converts these large activations into enormous delta predictions, causing:

1. `pred = tpl_normed + delta` where delta >> 1
2. `(pred - gt_normed)^2` = astronomically large
3. Gradient signal is dominated by outliers
4. Model cannot recover through normal gradient descent

The `scale` floor in `normalize_coords` was set to `1e-8`, which for short sequences with near-zero variance means `gt_normed = (gt - centroid) / 1e-8` = enormous values.

### Additional Issue: Internet Blocking Submission

The competition requires `enable_internet: false` for code submission. SUB002 had `enable_internet: true` because `build_database()` downloads from RCSB at runtime. Even if the model worked perfectly, we couldn't submit.

## Fixes Applied in SUB003

| Issue | Fix |
|-------|-----|
| Random head init -> huge deltas | Zero-initialize head weights (initial delta = 0) |
| Unbounded delta output | `tanh(raw) * delta_scale` constrains output to [-2, 2] in normalized space |
| MSE sensitive to outliers | Huber loss (`SmoothL1Loss`) for robustness |
| Scale floor too small | `scale = max(np.std(centered), 1.0)` instead of `+ 1e-8` |
| Internet dependency | Pre-built template DB uploaded as Kaggle dataset |
| ReLU accumulation in residuals | GELU activation + Kaiming initialization |
| 6 residual blocks (too deep) | Reduced to 4 blocks |
| Learning rate 3e-4 too high | Reduced to 1e-4 |
