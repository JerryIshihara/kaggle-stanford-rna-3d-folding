# Plan IT004: Train-Data Template-Based Prediction

**Iteration ID**: IT004
**Title**: Template-based prediction using competition training data
**Target Module(s)**: submissions/
**Hypothesis**: Using the competition's own training data (5716 sequences) as templates
will produce a valid submission with TM-score 0.1-0.3.

## Files to Create/Modify

| File | Action | Description |
|------|--------|-------------|
| `submissions/submission_SUB004.ipynb` | CREATE | New notebook using train-data templates |
| `submissions/submission_SUB004.md` | CREATE | Submission metadata |
| `submissions/kernel-metadata.json` | MODIFY | Point to SUB004 notebook |
| `submissions/scoreboard.md` | MODIFY | Add SUB004 entry |
| `analysis/SUB003_postmortem.md` | CREATE | Document SUB003 failure |

## Implementation Details

### Core Algorithm
1. Load `train_sequences.csv` + `train_labels.csv` as template library
2. Build k-mer index (5-mers, 2-bit encoded) for all templates
3. For each test target:
   a. Filter templates by length ratio (±30%)
   b. Score by k-mer Jaccard similarity (top 250)
   c. For top 30, compute alignment score using optimized NW
   d. Select top template(s) for coordinate transfer
   e. Full NW alignment + coordinate transfer with gap interpolation
   f. Apply RNA structural constraints
   g. Generate 5 diverse predictions
4. Write `submission.csv`

### Diversity Strategy (5 structures)
- Structure 1: Best template, direct transfer + constraints
- Structure 2: Best template + small Gaussian noise + constraints
- Structure 3: Hinge rotation at random pivot
- Structure 4: Chain jitter (rotation + translation per chain)
- Structure 5: Smooth wiggle (spline-based displacement)

### Key Differences from SUB003
- Templates from train data (5716 seqs), not external PDB (0 chains)
- No neural refinement (pure template matching)
- Chain-aware prediction using stoichiometry
- Proper structural constraints
- No dependency on external datasets

## Expected Metric Impact
- TM-score: 0.1-0.3 (from 0.0 / no submission)

## Evaluation Plan
- Kernel completes without errors
- Submission.csv generated with correct format
- Valid LB score obtained

## Rollback Plan
- Revert to SUB003 if SUB004 fails
- SUB003 template DB now has proper index file

## Linked Research
- `research/research_IT004_train_template.md`
