# Submission: SUB005

## Submission ID: SUB005
## Iteration: IT005

## Key Changes from SUB004
- **Multi-template prediction**: 5 different templates for 5 prediction slots (was 1+perturbations)
- **Template blending**: Slot 3 uses Kabsch-superposed weighted blend of top-3 templates
- **RNA-aware alignment**: Transition/transversion penalty distinction in NW scoring
- **Relaxed length filter**: ±50% (was ±30%) for better template coverage
- **Helical gap interpolation**: RNA-like helical geometry for gap regions
- **Local TM-score validation**: Evaluates on validation set before test predictions
- **Increased search**: PREFILTER_TOP=300, ALIGN_TOP=30 (was 200, 20)

## Module Versions
- Data: IT005 (train template library, improved filtering)
- Inferencer: IT005 (multi-template, Kabsch blend, helical gaps)
- Optimizer: N/A (no neural training)
- Validator: IT005 (TM-score computation)

## Expected Impact
- From 0.211 to estimated 0.28-0.35 TM-score
- Multi-template diversity: +0.05-0.10
- Better alignment + gap filling: +0.02-0.05

## Status: SUBMITTED

## Linked Artifacts
- Research: research/research_IT005_template_diversity.md
- Plan: plans/plan_IT005_template_diversity.md
- Analysis: analysis/SUB004_postmortem.md
