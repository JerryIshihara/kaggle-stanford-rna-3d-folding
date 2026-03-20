# Research IT004 — Train Data Template Pipeline

**Iteration ID**: IT004
**Title**: Template-Based Prediction Using Competition Training Data
**Target Module(s)**: submissions/, inferencer/
**Research Question**: Can we achieve a valid competition submission by using the competition's own training data as a template library?

## Background / Context

SUB001-SUB003 all failed to produce valid competition submissions:
- SUB001: inf loss (BatchNorm bug)
- SUB002: 7.5e33 loss (normalization floor), internet blocking
- SUB003: 0 predictions (empty template DB, competition data not found)

The fundamental flaw was using an external PDB template database instead of the competition's own training data (5716 sequences with ground-truth C1' 3D coordinates).

## Findings

### Competition Data Structure

| File | Rows | Key Columns |
|------|------|-------------|
| `train_sequences.csv` | 5716 | target_id, sequence, stoichiometry, all_sequences |
| `train_labels.csv` | ~7.7M | ID, resname, resid, x_1, y_1, z_1, chain, copy |
| `test_sequences.csv` | 28 | target_id, sequence, stoichiometry, all_sequences |
| `sample_submission.csv` | 9762 | ID, resname, resid, x_1..z_5 (5 structures) |
| `validation_sequences.csv` | 28 | Same as train_sequences |
| `validation_labels.csv` | 9762 | ID, ..., x_1..z_40 (40 structures) |
| `MSA/` | ~5716 | Multiple Sequence Alignments per target |

### Public Notebook Analysis: kami1976/stanford-template-based-rna-3d-folding-part-2

A pure template-based approach (no deep learning) that:
1. Uses train data as template library (5716 entries)
2. K-mer prefilter (k=5, top 250) → BioPython PairwiseAligner scoring (top 30)
3. Alignment-based coordinate transfer with interpolation for gaps
4. Chain-aware constraints (stoichiometry parsing, segment handling)
5. Adaptive RNA constraints (bond distance ~5.95Å, steric clash resolution)
6. Diversity via: best template, noise, hinge rotation, chain jitter, smooth wiggle
7. No internet, no GPU, no external datasets needed

### Public Notebook: llkh0a/protenix-tbm (TM-score ~0.408)

Uses Protenix (RNA structure prediction model) + Template-Based Modeling:
- Much more complex, uses pre-trained model weights
- TM-score 0.408 on public LB
- Requires specific model weights as dataset

### Key Metric: TM-score

- Range: 0.0 to 1.0 (higher is better)
- Final score = average of best-of-5 TM-scores across test targets
- TM-score accounts for global fold quality, not just local distances

## Candidate Ideas

1. **[SELECTED] Train-data template pipeline** — Use competition train data as templates
   - Expected impact: From 0 (no submission) to a valid submission with TM-score 0.1-0.3
   - Risk: Low — straightforward implementation
   - Scope: Medium — new notebook, reuse some existing code

2. **BioPython alignment** — Use BioPython PairwiseAligner for faster/better alignment
   - Blocked: BioPython not pre-installed on Kaggle, needs wheel dataset
   - Defer to IT005

3. **Protenix + TBM** — Use pre-trained Protenix model
   - Blocked: Requires model weights and specific setup
   - Expected TM-score: 0.3-0.4+
   - Defer to IT005/IT006

## Recommended Next Action

Implement the train-data template pipeline (Idea 1) as SUB004.
This is the minimum viable approach to get a valid competition submission.

## Source Links

| Title | URL | Relevance |
|-------|-----|-----------|
| Template-Based RNA 3D Folding Part 2 | https://www.kaggle.com/code/kami1976/stanford-template-based-rna-3d-folding-part-2 | Primary reference for template approach |
| Protenix+TBM | https://www.kaggle.com/code/llkh0a/stanford-rna-3d-folding-part-2-protenix-tbm | Top scoring approach reference |
| CompeteHub summary | https://www.competehub.dev/en/competitions/kagglestanford-rna-3d-folding-2 | Competition overview and metric details |
