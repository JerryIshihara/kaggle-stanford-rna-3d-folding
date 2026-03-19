# plans

## Purpose

Store implementation plans before coding. Every iteration must produce a plan artifact defining exact targets, files, functions, expected impact, evaluation method, and rollback strategy.

## Plan Files

| File | Iteration ID | Target Module(s) | Scope Summary |
|------|-------------|-------------------|--------------|
| [plan_IT001.md](plan_IT001.md) | IT001 | All | Full pipeline bootstrap: directories, code, docs, agent rules |

## Filename Convention

```
plans/plan_<ITERATION_ID>_<topic_slug>.md
```

- `<topic_slug>`: short lowercase underscore-separated descriptor (2–4 words, `[a-z0-9_]` only).
- The topic slug prevents merge conflicts when parallel agents create plan files simultaneously.
- Example: `plans/plan_IT003_template_pipeline.md`

> Legacy files (IT001, IT002) omit the topic slug and keep their original names.
