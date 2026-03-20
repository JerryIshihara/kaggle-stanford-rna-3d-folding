# SUB004 -- Length-Aware Multi-Model Ensemble with Short-RNA Optimization

**Submission ID**: SUB004
**Kernel**: jerryishihara/stanford-rna-3d-template-refinement (v4+)
**Lineage**: IT001 → IT002 → IT004 → SUB002 (0.211) → SUB003 → SUB004

## Problem Analysis: Why Long RNA > Short RNA

The TM-score metric has inherent length dependence via its d0 normalization:
- d0 = 1.24 × ∛(L-15) - 1.8  (for L > 21)
- Same 2 Å RMSD gives TM=0.03 at L=15 but TM=0.72 at L=200

Additional factors:
- PDB has far more long RNA structures (ribosomal RNA, ribozymes)
- Template search alignment is more robust for longer sequences
- Short RNAs have more diverse, non-canonical folds less represented in PDB

## Key Improvements over SUB003

| Feature | SUB003 | SUB004 |
|---------|--------|--------|
| Ensemble weighting | Fixed (40/30/30) | Length-aware: short=20/40/40, long=50/25/25 |
| Training loss | MSE | TM-aware MSE (d0-weighted) |
| Refinement iterations | 1 for all | 3 for short, 2 for medium, 1 for long |
| Short-RNA fallback | A-form helix | Secondary structure-guided coords |
| ResNet architecture | 128h, 6L, k=5, ReLU | 160h, 8L, k=7, GELU |
| Optimizer | Adam + CosineAnnealing | AdamW + CosineAnnealingWarmRestarts |
| Validation | None | Per-target TM-score on validation set |

## Method

1. Build PDB RNA template database (3000 entries, ≤4.5 Å)
2. Template prediction with SS-guided fallback for short RNAs
3. Multi-model refinement: ResNet + Transformer
4. Length-aware ensemble:
   - Short (<50nt): 20% template + 40% ResNet + 40% Transformer
   - Medium (50-200nt): 35% template + 35% ResNet + 30% Transformer
   - Long (>200nt): 50% template + 25% ResNet + 25% Transformer
5. Iterative refinement (3× for short, 2× for medium, 1× for long)
6. 5 diverse structures using model diversity + MC-dropout + SS-guided init for short

## Module Versions

| Module | Version |
|--------|---------|
| data_processor | IT002 |
| inferencer | IT004 + SUB004 improvements |
| optimizer | SUB004 (TM-aware loss, AdamW, warm restarts) |
| validator | SUB004 (TM-score evaluation) |
