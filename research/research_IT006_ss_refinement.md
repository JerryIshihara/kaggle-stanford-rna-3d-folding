# Research: IT006 — Secondary Structure Constraints and Template Refinement

## Iteration ID: IT006
## Title: Secondary Structure-Guided Coordinate Refinement + Expanded Template Bank
## Target Module(s): submissions/

## Research Question
How can we improve from 0.211 TM-score (SUB004 LB) toward 0.35+ by adding secondary structure constraints, expanding the template bank, and refining transferred coordinates?

## Background / Context
- SUB004: 0.211 TM (confirmed LB score)
- SUB005: Kernel COMPLETE, LB PENDING (val mean 0.113, multi-template diversity)
- SUB006: Kernel COMPLETE, LB PENDING (val mean 0.1794, fragment assembly)
- SUB006 analysis: 6/28 targets > 0.3 TM, 22/28 < 0.3 (most < 0.1)
- Bimodal: excellent when good template exists, poor otherwise
- Competition oracle: 0.554, RibonanzaNet2: 0.40, RNABaselineModel: 0.364

## Findings

### 1. Template Bank Expansion
- Currently using ~2671 templates from training data (valid C1' coordinates)
- Competition also provides validation labels with ~3000 additional structures
- Adding validation bank increases template coverage by ~100%
- Expected: some currently-poor targets will find matches in validation set

### 2. Secondary Structure Prediction (Nussinov Algorithm)
- Nussinov DP algorithm predicts RNA base pairs from sequence alone
- O(n^3) time, O(n^2) space — feasible for sequences up to ~5000 nt
- Watson-Crick pairs: A-U, G-C; wobble: G-U
- Predicted base pairs → distance constraints: C1'-C1' ~10.5 Å for base pairs
- Used by RNABaselineModel (score 0.364) for low-confidence coordinate refinement
- Key insight: even approximate secondary structure improves de novo coordinate quality

### 3. Iterative Coordinate Refinement
- After template coordinate transfer, many violations exist:
  - Bond distances outside 5.5-6.5 Å range
  - Steric clashes (atoms < 3.8 Å)
  - Incorrect base-pair distances
- Iterative constraint satisfaction (similar to distance geometry):
  1. Fix bond distances to ~5.9 Å
  2. Push apart steric clashes
  3. Pull base pairs to ~10.5 Å
  4. Repeat 3-5 iterations
- This is a lightweight alternative to molecular dynamics

### 4. Template Quality Scoring
- Current approach: score by sequence alignment similarity alone
- Better scoring: combine alignment similarity with coordinate quality metrics:
  - Valid coordinate fraction (reject >20% NaN templates)
  - Bond distance regularity (std dev of consecutive distances)
  - Coverage ratio: mapped positions / query length
- Composite score: `similarity * coverage * quality_factor`

### 5. Winning Strategy from RNA 3D Folding Part 1
- "Template-based RNA structure prediction advanced through a blind code competition" (bioRxiv 2025)
- Winning approach: template discovery pipeline WITHOUT deep learning
- Key techniques: better template search, multiple template combination, coordinate refinement
- Confirms that template quality and selection are the main bottleneck

### 6. RNABaselineModel Analysis (0.364 TM)
- Uses BioPython pairwise2 for alignment (slower but potentially more accurate)
- 60 candidate pool (vs our 30)
- Includes base-pair attraction for low-confidence templates
- De novo fold with base-pair tendency for no-template targets
- Coordinate refinement: bond distance + clash + base-pair constraints

## Candidate Ideas
1. **Expand template bank with validation data** — HIGH IMPACT, LOW EFFORT
2. **Nussinov secondary structure prediction** — MEDIUM IMPACT, MEDIUM EFFORT
3. **Iterative coordinate refinement** — MEDIUM IMPACT, MEDIUM EFFORT
4. **Better template quality scoring** — MEDIUM IMPACT, LOW EFFORT
5. **Larger candidate pool (top 60)** — LOW-MEDIUM IMPACT, LOW EFFORT
6. **De novo fallback with secondary structure** — MEDIUM IMPACT for poor targets

## Expected Impact
- Template bank expansion: +0.02-0.05 TM (more coverage)
- Secondary structure + refinement: +0.03-0.08 TM (better coordinates)
- Template quality scoring: +0.01-0.03 TM (better selection)
- Combined: target 0.25-0.35 TM

## Risks / Assumptions
- Validation data may not be available in test kernel environment (need to check)
- Nussinov is a simplistic SS predictor; real SS may differ significantly
- Iterative refinement may diverge if constraints conflict
- Runtime must stay under 9 hours (currently 1235s for SUB006)

## Source Links
- Template-based RNA prediction (bioRxiv 2025): https://www.biorxiv.org/content/10.64898/2025.12.30.696949v1
- RNABaselineModel (Kaggle): https://www.kaggle.com/models/andrometocs/rnabaselinemodel
- RibonanzaNet2 (Kaggle): https://www.kaggle.com/models/shujun717/ribonanzanet2
- Nussinov algorithm: https://en.wikipedia.org/wiki/Nussinov_algorithm
- NuFold (Nature 2025): https://www.nature.com/articles/s41467-025-56261-7
- GARN3 coarse-grained: https://www.biorxiv.org/content/10.1101/2025.07.05.663322v1

## Recommended Next Action
Implement all 6 improvements in a new SUB007 notebook building on top of the SUB006 fragment assembly approach.
