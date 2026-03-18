# Stanford RNA 3D Folding 2 — Kaggle Competition Pipeline

## Competition

- **Name**: Stanford RNA 3D Folding 2
- **URL**: https://www.kaggle.com/competitions/stanford-rna-3d-folding-2
- **Metric**: RMSD (Root Mean Square Deviation) — lower is better
- **Deadline**: March 25, 2026 (23:59 UTC)
- **Prize Pool**: $75,000 USD

## Current Best

- **Best Score**: N/A (bootstrap phase)
- **Best Submission ID**: N/A
- **Best Module Combination**: N/A

## Project Structure

```
kaggle-stanford-rna-3d-folding/
├── README.md                  # This file
├── iteration_registry.md      # Global iteration log
├── requirements.txt           # Python dependencies
├── setup.sh                   # Environment setup
├── configs/                   # YAML configuration files
├── scripts/                   # Utility and orchestration scripts
├── src/                       # Legacy source code (untouched)
│   └── AGENT_RULES.md        # Agent iteration protocol
├── data_processor/            # Data loading, feature engineering, dataset building
├── inferencer/                # Model architectures, inference, ensembling
├── optimizer/                 # Training loops, losses, schedulers
├── validator/                 # CV splits, metrics, evaluation
├── checkpoints/               # Saved model weights and training states
├── research/                  # Research artifacts per iteration
├── plans/                     # Implementation plans per iteration
├── reports/                   # Evaluation reports per iteration
└── submissions/               # Kaggle-ready submission assemblies
```

## Module Overview

| Module | Purpose | README |
|--------|---------|--------|
| data_processor | Data loading, cleaning, feature engineering, dataset building | [data_processor/README.md](data_processor/README.md) |
| inferencer | Model architecture, forward/inference logic, post-processing | [inferencer/README.md](inferencer/README.md) |
| optimizer | Training loop, loss functions, schedulers, checkpoint policy | [optimizer/README.md](optimizer/README.md) |
| validator | Cross-validation, metrics, split generation, ablation | [validator/README.md](validator/README.md) |

## Iteration Index

See [iteration_registry.md](iteration_registry.md) for the full iteration log.

### Promoted Improvements

| Iteration | Module | Description | Score Impact |
|-----------|--------|-------------|-------------|
| *(none yet)* | | | |

### Rejected Ideas

| Iteration | Module | Description | Reason |
|-----------|--------|-------------|--------|
| *(none yet)* | | | |

## Links

- [Iteration Registry](iteration_registry.md)
- [Checkpoints README](checkpoints/README.md)
- [Research README](research/README.md)
- [Plans README](plans/README.md)
- [Reports README](reports/README.md)
- [Submissions README](submissions/README.md)
- [Scoreboard](submissions/scoreboard.md)
