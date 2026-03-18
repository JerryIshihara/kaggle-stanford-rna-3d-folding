# validator

## Purpose

Cross-validation, leakage prevention, split generation, metric computation, local leaderboard estimation, ablation support, and model comparison support.

## Current Responsibilities

- RMSD metric computation (per-sample and fold-level)
- Cross-validation fold generation (GroupKFold for leakage prevention)
- Fold-level aggregation and statistics

## Active Files

| File | Description |
|------|-------------|
| `metrics.py` | RMSD computation, per-sample scoring, fold-level aggregation |
| `splitter.py` | Cross-validation fold generation with leakage prevention |

## Iteration History

| Iteration ID | File / Function / Feature | Description | Status | Research | Plan | Report |
|-------------|--------------------------|-------------|--------|----------|------|--------|
| *(none yet)* | | | | | | |

## Deprecated / Rejected Artifacts

*(none yet)*
