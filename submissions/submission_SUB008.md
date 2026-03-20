# Submission SUB008 — Distance Geometry De Novo + SA Refinement + Diversity Selection

## Submission ID: SUB008
## Related Iteration: IT007
## Kernel: jerryishihara/stanford-rna-3d-template-refinement

## Module Versions
- **Data**: IT006 (train + validation template bank, ~5700 templates)
- **Inferencer**: IT007 (distance geometry de novo, SA refinement, max-dispersion diversity)
- **Optimizer**: N/A (template-only approach)
- **Validator**: IT005 (TM-score validation)

## Key Changes from SUB007
1. **Distance geometry de novo folding**: MDS-based coordinate embedding from predicted distance matrix (Nussinov base pairs + backbone), replacing simplistic sequential placement
2. **Simulated annealing refinement**: 25-30 iterations with temperature schedule, RNA-specific energy terms (backbone, base-pair, stacking, clash, smoothing)
3. **Max-dispersion diversity selection**: Generate 10 candidates per target, select 5 most structurally diverse (maximizes best-of-5 metric)
4. **i,i+3 distance constraints**: A-form helix geometry enforcement (13.5 Å)
5. **Stacking distance constraints**: Consecutive paired bases at ~3.4 Å

## Expected Impact
- Distance geometry de novo: +0.02-0.04 TM on low-template targets
- SA refinement: +0.01-0.03 TM via better geometry
- Diversity selection: +0.01-0.02 TM via optimal use of 5 prediction slots
- Combined: target 0.22-0.28 TM on LB (from SUB004 baseline of 0.211)

## Validation Expectations
- SUB006 validation: mean 0.1794, max 0.7287, 6/28 > 0.3
- SUB007 expected similar or slightly better
- SUB008 improvement mainly on:
  - Currently-poor targets (< 0.1 TM) via distance geometry de novo
  - Mid-range targets via SA refinement
  - All targets via diversity optimization

## Status
- **Status**: SUBMITTED
- **Kernel version**: Pushed to Kaggle
