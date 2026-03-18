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

Examples:
- `checkpoints/IT002_best_fold0.pt`
- `checkpoints/IT002_best_fold1.pt`
- `checkpoints/IT002_ensemble_v1.pt`
