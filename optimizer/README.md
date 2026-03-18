# optimizer

## Purpose

Training loop, loss functions, optimizer/scheduler logic, checkpoint saving policy, fine-tuning strategy, pseudo-labeling, curriculum learning, and augmentation policy during training.

## Current Responsibilities

- Training loop with epoch handling, gradient clipping, early stopping
- RMSD loss function (competition metric)
- MSE loss fallback
- Checkpoint saving with iteration traceability

## Active Files

| File | Description |
|------|-------------|
| `trainer.py` | Training loop with epoch handling, gradient clipping, checkpoint saving, early stopping |
| `losses.py` | RMSD loss function and MSE fallback |

## Iteration History

| Iteration ID | File / Function / Feature | Description | Status | Research | Plan | Report |
|-------------|--------------------------|-------------|--------|----------|------|--------|
| *(none yet)* | | | | | | |

## Deprecated / Rejected Artifacts

*(none yet)*
