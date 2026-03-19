# Submission Scoreboard

Master scoreboard for full-pipeline performance tracking.

## Scoreboard

| Submission ID | Data Version | Inferencer Version | Optimizer Version | Validator Version | Checkpoints | Local CV | Public LB | Private LB | Rank | Status | Notes |
|--------------|-------------|-------------------|------------------|------------------|-------------|----------|-----------|-----------|------|--------|-------|
| SUB001 | IT002 | IT002 (C1' fix) | SUB001 (inline) | N/A | N/A | N/A | N/A | N/A | - | FAILED | Training loss=inf (normalization bug), not submitted to competition |
| SUB002 | IT002 | IT002 (C1' fix) | SUB002 (fixed) | N/A | N/A | N/A | N/A | N/A | - | FAILED | Loss ~7.5e33, internet blocking submission |
| SUB003 | IT002 | IT002 (C1' fix) | SUB003 (no-internet) | N/A | N/A | N/A | N/A | N/A | - | FAILED | Template DB empty (0 chains), competition data not found, no predictions |
| SUB004 | IT004 | IT004 (train template) | N/A | N/A | N/A | N/A | 0.211 | Pending | - | BEST_CURRENT | Train-data templates, chain-aware, structural constraints |
| SUB005 | IT005 | IT005 (multi-template) | N/A | N/A | N/A | N/A | Pending | Pending | - | SUBMITTED | Multi-template diversity, Kabsch blend, helical gaps, TM-score validation |

## Status Definitions

- **DRAFT**: Assembled but not yet validated locally
- **READY**: Validated locally, ready for Kaggle submission
- **SUBMITTED**: Uploaded to Kaggle
- **BEST_CURRENT**: Current best-performing submission
- **SUPERSEDED**: Replaced by a better submission
- **ARCHIVED**: No longer relevant
