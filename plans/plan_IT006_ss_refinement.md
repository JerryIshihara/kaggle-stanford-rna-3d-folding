# Plan: IT006 — Secondary Structure Constraints and Template Refinement

## Iteration ID: IT006
## Title: Secondary Structure-Guided Coordinate Refinement + Expanded Template Bank
## Target Module(s): submissions/
## Linked Research: research/research_IT006_ss_refinement.md

## Hypothesis
By expanding the template bank with validation data, adding Nussinov secondary structure prediction, and applying iterative coordinate refinement with base-pair constraints, we can improve TM-score from 0.211 to 0.25-0.35.

## Files to Create/Modify
- `submissions/submission_SUB007.ipynb` (NEW) — main submission notebook
- `submissions/submission_SUB007.md` (NEW) — submission metadata
- `submissions/kernel-metadata.json` (MODIFY) — point to SUB007
- `submissions/scoreboard.md` (MODIFY) — add SUB007 entry
- `iteration_registry.md` (MODIFY) — add IT006 entry

## Implementation Plan

### Component 1: Expanded Template Bank
- Load both train_labels.csv AND valid_labels.csv as template sources
- Combined bank: ~5700+ templates (train ~2671 + valid ~3000)
- Use target_id prefix grouping to build coordinate dictionaries

### Component 2: Nussinov Secondary Structure Prediction
- Implement Nussinov DP algorithm for base-pair prediction
- Score matrix: A-U: 2, G-C: 3, G-U: 1 (wobble pair)
- Traceback to extract list of (i,j) base pairs
- Min loop size: 4 nucleotides
- Cache predictions per target

### Component 3: Iterative Coordinate Refinement
- After template coordinate transfer:
  - Step 1: Fix consecutive C1' distances to 5.5-6.5 Å range (target 5.9)
  - Step 2: Resolve steric clashes (push apart atoms < 3.8 Å)
  - Step 3: Apply base-pair distance constraints from Nussinov (target 10.5 Å)
  - Step 4: Smooth backbone with moving average (window=3)
  - Repeat 3 iterations with decreasing step size

### Component 4: Better Template Quality Scoring
- Composite score: `alignment_similarity * sqrt(length_ratio) * valid_fraction * coverage`
- Reject templates with <60% valid coordinates
- Expand candidate pool from 30 to 60 templates
- For diversity: ensure 5 prediction slots use sufficiently different templates

### Component 5: Enhanced De Novo Fallback
- For targets with no good templates (best similarity < 0.3):
  - Use Nussinov SS to identify base pairs
  - Build coordinates using SS-guided chain growth:
    1. Start from one end, place residues along backbone
    2. When base pair encountered, bend chain to satisfy distance
    3. Use helical geometry for stem regions
  - Apply coordinate refinement after initial placement

### Component 6: Integration (SUB007 Notebook)
- Build on SUB006's per-chain, fragment assembly architecture
- Add the above 5 components into the prediction pipeline
- Use validation set for local TM-score evaluation
- Generate 5 diverse predictions per target

## Expected Metric Impact
- Current: 0.211 TM (LB), 0.1794 TM (SUB006 val mean)
- Expected: 0.25-0.35 TM (LB)
- Conservative: 0.23-0.28 TM

## Evaluation Plan
- Local validation on training set holdout
- Compare per-target TM-scores with SUB006
- Track: mean, median, >0.3 count, bottom-5 improvement

## Rollback Plan
- If validation worse than SUB006: revert to SUB006 approach
- Each component can be disabled independently via flags
