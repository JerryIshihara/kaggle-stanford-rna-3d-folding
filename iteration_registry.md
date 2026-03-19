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

### IT003 — Train-Data Template Library (SUB003-SUB004)

- **Iteration ID**: IT003
- **Title**: Train-data template library — using competition data as templates
- **Module**: inferencer (template matching pipeline)
- **Files**: `submissions/submission_SUB003.ipynb`, `submissions/submission_SUB004.ipynb`
- **Description**: Switched from external PDB template database to using competition's own training data (2671 templates). Implemented k-mer prefilter, NW alignment, chain-aware prediction, RNA structural constraints.
- **Motivation**: External PDB approach failed (no internet, missing data). Training data has C1' coordinates for 2671 sequences.
- **Status**: PROMOTED (SUB004 scored 0.211 TM on public LB)

---

### IT004 — Multi-Template Diversity (SUB005)

- **Iteration ID**: IT004
- **Title**: Multi-template diverse prediction with Kabsch blending
- **Module**: inferencer (prediction pipeline)
- **Files**: `submissions/submission_SUB005.ipynb` (Kaggle: stanford-rna-3d-template-refinement)
- **Description**: Use 5 different templates for 5 prediction slots, similarity-weighted template blending with Kabsch superposition, RNA-specific alignment scoring (transition/transversion), helical gap interpolation.
- **Motivation**: Improve diversity and quality of best-of-5 predictions over SUB004.
- **Status**: RUNNING (submitted to Kaggle, awaiting results)

---

### IT005 — Fragment Assembly + Per-Chain Prediction (SUB006)

- **Iteration ID**: IT005
- **Title**: Fragment-based assembly, per-chain prediction, coverage-weighted scoring
- **Module**: inferencer (prediction pipeline)
- **Files**: `submissions/submission_SUB006.ipynb` (Kaggle: stanford-rna-3d-fragment-assembly)
- **Functions / Features**:
  - `predict_single_chain` — independent per-chain template matching
  - `predict_complex` — assembles per-chain predictions into full complex
  - `fragment_assembly` — splits long chains into overlapping fragments, finds templates per fragment, stitches via Kabsch superposition
  - `find_templates_for_chain` — coverage-weighted template scoring (similarity × coverage × length ratio)
  - Affine gap NW alignment with RNA-specific transition/transversion scoring
- **Description**: Major architectural improvement: predict each chain independently (not full complex), use fragment assembly for long chains without good full-length templates, coverage-weighted template selection.
- **Motivation**: SUB004 matched full concatenated sequences against templates, producing poor matches for multi-chain targets. Per-chain matching + fragment assembly should significantly improve coverage.
- **Sources**:
  - Fragment assembly from Rosetta/I-TASSER protein structure prediction
  - Protenix+TBM approach analysis (scores 0.409 on LB)
  - DRfold2 RNA structure prediction
- **Research**: [research/research_IT005_fragment_assembly.md](research/research_IT005_fragment_assembly.md)
- **Plan**: [plans/plan_IT005_fragment_assembly.md](plans/plan_IT005_fragment_assembly.md)
- **Checkpoints**: None (template-based, no model weights)
- **Status**: RUNNING (pushed to Kaggle, awaiting results)
