# plans

## Purpose

Store implementation plans before coding. Every iteration must produce a plan artifact defining exact targets, files, functions, expected impact, evaluation method, and rollback strategy.

## Plan Files

| File | Iteration ID | Target Module(s) | Scope Summary |
|------|-------------|-------------------|--------------|
| [plan_IT001.md](plan_IT001.md) | IT001 | All | Full pipeline bootstrap: directories, code, docs, agent rules |

## Filename Convention

```
plans/plan_<ITERATION_ID>.md
```

`<ITERATION_ID>` includes a 4-character disambiguator for parallel-safety, e.g. `IT004_m2k7`.
Legacy IDs without a disambiguator (IT001, IT002) remain valid.
Always append new rows to the **end** of the table above to minimize merge conflicts.
