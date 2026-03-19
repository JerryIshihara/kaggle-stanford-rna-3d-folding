# SUB002 -- Template + Neural Refinement (Fixed)

**Submission ID**: SUB002
**Kernel**: jerryishihara/stanford-rna-3d-template-refinement (v2)
**Lineage**: IT001 -> IT002 -> SUB001 (failed) -> SUB002

## Fixes from SUB001 Post-Mortem

| Issue | Root Cause | Fix |
|-------|-----------|-----|
| Training loss = inf | Raw PDB coords (-100..100) overflowed Conv1d | `normalize_coords()`: center + scale before model |
| BatchNorm unstable | Batch size = 1 gives degenerate variance | Replaced with `InstanceNorm1d(affine=True)` |
| 58 min test inference | 5x redundant template search per target | Cache `template_model.predict()` once per target |
| No competition submission | `kernels push` != competition submit | Will submit output CSV via `kaggle competitions submit` |

## Method

1. Build PDB RNA template database (RCSB API, 2000 entries, ≤4.0 Å resolution)
2. Template-based prediction: k-mer filter + Needleman-Wunsch + Kabsch ensemble
3. Neural refinement: 1D ResNet with InstanceNorm, trained on normalized coordinates
4. Fallback: if refinement diverges, use pure template predictions
5. 5 diverse structures: MC-dropout + noise perturbation on cached template coords

## Key Parameters

- `max_pdb_entries`: 2000
- `refine_hidden`: 128, `refine_layers`: 6, `refine_kernel`: 5
- `refine_epochs`: 25, `refine_lr`: 3e-4
- `noise_std`: 0.5
- Coordinate normalization: centroid subtraction + std scaling

## Artifacts

- `submission_SUB002.ipynb` -- fixed notebook
- `kernel-metadata.json` -- updated to point to SUB002
- `analysis/SUB001_postmortem.md` -- detailed failure analysis
