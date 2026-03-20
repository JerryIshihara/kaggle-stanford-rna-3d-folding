# Research: IT007 — Distance Geometry De Novo + Enhanced Refinement

## Iteration ID: IT007
## Title: Distance Geometry De Novo Folding + Simulated Annealing Refinement
## Target Module(s): submissions/

## Research Question
How can we improve TM-scores for the 22/28 targets that currently score < 0.1 (no good template match), using principled de novo coordinate generation and more aggressive refinement?

## Background / Context
- SUB006 achieved mean TM=0.179, with 6/28 targets > 0.3 but 22/28 < 0.1
- SUB007 (IT006) added Nussinov SS prediction and expanded templates; still RUNNING
- Current de novo fallback (`ss_denovo_fold`) is simplistic: sequential backbone placement with SS bias
- For targets without good templates, even small improvements (0.03 → 0.08) on many targets will boost the mean
- Competition deadline: March 25, 2026 (6 days remaining)

## Findings

### 1. Distance Geometry / Multidimensional Scaling (MDS)
- Classical MDS (eigendecomposition of doubly-centered distance matrix) can embed predicted pairwise distances into 3D
- Given Nussinov-predicted base pairs: paired residues ~10.5 Å apart, consecutive residues ~5.95 Å apart
- Can construct a sparse distance matrix from these constraints
- Source: Crippen & Havel (1988), "Distance Geometry and Molecular Conformation"
- Expected impact: Much better initial coordinates for de novo targets

### 2. Simulated Annealing Refinement
- Current refinement: 4 passes of bond + SS + clash + smoothing with linear decay
- Better: 20-50 iterations with temperature schedule, accepting worse solutions probabilistically
- RNA-specific energy terms: backbone torsion angles, base stacking (3.3-3.5 Å), phosphate distances
- Source: SimRNA (Boniecki et al., 2016, NAR) uses coarse-grained SA for RNA folding
- Expected impact: +0.02-0.05 TM on targets with some template but poor refinement

### 3. Better Diversity via Max-Dispersion Selection
- Current: fixed 5 slots with predetermined strategies
- Better: generate 10-15 candidates, then select the 5 most structurally diverse (max min-RMSD)
- This optimizes the best-of-5 metric directly
- Source: Standard ensemble diversification technique
- Expected impact: +0.01-0.03 TM (better use of 5 prediction slots)

### 4. Short-Range Distance Matrix Completion
- For RNA, distances between residues i and i+k (k=1..5) are well-constrained by backbone geometry
- Can pre-compute expected short-range distances from A-form helix parameters
- Use these to fill in the distance matrix for MDS
- Source: RNA A-form helix: rise=2.81 Å, twist=32.7°, C1'-C1' ~5.95 Å

### 5. Competition Landscape (March 19, 2026)
- Top LB: 0.554 (oracle), AyPy 0.499, RibonanzaNet2-based 0.40
- Template-based approaches dominate
- RibonanzaNet2 model available on Kaggle (shujun717/ribonanzanet2) but requires specific model code
- Top approach from Part 1 used template pipeline without deep learning

## Candidate Ideas
1. **Distance geometry de novo** (SELECTED) — MDS from Nussinov-predicted distance matrix
2. **SA refinement with temperature schedule** (SELECTED) — More iterations, RNA energy terms
3. **Max-dispersion diversity** (SELECTED) — Generate many, pick diverse 5
4. **Backbone torsion constraints** (SELECTED) — A-form helix geometry enforcement
5. RibonanzaNet2 integration (DEFERRED) — Requires model architecture code, high complexity

## Expected Impact
- De novo targets (22/28 < 0.1): improve from ~0.04 mean to ~0.08 mean → +0.03 overall
- Template targets (6/28 > 0.3): improve via better refinement → +0.01-0.02 overall
- Diversity optimization → +0.01-0.02 overall
- Combined expected: 0.18 → 0.22-0.26 on validation

## Risks / Assumptions
- MDS may produce non-physical geometries requiring heavy post-processing
- SA refinement increases compute time; must stay within Kaggle 9-hour limit
- Nussinov SS predictions may be inaccurate for pseudoknots/non-canonical pairs

## Source Links
1. "Template-based RNA structure prediction advanced through a blind code competition" — PMC, 2025 — Validates template-based approach dominance
2. SimRNA (Boniecki et al., 2016) — Coarse-grained SA for RNA 3D prediction
3. DRfold2 — PLOS Biology, 2026 — Composite language modeling for RNA structure
4. Kaggle competition leaderboard — Top: 0.554 oracle
