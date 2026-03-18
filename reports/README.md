# reports

## Purpose

Store evaluation results after implementation. Every iteration must produce a report classifying the outcome as PROMOTED, REJECTED, PARKED, or NEEDS_FOLLOWUP.

## Report Files

| File | Iteration ID | Outcome | Summary |
|------|-------------|---------|---------|
| [report_IT001.md](report_IT001.md) | IT001 | PROMOTED | Pipeline bootstrap completed successfully |

## Filename Convention

```
reports/report_<ITERATION_ID>.md
```

`<ITERATION_ID>` includes a 4-character disambiguator for parallel-safety, e.g. `IT004_m2k7`.
Legacy IDs without a disambiguator (IT001) remain valid.
Always append new rows to the **end** of the table above to minimize merge conflicts.
