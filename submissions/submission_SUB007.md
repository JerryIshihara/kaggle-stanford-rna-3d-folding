# Submission SUB007 — Secondary Structure Refinement + Expanded Templates

## Submission ID: SUB007
## Related Iteration: IT006
## Kernel: jerryishihara/stanford-rna-3d-template-refinement

## Module Versions
- **Data**: IT006 (train + validation template bank, ~5700 templates)
- **Inferencer**: IT006 (SS-refined constraints, Nussinov base pairs, SS de novo fold)
- **Optimizer**: N/A (template-only approach)
- **Validator**: IT005 (TM-score validation)

## Key Changes from SUB006
1. **Expanded template bank**: Both train_labels AND validation_labels as template sources (~5700 vs ~2671)
2. **Nussinov secondary structure prediction**: Base pair constraints for coordinate refinement
3. **Enhanced iterative refinement**: Bond length + base-pair distance + clash + smoothing (4 passes)
4. **SS-guided de novo fallback**: Prediction slot 4 uses SS-guided coordinate generation
5. **Larger candidate pool**: PREFILTER_TOP=400, ALIGN_TOP=60 (vs 300/30)
6. **More aligned templates per target**: Up to 15 aligned (vs 10)

## Expected Impact
- Expanded templates: +0.02-0.05 TM (more coverage)
- SS constraints: +0.03-0.08 TM (better geometry)
- Combined: target 0.22-0.35 TM on LB

## Validation Expectations
- SUB006 validation: mean 0.1794, max 0.7287, 6/28 > 0.3
- Expected SUB007 improvement mainly on:
  - Currently-poor targets (< 0.1 TM) via expanded templates and SS de novo
  - Mid-range targets (0.1-0.3 TM) via better refinement

## Status
- **Status**: SUBMITTED
- **Kernel version**: Pending push
