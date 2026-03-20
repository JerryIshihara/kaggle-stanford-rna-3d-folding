# Report IT005 — Fragment Assembly + Per-Chain Template Prediction

## Iteration ID
IT005

## Title
Fragment-based assembly, per-chain prediction, coverage-weighted scoring

## Target Modules
- inferencer (prediction pipeline)

## Files Changed
- `submissions/submission_SUB006.ipynb` — New notebook (17 cells)

## Functions/Features Changed
- NEW: `predict_single_chain()` — independent per-chain template matching
- NEW: `predict_complex()` — assembles per-chain predictions into full complex
- NEW: `fragment_assembly()` — splits long chains (>200nt) into overlapping fragments, finds templates per fragment, stitches via Kabsch superposition
- NEW: `find_templates_for_chain()` — coverage-weighted template scoring
- NEW: `get_chain_info()` — returns chain sequences (not just segments)
- IMPROVED: `needleman_wunsch()` — affine gap penalties (_GAP_OPEN=-4, _GAP_EXTEND=-1)
- IMPROVED: `transfer_coordinates()` — returns coverage fraction alongside coordinates

## Experiment Setup
- Template library: ~2671 training sequences with valid C1' coordinates
- Test set: 28 targets
- Kaggle kernel: `jerryishihara/stanford-rna-3d-fragment-assembly`
- No GPU, no internet, no external packages

## Validation Setting
- Validation set used if available on Kaggle (validation_sequences.csv + validation_labels.csv)
- Best-of-5 TM-score metric

## Metrics and Comparison

| Submission | Approach | Public LB TM-score | Status |
|-----------|---------|-------------------|--------|
| SUB004 | Full-seq template matching | 0.211 | BEST_CURRENT |
| SUB005 | Multi-template diversity | RUNNING | Pending |
| SUB006 | Fragment assembly + per-chain | RUNNING | Pending |

## Key Architectural Differences from SUB004

1. **Per-chain prediction**: SUB004 matched the full concatenated sequence. SUB006 parses stoichiometry, extracts individual chain sequences, and matches each chain independently against templates.

2. **Fragment assembly**: For chains >200nt with poor full-length template similarity (<0.40), SUB006 splits into overlapping fragments of 100nt with 30nt overlap, finds templates per fragment, and stitches using Kabsch superposition on overlapping regions.

3. **Coverage-weighted scoring**: Template scoring now incorporates: `score = nw_similarity × sqrt(length_ratio) × valid_fraction`. This prefers templates that provide coordinates for more positions.

4. **Multi-strategy diversity**: 5 prediction slots use different strategies:
   - Slot 1: Best full-chain template
   - Slot 2: Fragment assembly (if applicable) or second-best template
   - Slot 3: Weighted blend of top-3 templates
   - Slot 4: Fourth-best template
   - Slot 5: Fragment assembly variant or fifth template

5. **Affine gap penalties**: Gap open (-4) vs gap extend (-1) to prefer fewer, longer gaps — more biologically realistic.

## Outcome Classification
**NEEDS_FOLLOWUP** — Awaiting Kaggle execution results.

## Decision and Follow-up
- Monitor kernel execution at https://www.kaggle.com/code/jerryishihara/stanford-rna-3d-fragment-assembly
- Compare SUB006 vs SUB004 (0.211) and SUB005 when results available
- If improved: investigate secondary structure constraints (Nussinov) and inter-chain distance constraints
- If no improvement: analyze which per-chain vs full-seq decisions hurt specific targets

## Expected Timeline
- Kaggle kernel runtime: ~5-15 minutes (depending on fragment assembly overhead)
- Results available: within 1 hour of push
