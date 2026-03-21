# Plan: IT008 — Neural Coordinate Refinement

## Iteration ID: IT008
## Title: Train RNATransformerModel on Competition Data + Template-Neural Hybrid Ensemble
## Submission: SUB009
## Status: IN_PROGRESS

---

## Problem Statement

22/28 test targets score < 0.1 TM because they lack template matches. Pure template
lookup cannot improve them. A neural model trained on 2671 sequences learns a
sequence-to-structure prior that produces reasonable coordinates even for novel sequences.

---

## Architecture Decision

Use `RNATransformerModel` (transformer_model.py) with `use_pair_bias=False`.

**Rationale:**
- GNN builds edges in Python loops — O(L) per sample, too slow for training
- Pair bias allocates (L, L, d_model) memory — at L=512 that is 128 MB/sample, OOM for batches
- Disabling pair bias → plain pre-norm Transformer, linear memory, fully CUDA-vectorized
- Sinusoidal PE handles variable-length sequences natively
- `max_len=4096` extended from 2048 to cover all training sequences

**Config:**
```python
RNATransformerModel(
    num_tokens=5,        # pad=0, A=1, C=2, G=3, U=4
    d_model=128,
    nhead=8,
    num_layers=6,
    dim_feedforward=512,
    dropout=0.1,
    output_dim=3,
    max_len=4096,
    use_pair_bias=False,
)
```
~1.15M parameters.

---

## Data Pipeline

**Source:** Already parsed in the notebook:
- `TRAIN_SEQS`: 2671 sequences (strings)
- `TRAIN_COORDS`: 2671 numpy arrays (L, 3), NaN for missing residues
- `TRAIN_IDS`: target IDs

**Build training samples inline:**
```python
neural_samples = []
for seq, coords in zip(TRAIN_SEQS, TRAIN_COORDS):
    valid_mask = ~np.isnan(coords[:, 0])
    if valid_mask.sum() >= 5:
        neural_samples.append({'seq': seq, 'coords': coords, 'valid': valid_mask})
```

**Tokenization:** pad=0, A=1, C=2, G=3, U=4 (shift by 1 from dataset.py to keep padding_idx=0 correct)

**Validation split:** Official 40-target val set (`val_seqs`, `val_labels` CSVs)

---

## Training Hyperparameters

```python
NEURAL_CFG = {
    "d_model": 128, "nhead": 8, "num_layers": 6,
    "dim_feedforward": 512, "dropout": 0.1,
    "use_pair_bias": False, "max_len": 4096,
    "learning_rate": 3e-4,
    "weight_decay": 1e-5,
    "gradient_clip": 1.0,
    "num_epochs": 60,
    "patience": 12,
    "warmup_epochs": 5,
    "use_amp": True,
    # Batch sizes per max-length bucket
    "batch_sizes": {100: 16, 250: 8, 500: 4, 1000: 2, 4096: 1},
    "max_train_len": 2048,  # truncate longer seqs during training
    "wall_clock_budget_s": 3 * 3600,  # 3-hour training budget
}
```

**Loss:** MSE for first 10 epochs (stable cold-start), RMSD thereafter.
**Scheduler:** Linear warm-up 5 epochs → CosineAnnealingLR.
**Optimizer:** AdamW (over Adam for correct weight decay on Transformers).
**AMP:** `torch.cuda.amp.autocast + GradScaler` on T4 (halves memory).

---

## Training Loop Design

- **BucketBatchSampler**: groups sequences by length bucket, shuffles within buckets
- **Sentinel masking**: `valid_mask = ~np.isnan(coords[:, 0])` → passed to loss function as `mask`
- **Gradient clipping**: `max_norm=1.0`
- **Early stopping**: patience=12 on val RMSD
- **Wall-clock budget**: stop training after 3 hours
- **Checkpoint**: save best state_dict in memory (`best_state = model.state_dict()`)
- **OOM guard**: catch `torch.cuda.OutOfMemoryError`, `empty_cache()`, `continue`

---

## Inference Strategy

### Two-Branch Prediction

**Branch A (IT007):** Template search + DG + SA → up to 10 candidates → max-dispersion 5

**Branch B (IT008 Neural):**
- One deterministic forward pass (`model.eval()`)
- Up to 3 MC-dropout passes (`model.train()`) for diversity

### Combined Diversity Pool (per test target)

```
Pool = [it007_cands (up to 10)] + [neural_det] + [neural_mc_1..3] = up to 14 candidates
Final 5 = max-dispersion greedy from pool, seeded with best-confidence candidate first
```

**Best-confidence candidate selection:**
- Template candidates: ranked by `best_sim` (NW similarity)
- Neural candidates: ranked by coordinate variance (higher = not collapsed)

### Template-Neural Blend (for partial coverage targets, identity 0.1-0.3)
```python
alpha = min(best_sim / 0.3, 1.0)
if alpha < 1.0:
    neural_aligned = kabsch_align_neural_to_template(neural_coords, template_coords)
    hybrid = alpha * template_coords + (1 - alpha) * neural_aligned
```

### Long Sequence Handling (> 2048 nt at inference)
- Sliding window: 2048 nt windows with 256 nt overlap, cosine blend in overlap
- Fallback: IT007 template + helical for sequences > 4000 nt

---

## Notebook Structure (SUB009.ipynb)

```
Cell 0:  Markdown header (SUB009, lineage, hypothesis)
Cell 1:  Imports + device + CFG
Cell 2:  Data loading
Cell 3:  Template library (train + val)
Cell 4:  K-mer index
Cell 5:  Nussinov SS prediction
Cell 6:  Alignment functions
Cell 7:  Kabsch + coordinate transfer
Cell 8:  Template retrieval
Cell 9:  Fragment assembly
Cell 10: Chain handling
Cell 11: Distance geometry de novo
Cell 12: SA refinement
Cell 13: Template blending
Cell 14: SS-guided de novo
Cell 15: TM-score computation
Cell 16: Max-dispersion diversity
Cell 17: Per-chain prediction pipeline (IT007)
Cell 18: ---- IT008 NEURAL MODEL ----
Cell 19: Model definition (inline RNATransformerModel, use_pair_bias=False)
Cell 20: Neural training data preparation
Cell 21: Neural training loop (AdamW, cosine LR, AMP, early stopping)
Cell 22: Train neural model
Cell 23: ---- INFERENCE ----
Cell 24: Neural inference function (det + MC-dropout)
Cell 25: Combined prediction pipeline (template + neural)
Cell 26: Validation evaluation
Cell 27: Generate test predictions
Cell 28: Build and save submission
```

---

## Risk Mitigation

| Risk | Trigger | Mitigation |
|------|---------|------------|
| No convergence | val_loss > 50 after 20 epochs | Switch to MSE-only; reduce LR 10x |
| OOM | CUDA error | BucketSampler with bs=1 for L>500 + OOM guard |
| Training > 5h | epoch_time * epochs > 5h | 3h wall-clock budget; use best checkpoint |
| Neural worse than templates | mean val TM < IT007 | Neural slots only used in max-dispersion, doesn't hurt template slots |
| Very long test seq (4640nt) | L > max_len | Sliding window inference |

---

## Expected Score Impact

- Conservative (+0.03-0.05): Neural provides signal for 5-8 of 22 low-coverage targets
- Optimistic (+0.05-0.12): Neural converges well, beats templates on 10-15 low-coverage targets
- Baseline fallback: if `neural_ok=False`, pure IT007 output (no regression from SUB008)

---

## Files Created/Modified

**New:**
- `research/research_IT008_neural_refinement.md` (done by previous agent)
- `plans/plan_IT008_neural_refinement.md` (this file)
- `submissions/submission_SUB009.ipynb`
- `submissions/submission_SUB009.md`

**Updated:**
- `iteration_registry.md` — add IT008 entry
- `submissions/scoreboard.md` — add SUB009 row
- `README.md` — update current best table
