# Report: IT006 — Secondary Structure Refinement + Expanded Templates

## Iteration ID: IT006
## Title: SS-Guided Coordinate Refinement + Expanded Template Bank
## Target Module(s): submissions/

## Files Changed
- `submissions/submission_SUB007.ipynb` (NEW) — Full submission notebook
- `submissions/submission_SUB007.md` (NEW) — Metadata and traceability
- `submissions/kernel-metadata.json` (MODIFIED) — Points to SUB007

## Functions/Features Changed
1. **build_template_bank()** — New function to build template library from any sequence+label pair
2. **nussinov_predict()** — Nussinov DP for secondary structure prediction (O(n³))
3. **_nussinov_windowed()** — Windowed SS prediction for sequences > 1500 nt
4. **get_secondary_structure()** — Cached SS prediction accessor
5. **ss_refined_constraints()** — Enhanced constraint function with base-pair distances from Nussinov
6. **ss_denovo_fold()** — SS-guided de novo coordinate generation
7. **predict_single_chain()** — Modified: slot 4 now uses SS de novo, slot 3 falls back to SS de novo when few templates
8. **predict_complex()** — Modified: passes chain sequences to constraint function for SS

## Experiment Setup
- Template bank: train + validation labels (estimated ~5700 templates)
- Candidate pool: PREFILTER_TOP=400, ALIGN_TOP=60
- Constraint passes: 4 (with 0.15 decay per pass)
- Nussinov scoring: A-U=2, G-C=3, G-U=1, min_loop=4
- Base-pair target distance: 10.5 Å (C1'-C1')

## Validation Setting
- Kernel pushed to Kaggle: RUNNING
- Local validation: pending kernel completion
- Comparison baseline: SUB006 (val mean 0.1794, 6/28 > 0.3)

## Expected Improvement Sources
1. Expanded templates: covers more test targets, especially those unique to validation set
2. SS constraints: better geometry for all targets, especially mid-range (0.1-0.3 TM)
3. SS de novo: better coordinates for no-template targets (currently < 0.05 TM)
4. Larger candidate pool: more template diversity

## Metrics and Comparison vs Previous Baseline
- SUB004 LB: 0.211 TM (confirmed)
- SUB006 val: 0.1794 mean, 0.7287 max, 6/28 > 0.3
- SUB007 expected: 0.20-0.30 TM (LB), improvement mainly on poor targets

## Outcome Classification
**NEEDS_FOLLOWUP** — Kernel is running, awaiting results.

## Decision and Follow-up
- Monitor kernel completion and LB score
- If improved: continue with neural refinement (GNN/Transformer integration)
- If not improved: diagnose which component underperformed
- Next priorities: RibonanzaNet2 integration, neural coordinate refinement
