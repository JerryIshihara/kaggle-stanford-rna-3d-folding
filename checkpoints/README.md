# Checkpoints

## Purpose

Store saved model weights, training states, and ensemble artifacts with full traceability to the iteration and report that produced each checkpoint.

## Checkpoint Registry

| Checkpoint File | Iteration ID | Model Summary | Training Config | Validation Result | Reason Saved | Report Link |
|----------------|-------------|---------------|----------------|-------------------|-------------|-------------|
| *(none yet)* | | | | | | |

## Naming Convention

```
checkpoints/<ITERATION_ID>_<description>.pt
```

`<ITERATION_ID>` includes a 4-character disambiguator for parallel-safety, e.g. `IT004_m2k7`.
Legacy IDs without a disambiguator remain valid.
Always append new rows to the **end** of the table above to minimize merge conflicts.

Examples:
- `checkpoints/IT004_m2k7_best_fold0.pt`
- `checkpoints/IT004_m2k7_best_fold1.pt`
- `checkpoints/IT005_b3x8_ensemble_v1.pt`
