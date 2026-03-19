# Submission Scoreboard

Master scoreboard for full-pipeline performance tracking.

## Scoreboard

| Submission ID | Data Version | Inferencer Version | Optimizer Version | Validator Version | Checkpoints | Local CV | Public LB | Private LB | Rank | Status | Notes |
|--------------|-------------|-------------------|------------------|------------------|-------------|----------|-----------|-----------|------|--------|-------|
| SUB001 | IT002 | IT002 (C1' fix) | SUB001 (inline) | N/A | N/A | N/A | N/A | N/A | - | FAILED | Training loss=inf (normalization bug), not submitted to competition |
| SUB002 | IT002 | IT002 (C1' fix) | SUB002 (fixed) | N/A | N/A | N/A | N/A | N/A | - | FAILED | Refinement loss ~1e34 due to sentinel values; fell back to pure template; never submitted |
| SUB003 | IT002 | IT002 (C1' fix) | SUB003 (sentinel fix) | N/A | N/A | Train loss: 40.6 | Pending | Pending | - | READY | Kernel complete; sentinel fix works; refinement converged; needs Kaggle UI submission |

## Status Definitions

- **DRAFT**: Assembled but not yet validated locally
- **READY**: Validated locally, ready for Kaggle submission
- **SUBMITTED**: Uploaded to Kaggle
- **BEST_CURRENT**: Current best-performing submission
- **SUPERSEDED**: Replaced by a better submission
- **ARCHIVED**: No longer relevant
