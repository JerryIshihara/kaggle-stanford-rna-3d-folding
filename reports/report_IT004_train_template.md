# Report IT004: Train-Data Template-Based Prediction

**Iteration ID**: IT004
**Title**: Template-based prediction using competition training data
**Target Module(s)**: submissions/

## Files Changed

| File | Action | Description |
|------|--------|-------------|
| `submissions/submission_SUB004.ipynb` | CREATED | New notebook using train-data templates |
| `submissions/submission_SUB004.md` | CREATED | Submission metadata |
| `submissions/kernel-metadata.json` | MODIFIED | Updated to SUB004 |
| `submissions/scoreboard.md` | MODIFIED | Updated SUB003 to FAILED, added SUB004 |
| `analysis/SUB003_postmortem.md` | CREATED | SUB003 failure analysis |
| `research/research_IT004_train_template.md` | CREATED | Research notes |
| `plans/plan_IT004_train_template.md` | CREATED | Implementation plan |
| `iteration_registry.md` | MODIFIED | Added IT004 entry |
| `learning/sources.md` | MODIFIED | Added IT004 sources and insights |

## Experiment Setup

- **Kernel**: `jerryishihara/stanford-rna-3d-train-template-prediction-v4`
- **Platform**: Kaggle GPU kernel (NVIDIA P100, no internet)
- **Data**: Competition train data as template library (2671 valid templates from 5716 sequences)
- **Method**: K-mer prefilter → NW alignment → coordinate transfer → structural constraints → diversity transforms

## Results

### Kaggle Kernel Execution

| Metric | Value |
|--------|-------|
| Status | COMPLETE |
| Runtime | 229 seconds (~3.8 minutes) |
| Templates loaded | 2671 |
| Test targets processed | 28/28 |
| Submission rows | 9762 (correct) |
| NaN values | 0 |
| Zero values | 0 |
| Format | Correct (ID, resname, resid, x_1..z_5) |

### Key Timings

| Target | Length | Time |
|--------|--------|------|
| 8ZNQ | 30 | 0.2s |
| 9IWF | 69 | 0.7s |
| 9JGM | 210 | 2.9s |
| 9MME | 4640 | 61.5s |
| Average | 349 | ~7s |

### Critical Discovery: Data Path

Competition data is at `/kaggle/input/competitions/stanford-rna-3d-folding-2/` (with `competitions/` subdirectory),
NOT at `/kaggle/input/stanford-rna-3d-folding-2/` as previously assumed. This explains why SUB003 couldn't find the data.

## Comparison vs Prior Submissions

| Aspect | SUB003 | SUB004 |
|--------|--------|--------|
| Kernel status | COMPLETE (no output) | COMPLETE (valid CSV) |
| Templates loaded | 0 | 2671 |
| Test targets processed | 0 | 28 |
| Submission generated | No | Yes (9762 rows) |
| Competition submission | None | Awaiting manual UI submit |

## LB Score

- **Pending**: Competition submission requires manual action via Kaggle UI.
- The kernel completed successfully and `submission.csv` was generated.
- Expected TM-score range: 0.1-0.3 based on public template approaches.

## Outcome Classification

**NEEDS_FOLLOWUP**: The notebook works correctly and produces a valid submission,
but we need:
1. Manual submission through Kaggle UI for LB score
2. Analysis of actual TM-score performance
3. Comparison with public baselines

## Follow-up Recommendations

1. **Submit to competition** via Kaggle UI (manual step)
2. **Install BioPython** as offline wheel dataset for faster alignment
3. **Add neural refinement** on top of template predictions (reintroduce from SUB003)
4. **Use MSA features** for better template selection
5. **Explore Protenix+TBM** for potential 0.4+ TM-score
