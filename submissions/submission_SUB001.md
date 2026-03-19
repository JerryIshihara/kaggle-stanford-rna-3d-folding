# Submission SUB001 — Template + Neural Refinement

## Submission ID
SUB001

## Title
Template-based prediction with 1D ResNet coordinate refinement

## Iteration Lineage
- **IT001**: Pipeline bootstrap (modular structure, baseline code)
- **IT002**: Template-based pipeline (PDB database, Needleman-Wunsch alignment, coordinate transfer, helix fallback)
- **SUB001**: Training notebook combining template pipeline with learned refinement

## Module Versions
| Module | Version | Key Files |
|--------|---------|-----------|
| data_processor | IT002 | `template_db.py` (inlined, C1' atom preference fix) |
| inferencer | IT002 | `template_model.py` (inlined) |
| optimizer | SUB001 | Inline training loop (MSE loss, Adam, CosineAnnealingLR) |
| validator | N/A | Validation via training loss tracking |

## Method Summary
1. **Template database**: 2000 RNA structures from RCSB PDB (resolution <= 4.0 A), indexed by chain with C1' atom coordinates
2. **Template prediction**: k-mer Jaccard pre-filter, Needleman-Wunsch alignment, identity-weighted coordinate transfer ensemble (top-5 templates)
3. **Neural refinement**: 1D ResNet (6 residual blocks, 128 hidden, dilated convolutions) trained to predict delta corrections on template coordinates
4. **Training data**: `validation_labels.csv` ground-truth coordinates paired with template predictions on `validation_sequences.csv`
5. **5 diverse structures**: MC-dropout + Gaussian noise perturbation on template inputs for structural diversity

## Key Parameters
```yaml
max_pdb_entries: 2000
max_resolution: 4.0
top_k_templates: 5
min_identity: 0.2
refine_hidden: 128
refine_layers: 6
refine_kernel: 5
refine_dropout: 0.15
refine_lr: 3e-4
refine_epochs: 25
noise_std: 0.3
```

## Artifacts
- Notebook: `submissions/submission_SUB001.ipynb`
- Metadata: `submissions/kernel-metadata.json`
- Kaggle kernel: `jerryishihara/stanford-rna-3d-template-refinement`

## Changes from Source Modules
- **C1' atom preference**: `_parse_pdb_text` atom priority changed from `["C3'", "C1'", "P"]` to `["C1'", "C3'", "P"]` to match competition evaluation metric (C1' coordinates)
- **All code inlined**: No module imports; entire pipeline is self-contained in the notebook

## Submission Date
March 18, 2026

## Score
Pending (awaiting Kaggle execution)
