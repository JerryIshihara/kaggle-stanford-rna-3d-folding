# Master Bibliography

All URLs, papers, notebooks, and references encountered across iterations. Tagged with the iteration that introduced them.

## Competition

| Title | URL | Iteration | Relevance |
|-------|-----|-----------|-----------|
| Stanford RNA 3D Folding Part 2 (competition page) | https://www.kaggle.com/competitions/stanford-rna-3d-folding-2 | IT001 | Main competition page |
| Stanford RNA 3D Folding Part 2 (data page) | https://www.kaggle.com/competitions/stanford-rna-3d-folding-2/data | IT001 | Data description and download |
| CompeteHub competition summary | https://www.competehub.dev/en/competitions/kagglestanford-rna-3d-folding-2 | SUB001 | Confirmed TM-score metric and C1' atom requirement |

## Kaggle Notebooks

| Title | URL | Iteration | Relevance |
|-------|-----|-----------|-----------|
| Stanford RNA 3D Baseline (ka ho fu) | https://www.kaggle.com/code/kahofu/stanford-rna-3d-baseline | SUB001 | Reference for submission format, column names, data loading pattern. Uses HistGradientBoostingRegressor + helical fallback. |
| Stanford RNA 3D - TBM Baseline (Yassine Alouini) | https://www.kaggle.com/code/yassinealouini/stanford-rna-3d-tbm-baseline | IT002 | Template-based modeling baseline |
| RNA 3D Folding Hybrid AI Pipeline (Hammad Farooq) | https://www.kaggle.com/code/hammadfarooq470/rna-3d-folding-hybrid-ai-pipeline | IT002 | Hybrid approach combining template and DL methods. 51 votes. |
| Stanford RNA 3D Folding Part 2 Winner (Hammad Farooq) | https://www.kaggle.com/code/hammadfarooq470/stanford-rna-3d-folding-part-2-winner | IT002 | Winner-inspired approach from first competition |
| RNA TaBM v74 Winner-Inspired TBM (Pawan Rama Mali) | https://www.kaggle.com/code/pawanmali/rna-tabm-v74-winner-inspired-tbm | IT002 | Template-based modeling with winner inspiration |
| Stanford RNA 3D - Protenix + TBM (Yassine Alouini) | https://www.kaggle.com/code/yassinealouini/stanford-rna-3d-protenix-tbm | IT002 | Combines Protenix with TBM |
| rna-protenix-tbm-v1 (Quadruped) | https://www.kaggle.com/code/jaclyndeem/rna-protenix-tbm-v1 | IT002 | Protenix + TBM approach, 38 votes |
| drfold (Furina) | https://www.kaggle.com/code/dfgtde/drfold | IT002 | DRfold-based approach, 24 votes |

## Academic Papers

| Title | Journal / Year | Iteration | Relevance |
|-------|---------------|-----------|-----------|
| Needleman & Wunsch, "A general method applicable to the search for similarities in the amino acid sequence of two proteins" | J. Mol. Biol. 48(3):443-453, 1970 | IT002 | Foundation of the global sequence alignment algorithm used in template search |
| Kabsch, "A solution for the best rotation to relate two sets of vectors" | Acta Crystallographica A32:922-923, 1976 | IT002 | Optimal rotation for coordinate superposition (RMSD calculation) |
| "Advances in RNA 3D structure prediction using deep learning" | Nature Methods, 2025 | IT002 | Overview of DL approaches for RNA structure prediction |
| "Geometric deep learning for biomolecular structure prediction" | Science, 2024 | IT002 | SE(3)-equivariant networks for structure prediction |
| "Template-based modeling of RNA 3D structures" | NAR, 2025 | IT002 | Methods and best practices for template-based RNA modeling |

## Tools and APIs

| Title | URL | Iteration | Relevance |
|-------|-----|-----------|-----------|
| RCSB PDB | https://www.rcsb.org/ | IT002 | Source of all template structures |
| RCSB Search API v2 | https://search.rcsb.org/rcsbsearch/v2/query | IT002 | Programmatic search for RNA structures |
| RCSB PDB file download | https://files.rcsb.org/download/ | IT002 | Download PDB coordinate files |
| HHpred (MPI Toolkit) | https://toolkit.tuebingen.mpg.de/tools/hhpred | IT002 | Profile-profile alignment for remote homology detection |
| Dali server | http://ekhidna2.biocenter.helsinki.fi/dali/ | IT002 | Structural alignment tool |
| Kaggle API (kernel push) | https://github.com/Kaggle/kaggle-api | SUB001 | CLI for pushing notebooks and managing submissions |
| Kaggle kernel metadata docs | https://github.com/Kaggle/kaggle-api/wiki/Kernel-Metadata | SUB001 | kernel-metadata.json format reference |

## Competition Leaderboard Snapshot (March 18, 2026) [IT002]

| Rank | Team | Score (TM-score) | Notes |
|------|------|----------|-------|
| 1 | best_template_oracle | 0.554 | Template-based approach |
| 2 | AyPy | 0.492 | Recent improvement (March 17) |
| 3 | Brad Shervheim and Jack Cole | 0.483 | Active team |
| 4 | Marcin Wojciechowski | 0.461 | Consistent performer |
| 5 | d4t4 | 0.460 | Strong contender |

Key insight: Template methods dominate the leaderboard. Score range is 0.448-0.554. Tight competition.

## Internal Debugging Insights [SUB001 -> SUB002]

| Finding | Source | Impact |
|---------|--------|--------|
| BatchNorm1d fails with batch_size=1 | SUB001 post-mortem | Training loss = inf, model never learns. Use InstanceNorm1d instead. |
| Raw PDB coordinates overflow Conv1d | SUB001 post-mortem | Coordinates (-100..100) * random weights -> overflow. Always normalize. |
| `kaggle kernels push` != competition submit | SUB001 post-mortem | Code competitions require notebook submission through UI, not just kernel push. |
| Template search is the bottleneck | SUB001 log analysis | 58 min for 28 targets because template search runs 5x per target. Cache it. |
| val_labels has 126 columns (not 18) | SUB001 log analysis | Richer training signal than expected. Worth investigating extra columns. |
