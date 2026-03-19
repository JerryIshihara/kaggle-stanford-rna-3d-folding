# SUB003 -- Multi-Model Ensemble: Template + ResNet + Transformer Refinement

**Submission ID**: SUB003
**Kernel**: jerryishihara/stanford-rna-3d-template-refinement (v3)
**Lineage**: IT001 → IT002 → IT004 → SUB001 (failed) → SUB002 (0.211) → SUB003

## Improvements over SUB002

| Change | SUB002 | SUB003 |
|--------|--------|--------|
| Template DB size | 2000 entries, 4.0 Å max | 3000 entries, 4.5 Å max |
| Top-k templates | 5 | 8 |
| Min identity threshold | 0.20 | 0.15 |
| Refinement models | ResNet only | ResNet + Transformer ensemble |
| Training structures | 5 per target | All available (auto-detected) |
| Alignment for long seqs | Full NW (O(N²) memory) | Banded NW for seqs > 1000 nt |
| Diversity strategy | Noise + MC-dropout (1 model) | Model diversity + noise + MC-dropout |
| Training epochs | 25 | 30 |

## Method

1. Build PDB RNA template database (RCSB API, 3000 entries, ≤4.5 Å resolution)
2. Template-based prediction: k-mer filter + Needleman-Wunsch + identity-weighted ensemble
3. Multi-model refinement:
   - **ResNet**: 1D dilated residual network with InstanceNorm (proven from SUB002)
   - **Transformer**: Pre-norm Transformer encoder with sinusoidal PE (from IT004 research)
4. Confidence-weighted ensemble of template + ResNet + Transformer predictions
5. 5 diverse structures using model diversity + MC-dropout + noise perturbation:
   - Struct 1: Full ensemble (template + ResNet + Transformer), no noise
   - Struct 2: ResNet with MC-dropout + noise
   - Struct 3: Transformer with MC-dropout + noise
   - Struct 4: ResNet with larger noise
   - Struct 5: Transformer with conservative noise

## Key Parameters

- `max_pdb_entries`: 3000
- `max_resolution`: 4.5 Å
- `top_k_templates`: 8
- `min_identity`: 0.15
- ResNet: hidden=128, layers=6, kernel=5, epochs=30
- Transformer: d_model=128, nhead=4, layers=4, epochs=30
- Ensemble weights: template=0.4, resnet=0.3, transformer=0.3

## Module Versions

| Module | Version | Notes |
|--------|---------|-------|
| data_processor | IT002 | PDB template database |
| inferencer | IT004 | Template + ResNet + Transformer |
| optimizer | SUB003 (inline) | Dual-model training with cosine annealing |
| validator | N/A | Validation via Kaggle LB |

## Artifacts

- `submission_SUB003.ipynb` -- notebook
- `kernel-metadata.json` -- updated to point to SUB003
- `submission_SUB003.md` -- this file
