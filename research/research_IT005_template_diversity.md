# Research: IT005 — Template Diversity and Multi-Template Prediction

## Iteration ID: IT005
## Title: Multi-Template Diversity with Local TM-Score Validation
## Target Module(s): submissions/

## Research Question
How can we improve from TM-score 0.211 to 0.35+ by better utilizing multiple templates, improving coordinate transfer, and validating locally?

## Background / Context
- SUB004 achieved 0.211 TM-score using single-template prediction with random perturbations
- Top leaderboard: 0.554 (best_template_oracle), meaning perfect template selection can get very high scores
- RibonanzaNet2 achieves 0.40 with a deep learning approach
- DRfold2 alone achieves ~0.24 on LB (similar to our score)
- Competition metric: TM-score (higher=better), best-of-5 predictions

## Findings

### 1. Template Selection is the Key Bottleneck
- Source: Leaderboard analysis, "best_template_oracle" at 0.554
- The gap between oracle (0.554) and our selection (0.211) shows template selection quality matters enormously
- Sequence similarity alone is insufficient — structures with low sequence identity can have high structural similarity

### 2. Best-of-5 Strategy
- Source: Competition rules, top notebook analysis
- Using 5 different templates maximizes the chance that at least one is structurally similar
- Random perturbations of a single template do NOT increase TM-score diversity meaningfully
- Each of 5 predictions should use a genuinely different structural hypothesis

### 3. TM-Score Computation
- Source: Zhang lab RNA-align (zhanggroup.org/RNA-align/)
- TM-score = (1/L) * sum(1 / (1 + (di/d0)^2)) where d0 = 0.6 * sqrt(L - 0.5) - 2.5
- Scale-independent, ranges [0, 1], >0.45 indicates correct fold
- Can be computed locally using validation set for feedback

### 4. Multi-Template Averaging
- Source: Template-based RNA structure prediction literature (bioRxiv 2025.12.30.696949)
- Averaging multiple template coordinate transfers can reduce noise
- Weighted average by similarity score produces smoother, more accurate structures

### 5. Fragment Assembly for Partial Matches
- For sequences where no single template covers >70% of positions, assemble from fragments
- Split query into segments, find best template for each segment independently
- Join with helical interpolation at boundaries

## Candidate Ideas
1. **Multi-template top-5 selection** — Use 5 different highest-scoring templates for 5 predictions (HIGH IMPACT)
2. **Local TM-score validation** — Compute TM-score on validation set for rapid feedback (HIGH IMPACT)
3. **Similarity-weighted template blending** — Blend top-3 templates for prediction slot 1 (MEDIUM IMPACT)
4. **Helical gap filling** — Use RNA A-form helix geometry for gap interpolation (LOW-MEDIUM IMPACT)
5. **Relaxed length filtering** — Expand from ±30% to ±50% for better template coverage (MEDIUM IMPACT)
6. **Fragment assembly** — For long sequences, assemble from multiple partial templates (MEDIUM IMPACT)

## Expected Impact
- Multi-template: +0.05-0.10 TM-score (from 0.211 to 0.26-0.31)
- Template blending: +0.02-0.05
- Better gap filling: +0.01-0.03
- Combined: target 0.30-0.35

## Risks / Assumptions
- Training data templates may not cover test structures well (temporal cutoff)
- Multi-template consensus may blur features if templates are too different
- Runtime must stay under 9 hours

## Source Links
- best_template_oracle analysis: Kaggle leaderboard (0.554 TM-score)
- RNA-align TM-score: https://zhanggroup.org/RNA-align/
- Template-based RNA prediction: https://www.biorxiv.org/content/10.64898/2025.12.30.696949v1
- RibonanzaNet2 model: https://www.kaggle.com/models/shujun717/ribonanzanet2
- DRfold2: https://github.com/leeyang/drfold2

## Recommended Next Action
Implement multi-template selection with 5 diverse templates and add local TM-score validation using the competition's validation set.
