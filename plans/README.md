# plans

## Purpose

Store implementation plans before coding. Every iteration must produce a plan artifact defining exact targets, files, functions, expected impact, evaluation method, and rollback strategy.

## Plan Files

| File | Iteration ID | Target Module(s) | Scope Summary |
|------|-------------|-------------------|--------------|
| [plan_IT001.md](plan_IT001.md) | IT001 | All | Full pipeline bootstrap: directories, code, docs, agent rules |
| [plan_IT002.md](plan_IT002.md) | IT002 | data_processor, inferencer | Template-based pipeline: PDB database, alignment, coordinate transfer |
| [plan_IT004_gnn_transformer.md](plan_IT004_gnn_transformer.md) | IT004 | inferencer, data_processor, scripts, configs | GNN and Transformer architecture implementation and pipeline integration |
| [plan_IT005_template_diversity.md](plan_IT005_template_diversity.md) | IT005 | submissions | Multi-template diversity with Kabsch blend and local validation |
| [plan_IT006_ss_refinement.md](plan_IT006_ss_refinement.md) | IT006 | submissions | SS constraints, expanded templates, Nussinov de novo |
| [plan_IT007_distance_geometry.md](plan_IT007_distance_geometry.md) | IT007 | submissions | Distance geometry de novo, SA refinement, diversity optimization |

## Filename Convention

```
plans/plan_<ITERATION_ID>_<topic_slug>.md
```

- `<topic_slug>`: short lowercase underscore-separated descriptor (2–4 words, `[a-z0-9_]` only).
- The topic slug prevents merge conflicts when parallel agents create plan files simultaneously.
- Example: `plans/plan_IT003_template_pipeline.md`

> Legacy files (IT001, IT002) omit the topic slug and keep their original names.
