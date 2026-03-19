# SUB003 -- Template + Neural Refinement (Sentinel Fix)

**Submission ID**: SUB003
**Kernel**: jerryishihara/stanford-rna-3d-template-refinement (v3)
**Lineage**: IT001 → IT002 → SUB001 (failed) → SUB002 (loss ~1e34) → SUB003

## Fixes from SUB002 Analysis

| Issue | Root Cause | Fix |
|-------|-----------|-----|
| Training loss ~1e34 | Sentinel values (-1e18) in validation_labels treated as valid coords | Filter residues where any coord < -1e15 |
| Loss on invalid residues | No masking for missing ground truth | Per-residue binary mask in loss computation |
| V3 kernel no data found | Wrong competition data path | Robust path detection trying multiple mount points |
| Never submitted | `kaggle kernels push` ≠ competition submission | Document proper submission process |
| Random head init -> huge deltas | Randomly initialized head weights | Zero-initialize head weights (initial delta = 0) |
| Unbounded delta output | No output constraint | `tanh(raw) * delta_scale` constrains output to [-2, 2] in normalized space |
| MSE sensitive to outliers | MSE loss | Huber loss (`SmoothL1Loss`) for robustness |
| Scale floor too small | `scale + 1e-8` | `scale = max(np.std(centered), 1.0)` |
| Internet dependency | Downloads from RCSB at runtime | Pre-built template DB uploaded as Kaggle dataset |
| ReLU accumulation in residuals | ReLU activation | GELU activation + Kaiming initialization |

## Method

1. Build PDB RNA template database (RCSB API, 2000 entries, ≤4.0 Å resolution)
2. Template-based prediction: k-mer filter + Needleman-Wunsch + Kabsch ensemble
3. Neural refinement: 1D ResNet with InstanceNorm, trained on **sentinel-filtered** normalized coordinates
4. Per-residue masked loss: Only residues with valid ground truth contribute to gradient
5. Fallback: if refinement diverges, use pure template predictions
6. 5 diverse structures: MC-dropout + noise perturbation on cached template coords

## Key Parameters

- `max_pdb_entries`: 2000
- `refine_hidden`: 128, `refine_layers`: 6, `refine_kernel`: 5
- `refine_epochs`: 40, `refine_lr`: 1e-4
- `noise_std`: 0.5
- `SENTINEL_THRESHOLD`: -1e15
- Coordinate normalization: centroid subtraction + std scaling
- Valid residue threshold: 30% minimum per structure

## Module Versions

| Module | Version | Key Changes |
|--------|---------|-------------|
| data_processor | IT002 | `template_db.py` (inlined, C1' atom preference) |
| inferencer | IT002 | `template_model.py` (inlined) |
| optimizer | SUB003 | Sentinel filtering + masked loss |
| validator | N/A | Validation via training loss tracking |

## Artifacts

- `submission_SUB003.ipynb` — fixed notebook
- `kernel-metadata.json` — updated to point to SUB003
- `research/research_IT003_sentinel_fix.md` — root cause analysis
- `plans/plan_IT003_sentinel_fix.md` — implementation plan
