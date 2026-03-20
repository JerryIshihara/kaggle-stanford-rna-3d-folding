# Report: IT005 — Multi-Template Diverse Prediction

## Iteration ID: IT005
## Title: Multi-Template Diversity with Local TM-Score Validation
## Target Module(s): submissions/

## Files Changed
- `submissions/submission_SUB005.ipynb` — New submission notebook
- `submissions/submission_SUB005.md` — Submission metadata
- `submissions/kernel-metadata.json` — Updated kernel reference
- `analysis/SUB004_postmortem.md` — Post-mortem of SUB004 (LB 0.211)
- `research/research_IT005_template_diversity.md` — Research notes
- `plans/plan_IT005_template_diversity.md` — Implementation plan

## Key Changes
1. **Multi-template prediction**: 5 different templates instead of 1+perturbations
   - Slot 1: Best template
   - Slot 2: Second-best template
   - Slot 3: Kabsch-weighted blend of top-3
   - Slot 4: Fourth-best template
   - Slot 5: Fifth-best template
2. **RNA-aware NW alignment**: Transition penalty=-0.5, transversion=-1.5
3. **Kabsch superposition for blending**: Proper structural alignment before averaging
4. **TM-score local validation**: Evaluate on validation set before test predictions
5. **Relaxed length filter**: ±50% (from ±30%)
6. **Helical gap interpolation**: RNA-like geometry for gap regions
7. **Expanded search**: PREFILTER_TOP=300, ALIGN_TOP=30

## Experiment Setup
- Kernel: `jerryishihara/stanford-rna-3d-template-refinement` v2
- Status: RUNNING on Kaggle
- Expected runtime: ~200-400s (increased due to more alignments)

## Metrics
- SUB004 baseline: 0.211 TM-score (public LB)
- SUB005 expected: 0.28-0.35 TM-score
- Actual: Pending (kernel running)

## Comparison vs Previous
| Aspect | SUB004 | SUB005 |
|--------|--------|--------|
| Template selection | Top-1 only | Top-5 different |
| Diversity method | Random perturbation | Different templates |
| Template blending | None | Kabsch-weighted top-3 |
| NW scoring | Uniform mismatch | Transition/transversion |
| Length filter | ±30% | ±50% |
| Gap filling | Linear interpolation | Helical interpolation |
| Validation | None | TM-score on val set |
| Search scope | 200/20 | 300/30 |

## Outcome Classification
**NEEDS_FOLLOWUP** — Kernel running, awaiting LB score.

## Decision and Follow-up
- If score improves significantly (>0.25): PROMOTE and iterate further
- If score similar or worse: investigate validation TM-scores for debugging
- Next potential improvements: DRfold2 integration, fragment assembly, better template selection with structural features
