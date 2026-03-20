# SUB003 -- Template + Neural Refinement (No Internet)

**Submission ID**: SUB003
**Kernel**: jerryishihara/stanford-rna-3d-template-neural-refinement-v3
**Lineage**: IT001 -> IT002 -> SUB001 (inf) -> SUB002 (7.5e33) -> SUB003

## Key Changes from SUB002

| Change | Why |
|--------|-----|
| `enable_internet: false` | Competition requires no internet for submission |
| Pre-built template DB as Kaggle dataset (`jerryishihara/rna-pdb-template-db`) | Loads 499 PDB entries offline |
| Zero-initialized head weights | Initial prediction = template (delta=0), loss starts reasonable |
| `tanh(raw) * delta_scale` output | Constrains deltas to [-2, 2] in normalized space |
| Huber loss (SmoothL1Loss) | Robust to outlier residues |
| `scale = max(std, 1.0)` | Prevents division by tiny values for short sequences |
| GELU activation + Kaiming init | More stable gradient flow than ReLU |
| 4 residual blocks (was 6) | Reduce risk of activation growth |
| lr=1e-4 (was 3e-4), 40 epochs (was 25) | Slower, more stable convergence |

## Method

1. Load pre-built PDB RNA template database (499 entries, ~3700 chains)
2. Template-based prediction: k-mer filter + Needleman-Wunsch + identity-weighted ensemble
3. Neural refinement: 1D ResNet with InstanceNorm, trained on normalized coordinates
4. Fallback: if refinement diverges, use pure template predictions
5. 5 diverse structures: MC-dropout + noise perturbation on cached template coords

## Artifacts

- `submission_SUB003.ipynb` -- the submission notebook
- `kernel-metadata.json` -- points to SUB003, internet disabled
- `analysis/SUB002_postmortem.md` -- documents the 7.5e33 loss failure
