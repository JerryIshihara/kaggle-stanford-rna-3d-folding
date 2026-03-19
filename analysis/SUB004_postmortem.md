# SUB004 Post-Mortem Analysis

## Submission Details
- **Submission ID**: SUB004
- **Kernel**: `jerryishihara/stanford-rna-3d-train-template-prediction-v4`
- **Status**: COMPLETE
- **Public LB Score**: 0.211 (TM-score, higher is better)
- **Date**: 2026-03-19

## Execution Summary
- Runtime: 193.5s (well within 9h limit)
- Templates: 2671 valid templates from training data
- Test targets: 28 (9762 residues total)
- No errors, no NaN values, valid submission.csv

## Leaderboard Context
- Our score: 0.211
- Top score: 0.554 (best_template_oracle)
- Competitive range: 0.45-0.55
- Median competitive: ~0.45
- RibonanzaNet2 model: 0.40
- DRfold2 baseline: 0.241

## Root Cause Analysis for Low Score

### 1. Template Selection Quality
- K-mer Jaccard + NW score is a weak proxy for structural similarity
- Length filter (±30%) may miss structurally similar shorter/longer templates
- Only using sequence similarity, not structural features

### 2. Coordinate Transfer Limitations
- Simple position-by-position copy from template alignment
- No structural superposition (Kabsch) on matched regions
- Linear interpolation for gaps produces unphysical geometry
- No consideration of RNA secondary structure

### 3. Diversity Strategy Suboptimal
- Best-of-5 metric means we should maximize prediction diversity
- Currently: 1 best template + 4 random perturbations
- Better: use 5 different templates, each with proper alignment
- Random perturbations (noise, hinge, jitter) likely degrade quality

### 4. Missing Validation Loop
- No local TM-score computation
- No way to evaluate quality before submission
- Validation set available (40 structures) but unused

## Improvement Priorities (for IT005/SUB005)
1. **Template diversity for 5 predictions** - Use top-5 different templates instead of perturbing one
2. **Fragment-based assembly** - For sequences with partial template matches, assemble from multiple fragments
3. **Local TM-score validation** - Implement TM-score and evaluate on validation set
4. **Better gap interpolation** - Use RNA helical geometry for gap regions
5. **Weighted template averaging** - For prediction slots, blend top templates by similarity
