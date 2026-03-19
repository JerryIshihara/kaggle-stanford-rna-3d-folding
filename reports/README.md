# reports

## Purpose

Store evaluation results after implementation. Every iteration must produce a report classifying the outcome as PROMOTED, REJECTED, PARKED, or NEEDS_FOLLOWUP.

## Report Files

| File | Iteration ID | Outcome | Summary |
|------|-------------|---------|---------|
| [report_IT001.md](report_IT001.md) | IT001 | PROMOTED | Pipeline bootstrap completed successfully |
| [report_IT002.md](report_IT002.md) | IT002 | PROMOTED | Template-based pipeline implemented, core logic verified |
| [report_IT004_gnn_transformer.md](report_IT004_gnn_transformer.md) | IT004 | PROMOTED | GNN and Transformer models implemented, end-to-end training validated on dummy data |
| [report_IT005_template_diversity.md](report_IT005_template_diversity.md) | IT005 | NEEDS_FOLLOWUP | SUB005 val=0.113, awaiting LB score |
| [report_IT006_ss_refinement.md](report_IT006_ss_refinement.md) | IT006 | NEEDS_FOLLOWUP | SUB007 kernel running, expanded templates + SS constraints |
| [report_IT007_distance_geometry.md](report_IT007_distance_geometry.md) | IT007 | NEEDS_FOLLOWUP | SUB008 kernel running, distance geometry + SA refinement |

## Filename Convention

```
reports/report_<ITERATION_ID>_<topic_slug>.md
```

- `<topic_slug>`: short lowercase underscore-separated descriptor (2–4 words, `[a-z0-9_]` only).
- The topic slug prevents merge conflicts when parallel agents create report files simultaneously.
- Example: `reports/report_IT003_template_pipeline.md`

> Legacy files (IT001) omit the topic slug and keep their original names.
