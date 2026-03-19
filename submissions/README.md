# submissions

## Purpose

Store Kaggle-submit-ready aggregated notebooks/scripts combining selected versions from each module into full pipeline submissions. Each submission must be traceable to research, plan, report, and checkpoint artifacts.

## Submission Artifacts

| Submission ID | Title | Data Version | Inferencer Version | Optimizer Version | Validator Version | Notebook | Markdown | Score |
|--------------|-------|-------------|-------------------|------------------|------------------|----------|----------|-------|
| SUB001 | Template + Neural Refinement | IT002 | IT002 (C1' fix) | SUB001 (inline) | N/A | [notebook](submission_SUB001.ipynb) | [metadata](submission_SUB001.md) | FAILED |
| SUB004 | Train-Data Templates | IT003 | Template matching | N/A | N/A | N/A | N/A | **0.211** |
| SUB005 | Multi-Template Diversity | IT004 | Multi-template + blend | N/A | N/A | N/A | N/A | RUNNING |
| SUB006 | Fragment Assembly + Per-Chain | IT005 | Fragment assembly | N/A | N/A | [notebook](submission_SUB006.ipynb) | [metadata](submission_SUB006.md) | RUNNING |

## Filename Convention

```
submissions/submission_<SUBMISSION_ID>.ipynb
submissions/submission_<SUBMISSION_ID>.py    (optional)
submissions/submission_<SUBMISSION_ID>.md
```

Always append new rows to the **end** of the table above to minimize merge conflicts.

## Links

- [Scoreboard](scoreboard.md)
