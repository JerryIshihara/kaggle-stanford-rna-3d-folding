# submissions

## Purpose

Store Kaggle-submit-ready aggregated notebooks/scripts combining selected versions from each module into full pipeline submissions. Each submission must be traceable to research, plan, report, and checkpoint artifacts.

## Submission Artifacts

| Submission ID | Title | Data Version | Inferencer Version | Optimizer Version | Validator Version | Notebook | Markdown | Score |
|--------------|-------|-------------|-------------------|------------------|------------------|----------|----------|-------|
| SUB001 | Template + Neural Refinement | IT002 | IT002 (C1' fix) | SUB001 (inline) | N/A | [notebook](submission_SUB001.ipynb) | [metadata](submission_SUB001.md) | FAILED (inf loss) |
| SUB002 | Template + Refinement (Fixed) | IT002 | IT002 (C1' fix) | SUB002 (fixed) | N/A | [notebook](submission_SUB002.ipynb) | [metadata](submission_SUB002.md) | FAILED (loss ~1e34) |
| SUB003 | Template + Refinement (Sentinel Fix) | IT002 | IT002 (C1' fix) | SUB003 (sentinel) | N/A | [notebook](submission_SUB003.ipynb) | [metadata](submission_SUB003.md) | Pending |

## Filename Convention

```
submissions/submission_<SUBMISSION_ID>.ipynb
submissions/submission_<SUBMISSION_ID>.py    (optional)
submissions/submission_<SUBMISSION_ID>.md
```

Always append new rows to the **end** of the table above to minimize merge conflicts.

## Links

- [Scoreboard](scoreboard.md)
