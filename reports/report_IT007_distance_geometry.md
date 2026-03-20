# Report: IT007 — Distance Geometry De Novo + SA Refinement + Diversity Selection

## Iteration ID: IT007
## Title: Distance Geometry De Novo + Simulated Annealing Refinement + Max-Dispersion Diversity
## Target Module(s): submissions/

## Files Changed
- `submissions/submission_SUB008.ipynb` (NEW) — Full submission notebook with IT007 improvements
- `submissions/submission_SUB008.md` (NEW) — Submission metadata and traceability
- `submissions/kernel-metadata.json` (MODIFIED) — Points to SUB008
- `scripts/build_sub008.py` (NEW) — Notebook construction script

## Functions/Features Changed
1. **distance_geometry_fold()** — MDS-based 3D coordinate embedding from distance matrix
2. **_mds_subsampled()** — Subsampled MDS for large structures (> 500 residues)
3. **_enforce_backbone()** — Iterative backbone distance enforcement
4. **sa_refine_coordinates()** — SA with temperature schedule (T_init → T_final over 25 iterations)
5. **select_diverse_predictions()** — Greedy max-dispersion (10 candidates → 5 selected)
6. **compute_rmsd()** — RMSD for diversity matrix computation
7. **predict_single_chain()** — Modified: generates N_CANDIDATES=10, diversity-selects 5
8. **predict_complex()** — Modified: uses sa_refine_coordinates instead of ss_refined_constraints
9. **ss_denovo_fold()** — Enhanced: uses distance_geometry_fold for short sequences with SS info

## Experiment Setup
- Template bank: train + validation labels (~5700 templates, from IT006)
- Candidate pool: PREFILTER_TOP=400, ALIGN_TOP=60 (from IT006)
- SA iterations: 25, temperature: exponential decay from T_init to 0.005
- Distance geometry: backbone + i,i+2 + base-pair + stacking constraints
- Diversity: generate 10 candidates, greedy max-min-RMSD selection of 5

## Validation Setting
- Kernel pushed to Kaggle: RUNNING (stanford-rna-3d-template-refinement-v8)
- Local validation: pending kernel completion
- Comparison baseline: SUB006 (val mean 0.1794, 6/28 > 0.3)

## Expected Improvement Sources
1. Distance geometry de novo: better initial coordinates for 22/28 low-template targets
2. SA refinement: better geometry via temperature-scheduled constraint satisfaction
3. Max-dispersion diversity: optimal use of 5 prediction slots (best-of-5 metric)
4. i,i+3 + stacking constraints: enforce A-form helix geometry

## Metrics and Comparison vs Previous Baseline
- SUB004 LB: 0.211 TM (confirmed)
- SUB006 val: 0.1794 mean, 0.7287 max, 6/28 > 0.3
- SUB007: RUNNING (IT006 improvements)
- SUB008 expected: 0.20-0.28 TM (LB), improvement mainly on de novo targets

## Outcome Classification
**NEEDS_FOLLOWUP** — Kernel is running, awaiting results.

## Decision and Follow-up
- Monitor kernel completion and LB score
- Compare per-target TM-scores with SUB006/SUB007
- If improved: continue with RibonanzaNet2 integration (highest remaining potential)
- If not improved: diagnose which component (MDS, SA, diversity) needs adjustment
- Competition deadline: March 25, 2026
