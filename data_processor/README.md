# data_processor

## Purpose

Data loading, cleaning, transformation, feature engineering, fold preparation, template building, augmentation, graph/tensor construction, caching, and preprocessing utilities.

## Current Responsibilities

- RNA sequence loading and encoding
- MSA file parsing
- Train/test data loading from CSV
- PyTorch Dataset and DataLoader construction
- Nucleotide-to-index mapping and padding
- Collation for variable-length sequences

## Active Files

| File | Description |
|------|-------------|
| `loader.py` | RNA data loading, MSA parsing, train/test CSV reading |
| `dataset.py` | PyTorch Dataset for RNA sequences and 3D structures |
| `template_db.py` | PDB RNA template database: search, download, index, alignment |

## Iteration History

| Iteration ID | File / Function / Feature | Description | Status | Research | Plan | Report |
|-------------|--------------------------|-------------|--------|----------|------|--------|
| IT002 | `template_db.py` / `PDBRNADatabase`, `needleman_wunsch`, `sequence_identity` | PDB RNA template database with RCSB API search, PDB parsing, k-mer pre-filter, Needleman-Wunsch alignment | PROMOTED | [research](../research/research_IT002.md) | [plan](../plans/plan_IT002.md) | [report](../reports/report_IT002.md) |

## Deprecated / Rejected Artifacts

*(none yet)*
