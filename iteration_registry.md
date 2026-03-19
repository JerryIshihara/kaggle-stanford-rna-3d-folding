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

---

### IT004 — GNN and Transformer Models

- **Iteration ID**: IT004
- **Title**: GNN and Transformer architectures for RNA 3D structure prediction
- **Module**: inferencer (primary), data_processor, scripts, configs
- **Files**:
  - `inferencer/gnn_model.py` (new)
  - `inferencer/transformer_model.py` (new)
  - `configs/train_gnn_config.yaml` (new)
  - `configs/train_transformer_config.yaml` (new)
  - `inferencer/baseline_model.py` (modified)
  - `optimizer/trainer.py` (modified)
  - `scripts/run_pipeline.py` (modified)
- **Functions / Features**:
  - `build_rna_graph` (RNA graph construction with backbone, skip, k-NN edges)
  - `EGNNLayer` (E(n)-equivariant message-passing layer with coordinate updates)
  - `RNAGraphModel` (full GNN model: embedding → graph → EGNN → coords)
  - `SinusoidalPositionalEncoding` (fixed sin/cos PE for length generalization)
  - `PreNormTransformerLayer` (pre-LN attention + FFN with optional pair bias)
  - `PairRepresentation` (AlphaFold-style outer product + relative PE)
  - `StructureModule` (MLP coordinate head)
  - `RNATransformerModel` (full Transformer: embedding → encoder → structure module)
  - `_get_full_registry()` (lazy-import model registry expansion)
  - `_model_kwargs()` (config → model constructor kwargs extraction)
- **Description**: Implemented two new deep learning architectures for RNA 3D structure prediction — an E(n)-equivariant Graph Neural Network (EGNN-style) and a pre-norm Transformer encoder with AlphaFold-style pair bias. Both integrated into the pipeline with full training support, config files, and backward-compatible model registry.
- **Motivation**: GNNs capture non-local base-pairing interactions through graph message passing; Transformers learn global pairwise relationships through self-attention. Both architectures are proven in state-of-the-art RNA structure prediction (EquiRNA, RhoFold+, trRosettaRNA).
- **Sources**:
  - Satorras et al., "E(n) Equivariant Graph Neural Networks", ICML 2021
  - RhoFold+, Nature Methods 2024
  - trRosettaRNA, Nature Communications 2023
  - EquiRNA, ICLR 2025
- **Research**: [research/research_IT004_gnn_transformer.md](research/research_IT004_gnn_transformer.md)
- **Plan**: [plans/plan_IT004_gnn_transformer.md](plans/plan_IT004_gnn_transformer.md)
- **Report**: [reports/report_IT004_gnn_transformer.md](reports/report_IT004_gnn_transformer.md)
- **Checkpoints**: `IT004_gnn_best.pt`, `IT004_transformer_best.pt` (dummy data validation)
- **Status**: PROMOTED

---

### IT004 — Train-Data Template-Based Prediction

- **Iteration ID**: IT004
- **Title**: Template-based prediction using competition training data
- **Module**: submissions/
- **Files**:
  - `submissions/submission_SUB004.ipynb`
  - `submissions/submission_SUB004.md`
  - `analysis/SUB003_postmortem.md`
- **Functions / Features**:
  - Train-data template library (2671+ sequences with C1' coordinates)
  - K-mer prefilter (5-mers, 2-bit encoded, Jaccard similarity)
  - Needleman-Wunsch alignment with banded mode for long sequences
  - Coordinate transfer with gap interpolation
  - Chain-aware prediction via stoichiometry parsing
  - RNA structural constraints (C1' bond distance, steric repulsion, smoothing)
  - Diversity transforms (hinge rotation, chain jitter, smooth wiggle)
  - Diagnostic file listing for data access debugging
- **Description**: Complete rewrite of submission approach. Uses competition's own training data as template library instead of broken external PDB database. No neural refinement, no internet, no external datasets.
- **Motivation**: SUB001-SUB003 all failed. SUB003 had empty template DB (0 chains) and couldn't find competition data files. Public notebooks demonstrate TM-score 0.1-0.4 with pure template matching from train data.
- **Sources**:
  - Public notebook: kami1976/stanford-template-based-rna-3d-folding-part-2
  - Public notebook: llkh0a/stanford-rna-3d-folding-part-2-protenix-tbm
- **Research**: [research/research_IT004_train_template.md](research/research_IT004_train_template.md)
- **Plan**: [plans/plan_IT004_train_template.md](plans/plan_IT004_train_template.md)
- **Report**: [reports/report_IT004_train_template.md](reports/report_IT004_train_template.md)
- **Checkpoints**: None (template-only approach, no model weights)
- **Status**: PROMOTED (LB Score: 0.211)

---

### IT005 — Multi-Template Diverse Prediction

- **Iteration ID**: IT005
- **Title**: Multi-template diversity with Kabsch blend and local TM-score validation
- **Module**: submissions/
- **Files**:
  - `submissions/submission_SUB005.ipynb`
  - `submissions/submission_SUB005.md`
  - `analysis/SUB004_postmortem.md`
- **Functions / Features**:
  - Multi-template prediction: 5 different templates for 5 prediction slots
  - Kabsch superposition for template blending (weighted average of top-3)
  - RNA-aware NW alignment (transition/transversion penalties)
  - Relaxed length filter (±50% from ±30%)
  - Helical gap interpolation (RNA A-form geometry)
  - Local TM-score validation on validation set
  - Expanded search (PREFILTER_TOP=300, ALIGN_TOP=30)
- **Description**: Major improvement to template utilization. Instead of using 1 template + 4 random perturbations, uses 5 different templates for true structural diversity. Adds Kabsch-based template blending and local validation.
- **Motivation**: SUB004 achieved 0.211 but top oracle is 0.554. Analysis shows template selection diversity is the primary bottleneck. Best-of-5 metric means maximizing diversity across predictions is critical.
- **Sources**:
  - SUB004 post-mortem analysis
  - Zhang lab RNA-align TM-score: https://zhanggroup.org/RNA-align/
  - Template-based RNA prediction: https://www.biorxiv.org/content/10.64898/2025.12.30.696949v1
- **Research**: [research/research_IT005_template_diversity.md](research/research_IT005_template_diversity.md)
- **Plan**: [plans/plan_IT005_template_diversity.md](plans/plan_IT005_template_diversity.md)
- **Report**: Pending (kernel running on Kaggle)
- **Checkpoints**: None (template-only approach)
- **Status**: IN PROGRESS
