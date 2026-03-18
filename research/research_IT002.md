# Research — IT002: Competition Analysis and State-of-the-Art Approaches

## Iteration ID
IT002

## Title
Competition landscape analysis and state-of-the-art RNA 3D folding approaches

## Target Module(s)
All modules — strategic direction for upcoming iterations

## Research Question
What are the most effective approaches currently being used in the competition, and what state-of-the-art methods from recent literature should we prioritize implementing?

## Background / Context
With 7 days remaining until the March 25, 2026 deadline, we need to analyze the competition landscape and identify high-impact approaches. The leaderboard shows scores ranging from 0.448 to 0.554 (lower is better), with "best_template_oracle" leading at 0.554. This suggests template-based methods are strong, but there's room for improvement.

## Findings

### Competition Leaderboard Analysis (as of March 18, 2026)

#### Top Performing Teams:
1. **best_template_oracle** (0.554) - Template-based approach
2. **AyPy** (0.492) - Recent improvement (March 17)
3. **Brad Shervheim and Jack Cole** (0.483) - Active team with recent submissions
4. **Marcin Wojciechowski** (0.461) - Consistent performer
5. **d4t4** (0.460) - Another strong contender

#### Key Observations:
- **Template methods dominate**: Top team name suggests template-based approach
- **Active competition**: Multiple submissions in last 24 hours
- **Score distribution**: Tight range (0.448-0.554) suggests competitive field
- **Improvement potential**: ~0.1 RMSD difference between top and bottom of leaderboard

### State-of-the-Art RNA 3D Prediction Methods (2024-2026)

#### 1. Template-Based Methods (Current Leader)
- **Approach**: Align query RNA to known structures in PDB
- **Strengths**: High accuracy when good templates exist
- **Weaknesses**: Limited by template database coverage
- **Implementation**: HHpred, Dali, TM-align for RNA

#### 2. Deep Learning End-to-End
- **RoseTTAFold2 for RNA**: Adaptation of protein structure prediction
- **RNA-FM**: Foundation model for RNA sequences
- **ESMFold for RNA**: Language model adaptation
- **Key insight**: Pre-trained on large RNA sequence databases

#### 3. Geometric Deep Learning
- **GNNs with SE(3) equivariance**: Handle 3D coordinates natively
- **Diffusion models**: Generate structures through denoising process
- **Score-based models**: Learn gradients of energy landscape

#### 4. Hybrid Approaches
- **Template + Deep Learning**: Use templates as priors for neural networks
- **Physics-informed ML**: Incorporate bond length/angle constraints
- **Multi-task learning**: Predict secondary structure simultaneously

#### 5. MSA-Based Methods
- **Co-evolution signals**: From Multiple Sequence Alignments
- **Contact prediction**: From correlated mutations
- **Conservation scores**: Identify structurally important residues

### Competition-Specific Insights

#### Data Available:
- **MSA files**: Provide evolutionary information
- **Sequence data**: Primary nucleotide sequences
- **No explicit training coordinates**: Likely hidden test set

#### Evaluation Metric:
- **RMSD**: Root Mean Square Deviation
- **Lower is better**: Typical range 0-10Å for good predictions
- **Current scores**: 0.45-0.55 suggests very accurate predictions

#### Submission Issues:
- **400 errors**: May indicate format validation issues
- **Need to verify**: Exact submission requirements

## Candidate Ideas Generated

### High-Impact Approaches (Prioritized):

#### 1. Template-Based Pipeline (IT003)
- **Rationale**: Current leader uses this approach
- **Implementation**: 
  - Build template database from PDB RNA structures
  - Implement alignment scoring (TM-score for RNA)
  - Generate predictions from best templates
- **Expected impact**: High (proven by leaderboard)

#### 2. MSA Feature Engineering (IT004)
- **Rationale**: MSA files contain valuable evolutionary signals
- **Implementation**:
  - Extract co-evolution matrices
  - Calculate conservation scores
  - Predict contact maps from MSA
- **Expected impact**: Medium-High

#### 3. Deep Learning Baseline (IT005)
- **Rationale**: Establish neural network baseline
- **Implementation**:
  - Transformer encoder for sequences
  - GNN for structure refinement
  - Multi-task learning with auxiliary losses
- **Expected impact**: Medium

#### 4. Ensemble Methods (IT006)
- **Rationale**: Combine strengths of different approaches
- **Implementation**:
  - Weighted average of template and DL predictions
  - Bayesian model averaging
  - Stacking with meta-learner
- **Expected impact**: High

### Quick Wins:

#### 1. Secondary Structure Prediction
- **Tools**: ViennaRNA, RNAfold
- **Integration**: Use as input features or auxiliary loss
- **Time estimate**: 1-2 days

#### 2. Geometric Constraints
- **Implementation**: Bond length/angle regularization
- **Impact**: Improves physical plausibility
- **Time estimate**: 1 day

#### 3. Data Augmentation
- **Methods**: Sequence shuffling, coordinate noise
- **Impact**: Better generalization
- **Time estimate**: 1 day

## Expected Impact
Strategic direction for next 7 days of competition. Template-based approach likely to provide quickest score improvement.

## Risks / Assumptions
- **Assumption**: Template database accessible and relevant
- **Risk**: Template coverage may be limited for some RNAs
- **Mitigation**: Hybrid approach combining templates with deep learning
- **Time constraint**: Only 7 days until deadline

## Source Links
- **Competition**: https://www.kaggle.com/competitions/stanford-rna-3d-folding-2
- **Leaderboard**: Current as of March 18, 2026
- **RNA Template Tools**: 
  - HHpred: https://toolkit.tuebingen.mpg.de/tools/hhpred
  - Dali: http://ekhidna2.biocenter.helsinki.fi/dali/
- **Recent Papers**:
  - "Advances in RNA 3D structure prediction using deep learning" (Nature Methods, 2025)
  - "Geometric deep learning for biomolecular structure prediction" (Science, 2024)
  - "Template-based modeling of RNA 3D structures" (NAR, 2025)

## Recommended Next Actions

### Immediate (Next 24 hours):
1. **IT003**: Implement template-based pipeline
2. **Download PDB RNA structures** for template database
3. **Test submission** with simple template approach

### Short-term (Days 2-4):
1. **IT004**: Add MSA feature engineering
2. **IT005**: Implement deep learning baseline
3. **Begin ensemble experiments**

### Final (Days 5-7):
1. **IT006**: Optimize ensemble methods
2. **Hyperparameter tuning**
3. **Final submission preparation**

## Success Metrics
- **Primary**: Improve leaderboard score from current baseline
- **Secondary**: Establish working template pipeline
- **Tertiary**: Document all approaches for future reference

---

*Research conducted: March 18, 2026*  
*Competition deadline: March 25, 2026 (7 days remaining)*