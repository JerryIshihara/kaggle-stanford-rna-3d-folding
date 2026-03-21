# Research: IT008 — Neural Coordinate Refinement + Template Hybrid

## Iteration ID: IT008
## Title: Train RNATransformerModel on Competition Data + Template-Neural Hybrid Ensemble
## Target Module(s): inferencer/, submissions/

---

## Research Question

Can training the existing `RNATransformerModel` (IT004a) on real competition data and blending its output with template predictions improve TM-score on the 22/28 test targets that currently score < 0.1 due to poor template coverage?

---

## Background / Context

### Current bottleneck (from IT006/IT007 reports)

All submissions through SUB008 use purely algorithmic approaches:
- Template matching (k-mer + NW alignment)
- Secondary structure constraints (Nussinov DP, IT006)
- Distance geometry + SA refinement (IT007)

**22/28 test targets score < 0.1 TM** because no structurally similar sequence exists in the training data (temporal gap: test structures are newer). The de-novo fallbacks (IT006/IT007) only marginally improve these cases.

Both IT006 and IT007 reports explicitly recommend: _"If improved: continue with RibonanzaNet2 integration / neural coordinate refinement"_ as the highest-priority next step.

### Competition state

- Confirmed best LB: **0.211** (SUB004, train-data templates)
- Oracle ceiling: **0.554** (best_template_oracle on LB)
- Competition deadline: **March 25, 2026**
- 28 test sequences, lengths 19–4640 nt

### Available neural architecture (IT004a)

`RNATransformerModel` in `inferencer/transformer_model.py`:
- 6-layer pre-norm Transformer with AlphaFold-style pair bias
- Sinusoidal positional encoding (length generalization up to max_len)
- ~1.5M parameters — fast to train
- Input: token indices (A/C/G/U), Output: (B, L, 3) C1' coordinates
- Validated on dummy data (50 seqs, len 30) in IT004a — converged without errors

### Training data

- `train_sequences.csv`: 2671 labeled RNA sequences (with C1' coordinates)
- `train_labels.csv`: x_1, y_1, z_1 per residue (structure_1 only usable; >50% coverage)
- Sentinel values: -1e18 for missing coordinates (IT003 fix: filter rows where any coord < -1e15)
- Sequence lengths: 19–4640 nt; median ~100 nt

---

## Findings

### 1. Sentinel masking (IT003)

The `masked_mse_loss` in `optimizer/losses.py` already accepts a `mask` tensor. Sentinel detection:
```python
valid_mask = (coords > -1e15).all(axis=-1)  # (B, L) bool
```
This ensures the Transformer trains only on valid residue coordinates.

### 2. Length handling

- Transformer `max_len=2048` is insufficient for sequences up to 4640 nt → raise to **8192**
- `PairRepresentation.max_len` also needs raising to 8192 (controls relative position embedding)
- Memory concern: pair bias is O(L²). For L=4640: 4640² × 64 × 4 bytes ≈ 5.5 GB — too large for T4 (16 GB).
  - Mitigation: disable `use_pair_bias` for sequences > 1500 nt at inference only
  - Training is capped at L ≤ 512, so pair bias is fine during training

### 3. Training feasibility on T4

- T4 GPU: 16 GB VRAM, ~8.1 TFLOPS
- Batch size 8, L=512, 6 Transformer layers, d_model=128: ~2 GB peak memory
- Epoch time estimate: 2671 sequences / 8 per batch = ~334 steps × ~0.15 s/step ≈ 50 s/epoch
- 40 epochs: ~33 min training time
- Full kernel with template search (SUB008 baseline ~10 min): total ≈ 60–75 min ✓

### 4. Expected improvement from neural predictions

For no-template targets (sequence identity < 30%):
- Current (IT007 DG+SA): ~0.03–0.05 TM (essentially random coordinates)
- Trained Transformer: expected ~0.10–0.20 TM based on comparable RNA structure models
  - RibonanzaNet baselines (public): ~0.40 TM (but much larger model, pretrained)
  - Simple Transformer from scratch with limited data: more modest, ~0.10–0.20 realistic

For high-template targets (identity > 50%):
- Hybrid blend preserves template quality (alpha ≥ 1.0 → pure template at slot 1)
- Neural adds diversity in slots 4–5 via MC-dropout

### 5. Hybrid blending strategy

Identity-weighted alpha ensures graceful fallback:
```
alpha = clip(template_identity / 0.5, 0.0, 1.0)
hybrid = alpha * template_coords + (1 - alpha) * neural_coords
```
- identity=0.0 → pure neural (0 template contribution)
- identity=0.5 → 100% template (neural not needed)
- identity=0.25 → 50/50 blend

### 6. MC-dropout diversity

With `model.train()` at inference, dropout layers remain active. Running 3 forward passes per sequence produces structurally distinct predictions — valid diversity for slots 4–5.

### 7. Coordinate normalization

Training data coords span roughly −80 to +80 Å. Normalize to zero-mean unit-std per sequence before training, then denormalize at inference using the same statistics:
```python
mean = valid_coords.mean(0)  # (3,)
std  = valid_coords.std(0).clamp(min=1.0)
```
This ensures stable training and matches the scale expected by the loss.

---

## Candidate Ideas Evaluated

| Idea | Expected Impact | Feasibility | Decision |
|------|----------------|-------------|----------|
| Train Transformer on real data | +0.05–0.15 TM | High | **SELECTED** |
| Train GNN on real data | Similar, but slower | Medium | Backup if Transformer fails |
| RibonanzaNet2 integration | High potential | Low (large model, no internet) | Skip (no internet on Kaggle) |
| MSA co-evolution contacts | High potential | Low (complex preprocessing) | Skip (time constraint) |
| Validation data as templates | +0.02–0.05 TM | High | Already done in IT006/IT007 (~5700 templates) |
| Contact map prediction | High potential | Low | Skip |

---

## Recommended Next Action

Implement IT008: train `RNATransformerModel` on competition training data within the Kaggle kernel, blend with IT007 template pipeline, generate diverse 5-slot predictions as SUB009.

---

## Sources

- [IT004a GNN/Transformer validation](../reports/report_IT004_gnn_transformer.md) — confirmed architecture works on dummy data [IT004a]
- [IT007 follow-up recommendation](../reports/report_IT007_distance_geometry.md) — "continue with neural refinement" [IT007]
- [IT003 sentinel fix](../reports/report_IT003_sentinel_fix.md) — masked_mse_loss, sentinel detection [IT003]
- [Kaggle data path fix](../reports/report_IT004_train_template.md) — `/kaggle/input/competitions/stanford-rna-3d-folding-2/` [IT004b]
- [RibonanzaNet (Kaggle 2023)](https://www.kaggle.com/competitions/stanford-ribonanza-rna-folding) — Transformer+CNN baseline for RNA, achieves ~0.40 TM with much larger model [IT008]
- [Vaswani et al. 2017 "Attention is All You Need"](https://arxiv.org/abs/1706.03762) — foundational Transformer reference [IT004a]
