# submissions

## Purpose

Store Kaggle-submit-ready aggregated notebooks/scripts combining selected versions from each module into full pipeline submissions. Each submission must be traceable to research, plan, report, and checkpoint artifacts.

## Submission Artifacts

| Submission ID | Title | Data Version | Inferencer Version | Optimizer Version | Validator Version | Notebook | Markdown | Score |
|--------------|-------|-------------|-------------------|------------------|------------------|----------|----------|-------|
| SUB001 | Template + Neural Refinement | IT002 | IT002 (C1' fix) | SUB001 (inline) | N/A | [notebook](submission_SUB001.ipynb) | [metadata](submission_SUB001.md) | Pending |
| SUB002 | Template + Neural Refinement (Fixed) | IT002 | IT002 (C1' fix) | SUB002 (fixed) | N/A | [notebook](submission_SUB002.ipynb) | [metadata](submission_SUB002.md) | 0.211 |
| SUB003 | Multi-Model Ensemble (Template + ResNet + Transformer) | IT002 | IT004 (ResNet + Transformer) | SUB003 (inline) | N/A | [notebook](submission_SUB003.ipynb) | [metadata](submission_SUB003.md) | Pending |
| SUB004 | Length-Aware Ensemble with Short-RNA Optimization | IT002 | IT004 + SUB004 | SUB004 (TM-aware) | SUB004 (TM-score) | [notebook](submission_SUB004.ipynb) | [metadata](submission_SUB004.md) | Pending |

## Filename Convention

```
submissions/submission_<SUBMISSION_ID>.ipynb
submissions/submission_<SUBMISSION_ID>.py    (optional)
submissions/submission_<SUBMISSION_ID>.md
```

Always append new rows to the **end** of the table above to minimize merge conflicts.

## Links

- [Scoreboard](scoreboard.md)
