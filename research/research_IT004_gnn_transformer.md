# Research — IT004: GNN and Transformer Models for RNA 3D Structure Prediction

## Iteration ID
IT004

## Title
GNN and Transformer architectures — deep learning models for RNA 3D coordinate prediction

## Target Module(s)
`inferencer/` (primary — new model architectures), `data_processor/` (secondary — graph construction), `scripts/run_pipeline.py` (integration)

## Research Question
Can Graph Neural Network (GNN) and Transformer architectures improve RNA 3D coordinate prediction over the current RNN/CNN baselines, and how should they be designed for template-specific and sequence-to-structure tasks?

## Background / Context

The current pipeline has two learnable baselines (RNN, CNN) in `inferencer/baseline_model.py` and a non-parametric template-based approach in `inferencer/template_model.py`. Both learned baselines use simple sequence embeddings (token + positional) and predict per-residue (x, y, z) coordinates directly. Competition leaderboard analysis (IT002) shows:
- DRfold2: 0.241 RMSD (best public)
- RibonanzaNet2: 0.632 (RibonanzaNet2 alpha)
- Template oracle: 0.554 RMSD

Key insight from IT003 research: rich feature engineering (BPPM, MSA, RNA-FM embeddings) and advanced architectures (GNN, Transformer) are the dominant strategies among top competitors.

**Why GNN?** RNA molecules have natural graph structure: nucleotides as nodes, backbone bonds and base-pairing interactions as edges. GNNs can:
1. Capture non-local base-pairing interactions that sequential models miss
2. Be SE(3)-equivariant, naturally handling 3D rotational/translational symmetry
3. Be trained on template-derived graphs where edge features encode structural priors
4. Process variable-length sequences without padding overhead

**Why Transformer?** Transformer architectures have proven dominant in structure prediction:
1. RhoFold+ (Nature Methods 2024): RNA language model + IPA module, state-of-the-art
2. trRosettaRNA (Nature Communications 2023): Transformer for distance/geometry prediction
3. RibonanzaNet: Transformer+CNN architecture used by top Kaggle competitors
4. Self-attention captures all pairwise interactions in O(L²) complexity

## Findings

### 1. GNN Approaches for RNA 3D Structure

#### 1.1 DeepFoldRNA
- **Architecture**: Message-passing GNN with evolutionary co-variation features
- **Graph**: Nucleotides as nodes; backbone, base-pair, and spatial proximity edges
- **Performance**: Average RMSD 3.21 Å, TM-score 0.82 on RNA-Puzzles
- **Key insight**: 28% improvement over non-GNN methods; strong on riboswitches/ribozymes
- **Source**: Bioinformatics and Code, 2024

#### 1.2 EquiRNA (ICLR 2025)
- **Architecture**: E(3)-equivariant geometric GNN with hierarchical geometries
- **Key innovation**: Size-insensitive K-nearest neighbor sampling for generalization
- **Graph**: Geometric graph with E(3)-symmetry-conforming message passing
- **Addresses**: Size generalization problem (train on short, predict on long)
- **Source**: ICLR 2025 proceedings

#### 1.3 GraphFold3D
- **Architecture**: GNN predicting tertiary from secondary structure
- **Graph**: Secondary structure graph (stems, loops as subgraphs)
- **Source**: Stanford CS224W project

#### 1.4 E(n)-Equivariant GNN (EGNN)
- **Architecture**: Message-passing with coordinate updates that respect E(n) symmetry
- **Key advantage**: No expensive higher-order representations (spherical harmonics)
- **Implementation**: Available in PyTorch (`egnn-pytorch` by lucidrains)
- **Applicable**: Directly to coordinate prediction task
- **Source**: Satorras et al., 2021; GitHub: vgsatorras/egnn

#### 1.5 Geometric Vector Perceptron (GVP)
- **Architecture**: Equivariant message passing with scalar + vector features
- **Performance**: Strong on ATOM3D benchmark for macromolecular tasks
- **Source**: Jing et al., ICLR 2021

### 2. Transformer Approaches for RNA 3D Structure

#### 2.1 RhoFold+ (Nature Methods 2024)
- **Architecture**: RNA-FM (language model on 23.7M sequences) → Evoformer-like trunk → IPA (Invariant Point Attention) → structure module
- **Key components**:
  - Single representation (per-residue) + pair representation (pairwise)
  - IPA module from AlphaFold2 for 3D coordinate generation
  - End-to-end differentiable
- **Performance**: State-of-the-art on RNA-Puzzles and CASP15
- **Prediction time**: ~0.14 seconds per structure

#### 2.2 trRosettaRNA (Nature Communications 2023)
- **Architecture**: MSA Transformer → distance/geometry prediction → Rosetta energy minimization
- **Two stages**: (1) Transformer predicts inter-nucleotide distances, (2) Energy minimization builds 3D model
- **Performance**: Competitive with top human predictions in CASP15, 4th in CASP16
- **Source**: Yang Lab, Shandong University

#### 2.3 RibonanzaNet (Kaggle Competition)
- **Architecture**: Transformer encoder + CNN layers for processing BPPM features
- **Key insight**: Multi-scale attention + convolutional processing of pairwise features
- **Performance**: 0.632 public score (RibonanzaNet2 alpha)
- **Source**: Kaggle Stanford RNA 3D Folding competition

#### 2.4 SE(3)-Transformer
- **Architecture**: Self-attention with SE(3)-equivariant fiber features
- **Key advantage**: Combines attention mechanism with geometric equivariance
- **Implementation**: Available in PyTorch (lucidrains/se3-transformer-pytorch)
- **Source**: Fuchs et al., NeurIPS 2020

### 3. Graph Construction for RNA

#### 3.1 Node Features (per nucleotide)
- Nucleotide identity (one-hot, 4 dim)
- Positional encoding (sinusoidal, configurable dim)
- Optional: MSA conservation, secondary structure context, RNA-FM embeddings

#### 3.2 Edge Types
- **Backbone edges**: Sequential connectivity (i, i+1) — always present
- **Base-pair edges**: From predicted secondary structure (BPPM threshold)
- **K-nearest neighbor edges**: Spatial proximity in template coordinates
- **Long-range edges**: Skip connections (i, i+k) for k in {2, 4, 8, ...}

#### 3.3 Edge Features
- Edge type encoding (one-hot or learned embedding)
- Sequence distance |i - j| (scalar or binned)
- Relative positional encoding
- Optional: base-pair probability from BPPM, template distance

### 4. Template-Specific GNN Training

A unique opportunity for this competition: train GNN on template-derived graphs:
1. For each training RNA, find top-K templates from PDB
2. Construct graph with template-informed edges (where template has contacts)
3. Use template coordinates as node features or edge distance features
4. GNN refines template coordinates toward true coordinates

This combines the proven template-based approach (0.554 oracle) with learnable refinement.

## Candidate Architectures

### Architecture A: RNA-GNN (Template-Aware Graph Neural Network)
- **Input**: Nucleotide sequence → graph with backbone + k-NN + skip-connection edges
- **Node features**: Nucleotide embedding + sinusoidal position
- **Edge features**: Edge type + sequence distance + relative position
- **Architecture**: Multi-layer message-passing GNN (EGNN-style or GVP-style)
  - 6-8 message-passing layers
  - Hidden dim 128-256
  - Coordinate update at each layer (EGNN approach)
- **Output**: Per-residue (x, y, z) coordinates
- **Training**: RMSD loss with masked padding

### Architecture B: RNA-Transformer (Sequence-to-Structure Transformer)
- **Input**: Nucleotide sequence → token + positional embeddings
- **Architecture**: Standard Transformer encoder with:
  - Multi-head self-attention (captures all pairwise interactions)
  - Feed-forward layers with GELU activation
  - Pre-layer normalization (more stable training)
  - 6-8 encoder layers, 4-8 attention heads
  - Hidden dim 128-256
  - Optional: pair representation bias in attention (AlphaFold-style)
- **Output**: Per-residue (x, y, z) coordinates via linear head
- **Training**: RMSD loss with masked padding

## Expected Impact

| Model | Expected RMSD Improvement | Rationale |
|-------|--------------------------|-----------|
| GNN | 0.05-0.15 over RNN/CNN | Graph structure captures non-local interactions; template-aware edges |
| Transformer | 0.05-0.20 over RNN/CNN | Global attention captures all pairwise relationships; proven in RNA structure prediction |
| Combined/Ensemble | 0.10-0.25 over RNN/CNN | Complementary strengths: local graph structure + global attention |

Conservative estimates based on literature comparisons and competition context.

## Risks / Assumptions

1. **Compute constraints**: No GPU on cloud VMs; training will be CPU-only. Models must be efficient enough for CPU training with dummy data. Real training would need GPU.
2. **No PyTorch Geometric**: torch-geometric is commented out in requirements.txt. GNN implementation must use pure PyTorch or we install it.
3. **Data scarcity**: Limited experimental RNA structures for training. Template augmentation helps.
4. **Overfitting risk**: Complex models on small datasets. Need strong regularization.
5. **Implementation complexity**: EGNN coordinate updates require careful numerical handling.
6. **Graph construction overhead**: Building k-NN graphs adds preprocessing time.
7. **Assumption**: Both models can be validated end-to-end with dummy data on CPU.

## Source Links

### Key Papers
- **EGNN**: Satorras et al., "E(n) Equivariant Graph Neural Networks" — https://github.com/vgsatorras/egnn
- **RhoFold+**: Chen et al., Nature Methods 2024 — https://www.nature.com/articles/s41592-024-02487-0
- **trRosettaRNA**: Yang Lab, Nature Communications 2023 — https://www.nature.com/articles/s41467-023-42528-4
- **EquiRNA**: ICLR 2025 — https://proceedings.iclr.cc/paper_files/paper/2025/file/691fe5a436d53e23c08fbbb2da529617-Paper-Conference.pdf
- **SE(3)-Transformer**: Fuchs et al., NeurIPS 2020 — https://github.com/lucidrains/se3-transformer-pytorch
- **GVP**: Jing et al., ICLR 2021 — https://github.com/drorlab/gvp-pytorch

### Kaggle Competition
- **Stanford RNA 3D Folding 2**: https://www.kaggle.com/competitions/stanford-rna-3d-folding-2
- **RibonanzaNet models**: https://www.kaggle.com/competitions/stanford-rna-3d-folding/models
- **DTU solution notebook**: https://www.kaggle.com/code/olaflundstrom/stanford-rna-3d-folding-kaggle-competition-dtu

### Implementations
- **EGNN PyTorch**: https://github.com/lucidrains/egnn-pytorch
- **SE3-Transformer PyTorch**: https://github.com/lucidrains/se3-transformer-pytorch
- **Graphein RNA**: https://graphein.ai/notebooks/rna_graph_tutorial.html

### Benchmarks
- **RNA 3D Structure-Function Benchmark**: https://arxiv.org/html/2503.21681v1

## Recommended Next Action
Proceed to Phase 2 (Plan) for IT004 implementation. Implement both GNN and Transformer architectures in `inferencer/` with full pipeline integration. Start with Transformer (simpler integration with existing sequence pipeline), then GNN (requires graph construction utilities).

---

*Research conducted: March 19, 2026*
*Competition deadline: March 25, 2026 (6 days remaining)*
*Sources: ICLR 2025, Nature Methods 2024, Nature Communications 2023, Kaggle competition, GitHub repositories*
