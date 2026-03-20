# analysis

## Purpose

Post-mortem analysis of Kaggle submissions. Each submission gets a report documenting execution results, bugs found, performance bottlenecks, and actionable fixes.

## Reports

| Report | Submission | Status | Key Finding |
|--------|-----------|--------|-------------|
| [SUB001_postmortem.md](SUB001_postmortem.md) | SUB001 | FAILED | Training loss = inf (feature normalization bug), no competition submission |
| [SUB002_postmortem.md](SUB002_postmortem.md) | SUB002 | FAILED | Loss ~7.5e33 (random head init + residual accumulation), internet blocking submission |

## Filename Convention

```
analysis/<SUBMISSION_ID>_postmortem.md
```
