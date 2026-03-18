# Plan — IT001: Pipeline Bootstrap

## Iteration ID
IT001

## Title
Pipeline bootstrap — create modular project structure, baseline code, and tracking infrastructure

## Target Module(s)
All (data_processor, inferencer, optimizer, validator, checkpoints, research, plans, reports, submissions)

## Hypothesis
A fully modular, documented pipeline with iteration tracking will enable rapid, disciplined experimentation and prevent loss of knowledge across iterations.

## Files to Create / Modify

### New directories
- `data_processor/`, `inferencer/`, `optimizer/`, `validator/`, `checkpoints/`
- `research/`, `plans/`, `reports/`, `submissions/`

### New files — module code
- `data_processor/loader.py` — RNA data loading, MSA parsing
- `data_processor/dataset.py` — PyTorch Dataset and collation
- `inferencer/baseline_model.py` — RNN and CNN baseline models
- `inferencer/predict.py` — inference wrapper
- `optimizer/losses.py` — RMSD and MSE loss functions
- `optimizer/trainer.py` — training loop with checkpointing
- `validator/metrics.py` — RMSD metric computation
- `validator/splitter.py` — CV fold generation

### New files — documentation and tracking
- `README.md` (root, rewritten)
- `iteration_registry.md`
- `checkpoints/README.md`
- All module README files
- `research/README.md`, `plans/README.md`, `reports/README.md`
- `submissions/README.md`, `submissions/scoreboard.md`

### New files — agent automation
- `.cursor/rules/kaggle-iteration.mdc`
- `src/AGENT_RULES.md`

### New files — orchestration
- `scripts/run_pipeline.py`

## Exact Functions / Features to Add
- `RNADataLoader` class with `load_train`, `load_test`, `load_msa`, `load_sample_submission`
- `encode_sequence`, `parse_coordinates` utility functions
- `RNAStructureDataset`, `RNATestDataset` PyTorch datasets with `collate_rna`
- `RNNModel`, `CNNModel` with `create_model` factory
- `load_checkpoint`, `predict_batch`, `predict_sequences` inference functions
- `rmsd_loss`, `masked_mse_loss` differentiable losses
- `Trainer` class with `fit` method, early stopping, checkpointing
- `rmsd`, `rmsd_per_sample`, `evaluate_fold`, `evaluate_cv` metric functions
- `simple_kfold`, `group_kfold`, `length_stratified_kfold` split strategies

## Evaluation Plan
IT001 is structural. Success criteria:
1. All directories and files exist
2. All README files contain required content per spec
3. Module code is syntactically valid
4. Pipeline runner script can be invoked
5. Agent rules are in place for future iteration automation

## Rollback Plan
Delete all newly created directories and files; restore original README.md from git.

## Linked Research File
[research/research_IT001.md](../research/research_IT001.md)
