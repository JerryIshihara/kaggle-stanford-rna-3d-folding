# Submission SUB006

## Submission ID
SUB006

## Iteration
IT005

## Kaggle Kernel
- **Name**: Stanford RNA 3D - Fragment Assembly
- **URL**: https://www.kaggle.com/code/jerryishihara/stanford-rna-3d-fragment-assembly
- **Version**: 1
- **Status**: RUNNING

## Module Versions
- **Data Processor**: IT005 (train-data template library with coverage tracking)
- **Inferencer**: IT005 (per-chain prediction + fragment assembly + coverage-weighted scoring)
- **Optimizer**: N/A (template-based, no training)
- **Validator**: IT005 (TM-score computation with Kabsch alignment)

## Key Components
1. Template library from training data (~2671 templates)
2. K-mer prefilter (k=5, top 300 candidates)
3. Affine gap Needleman-Wunsch with RNA-specific scoring
4. Per-chain independent template matching
5. Fragment assembly for long chains (>200nt, low similarity)
6. Coverage-weighted template scoring
7. Kabsch-based template blending and fragment stitching
8. RNA structural constraints (C1'-C1' distance, steric repulsion)
9. Multi-strategy diversity for best-of-5

## Expected Improvement
- SUB004 (baseline): 0.211 TM-score
- SUB006 (expected): 0.25-0.30 TM-score

## Lineage
SUB004 (0.211) → SUB005 (pending) → SUB006

## Status
SUBMITTED — awaiting Kaggle execution results
