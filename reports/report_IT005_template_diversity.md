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
- SUB005 validation: Mean 0.113, Median 0.062, Best 0.582 (9IWF), 2/20 targets > 0.3
- SUB005 runtime: 828s for 28 test targets + 128s for 20 validation targets
- Templates used: 5716 (up from 2671 due to relaxed sentinel filtering)
- Public LB: Pending manual submission via Kaggle UI

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

## Validation Analysis
- 2 targets achieved excellent TM-scores: 9IWF (0.582), 9E9Q (0.504)
- 18 other targets scored < 0.20, most below 0.10
- This bimodal distribution suggests: when a good template exists, our method works well;
  but most targets lack a structurally similar template in the training data
- The relaxed sentinel filtering increased templates from 2671 to 5716, including many
  with partial NaN coordinates — these may introduce noise

## Key Observations
- More templates doesn't help if they're not structurally similar to the test targets
- The temporal cutoff means test structures are newer than training data
- Random template selection for slots 2-5 may not add meaningful diversity
  if top templates are all poor matches

## Outcome Classification
**NEEDS_FOLLOWUP** — Kernel completed, awaiting LB score (manual submission required).

## Decision and Follow-up
- Manual LB submission needed via Kaggle UI
- If LB score improves: PROMOTE
- Key bottleneck: template coverage, not template diversity
- Next priorities:
  1. Filter templates more strictly (require >80% valid coordinates)
  2. Consider DRfold2 or RibonanzaNet2 model integration for better ab initio prediction
  3. Fragment assembly for partial template coverage
  4. Secondary structure-guided template selection
