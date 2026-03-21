# CLAUDE.md

## Project Overview

Kaggle competition pipeline for **Stanford RNA 3D Folding 2** — predicting 3D atomic coordinates (C1' atoms) of RNA molecules from sequence.

- **Competition**: https://www.kaggle.com/competitions/stanford-rna-3d-folding-2
- **Metric**: RMSD (lower is better) for training; TM-score best-of-5 (higher is better) for submission
- **Deadline**: March 25, 2026
- **Prize**: $75,000 USD
- **Current best public LB**: 0.246 (SUB003, multi-model ensemble)

## Session Startup

At the start of every session, read these files to understand current state:

1. `iteration_registry.md` — full history of iterations (IT001–IT005)
2. `submissions/scoreboard.md` — submission scores and statuses
3. `AGENT_RULES.md` — the 6-phase iteration protocol (Research → Plan → Implement → Evaluate → Document → Submit)

## Repository Structure

```
kaggle-stanford-rna-3d-folding/
├── CLAUDE.md                     # This file
├── AGENT_RULES.md                # 6-phase iteration protocol (MUST follow)
├── AGENTS.md                     # Cursor Cloud instructions
├── README.md                     # Project overview
├── iteration_registry.md         # Global iteration log
├── requirements.txt              # Python dependencies
├── setup.sh                      # Environment setup (venv + deps + data dirs)
├── configs/                      # YAML configs for each model type
│   ├── train_config.yaml         # RNN/CNN baseline
│   ├── train_gnn_config.yaml     # Graph Neural Network
│   ├── train_transformer_config.yaml  # Transformer
│   └── submit_config.yaml        # Submission pipeline
├── scripts/                      # Entry points and utilities
│   ├── run_pipeline.py           # Main CLI: train/validate/predict/submit
│   ├── download_pdb_rna.py       # Download RNA structures from RCSB PDB
│   ├── build_template_db.py      # Build template database
│   └── download_data.sh          # Download competition data via Kaggle API
├── data_processor/               # Data loading, features, dataset building
│   ├── loader.py                 # RNADataLoader (CSV, MSA parsing)
│   ├── dataset.py                # PyTorch Datasets + collate_rna()
│   └── template_db.py            # PDB template search, NW alignment
├── inferencer/                   # Model architectures and inference
│   ├── baseline_model.py         # RNN (GRU) and CNN models + model registry
│   ├── gnn_model.py              # E(n)-equivariant GNN (EGNN)
│   ├── transformer_model.py      # Pre-norm Transformer with pair bias
│   ├── template_model.py         # Template-based prediction + ensemble
│   └── predict.py                # Checkpoint loading, batch inference
├── optimizer/                    # Training infrastructure
│   ├── trainer.py                # Training loop, early stopping, checkpointing
│   └── losses.py                 # RMSD loss, masked MSE loss
├── validator/                    # Evaluation and splitting
│   ├── metrics.py                # RMSD, TM-score, Kabsch alignment
│   └── splitter.py               # KFold, GroupKFold, length-stratified
├── checkpoints/                  # Saved model weights (traceable to iteration IDs)
├── submissions/                  # Kaggle submission notebooks (SUB001–SUB005)
├── research/                     # Research artifacts per iteration
├── plans/                        # Implementation plans per iteration
├── reports/                      # Evaluation reports per iteration
├── analysis/                     # Submission post-mortems
└── learning/                     # Persistent knowledge base (cs/, ml/, bio/, sources.md)
```

## Running the Pipeline

Single entry point with subcommands:

```bash
# Setup environment
bash setup.sh

# Train a model
python scripts/run_pipeline.py train --config configs/train_transformer_config.yaml

# Validate with checkpoint
python scripts/run_pipeline.py validate --checkpoint checkpoints/IT004_best.pt

# Generate predictions
python scripts/run_pipeline.py predict --checkpoint checkpoints/IT004_best.pt

# Create submission
python scripts/run_pipeline.py submit --checkpoint checkpoints/IT004_best.pt
```

Without real competition data in `data/raw/`, the pipeline falls back to dummy/random data for smoke testing.

## Code Architecture

### Model Registry Pattern

Models are registered via dictionaries with factory functions:

```python
from inferencer.baseline_model import create_model
model = create_model("transformer", d_model=128, nhead=8, num_layers=6)
```

Available model types: `rnn`, `cnn`, `gnn`, `transformer`

The registry uses lazy imports (`_get_full_registry()` in `baseline_model.py`) so GNN/Transformer are optional.

### Factory Functions

- `create_model(model_type, **kwargs)` — model instantiation (`inferencer/baseline_model.py`)
- `get_loss_fn(name)` — loss function lookup (`optimizer/losses.py`)
- `get_splitter(name)` — CV splitter lookup (`validator/splitter.py`)

### Data Flow

```
CSV → RNADataLoader → RNAStructureDataset → DataLoader(collate_fn=collate_rna)
→ Padded batches: {seq_indices, coordinates, mask, lengths, ids}
```

All model outputs are `(batch, seq_len, 3)` tensors of xyz coordinates.

### Key Constants

- Nucleotide mapping: `{"A": 0, "C": 1, "G": 2, "U": 3, "T": 3}`
- Sentinel value threshold: coordinates < -1e15 are invalid (must be masked)

## Iteration Protocol

**All pipeline changes MUST follow the 6-phase cycle defined in `AGENT_RULES.md`:**

1. **Research** → `research/research_<ID>.md`
2. **Plan** → `plans/plan_<ID>.md`
3. **Implement** → Code changes tagged with iteration ID
4. **Evaluate** → Run pipeline, measure CV scores
5. **Document** → `reports/report_<ID>.md`, update iteration_registry.md and all READMEs
6. **Submit** (when applicable) → `submissions/submission_<SUB_ID>.ipynb`

### Iteration IDs

Format: `IT001`, `IT002`, ... (zero-padded to 3 digits). Check `iteration_registry.md` for the next available ID.

### Outcome Classification

Every iteration report must classify as: **PROMOTED**, **REJECTED**, **PARKED**, or **NEEDS_FOLLOWUP**.

### Learning Knowledge Base

After each iteration, sync new domain knowledge to `learning/`:
- `learning/cs/` — algorithms, data structures
- `learning/ml/` — architectures, training techniques
- `learning/bio/` — RNA biology, PDB format
- `learning/sources.md` — master bibliography (tag with iteration ID)

## Key Conventions

### Coding Style
- NumPy-style docstrings with Parameters/Returns sections
- Type hints on function signatures
- One main class per file with supporting utilities
- Registry/factory patterns for extensibility

### File Naming
| Artifact | Pattern |
|----------|---------|
| Research | `research/research_<ID>.md` |
| Plan | `plans/plan_<ID>.md` |
| Report | `reports/report_<ID>.md` |
| Checkpoint | `checkpoints/<ID>_<description>.pt` |
| Submission | `submissions/submission_<SUB_ID>.ipynb` |

## Important Caveats

- **No GPU available**: PyTorch runs on CPU only. Dummy data trains in seconds; real data will be slow.
- **No automated tests or linting**: No pytest, flake8, ruff, or pyproject.toml. Verify modules with `python -c "import <module>"` or run the pipeline as a smoke test.
- **No CI/CD**: No GitHub Actions or similar configured.
- **No external services**: Self-contained ML pipeline. No databases, Docker, or APIs required (except RCSB PDB for template download).
- **Data directories**: `data/{raw,processed,external}` must exist. `setup.sh` creates them.

## Current State (as of IT005)

### Completed Iterations
| ID | Title | Status |
|----|-------|--------|
| IT001 | Pipeline Bootstrap | PROMOTED |
| IT002 | Template Pipeline | PROMOTED |
| IT003 | Sentinel Value Fix | PROMOTED |
| IT004 | GNN & Transformer + Train-Data Templates | PROMOTED |
| IT005 | Multi-Template Diversity | IN PROGRESS |

### Submission Scores
| ID | Public LB | Status |
|----|-----------|--------|
| SUB001 | N/A | FAILED (loss=inf) |
| SUB002 | 0.211 | SUBMITTED |
| SUB003 | 0.246 | SUBMITTED (best) |
| SUB004 | Pending | SUBMITTED |
| SUB005 | Pending | SUBMITTED |

### Dependencies

Core: numpy, pandas, scikit-learn, torch, biopython, pyyaml, tqdm, requests, matplotlib, seaborn, jupyter, kaggle
