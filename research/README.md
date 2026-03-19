# research

## Purpose

Track research and idea generation for each iteration. Every iteration must produce a research artifact before implementation documenting what was researched, which modules it applies to, ideas generated, and source links.

## Research Files

| File | Iteration ID | Target Module(s) | Idea Summary |
|------|-------------|-------------------|-------------|
| [research_IT001.md](research_IT001.md) | IT001 | All | Competition analysis, approach survey, pipeline bootstrap |
| [research_IT002.md](research_IT002.md) | IT002 | All | Competition landscape analysis, state-of-the-art approaches |
| [research_IT003.md](research_IT003.md) | IT003 | data_processor, inferencer | Feature engineering — MSA, secondary structure, BPPM, RNA-FM, co-evolution, positional encoding |
| [research_IT004_gnn_transformer.md](research_IT004_gnn_transformer.md) | IT004 | inferencer, data_processor, scripts | GNN (EGNN-style) and Transformer (pre-norm + pair bias) architectures for RNA 3D structure prediction |

## Filename Convention

```
research/research_<ITERATION_ID>_<topic_slug>.md
```

- `<topic_slug>`: short lowercase underscore-separated descriptor (2–4 words, `[a-z0-9_]` only).
- The topic slug prevents merge conflicts when parallel agents create research files simultaneously.
- Example: `research/research_IT003_template_pipeline.md`

> Legacy files (IT001, IT002) omit the topic slug and keep their original names.
