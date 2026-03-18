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
  - `PDBRNADatabase` (download, build, search, align templates)
  - `RNAStructureAligner` (TM-score, structural alignment, sequence identity)
  - `TemplateModel` (predict, ensemble_predict)
  - `TemplateEnsemble` (weighted_average, consensus_structure)
  - Enhanced `RNADataLoader` with template functionality
- **Description**: Analyze competition leaderboard, identify template-based approach as current best performer, implement complete template prediction pipeline.
- **Motivation**: Leverage proven approach (template-based) for quick score improvement with 7 days remaining until deadline.
- **Sources**:
  - Competition leaderboard analysis (March 18, 2026)
  - Top team: "best_template_oracle" (0.554 RMSD)
  - Recent RNA structure prediction literature (2024-2026)
- **Research**: [research/research_IT002.md](research/research_IT002.md)
- **Plan**: [plans/plan_IT002.md](plans/plan_IT002.md)
- **Report**: [reports/report_IT002.md](reports/report_IT002.md) *(pending)*
- **Checkpoints**: Template database, trained alignment models
- **Status**: IN PROGRESS
