# SUB009 — Neural Coordinate Refinement (IT008)

## Metadata

| Field | Value |
|-------|-------|
| Submission ID | SUB009 |
| Iteration | IT008 |
| Based on | SUB008 (IT007: Distance Geometry + SA + Diversity) |
| Competition | Stanford RNA 3D Folding Part 2 |
| Metric | TM-score (best-of-5, higher is better) |
| Status | READY |
| Kernel file | submission_SUB009.ipynb |

## Hypothesis

Training RNATransformerModel (6-layer, d_model=128, ~1.15M params) on 2671 competition
training sequences provides structural priors for the 22/28 test targets that lack template
matches. The neural model fills the gap left by the IT007 template+DG+SA pipeline, which
produces near-random coordinates for low-coverage targets.

## Key Changes from SUB008

1. **IT008 Neural Training**: In-kernel training of RNATransformerModel on train_labels.csv
   - use_pair_bias=False (avoids O(L²) memory)
   - AdamW optimizer, CosineAnnealingLR, AMP (mixed precision on T4)
   - BucketBatchSampler (batch size 16 for L<100, down to 1 for L>1000)
   - MSE loss (first 10 epochs) + RMSD loss (remaining) for stable cold-start
   - Early stopping (patience=12), 3-hour wall-clock budget

2. **Neural Inference**: Per-test-sequence prediction
   - 1 deterministic pass (model.eval())
   - Up to 3 MC-dropout passes (model.train()) for structural diversity
   - Sliding window for sequences > 2048 nt

3. **Extended Candidate Pool**: 14 candidates per target → select 5 via max-dispersion
   - IT007 pool (10) + neural deterministic (1) + neural MC-dropout (3)

4. **Template-Neural Blend**: For partial-coverage targets (sim 0.1-0.3), Kabsch-aligned
   weighted blend: alpha * template + (1-alpha) * neural_aligned

## Expected Impact

- Conservative: +0.03-0.05 LB (5-8 of 22 low-coverage targets improve from 0.05 → 0.10-0.15)
- Optimistic: +0.05-0.12 LB (10-15 of 22 targets improve)
- Fallback: if neural_ok=False, pure IT007 output (no regression from SUB008)

## Estimated Runtime

- Template library build: ~30s
- Neural training (60 epochs max, 3h budget): ~30-45 min
- Inference (28 test targets): ~5-8 min
- Total: ~1.5-2 hours (well within 9-hour kernel limit)

## Module Versions

- Data: IT006 (train + validation templates, ~5700 entries)
- Inferencer: IT008 (RNATransformerModel trained on competition data)
- Template pipeline: IT007 (DG + SA + max-dispersion)
- Validator: IT005 (TM-score)
