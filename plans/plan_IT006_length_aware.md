# Plan: IT006 — Length-Aware Modeling

## Iteration ID: IT006
## Title: Length-Aware Modeling with Short-RNA Specialization
## Priority: HIGH (4 days to deadline)

## Overview
Implement systematic length-aware strategies across the entire pipeline: template search, loss functions, model architecture, and ensemble weighting. The goal is to improve TM-score from 0.246 to 0.28-0.32 by treating sequence length as a first-class feature.

## Implementation Steps

### Step 1: Length-Aware Loss Functions (`optimizer/losses.py`)
**Priority**: HIGH | **Effort**: Small

Add two new loss functions:
1. **`tm_aware_loss`** — Weights per-residue MSE by the TM-score d0 normalization factor, so the loss directly approximates TM-score optimization
2. **`length_weighted_loss`** — Upweights short sequences in the batch to counteract length bias in training data

Register both in `LOSS_REGISTRY`.

### Step 2: Length-Stratified Template Search (`data_processor/template_db.py`)
**Priority**: HIGH | **Effort**: Medium

Add `search_templates_length_aware()` method to `PDBRNADatabase`:
- **Short (<50nt)**: k=3 k-mers (finer resolution), lower identity threshold (0.15), expand candidate pool (top_k*10), prefer exact-length matches
- **Medium (50-200nt)**: Standard parameters (k=4, identity 0.2, top_k*5)
- **Long (>200nt)**: Banded NW alignment, relaxed length filter (±60%), fragment assembly support

### Step 3: Length-Aware Ensemble (`inferencer/length_ensemble.py`)
**Priority**: HIGH | **Effort**: Medium

New module implementing:
1. **`LengthAwareEnsemble`** class — Computes ensemble weights as a smooth function of sequence length (sigmoid interpolation between bins, not hard cutoffs)
2. **`get_ensemble_weights(length)`** — Returns dict of component weights
3. **`get_refinement_iterations(length)`** — Returns number of iterative refinement steps
4. **`ensemble_predict(predictions_dict, length)`** — Weighted combination of multi-model predictions

Default weight curves:
- Template weight: sigmoid ramp from 0.15 (L=20) to 0.55 (L=500)
- Neural weight: 1 - template_weight, split between ResNet and Transformer

### Step 4: Short RNA Specialization (`inferencer/short_rna.py`)
**Priority**: MEDIUM | **Effort**: Medium

New module for short RNA (<50nt) specialized prediction:
1. **`build_short_rna_motif_library(templates)`** — Extract short RNA structures from training data, cluster by secondary structure pattern
2. **`predict_short_rna(sequence, motif_library)`** — For short queries, search motif library by sequence + secondary structure similarity
3. **`nussinov_fold(sequence)`** — Minimal secondary structure prediction (no external deps)
4. **`ss_to_distance_constraints(ss_string)`** — Convert dot-bracket notation to distance constraints for coordinate generation

### Step 5: SUB006 Submission Notebook
**Priority**: HIGH | **Effort**: Large

Create `submissions/submission_SUB006.ipynb` integrating all length-aware components:
1. Build train-data template library (reuse SUB004/SUB005 approach)
2. For each test target:
   a. Determine length bin (short/medium/long)
   b. Run length-stratified template search
   c. For short RNAs: also run motif-based prediction
   d. Run neural refinement (if applicable) with TM-aware loss
   e. Combine via length-aware ensemble
   f. Generate 5 diverse predictions with length-adaptive strategies
3. Local TM-score validation on validation set
4. Output submission.csv

### Step 6: Update Tracking Files
- `iteration_registry.md` — Add IT006 entry
- `submissions/scoreboard.md` — Add SUB006 row
- `submissions/submission_SUB006.md` — Submission metadata

## File Changes Summary

| File | Action | Description |
|------|--------|-------------|
| `optimizer/losses.py` | MODIFY | Add tm_aware_loss, length_weighted_loss |
| `data_processor/template_db.py` | MODIFY | Add search_templates_length_aware() |
| `inferencer/length_ensemble.py` | NEW | Length-aware ensemble module |
| `inferencer/short_rna.py` | NEW | Short RNA specialization module |
| `submissions/submission_SUB006.ipynb` | NEW | Submission notebook |
| `submissions/submission_SUB006.md` | NEW | Submission metadata |
| `iteration_registry.md` | MODIFY | Add IT006 entry |
| `submissions/scoreboard.md` | MODIFY | Add SUB006 row |

## Verification
1. Unit test: `tm_aware_loss` produces lower loss for better-aligned structures
2. Unit test: `length_weighted_loss` upweights short sequences
3. Unit test: `search_templates_length_aware` returns different params per bin
4. Unit test: `LengthAwareEnsemble` weights sum to 1.0 for all lengths
5. Integration: SUB006 notebook runs end-to-end on sample data
6. Local validation: TM-score on validation set ≥ SUB003 baseline

## Timeline
- Day 1 (March 21): Steps 1-3 (losses, template search, ensemble)
- Day 2 (March 22): Steps 4-5 (short RNA module, notebook)
- Day 3 (March 23): Testing, validation, notebook refinement
- Day 4 (March 24): Submit to Kaggle, monitor results
