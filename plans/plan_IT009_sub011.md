# Plan: IT009 — SUB011 High-Impact Template Improvements

## Iteration ID: IT009
## Title: Fix Neural Training + External Templates + Improved Retrieval for SUB011
## Target Module(s): submissions/
## Linked Research: research/research_IT008_neural_refinement.md, competition analysis

---

## Diagnosis of SUB009/SUB010 Failure

The neural model (IT008) produced ZERO improvement across all 28 validation targets. Root causes:

1. **Training divergence**: Val loss went from 81.4 (epoch 1) to 106.8 (epoch 5) and never recovered. The model is memorizing noise rather than learning structure.
2. **Insufficient data**: 2,671 training sequences is far too few for a 1.15M-param Transformer to learn sequence-to-structure mapping from scratch.
3. **Wrong problem formulation**: Predicting absolute 3D coordinates from sequence alone is a nearly impossible task for a small model with limited data. The coordinate space is arbitrary (rotation/translation invariant), yet the model is trained to predict absolute coordinates.
4. **No coordinate normalization**: Training data coords span ~[-80, +80] Angstroms with arbitrary global orientation. The research notes recommended normalization but implementation is unclear.
5. **MSE/RMSD loss on absolute coords**: Without per-sample centering/alignment, the loss function fights against arbitrary reference frames.

**Critical insight**: The top teams in Part 1 used NO deep learning at all. Pure template-based modeling beat AlphaFold3. The neural model is a distraction from the real bottleneck: template coverage and retrieval quality.

---

## Priority-Ordered Changes

### PRIORITY 1: Use Pre-Computed External Templates (Expected: +0.05-0.15 TM)
**Effort: 2-4 hours | Risk: Low | Impact: High**

**What**: Add the `rhijudas/rna-3d-folding-templates` Kaggle dataset as a supplementary input to the kernel. This provides pre-computed PDB templates that cover 2024-2025 structures not in the training set.

**Why**: Research Finding 2 shows that updated PDB templates are the single biggest differentiator between top and bottom teams. Our template library is limited to 5,744 competition entries. The test set likely contains sequences similar to recent PDB deposits.

**How**:
- Add the external dataset as an additional Kaggle input: `rhijudas/rna-3d-folding-templates`
- Parse the template format (likely PDB/mmCIF files or pre-computed coordinate arrays)
- Merge external templates into `TRAIN_IDS, TRAIN_SEQS, TRAIN_COORDS, TRAIN_LENS, TRAIN_VALID_FRAC`
- Rebuild the k-mer index to include external templates
- No code logic changes needed beyond the data loading

**Stage changes**: Stage 2 (Template Library) — add external template loading after competition templates

**Risks**:
- Dataset format may be unexpected (need to handle gracefully)
- May significantly increase runtime if library becomes very large (mitigate: increase PREFILTER_TOP proportionally, or subsample)
- Dataset may not be available (fallback: proceed without it, no regression)

**Fallback**: If the dataset cannot be loaded, the pipeline falls back to the existing 5,744 templates with no regression.

---

### PRIORITY 2: Drop the Neural Model Entirely (Expected: +0.00 TM, saves 30-45 min runtime)
**Effort: 30 minutes | Risk: None | Impact: Indirect (runtime savings)**

**What**: Remove Stage 6 (IT008 neural model) completely. Use the freed runtime budget for more template candidates and better refinement.

**Why**: The neural model has ZERO improvement on every target. It wastes 30-45 minutes of the 9-hour kernel budget on training, and the neural candidates it adds to the pool are effectively random noise. Removing it:
- Eliminates risk of neural candidates polluting the diversity selection
- Frees runtime for expanded template search or more SA iterations
- Simplifies the pipeline (less code = fewer bugs)

**Stage changes**:
- Remove Stage 6 entirely
- Simplify Stage 7 to just Stage 5 (IT007 pipeline)
- Stage 8 calls `predict_complex()` directly instead of `predict_complex_it008()`

**Risks**: None. The neural model has 0.0000 delta on all targets.

---

### PRIORITY 3: Improve Template Retrieval Quality (Expected: +0.02-0.05 TM)
**Effort: 3-4 hours | Risk: Low | Impact: Medium**

**What**: Multiple retrieval improvements:

#### 3a. Increase k-mer k from 5 to 6 or 7
- Current k=5 produces 4^5=1024 possible k-mers. With RNA's 4-letter alphabet, many sequences share most 5-mers by chance.
- k=6 (4096 k-mers) or k=7 (16384) provides more discriminative power.
- **Stage change**: Cell 6, change `KMER_K = 5` to `KMER_K = 6`

#### 3b. Add reverse complement matching
- RNA sequences can fold into complementary structures. A template matching the reverse complement may have relevant structural features.
- Add `rev_comp()` function and search both orientations.
- **Stage change**: Cell 13 `find_templates_for_chain()`

#### 3c. Weighted NW alignment scoring
- Current NW uses uniform match/mismatch scores. RNA-specific substitution matrices (e.g., purine-purine transitions are more conservative than transversions) improve alignment quality.
- The code already has some RNA-aware NW in IT005 but may not be in the latest notebook.
- **Stage change**: Cell 9, NW alignment

#### 3d. Profile-based search for multi-chain targets
- For homo-multimers (same sequence repeated), pool template hits across chains to increase coverage.
- Already partially implemented via `chain_cache` but not exploited for retrieval boosting.

**Risks**: Changing k-mer size could reduce recall for short sequences (mitigate: use k=5 for sequences < 50 nt). Reverse complement matching may not help for most targets.

---

### PRIORITY 4: Better Candidate Generation Strategy (Expected: +0.02-0.04 TM)
**Effort: 2-3 hours | Risk: Low | Impact: Medium**

**What**: Restructure the 10-candidate pool to maximize structural diversity more effectively.

Current allocation (Cell 22):
- Slots 0-5: Direct template transfers (top 5 templates + fragment assembly)
- Slots 6-7: Template blends (3-way and 5-way Kabsch average)
- Slots 8-9: De novo (SS-guided distance geometry)

**Problem**: Template blends average out structural features, producing "averaged" coordinates that are worse than any individual template. The 3/5-template blends converge toward the same mean structure, wasting diversity slots.

**Proposed allocation**:
- Slot 0: Best template (direct transfer)
- Slot 1: Best template + aggressive SA refinement (100 iterations instead of 30)
- Slots 2-4: Next 3 best templates (direct transfer)
- Slot 5: Fragment assembly from best template
- Slots 6-7: De novo with different random seeds (SS-guided distance geometry)
- Slots 8-9: Best template with large Gaussian perturbation (std=2.0, 3.0 Angstroms)

**Why**: Each slot should be structurally distinct. Blends reduce diversity. More templates and more random seeds increase the chance that one prediction lands close to the true structure.

**Stage change**: Cell 22, `predict_single_chain_raw()`

**Risks**: Low. Even if the new allocation is not better, max-dispersion selection will pick the best 5 from the pool.

---

### PRIORITY 5: SA Refinement Improvements (Expected: +0.01-0.03 TM)
**Effort: 2 hours | Risk: Low | Impact: Low-Medium**

**What**: Improve the simulated annealing refinement.

#### 5a. Increase SA iterations for de novo candidates
- De novo candidates (slots 6-9) have poor starting geometry. Give them 60-100 SA iterations instead of 25-30.
- Template-based candidates need fewer (15-20 iterations) since they start with good geometry.

#### 5b. Add base-pair distance constraints in SA
- The Nussinov SS prediction gives base pairs. Use these as attractive constraints during SA (target ~10.5 Angstroms C1'-C1' for paired bases).
- Currently SA only uses backbone bond/skip constraints.

#### 5c. Add clash resolution
- Add repulsive force for atoms closer than 3.0 Angstroms (non-bonded) during SA.
- Prevents physically impossible conformations.

**Stage change**: Cell 17, `sa_refine_coordinates()`

**Risks**: Over-constraining SA can collapse structures. Use conservative force constants.

---

### PRIORITY 6: Fix Neural Model (IF TIME PERMITS — lowest priority)
**Effort: 4-6 hours | Risk: High | Impact: Uncertain**

If there is time after Priorities 1-5, the neural model could be fixed, but it requires fundamental changes:

#### 6a. Switch to distance matrix prediction
- Instead of predicting absolute (x, y, z) coordinates, predict the pairwise distance matrix D_{ij}.
- Reconstruct 3D coordinates via MDS (already implemented in `distance_geometry_fold()`).
- This eliminates the rotation/translation invariance problem.

#### 6b. Use coordinate normalization
- Center each training sample: subtract centroid, scale to unit radius of gyration.
- At inference, denormalize using predicted chain length to estimate scale.

#### 6c. Reduce model size
- 1.15M params is too many for 2,671 samples. Use 2-3 layers, d_model=64.
- ~100K params is more appropriate for this data size.

#### 6d. Better loss function
- Use FAPE (Frame Aligned Point Error) or dRMSD (distance RMSD) instead of coordinate MSE/RMSD.
- dRMSD = RMSD of predicted pairwise distances vs true pairwise distances. Rotation-invariant.

**Why this is low priority**: Top teams in Part 1 used NO neural networks. Even if fixed, the neural model is unlikely to contribute more than +0.02 TM given the tiny training set. The same engineering time on template improvements (Priorities 1-3) has much higher expected value.

---

## Implementation Order (4-Day Schedule)

### Day 1 (March 21): Core improvements
- [x] Analyze codebase (this plan)
- [ ] Priority 2: Remove neural model, create clean SUB011 base from SUB010
- [ ] Priority 1: Investigate and integrate external template dataset
- [ ] Priority 4: Restructure candidate generation

### Day 2 (March 22): Retrieval + refinement
- [ ] Priority 3: Improve k-mer retrieval (k=6, RNA-aware NW)
- [ ] Priority 5: SA refinement improvements
- [ ] Local validation of all changes
- [ ] Create SUB011 notebook

### Day 3 (March 23): Test and submit
- [ ] Full pipeline smoke test
- [ ] Submit SUB011 to Kaggle
- [ ] If SUB011 improves, iterate on SUB012 with remaining ideas

### Day 4 (March 24): Buffer
- [ ] Fix any issues from SUB011 results
- [ ] Emergency submission if needed
- [ ] Priority 6 (neural fix) only if all else is done

---

## Expected Combined Impact

| Change | Expected TM Delta | Confidence |
|--------|------------------|------------|
| External templates (P1) | +0.05 to +0.15 | Medium-High |
| Remove neural noise (P2) | +0.00 to +0.01 | High |
| Better retrieval (P3) | +0.02 to +0.05 | Medium |
| Better candidates (P4) | +0.02 to +0.04 | Medium |
| SA improvements (P5) | +0.01 to +0.03 | Medium |
| **Total estimated** | **+0.10 to +0.28** | - |

Current best: 0.211 (SUB004). Target: 0.30-0.40 range.
Competition leader reference: "Protenix + Template" at 0.409.

---

## Rollback Plan

Each priority is independent and additive. If any change causes regression:
1. Revert that specific change
2. Keep all other improvements
3. The base pipeline (IT007 template-only) is preserved as the safe fallback

SUB010 notebook is the rollback target — it can be resubmitted unchanged if SUB011 regresses.

---

## Files to Create/Modify

| File | Action | Description |
|------|--------|-------------|
| `submissions/submission_SUB011.ipynb` | Create | New notebook with all improvements |
| `submissions/submission_SUB011.md` | Create | Submission metadata |
| `submissions/kernel-metadata.json` | Modify | Point to SUB011 notebook |

## Evaluation Plan

1. Local validation on the 28 validation targets (if available)
2. Compare per-target TM-scores vs SUB010 baseline
3. Check that template library size increased (if external templates loaded)
4. Verify runtime is within 9-hour limit
5. Submit to Kaggle and compare LB score vs 0.211 (SUB004 best)
