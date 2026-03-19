# Research — IT003: Feature Engineering for RNA 3D Structure Prediction

## Iteration ID
IT003

## Title
Feature engineering — comprehensive feature set for RNA 3D coordinate prediction

## Target Module(s)
`data_processor/` (primary), `inferencer/` (secondary — model input dimensions)

## Research Question
What feature engineering techniques — beyond raw one-hot sequence encoding — can we extract from RNA sequences, MSA files, and auxiliary tools to improve 3D coordinate prediction accuracy?

## Background / Context

The current pipeline (`data_processor/loader.py`, `data_processor/dataset.py`) uses only **one-hot encoded nucleotide identity** (A/C/G/U → 4-dim vector) as input features. This is the bare minimum representation and discards vast amounts of information available from MSA files, secondary structure tools, evolutionary analysis, and positional/geometric priors.

Competition leaderboard analysis (IT002) shows the top public scores on Stanford RNA 3D Folding Part 2 are:
- DRfold2: 0.241 RMSD (best public)
- RNABaselineModel: 0.364
- RibonanzaNet2: 0.4

Insights from Part 1 winners and Kaggle discussions highlight that **template-based methods, RNA language models, and rich feature engineering** are the dominant strategies. The 1st place Part 1 solution specifically avoided MSA in favour of an RNA language model for evolutionary information, combined with energy scoring and multi-model ensembling. However, several competitive approaches rely on engineered features extracted from MSAs, secondary structure predictors, and thermodynamic tools.

This research surveys all feature categories that could improve our pipeline, prioritized by expected impact and implementation feasibility.

## Findings

### 1. Per-Residue (Node-Level) Features

#### 1.1 Nucleotide Identity (Already Implemented)
- One-hot encoding of A, C, G, U (4 dimensions)
- Current implementation in `encode_sequence()` and `NUC_TO_IDX`

#### 1.2 MSA Conservation Features
- **Per-position conservation score**: Shannon entropy at each alignment column; low entropy = highly conserved = structurally important
- **Position-specific scoring matrix (PSSM)**: Frequency profile of each nucleotide at each alignment position (4 dimensions per position)
- **Gap fraction**: Fraction of sequences with gaps at each position; high gap fraction indicates insertions/flexible regions
- **Effective number of sequences (Neff)**: Measures MSA depth/diversity; global scalar that indicates co-evolution signal strength
- **Source**: Standard bioinformatics practice; used widely in protein structure prediction (AlphaFold) and RNA methods

#### 1.3 Secondary Structure Features
- **Base pair probability per position**: Probability that position i is paired (scalar, from ViennaRNA / EternaFold / RNAfold)
- **Unpaired probability**: 1 - sum of pairing probabilities; indicates loop/flexible regions
- **Structural context label**: Classify each position as stem, hairpin loop, internal loop, bulge, multiloop, or external (6-dim one-hot or integer label)
- **Minimum free energy (MFE) structure**: Binary paired/unpaired annotation from MFE prediction
- **Source**: ViennaRNA package (RNAfold), EternaFold, LinearPartition; Kaggle Ribonanza 1st place solution used BPPM from LinearPartition-EternaFold

#### 1.4 Thermodynamic Features
- **Positional entropy**: Shannon entropy of the base-pairing probability distribution at each position
- **Accessibility (unpaired probability)**: From partition function computation
- **Local free energy contribution**: Estimated energy contribution of each nucleotide context
- **Source**: ViennaRNA partition function; used in Ribonanza competition winning solutions

#### 1.5 Positional Encoding
- **Sinusoidal positional encoding**: Standard transformer-style sin/cos encoding of position index
- **Relative position features**: Normalized position (i/L), distance from 5' end, distance from 3' end
- **Dynamic positional encoding**: Learned or relative encoding that generalizes to unseen lengths (Ribonanza 1st place used this)
- **Source**: Vaswani et al. 2017; Kaggle Ribonanza 1st place solution

#### 1.6 RNA Language Model Embeddings
- **RNA-FM embeddings**: From pre-trained RNA Foundation Model (~23.7M sequences); provides rich per-token representations
- **MultiMolecule RNA-FM**: Available on Kaggle models hub for the competition; Transformers-based
- **RhoFold+ language model features**: Used internally in RhoFold+ for end-to-end structure prediction
- **Source**: RhoFold+ (Nature Methods, 2024); MultiMolecule RNA-FM on Kaggle; Part 1 9th place discussion recommended RNA LM over MSA

#### 1.7 Backbone Torsion Angle Predictions
- **Pseudo-torsion angles (η, θ)**: Predicted from sequence using SPOT-RNA-1D or RNA-TorsionBERT
- **Sin/cos encoding of predicted angles**: Encodes angular features as (sin η, cos η, sin θ, cos θ)
- **Seven backbone torsion angles (α–ζ, χ)**: Full torsion prediction from RNA-TorsionBERT
- **Source**: RNA-TorsionBERT (bioRxiv, 2024); SPOT-RNA-1D (GitHub); BetaBend pipeline uses sin/cos dihedral encoding

### 2. Pairwise (Edge-Level) Features

#### 2.1 Base Pair Probability Matrix (BPPM)
- **Full L×L pairing probability matrix**: From partition function (ViennaRNA, EternaFold, Contrafold)
- **Multi-source BPPM**: Combine predictions from Vienna, Contrafold, and RNAformer for robustness
- **Key insight**: Ribonanza 1st place used CNN layers specifically designed to process BPPM features; DrHB/rna-stanford solution combined multi-source BPP with GAT
- **Source**: LinearPartition-EternaFold; ViennaRNA RNAfold; Kaggle Ribonanza winning solutions

#### 2.2 MSA Co-evolution / Direct Coupling Features
- **Mutual Information (MI) matrix**: Pairwise MI between alignment columns; baseline co-evolution signal
- **Direct Coupling Analysis (DCA)**: Distinguishes direct from indirect correlations
  - Mean-field DCA (mfDCA)
  - Pseudo-likelihood maximization DCA (plmDCA)
  - Both perform similarly for RNA (unlike proteins where plmDCA dominates)
- **Average Product Correction (APC)**: Corrects MI for phylogenetic and entropic biases
- **Contact prediction maps**: Binary or probabilistic contact maps derived from co-evolution
- **Source**: Weinreb et al. 2016; De Leonardis et al. 2015; RNA Journal 2020 evaluation

#### 2.3 Predicted Distance Maps
- **Inter-residue distance predictions**: From models like RNAcontact, CoCoNet
- **Distance binning**: Discretize predicted distances into bins (e.g., <8Å, 8-12Å, 12-16Å, >16Å)
- **Source**: CoCoNet (bioRxiv, 2020); RNArank (Communications Biology, 2026)

#### 2.4 Structural MSA Features (Pairwise)
- **Covariation scores per pair**: From Rfam-based structural alignments
- **Base pair type annotations**: Watson-Crick, Hoogsteen, Sugar-edge; cis/trans configuration
- **R-scape covariance scores**: Statistically significant covarying pairs
- **Source**: Szikszai et al. "On inputs to deep learning for RNA 3D structure prediction" (ICLR 2025); CaCoFold-R3D (Nature Methods, 2025)

#### 2.5 3D Motif Annotations
- **RNA 3D motif labels**: Over 50 known recurrent motifs (kink-turns, T-loops, GNRA tetraloops, etc.)
- **Motif position masks**: Binary L×L mask indicating which residue pairs participate in known motifs
- **Source**: CaCoFold-R3D (Nature Methods, 2025); RNA 3D Motif Atlas

### 3. Global (Sequence-Level) Features

#### 3.1 Sequence Statistics
- **Sequence length**: Raw length and log-length
- **GC content**: Fraction of G+C nucleotides; correlates with structural stability
- **Dinucleotide frequencies**: 16-dimensional vector of all dinucleotide counts
- **K-mer composition**: Higher-order sequence composition (3-mers = 64 dims, 4-mers = 256 dims)

#### 3.2 MSA Statistics
- **Effective number of sequences (Neff)**: Depth of evolutionary information
- **MSA depth**: Raw number of sequences in alignment
- **Average pairwise identity**: Diversity measure
- **Coverage profile**: Fraction of positions with non-gap characters

#### 3.3 Thermodynamic Global Features
- **Minimum Free Energy (MFE)**: Predicted folding stability
- **Ensemble free energy**: From partition function
- **MFE per nucleotide**: Normalized stability metric

### 4. Graph Construction Features (for GNN-based models)

#### 4.1 Node Features for GNN
- All per-residue features from Section 1
- **Nucleobase center representation**: Flexible backbone representation from NuFold (Nature Communications, 2025)

#### 4.2 Edge Features and Types for GNN
- **Edge type encoding**: Backbone (i, i+1), base-paired (from secondary structure), spatial proximity (from predicted contacts)
- **Relational edge features**: Primary structure, secondary structure, spatial edges as in Relational GNN for RNA (MDPI, 2025)
- **SE(3)-equivariant features**: For equivariant GNNs; DualEquiNet operates in both Euclidean and Spherical Harmonics spaces

### 5. Data Augmentation as Feature Engineering

#### 5.1 Sequence-Level Augmentation
- **Reverse complement**: RNA palindromic augmentation
- **Synonymous mutations**: Preserve structure while varying sequence
- **Homologous sequences from MSA**: Use MSA sequences as augmented training examples

#### 5.2 Structure-Level Augmentation
- **Random rotation/translation**: SE(3) augmentation of target coordinates
- **Coordinate noise injection**: Gaussian noise on target coordinates for robustness
- **Cropping strategies**: Structure-informed cropping from ICLR 2025 paper (Szikszai et al.)

## Candidate Ideas Generated

### Tier 1 — High Impact, Moderate Effort
| # | Feature Set | Dims Added | Dependencies | Expected Impact |
|---|-------------|-----------|--------------|-----------------|
| 1 | PSSM + conservation from MSA | 4 + 1 per residue | MSA files (available) | High — proven in AlphaFold-style methods |
| 2 | BPPM from ViennaRNA/EternaFold | L×L matrix | ViennaRNA install | High — 1st place Ribonanza feature |
| 3 | Secondary structure context | 6-8 per residue | ViennaRNA install | High — constrains folding space |
| 4 | RNA-FM embeddings | 640 per residue | MultiMolecule model | Very High — bypasses need for MSA |

### Tier 2 — Medium Impact, Lower Effort
| # | Feature Set | Dims Added | Dependencies | Expected Impact |
|---|-------------|-----------|--------------|-----------------|
| 5 | Positional encoding (sin/cos) | Configurable (32-128) | None | Medium — helps transformers |
| 6 | Sequence statistics (GC content, length, etc.) | ~5 global | None | Low-Medium |
| 7 | Gap fraction + Neff from MSA | 1 + 1 per residue | MSA files | Medium |
| 8 | DCA / MI co-evolution matrix | L×L | MSA + DCA library | Medium-High |

### Tier 3 — High Impact, High Effort
| # | Feature Set | Dims Added | Dependencies | Expected Impact |
|---|-------------|-----------|--------------|-----------------|
| 9 | Predicted torsion angles | 4-14 per residue | SPOT-RNA-1D / RNA-TorsionBERT | Medium-High |
| 10 | 3D motif annotations | Variable | CaCoFold-R3D or manual | Medium |
| 11 | Graph construction with multi-edge types | Edge features | PyTorch Geometric | High (for GNN models) |
| 12 | Structural MSA + R-scape covariation | L×L | Rfam alignment pipeline | High but complex |

### Recommended Implementation Order
1. **IT003a**: MSA-derived per-residue features (PSSM, conservation, gap fraction) — uses existing MSA loader
2. **IT003b**: Secondary structure features (BPPM, MFE structure, structural context) — requires ViennaRNA
3. **IT003c**: Positional encoding (sinusoidal) — zero dependencies
4. **IT003d**: RNA language model embeddings — requires model download
5. **IT003e**: Pairwise features (BPPM matrix, co-evolution) — for pair representation or GNN edges

## Expected Impact
Adding rich features is expected to significantly improve model accuracy. Literature and competition results show:
- BPPM features alone improved Ribonanza models substantially (1st place solution)
- MSA co-evolution features are the foundation of AlphaFold-style approaches
- RNA-FM embeddings achieved state-of-the-art without MSA (RhoFold+, Nature Methods 2024)
- Geometric context features yield ~12% RMSE reduction on RNA tasks (ICLR 2025)

Conservative estimate: **0.05–0.15 RMSD improvement** from comprehensive feature engineering vs. one-hot-only baseline, depending on model architecture.

## Risks / Assumptions
- **Tool availability**: ViennaRNA, EternaFold require installation; may have version/platform issues
- **Compute cost**: BPPM computation scales O(L³) for partition function; may be slow for long RNAs (>500 nt)
- **MSA quality**: Feature quality depends on MSA depth; shallow MSAs yield noisy co-evolution signals
- **Feature dimensionality**: Adding too many features without proper normalization/selection may hurt simple models
- **Model compatibility**: Current RNN/CNN baselines have fixed input_dim=4; must update model input handling
- **RNA-FM model size**: Language model embeddings require GPU memory; may not fit alongside structure prediction model
- **Assumption**: MSA files are available for all training/test sequences (needs verification)

## Source Links

### Kaggle Competition & Discussions
- **Stanford RNA 3D Folding Part 2**: https://www.kaggle.com/competitions/stanford-rna-3d-folding-2 — Active competition, deadline March 25, 2026
- **Part 1 Discussion — RNA LM vs MSA**: https://www.kaggle.com/c/stanford-rna-3d-folding/discussion/566906 — 9th place recommends RNA language model over MSA; energy scoring for model selection
- **Template-Based Starter for Part 2**: https://www.kaggle.com/code/kami1976/stanford-template-based-rna-3d-folding-part-2 — Template alignment approach notebook
- **Part 2 Starter Notebook**: https://www.kaggle.com/code/masanakashima/stanford-rna-3d-folding-2-starter — Basic pipeline starter
- **Ribonanza 1st Place Solution**: https://kaggle.curtischong.me/competitions/Stanford-Ribonanza-RNA-Folding — BPPM features, dynamic positional encoding, Transformer+CNN architecture
- **DrHB/rna-stanford GitHub**: https://github.com/DrHB/rna-stanford — Multi-source BPP (Vienna, Contrafold, RNAformer) + GAT architecture

### Academic Papers
- **Szikszai et al. (ICLR 2025)**: "On inputs to deep learning for RNA 3D structure prediction" — Structural MSAs, evolutionary features, base pair type annotations; https://www.biorxiv.org/content/10.1101/2025.02.14.638364v1.full
- **CaCoFold-R3D (Nature Methods, 2025)**: "All-at-once RNA folding with 3D motif prediction framed by evolutionary information" — Covariation-based 3D motif prediction; https://www.nature.com/articles/s41592-025-02833-w
- **RhoFold+ (Nature Methods, 2024)**: "Accurate RNA 3D structure prediction using a language model-based deep learning approach" — RNA-FM embeddings, IPA module, end-to-end prediction; https://www.nature.com/articles/s41592-024-02487-0
- **NuFold (Nature Communications, 2025)**: "End-to-end approach for RNA tertiary structure prediction with flexible nucleobase center representation" — Graph-based nucleobase center representation; https://www.nature.com/articles/s41467-025-56261-7
- **DualEquiNet (ICLR 2025)**: Dual-space equivariant network for RNA — Euclidean + Spherical Harmonics spaces, hierarchical aggregation; https://openreview.net/pdf/62a4341b5bb581f46f0921ce20ec78e172b9bc38.pdf
- **RNA-TorsionBERT (bioRxiv, 2024)**: Torsion angle prediction from RNA language models; https://www.biorxiv.org/content/10.1101/2024.06.06.597803v2.full-text
- **SPOT-RNA-1D**: Backbone torsion prediction with dilated CNNs; https://github.com/jaswindersingh2/SPOT-RNA-1D
- **RNArank (Communications Biology, 2026)**: Quality assessment using contact maps and distance deviation maps; https://www.nature.com/articles/s42003-026-09582-2

### DCA and Co-evolution Methods
- **DCA for RNA contacts**: https://archive.intlpress.com/site/pub/files/_fulltext/journals/cis/2019/0019/0003/CIS-2019-0019-0003-a003.pdf — Direct Coupling Analysis for RNA
- **DCA evaluation on RNA**: https://rnajournal.cshlp.org/content/26/5/637 — Assessing DCA accuracy for RNA contact prediction
- **CoCoNet**: https://www.biorxiv.org/content/10.1101/2020.07.30.229484v1.full-text — CNN-boosted RNA contact prediction

### Tools & Libraries
- **ViennaRNA**: https://www.tbi.univie.ac.at/RNA/ — Secondary structure prediction, partition function, BPPM
- **EternaFold**: https://github.com/eternagame/EternaFold — BPPM with multitask learning on crowdsourced data
- **LinearPartition**: Fast partition function for BPPM computation
- **PyTorch Geometric**: https://pytorch-geometric.readthedocs.io/ — GNN framework for graph features
- **MultiMolecule RNA-FM**: Available on Kaggle models — Pre-trained RNA Foundation Model

## Recommended Next Action
Proceed to Phase 2 (Plan) for IT003 implementation. Recommended to start with **IT003a** (MSA-derived per-residue features) since MSA files are already available and the loader exists, followed by **IT003b** (secondary structure features from ViennaRNA). These two feature sets together provide the highest expected impact with moderate implementation effort.

---

*Research conducted: March 18, 2026*
*Competition deadline: March 25, 2026 (7 days remaining)*
*Sources: Kaggle discussions, ICLR 2025, Nature Methods 2024-2025, bioRxiv 2024-2025, GitHub repositories*
