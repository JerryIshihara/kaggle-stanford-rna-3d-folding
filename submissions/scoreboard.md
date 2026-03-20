# Submission Scoreboard

Master scoreboard for full-pipeline performance tracking.

## Scoreboard

| Submission ID | Data Version | Inferencer Version | Optimizer Version | Validator Version | Checkpoints | Local CV | Public LB | Private LB | Rank | Status | Notes |
|--------------|-------------|-------------------|------------------|------------------|-------------|----------|-----------|-----------|------|--------|-------|
| SUB001 | IT002 | IT002 (C1' fix) | SUB001 (inline) | N/A | N/A | N/A | N/A | N/A | - | FAILED | Training loss=inf (normalization bug), not submitted to competition |
| SUB002 | IT002 | IT002 (C1' fix) | SUB002 (fixed) | N/A | N/A | N/A | 0.211 | Pending | - | SUBMITTED | Fixed: InstanceNorm, coord normalization, cached inference |
| SUB003 | IT002 | IT004 (ResNet + Transformer) | SUB003 (inline) | N/A | N/A | N/A | 0.246 | Pending | - | SUBMITTED | Multi-model ensemble: expanded templates, ResNet + Transformer refinement |
| SUB004 | IT002 | IT004 + SUB004 (length-aware) | SUB004 (TM-aware) | SUB004 (TM-score) | N/A | N/A | Pending | Pending | - | SUBMITTED | Length-aware ensemble, TM-aware loss, iterative refinement, SS-guided fallback |
| SUB005 | IT005 | IT005 (multi-template) | N/A | N/A | N/A | N/A | Pending | Pending | - | SUBMITTED | Multi-template diversity, Kabsch blend, helical gaps, TM-score validation |

## Status Definitions

- **DRAFT**: Assembled but not yet validated locally
- **READY**: Validated locally, ready for Kaggle submission
- **SUBMITTED**: Uploaded to Kaggle
- **BEST_CURRENT**: Current best-performing submission
- **SUPERSEDED**: Replaced by a better submission
- **ARCHIVED**: No longer relevant
