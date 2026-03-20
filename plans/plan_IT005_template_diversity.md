# Plan: IT005 — Template Diversity and Multi-Template Prediction

## Iteration ID: IT005
## Title: Multi-Template Diversity with Local TM-Score Validation
## Target Module(s): submissions/

## Hypothesis
Using 5 genuinely different templates for 5 predictions (instead of 1 template + 4 perturbations) will significantly improve TM-score by increasing the probability that at least one prediction closely matches the target structure. Adding template blending and helical gap filling will further improve quality.

## Files to Create/Modify
- `submissions/submission_SUB005.ipynb` — New submission notebook
- `submissions/submission_SUB005.md` — Submission metadata
- `submissions/kernel-metadata.json` — Updated kernel reference
- `submissions/scoreboard.md` — Updated scoreboard
- `iteration_registry.md` — New IT005 entry

## Key Changes

### 1. Multi-Template Prediction (prediction slots)
- Slot 1: Best template, direct coordinate transfer
- Slot 2: Second-best template (different from slot 1)
- Slot 3: Third-best template (different from slots 1-2)
- Slot 4: Similarity-weighted blend of top-3 templates
- Slot 5: Fourth-best template OR fragment assembly if no good single template

### 2. Improved Template Selection
- Relax length filter from ±30% to ±50%
- Increase PREFILTER_TOP from 200 to 300
- Increase ALIGN_TOP from 20 to 30
- Better NW scoring: RNA-aware with transition/transversion penalties

### 3. Similarity-Weighted Template Blending
- For blended prediction, use Kabsch superposition on shared aligned positions
- Weight contribution by NW normalized score
- Produces consensus structure

### 4. Local TM-Score Validation
- Implement TM-score computation
- Evaluate on validation set (40 structures)
- Print per-target and mean TM-score for debugging

### 5. Helical Gap Interpolation
- For gaps in alignment, generate RNA-like helical trace instead of linear interpolation
- Use A-form helix parameters: rise=2.81Å, twist=32.7°, radius=9.4Å per base pair

## Expected Metric Impact
- From 0.211 to estimated 0.28-0.35 TM-score
- Multi-template diversity is expected to contribute +0.05-0.10
- Blending + better gap filling: +0.02-0.05

## Evaluation Plan
- Test with validation set locally (if possible) to verify TM-score improvement
- Time the execution to ensure <9 hours (current: 193s, plenty of headroom)

## Rollback Plan
- If score decreases, revert to SUB004 approach
- Each change is modular and can be enabled/disabled independently

## Linked Research
- [research/research_IT005_template_diversity.md](../research/research_IT005_template_diversity.md)
