# inferencer

## Purpose

Model architecture definition, forward/inference logic, decoding, post-processing, ensembling logic, confidence estimation, and template-aware inference integration.

## Current Responsibilities

- Baseline RNN and CNN model architectures for RNA 3D coordinate prediction
- Model loading from checkpoints
- Batch inference with padding handling
- Post-processing of predicted coordinates

## Active Files

| File | Description |
|------|-------------|
| `baseline_model.py` | RNN and CNN models mapping nucleotide sequences to (x,y,z) coordinates |
| `predict.py` | Inference wrapper: checkpoint loading, batch prediction, post-processing |
| `template_model.py` | Template-based prediction: coordinate transfer, helix fallback, Kabsch RMSD, ensemble |

## Iteration History

| Iteration ID | File / Function / Feature | Description | Status | Research | Plan | Report |
|-------------|--------------------------|-------------|--------|----------|------|--------|
| IT002 | `template_model.py` / `TemplateModel`, `TemplateEnsemble`, `transfer_coordinates`, `kabsch_rmsd` | Template-based 3D prediction via coordinate transfer from PDB templates with identity-weighted ensemble and helix fallback | PROMOTED | [research](../research/research_IT002.md) | [plan](../plans/plan_IT002.md) | [report](../reports/report_IT002.md) |

## Deprecated / Rejected Artifacts

*(none yet)*
