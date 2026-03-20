# Plan IT004 — Train Data Template Pipeline

**Iteration ID**: IT004
**Title**: Template-Based Prediction Using Competition Training Data
**Target Module(s)**: submissions/submission_SUB004.ipynb
**Hypothesis**: Using competition train data (5716 sequences) as templates with k-mer prefilter and alignment-based coordinate transfer will produce a valid submission with TM-score > 0.1.

## Files to Create/Modify

| File | Action | Purpose |
|------|--------|---------|
| `submissions/submission_SUB004.ipynb` | CREATE | New submission notebook |
| `submissions/submission_SUB004.md` | CREATE | Submission metadata |
| `submissions/kernel-metadata.json` | MODIFY | Point to SUB004 |
| `submissions/scoreboard.md` | MODIFY | Add SUB004 entry |
| `analysis/SUB003_postmortem.md` | CREATE | SUB003 analysis |
| `iteration_registry.md` | MODIFY | Add IT004 entry |

## Implementation Details

### Notebook Structure (10 cells)

1. **Setup & diagnostics**: List `/kaggle/input/` contents, detect data paths
2. **Load competition data**: train_sequences, train_labels, test_sequences, sample_submission
3. **Build template library**: Process train data into searchable index
4. **K-mer prefilter**: Fast candidate selection using 5-mer Jaccard + length ratio
5. **Alignment & coordinate transfer**: NW alignment + position mapping
6. **Chain-aware handling**: Parse stoichiometry, handle multi-chain complexes
7. **Structural constraints**: Bond distance enforcement, steric clash resolution
8. **Diversity generation**: 5 diverse predictions per target
9. **Build submission**: Write submission.csv in correct format
10. **Summary & validation**: Stats, NaN check, shape verification

### Key Design Decisions

- **No external datasets**: Use only competition data (train as templates)
- **No internet required**: Everything runs offline
- **No GPU required**: Pure numpy/pandas computation
- **No BioPython**: Use our own NW implementation (adequate for this task)
- **Time budget**: Target <30 minutes total runtime on Kaggle

## Expected Metric Impact

- Current: No submission (SUB003 produced 0 predictions)
- Expected: Valid submission with TM-score 0.1-0.3
- Best case: TM-score 0.2-0.4 if template matching works well

## Evaluation Plan

1. Verify notebook runs to completion on Kaggle
2. Verify submission.csv has correct shape and format
3. Check for NaN/inf values
4. Monitor Kaggle execution logs
5. Check TM-score on public leaderboard

## Rollback Plan

If SUB004 fails, revert kernel-metadata.json to SUB003 with fixed template DB.

## Linked Research

- `research/research_IT004_train_template_pipeline.md`
