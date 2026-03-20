# Plan: IT007 — Distance Geometry De Novo + Enhanced Refinement

## Iteration ID: IT007
## Title: Distance Geometry De Novo Folding + SA Refinement + Diversity Optimization
## Target Module(s): submissions/

## Hypothesis
Replacing the simplistic sequential de novo fallback with distance geometry (MDS-based) coordinate generation, adding more aggressive simulated annealing refinement, and optimizing prediction diversity via max-dispersion selection will improve TM-scores especially for the 22/28 targets currently scoring < 0.1.

## Files to Create/Modify
1. `submissions/submission_SUB008.ipynb` (NEW) — Full submission notebook with IT007 improvements
2. `submissions/submission_SUB008.md` (NEW) — Submission metadata
3. `submissions/kernel-metadata.json` (MODIFY) — Point to SUB008

## Key Changes

### 1. Distance Geometry De Novo Folding (`distance_geometry_fold`)
- Build sparse distance matrix from:
  - Backbone: d(i,i+1) = 5.95 Å
  - Backbone i,i+2: d(i,i+2) = 10.2 Å
  - Nussinov base pairs: d(i,j) = 10.5 Å
  - Base stacking: if i,j paired and i+1,j-1 paired: d(i,i+1) ≈ 3.4 Å (stacking)
- Apply classical MDS (eigendecomposition) to get initial 3D embedding
- Post-process: enforce backbone distances, resolve clashes

### 2. Simulated Annealing Refinement (`sa_refine_coordinates`)
- Temperature schedule: T_init=1.0, T_final=0.01, 30 iterations
- Energy terms:
  - E_bond: backbone C1'-C1' distance deviation from 5.95 Å
  - E_pair: base-pair distance deviation from 10.5 Å
  - E_stack: stacking distance deviation from 3.4 Å
  - E_clash: penalty for distances < 3.2 Å (non-consecutive)
  - E_smooth: backbone smoothness (Laplacian penalty)
- Accept worse solutions with probability exp(-ΔE/T)
- Apply to ALL predictions, not just de novo

### 3. Max-Dispersion Diversity Selection (`select_diverse_predictions`)
- Generate 8-12 candidate predictions per target
- Compute pairwise RMSD matrix
- Greedily select 5 most diverse: pick best first, then iteratively pick the one maximizing minimum RMSD to already-selected set
- This directly optimizes the best-of-5 competition metric

### 4. Enhanced Template Scoring
- Weight templates by: alignment_score × coverage × valid_fraction
- Penalize templates with many NaN coordinates more heavily
- Use log-length-ratio penalty instead of hard cutoff

## Expected Metric Impact
- Validation TM: 0.179 → 0.22-0.26 (conservative)
- De novo targets: ~0.04 → ~0.08 (distance geometry)
- Template targets: ~0.5 → ~0.52 (SA refinement)
- LB expected: 0.211 → 0.24-0.30

## Evaluation Plan
- Run validation on 28 targets within the notebook
- Compare per-target TM-scores with SUB006/SUB007 baselines
- Check runtime stays under 4000s for 28 test targets

## Rollback Plan
- If distance geometry produces worse de novo: revert to ss_denovo_fold from IT006
- If SA refinement is too slow: reduce iterations to 15
- If diversity selection hurts: revert to fixed 5-slot strategy

## Linked Research
- `research/research_IT007_distance_geometry.md`
