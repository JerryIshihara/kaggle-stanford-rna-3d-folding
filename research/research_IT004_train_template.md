# Research IT004: Train-Data Template-Based Prediction

**Iteration ID**: IT004
**Title**: Template-based prediction using competition training data
**Target Module(s)**: submissions/, inferencer/
**Research Question**: Can we achieve a valid LB submission using the competition's
own training data as templates instead of external PDB structures?

## Background / Context

SUB001-SUB003 all failed to produce valid Kaggle submissions. The core issues were:
1. External PDB template DB was empty/broken in the no-internet kernel environment
2. Neural refinement training diverged or had no training data
3. Competition data files were not accessed correctly

## Findings

### Competition Data Structure
- `train_sequences.csv`: 5716 sequences (lengths 10-125580, mean 1364)
- `train_labels.csv`: C1' atom coordinates for each residue (structure 1 only)
- `test_sequences.csv`: 28 test targets (lengths 19-4640, mean 349)
- `validation_labels.csv`: Up to 40 alternative structures per target
- `sample_submission.csv`: 5 structures required per test target

### Successful Public Approach (kami1976/stanford-template-based-rna-3d-folding-part-2)
- Uses **train data** as template library (5716 seqs with coords)
- BioPython PairwiseAligner for fast alignment (C implementation)
- Length-ratio prefilter (30%) → k-mer Jaccard prefilter (top 250) → alignment score (top 30)
- Alignment-based coordinate transfer with gap interpolation
- Chain-aware prediction using stoichiometry parsing
- Diversity via: best template, noise, hinge rotation, chain jitter, smooth wiggle
- RNA structural constraints: bond distance ~5.95Å, steric repulsion, smoothing

### Key Insights
1. No external data or internet needed — competition train data is the template library
2. No neural network needed for initial approach — pure template matching
3. Chain-aware handling is important for multi-chain RNA complexes
4. 5 diverse structures improve best-of-5 TM-score

## Candidate Ideas
1. **Direct port of public template approach** — highest certainty of working
2. **Hybrid: template + lightweight neural refinement** — for next iteration
3. **MSA features for better template selection** — future improvement

## Expected Impact
- From "no submission" to a valid LB score
- Expected TM-score: 0.1-0.3 (based on public template-only approaches)

## Risks / Assumptions
- Python NW implementation may be too slow for long sequences
- Need to handle NW memory for long sequences carefully
- BioPython not available without internet; need own NW or fast alternative

## Source Links
1. [Template-Based RNA 3D Folding (kami1976)](https://www.kaggle.com/code/kami1976/stanford-template-based-rna-3d-folding-part-2) — Full template approach with chain-aware constraints
2. [Protenix+TBM (llkh0a)](https://www.kaggle.com/code/llkh0a/stanford-rna-3d-folding-part-2-protenix-tbm) — Advanced approach combining Protenix with TBM, TM-score ~0.4
3. [Stanford RNA Folding 2 Template Approach (haradibots)](https://www.kaggle.com/code/haradibots/stanford-rna-folding-2-template-based-approach) — Another template-based approach

## Recommended Next Action
Implement the train-data template approach as SUB004, focusing on:
1. Correct data loading and diagnostic output
2. Fast k-mer prefilter + simplified alignment
3. Coordinate transfer with gap interpolation
4. Basic structural constraints
5. 5 diverse predictions via perturbation
