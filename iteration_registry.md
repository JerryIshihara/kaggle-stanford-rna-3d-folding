# Iteration Registry

Global registry of all iterations for the Stanford RNA 3D Folding 2 pipeline.

## Registry

---

### IT001 — Pipeline Bootstrap

- **Iteration ID**: IT001
- **Title**: Pipeline bootstrap — modular structure, baseline code, tracking infrastructure
- **Module**: All (data_processor, inferencer, optimizer, validator)
- **Files**:
  - `data_processor/loader.py`
  - `data_processor/dataset.py`
  - `inferencer/baseline_model.py`
  - `inferencer/predict.py`
  - `optimizer/losses.py`
  - `optimizer/trainer.py`
  - `validator/metrics.py`
  - `validator/splitter.py`
  - `scripts/run_pipeline.py`
- **Functions / Features**:
  - `RNADataLoader` (load_train, load_test, load_msa, load_sample_submission)
  - `RNAStructureDataset`, `RNATestDataset`, `collate_rna`
  - `RNNModel`, `CNNModel`, `create_model`
  - `load_checkpoint`, `predict_batch`, `predict_sequences`
  - `rmsd_loss`, `masked_mse_loss`
  - `Trainer.fit` with early stopping and checkpointing
  - `rmsd`, `evaluate_fold`, `evaluate_cv`
  - `simple_kfold`, `group_kfold`, `length_stratified_kfold`
- **Description**: Created the full modular pipeline structure, baseline model code, loss functions, training loop, validation metrics, CV splitting, documentation, and agent iteration automation.
- **Motivation**: Establish a disciplined, traceable competition operating system before any model improvement work.
- **Sources**:
  - https://www.kaggle.com/competitions/stanford-rna-3d-folding-2
  - https://www.nature.com/articles/s41576-019-0203-6
- **Research**: [research/research_IT001.md](research/research_IT001.md)
- **Plan**: [plans/plan_IT001.md](plans/plan_IT001.md)
- **Report**: [reports/report_IT001.md](reports/report_IT001.md)
- **Checkpoints**: None (structural iteration)
- **Status**: PROMOTED

---

### IT002 — Competition Analysis and Template Pipeline

- **Iteration ID**: IT002
- **Title**: Competition landscape analysis and template-based pipeline implementation
- **Module**: All modules — strategic direction and template implementation
- **Files**:
  - `data_processor/template_db.py`
  - `inferencer/template_model.py`
  - `scripts/download_pdb_rna.py`
  - `scripts/build_template_db.py`
- **Functions / Features**:
  - `PDBRNADatabase` (search_rna_entries, download_entry, build_database, search_templates)
  - `needleman_wunsch`, `sequence_identity`, `_kmer_set` (alignment utilities)
  - `TemplateModel` (predict, predict_batch, _weighted_ensemble)
  - `TemplateEnsemble` (predict — multi-model confidence-weighted ensemble)
  - `transfer_coordinates` (alignment-based coordinate transfer with gap interpolation)
  - `generate_helix_coords` (A-form RNA helix fallback)
  - `kabsch_rmsd` (optimal superposition via Kabsch algorithm)
- **Description**: Implemented complete template-based prediction pipeline: RCSB PDB API search, PDB text parsing for RNA chains, Needleman-Wunsch alignment, coordinate transfer with interpolation, identity-weighted ensemble, and geometric helix fallback.
- **Motivation**: Leverage proven template-based approach (competition leader "best_template_oracle" at 0.554 RMSD) for quick score improvement.
- **Sources**:
  - Competition leaderboard analysis (March 18, 2026)
  - RCSB PDB REST API: https://search.rcsb.org
  - RNA structure prediction literature (2024-2026)
- **Research**: [research/research_IT002.md](research/research_IT002.md)
- **Plan**: [plans/plan_IT002.md](plans/plan_IT002.md)
- **Report**: [reports/report_IT002.md](reports/report_IT002.md)
- **Checkpoints**: None yet (template database pending download)
- **Status**: PROMOTED

---

### IT003 — Sentinel Value Fix and Submission Pipeline

- **Iteration ID**: IT003
- **Title**: Fix sentinel value handling in training data and establish working competition submission pipeline
- **Module**: submissions, optimizer
- **Files**:
  - `submissions/submission_SUB003.ipynb`
  - `submissions/submission_SUB003.md`
  - `submissions/kernel-metadata.json`
- **Functions / Features**:
  - `build_training_data()` — sentinel filter (< -1e15), per-residue valid_mask
  - `train_refinement()` — masked loss computation, loss clamping
  - Robust Kaggle path detection (multiple mount points)
- **Description**: Fixed critical bug where validation_labels.csv sentinel values (-1e18) were treated as valid coordinates, causing training loss ~10^34. Added per-residue masking so only residues with valid ground truth contribute to loss. Added robust data path detection for Kaggle.
- **Motivation**: SUB002 refinement model never converged due to sentinel contamination. V3 kernel failed due to wrong data path. No submission was ever made to the competition.
- **Sources**:
  - SUB001 post-mortem: `analysis/SUB001_postmortem.md`
  - V2 kernel log analysis
  - V3 kernel log analysis
  - Competition data format inspection
- **Research**: [research/research_IT003_sentinel_fix.md](research/research_IT003_sentinel_fix.md)
- **Plan**: [plans/plan_IT003_sentinel_fix.md](plans/plan_IT003_sentinel_fix.md)
- **Report**: [reports/report_IT003_sentinel_fix.md](reports/report_IT003_sentinel_fix.md)
- **Checkpoints**: N/A (model trained within Kaggle kernel)
- **Kaggle Results**: Loss 63.4 → 40.6 over 40 epochs; refinement usable; 37,322 sentinel residues filtered
- **Status**: PROMOTED
