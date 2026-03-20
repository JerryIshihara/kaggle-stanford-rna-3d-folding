# Research IT005 — Fragment Assembly and Per-Chain Template Matching

## Iteration ID
IT005

## Title
Fragment-based assembly, per-chain prediction, and secondary structure constraints

## Target Modules
- inferencer (prediction pipeline)
- data_processor (template library, alignment)

## Research Question
How can we improve template-based RNA 3D prediction from 0.211 TM-score by addressing the core weaknesses: poor template coverage for long sequences, suboptimal multi-chain handling, and lack of structural constraints?

## Background / Context
SUB004 scored 0.211 on public LB using a simple template matching approach with 2671 training templates. The top approaches score ~0.40+ (Protenix+TBM) and the oracle template score is 0.554. Key gaps identified:

1. **Full-sequence matching is suboptimal**: Many test targets are multi-chain complexes (concatenated chains). Matching the full concatenated sequence against templates finds poor matches because no single template covers the whole complex.
2. **No fragment-based assembly**: For queries longer than any good template, we need to split into fragments and assemble.
3. **Gap interpolation is crude**: Linear or simple helical interpolation doesn't capture real RNA geometry.
4. **Limited diversity in best-of-5**: Using different templates is good, but we don't systematically maximize structural diversity.

## Findings

### From Kaggle Competition Analysis
- **Protenix+TBM scores ~0.409**: Uses deep learning (Protenix) plus template-based modeling. Not achievable without pre-built wheels/models. [Source: Kaggle notebook by nihilisticneuralnet]
- **DRfold2 alone scores ~0.40**: Deep learning approach. Requires GPU and pre-installed package. [Source: Kaggle discussion]
- **Template oracle scores 0.554**: Best possible with perfect template selection, showing templates are sufficient for good scores.
- **Public template notebooks score 0.15-0.25**: Most pure template approaches without deep learning score in this range.

### From Literature
- **RNA-align** (Bioinformatics 2019): TM-score based RNA structure alignment. The TM-score metric: d0 = 0.6*sqrt(L-0.5) - 2.5 for L≥15. Key insight: even small improvements in structure reduce d/d0 ratio significantly.
- **Fragment assembly** is standard in protein structure prediction (Rosetta, I-TASSER). Split query into overlapping fragments, find templates per fragment, assemble with superposition.
- **Nussinov algorithm**: Simple O(n³) DP for RNA secondary structure prediction. Base pairs provide distance constraints.

### Key Insights
1. **Per-chain prediction is critical**: Test target "9MME" has 4640nt across multiple chains. Each chain should be predicted independently.
2. **Fragment assembly**: For chains longer than ~200nt with no good full-length template, splitting into overlapping fragments of 50-150nt and finding templates per fragment should improve coverage.
3. **Coverage-weighted scoring**: Template quality should factor in coverage percentage, not just sequence similarity.
4. **Base-pair distance constraints**: Watson-Crick pairs (A-U, G-C) and wobble pairs (G-U) have specific C1'-C1' distances (~10.4Å). Using these as constraints after coordinate transfer should improve local accuracy.

## Candidate Ideas

### Idea 1: Per-Chain Independent Prediction (HIGH priority)
- Parse stoichiometry to get individual chains
- Match each chain independently against template library
- Predict coordinates per-chain, then assemble
- Expected impact: HIGH for multi-chain targets (majority of test set)

### Idea 2: Fragment-Based Assembly (HIGH priority)
- Split long chains (>200nt) into overlapping fragments of 80-150nt
- Find best template per fragment
- Transfer coordinates per fragment
- Stitch fragments using Kabsch superposition on overlapping regions
- Expected impact: HIGH for long sequences with poor full-length matches

### Idea 3: Coverage-Weighted Template Scoring (MEDIUM priority)
- Score = sequence_similarity × coverage_fraction × length_ratio
- Prefer templates that cover more of the query
- Expected impact: MEDIUM, better template selection

### Idea 4: Base-Pair Distance Constraints (MEDIUM priority)
- Predict base pairs using Nussinov DP (O(n³) but can limit to n<2000)
- Add C1'-C1' distance constraints for predicted base pairs (~10.4Å)
- Apply during refinement phase
- Expected impact: MEDIUM, improves local geometry

### Idea 5: Multi-Template Region Assembly (HIGH priority)
- For each residue position, identify the best-matching template
- Use position-specific template coordinates rather than global template
- Combine via sliding window with Kabsch superposition
- Expected impact: HIGH, most sophisticated approach

## Expected Impact
- Per-chain + fragment assembly: 0.211 → 0.25-0.30 TM-score (conservative estimate)
- With base pair constraints: additional +0.02-0.05

## Risks / Assumptions
- Fragment assembly may introduce discontinuities at fragment boundaries
- Nussinov base pair prediction is approximate
- Kaggle 9-hour time limit constrains algorithm complexity
- Must fit in single notebook with no internet/external packages

## Source Links
1. "0.409 Stanford RNA Folding 2: Protenix+Template" - https://www.kaggle.com/code/nihilisticneuralnet/0-409-stanford-rna-folding-2-protenix-template - Protenix+TBM approach scoring 0.409
2. "Stanford Template Based RNA 3D Folding Part 2" - https://www.kaggle.com/code/kami1976/stanford-template-based-rna-3d-folding-part-2 - Public template-based notebook
3. RNA-align: https://academic.oup.com/bioinformatics/article/35/21/4459/5480133 - TM-score computation for RNA
4. DRfold2: https://journals.plos.org/plosbiology/article?id=10.1371/journal.pbio.3003659 - Deep learning RNA folding
5. Competition leaderboard: https://www.kaggle.com/competitions/stanford-rna-3d-folding-2/leaderboard

## Recommended Next Action
Implement Ideas 1, 2, 3, and 5 (per-chain prediction, fragment assembly, coverage scoring, multi-template region assembly) as they provide the highest expected improvement. Idea 4 (base pair constraints) is a follow-up if time permits.
