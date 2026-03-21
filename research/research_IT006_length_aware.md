# Research: IT006 — Length-Aware Modeling for RNA 3D Structure Prediction

## Iteration ID: IT006
## Title: Length-Aware Modeling with Short-RNA Specialization
## Target Module(s): optimizer/, data_processor/, inferencer/, submissions/

## Research Question
How can we systematically exploit RNA sequence length as a first-class feature to improve TM-score across all length bins, with particular focus on short RNAs (<50nt) where current methods perform worst?

## Background / Context
- SUB003 achieved 0.246 TM-score (current best); SUB004 achieved 0.211; SUB005 pending
- Top leaderboard: 0.554 (best_template_oracle)
- Competition metric: TM-score with length-dependent d0 normalization
- Test set: 28 targets, lengths 19–4640nt, mean 349nt
- Competition deadline: March 25, 2026

## Findings

### 1. TM-Score Length Dependence is the Core Challenge
- **Source**: TM-score formula, SUB004 analysis
- d0 = 1.24 × ∛(L-15) - 1.8 for L > 21; d0 = 0.5 for L ≤ 21
- At L=15: d0=0.5, so even 1 Å deviation gives TM ≈ 0.2 per residue
- At L=200: d0≈3.7, so 1 Å deviation gives TM ≈ 0.93 per residue
- **Implication**: Short RNA predictions need sub-angstrom accuracy to score well, while long RNAs are more forgiving

### 2. Short RNA Structural Diversity
- **Source**: PDB statistics, RNA structure literature
- Short RNAs (<50nt) include: hairpins, riboswitches, aptamers, pseudoknots
- These have highly diverse, non-canonical structures poorly represented in template libraries
- Many adopt unique 3D folds driven by non-Watson-Crick base pairs and tertiary contacts
- Template matching by sequence similarity is particularly unreliable for short RNAs

### 3. Long RNA Template Advantage
- **Source**: Leaderboard analysis, template pipeline results
- Long RNAs (>200nt) are often ribosomal RNA fragments or known ribozymes
- Template libraries have better coverage for long, conserved RNA families
- Sequence-based alignment is more informative for longer sequences (more signal)
- Template-heavy ensemble weights are appropriate for long RNAs

### 4. Length-Stratified Training Improves Generalization
- **Source**: ML literature on class-imbalanced learning
- Training data is heavily skewed toward medium-length RNAs
- Without stratification, models underfit on rare short and very long sequences
- Length-stratified batching ensures all length bins get equal gradient contribution
- TM-aware loss directly optimizes the competition metric

### 5. Motif-Based Prediction for Short RNAs
- **Source**: RNA structural biology, Rfam database
- Short RNAs often belong to known structural families (tRNA, hairpin, stem-loop)
- Secondary structure → 3D coordinate mapping is more tractable for short sequences
- Nussinov/ViennaRNA-style folding can provide structural priors
- Known motif geometries (tetraloops, kink-turns, U-turns) can seed coordinates

## Candidate Ideas

### HIGH IMPACT
1. **Length-stratified template search** — Different search parameters per length bin:
   - Short (<50nt): strict sequence match, expanded candidate pool, motif-aware scoring
   - Medium (50-200nt): standard NW alignment with transition/transversion penalties
   - Long (>200nt): banded NW, fragment assembly from partial matches
2. **TM-aware training loss** — Use d0(L) normalization in the loss function so the model directly optimizes TM-score
3. **Length-dependent ensemble** — Modular ensemble weights as continuous function of length, not hardcoded bins

### MEDIUM IMPACT
4. **Short RNA motif library** — Build a library of known short RNA structural motifs from training data, match by secondary structure pattern
5. **Length-conditioned model** — Add sequence length as an explicit feature (length embedding) to Transformer/GNN models
6. **Adaptive refinement** — More refinement iterations for short RNAs (where accuracy matters most), fewer for long

### LOWER IMPACT
7. **Length-stratified cross-validation** — Already exists in validator/splitter.py; ensure it's used for model selection
8. **Per-length-bin error analysis** — Diagnostic tool to identify which length bins have most room for improvement

## Expected Impact
- Length-stratified templates: +0.02-0.05 TM-score
- TM-aware loss: +0.01-0.03
- Length-dependent ensemble: +0.01-0.03
- Short RNA specialization: +0.02-0.05 (on short targets)
- Combined: target 0.28-0.32 from current 0.246

## Risks / Assumptions
- Short RNA improvement may not move overall score much if test set is dominated by long sequences
- TM-aware loss may be harder to optimize than MSE (non-smooth gradients near d0)
- Motif matching requires secondary structure prediction, adding pipeline complexity
- Only 4 days until deadline — must focus on highest-impact changes

## Source Links
- TM-score: Zhang & Skolnick, Proteins 2004
- RNA-align: https://zhanggroup.org/RNA-align/
- Rfam database: https://rfam.org/
- RibonanzaNet2: https://www.kaggle.com/models/shujun717/ribonanzanet2
- ViennaRNA: https://www.tbi.univie.ac.at/RNA/
