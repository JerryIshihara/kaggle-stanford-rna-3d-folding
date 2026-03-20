# Submission Scoreboard

Master scoreboard for full-pipeline performance tracking.

## Scoreboard

| Submission ID | Data Version | Inferencer Version | Optimizer Version | Validator Version | Checkpoints | Local CV | Public LB | Private LB | Rank | Status | Notes |
|--------------|-------------|-------------------|------------------|------------------|-------------|----------|-----------|-----------|------|--------|-------|
| SUB001 | IT002 | IT002 (C1' fix) | SUB001 (inline) | N/A | N/A | N/A | N/A | N/A | - | FAILED | Training loss=inf (normalization bug), not submitted to competition |
| SUB002 | IT002 | IT002 (C1' fix) | SUB002 (fixed) | N/A | N/A | N/A | FAILED | N/A | - | FAILED | Fixed norms but template DB empty |
| SUB003 | IT003 | Template matching | N/A | N/A | N/A | N/A | FAILED | N/A | - | FAILED | Template DB dataset had 0 chains |
| SUB004 | IT003 | Train-data templates | N/A | N/A | N/A | N/A | **0.211** | Pending | - | BEST_CURRENT | First successful submission! 2671 templates, 28/28 targets |
| SUB005 | IT004 | Multi-template + blend | N/A | N/A | N/A | N/A | RUNNING | Pending | - | SUBMITTED | 5 different templates, Kabsch blending |
| SUB006 | IT005 | Fragment assembly + per-chain | N/A | N/A | N/A | N/A | RUNNING | Pending | - | SUBMITTED | Fragment assembly, per-chain matching, coverage scoring |

## Status Definitions

- **DRAFT**: Assembled but not yet validated locally
- **READY**: Validated locally, ready for Kaggle submission
- **SUBMITTED**: Uploaded to Kaggle
- **BEST_CURRENT**: Current best-performing submission
- **SUPERSEDED**: Replaced by a better submission
- **ARCHIVED**: No longer relevant
