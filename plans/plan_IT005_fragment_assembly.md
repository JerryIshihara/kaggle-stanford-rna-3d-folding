# Plan IT005 — Fragment Assembly and Per-Chain Template Matching

## Iteration ID
IT005

## Title
Fragment-based assembly, per-chain prediction, and improved template scoring

## Target Modules
- inferencer (prediction pipeline)
- data_processor (template library)

## Hypothesis
Per-chain independent prediction combined with fragment-based assembly for long chains will significantly improve TM-score by:
1. Avoiding poor full-sequence matches for multi-chain targets
2. Achieving better coverage for long sequences via fragment-based matching
3. Using position-aware template scoring to select the best template per region

Expected improvement: 0.211 → 0.25-0.30 TM-score

## Files to Create/Modify
- `submissions/submission_SUB006.ipynb` — New notebook implementing all improvements

## Features to Add

### 1. Per-Chain Independent Prediction
- Parse stoichiometry → individual chain sequences
- For each chain, run template matching independently
- Use chain-specific length filtering (chain length ±50% vs full complex length)
- Assemble per-chain predictions into full complex coordinates

### 2. Fragment-Based Assembly
- For chains > 200nt without good full-length template (similarity < 0.5):
  - Split into overlapping fragments of 100nt with 30nt overlap
  - Find best template per fragment
  - Transfer coordinates per fragment
  - Stitch fragments using Kabsch superposition on overlapping regions
- For chains ≤ 200nt or with good templates: use standard full-chain matching

### 3. Coverage-Weighted Template Scoring
- New scoring: `score = nw_similarity × coverage × sqrt(min(qlen, tlen) / max(qlen, tlen))`
- Coverage = fraction of query positions mapped to template positions with valid coordinates
- This prefers templates that provide coordinates for more residue positions

### 4. Multi-Template Region Assembly
- For each prediction slot, use a different assembly strategy:
  - Slot 1: Best full-chain template
  - Slot 2: Fragment assembly from best per-fragment templates
  - Slot 3: Weighted blend of top 3 templates (existing)
  - Slot 4: Best alternative template (different from slot 1)
  - Slot 5: Fragment assembly with second-best fragments

### 5. Improved Constraint Refinement
- Apply constraints per-chain (not per-complex)
- Add inter-chain proximity constraints for multi-chain targets
- Increase refinement passes for low-confidence predictions

## Expected Metric Impact
- TM-score: 0.211 → 0.25-0.30 (conservative)
- Most improvement expected on multi-chain targets and long sequences

## Evaluation Plan
- Local validation on validation set (if available on Kaggle)
- Submit to public LB and compare with SUB004 (0.211)
- Track per-target scores to identify which improvements helped most

## Rollback Plan
If SUB006 scores worse than SUB004:
- Revert to SUB004/SUB005 approach
- Analyze which specific change caused regression
- Apply only the improvements that help

## Linked Research
- [research/research_IT005_fragment_assembly.md](../research/research_IT005_fragment_assembly.md)
