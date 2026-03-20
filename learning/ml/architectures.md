# Model Architectures

## Bidirectional GRU (RNNModel) [IT001]

- **What**: Bidirectional Gated Recurrent Unit encoder with a linear head predicting per-residue (x, y, z) coordinates.
- **Input**: (B, L) integer nucleotide indices (0-4 including padding).
- **Embedding**: Token embedding + positional embedding, summed. num_tokens=5, embed_dim=64, max_len=2048.
- **Encoder**: nn.GRU(embed_dim, hidden_dim, num_layers=2, bidirectional=True, dropout=0.1).
- **Head**: Linear(hidden_dim*2, hidden_dim) -> ReLU -> Dropout -> Linear(hidden_dim, 3).
- **Output**: (B, L, 3) predicted coordinates.
- **Status**: Defined in IT001, not yet trained on real data.

## 1D Dilated CNN (CNNModel) [IT001]

- **What**: Stack of 1D dilated convolutions with BatchNorm for per-residue coordinate prediction.
- **Input**: Same as RNNModel -- (B, L) nucleotide indices.
- **Architecture**: 6 Conv1d layers, dilation pattern 2^(i % 4) = [1, 2, 4, 8, 1, 2]. Kernel size 5, hidden_dim 128. BatchNorm + ReLU + Dropout after each conv.
- **Receptive field**: With 6 layers and dilations [1,2,4,8,1,2], effective receptive field is approximately 77 residues.
- **Head**: Linear(hidden_dim, 3).
- **Status**: Defined in IT001, not yet trained on real data.

## 1D ResNet Refinement (RefinementNet) [SUB001]

- **What**: 1D convolutional ResNet that predicts delta corrections to template-predicted coordinates.
- **Input**: (B, 9, L) features per residue: template_xyz (3) + onehot_ACGU (4) + relative_position (1) + template_confidence (1).
- **Architecture**:
  - Projection: Conv1d(9, 128, 1) -> BatchNorm -> ReLU
  - 6 ResidualBlocks, each with: Conv1d -> BN -> ReLU -> Dropout -> Conv1d -> BN + skip connection
  - Dilation pattern: 2^(i % 4) = [1, 2, 4, 8, 1, 2] for blocks 0-5
  - Head: Conv1d(128, 3, 1)
- **Output**: (B, 3, L) delta corrections. Final prediction = template_coords + delta.
- **Parameters**: Approximately 650K.
- **Training**: MSE loss, Adam (lr=3e-4, weight_decay=1e-5), CosineAnnealingLR, gradient clipping 1.0, 25 epochs.
- **Status**: Deployed in SUB001.

## Template-Based Model (TemplateModel) [IT002]

- **What**: Non-parametric method. Finds structurally homologous templates in PDB, transfers their coordinates to the query via alignment.
- **Pipeline**: query -> k-mer pre-filter -> Needleman-Wunsch alignment -> coordinate transfer -> identity-weighted ensemble.
- **Ensemble**: Top-5 templates, weighted by sequence identity. coords = sum(w_i * coords_i) where w_i = identity_i / sum(identities).
- **Fallback**: When no templates found (identity < 0.2), generates idealized A-form RNA helix geometry.
- **Strengths**: Very accurate when good templates exist (identity > 0.5). No training needed.
- **Weaknesses**: Cannot handle novel folds with no structural homologs in PDB.
- **Status**: Core of IT002 and SUB001 pipeline.

## E(n)-Equivariant Graph Neural Network (RNAGraphModel) [IT004]

- **What**: EGNN-style message-passing GNN that updates both node features and 3D coordinates while maintaining E(n)-equivariance (rotation, translation, reflection invariance).
- **Graph construction**: Three edge types per RNA:
  - Backbone edges: (i, i+1) bidirectional
  - Skip-connection edges: (i, i+k) for k ∈ {2, 4, 8, 16}
  - K-nearest-neighbor edges: based on sequence distance heuristic (k=10 default)
- **Node features**: Token embedding + sinusoidal positional encoding → MLP projection (64→128 dim).
- **Coordinate initialization**: Learned MLP from node features → initial (x, y, z).
- **EGNN layers**: 6 layers, each performing:
  1. Message: concat(h_src, h_dst, edge_attr, dist²) → MLP → message vector
  2. Coordinate update: Δx = rel_pos × coord_MLP(message), averaged over neighbors (equivariant)
  3. Node update: concat(h, aggregated_messages) → MLP → h_new + residual, LayerNorm
- **Output**: EGNN coordinates + learned correction head.
- **Parameters**: ~870K with default settings.
- **Key insight**: Coordinate updates use relative positions multiplied by learned scalars — this is the mechanism that ensures E(n)-equivariance without expensive spherical harmonics.
- **Source**: Satorras et al., ICML 2021; implemented in `inferencer/gnn_model.py`.
- **Status**: Implemented in IT004, validated on dummy data.

## Pre-Norm Transformer with Pair Bias (RNATransformerModel) [IT004]

- **What**: Transformer encoder for sequence-to-coordinate prediction with AlphaFold-inspired pair bias in attention.
- **Architecture**:
  - Token embedding (5 tokens, d_model=128) + sinusoidal positional encoding (fixed, not learned)
  - 6 PreNormTransformerLayers with 8 attention heads, FFN dim 512
  - Optional pair representation: outer product of single representations + relative positional embedding → bias term in attention logits
  - Structure module: LayerNorm → MLP (128→128→3) for coordinate output
- **Pre-norm design**: LayerNorm applied before attention and FFN (not after), enabling more stable gradient flow in deeper models.
- **Pair bias mechanism**: Pair representation is (B, L, L, D) computed as left_proj(x)ᵢ + right_proj(x)ⱼ + rel_pos_embed(i-j), projected to nhead bias values added to attention logits. Inspired by AlphaFold2's Evoformer pair representation.
- **Sinusoidal PE**: Not learned — enables generalization to sequence lengths not seen during training.
- **Parameters**: ~1.5M with default settings.
- **Source**: Inspired by RhoFold+ (Nature Methods 2024), trRosettaRNA (Nature Communications 2023). Implemented in `inferencer/transformer_model.py`.
- **Status**: Implemented in IT004, validated on dummy data.

## Approaches Considered but Not Yet Implemented [IT002, IT004]

- **Diffusion models**: Generate structures via iterative denoising. State-of-the-art for protein structure generation (RFdiffusion).
- **RoseTTAFold2 for RNA**: Adaptation of the protein structure prediction system. Uses MSA + templates + pair representations.
- **RNA-FM / ESMFold for RNA**: Foundation models pre-trained on large RNA sequence databases.
- **SE(3)-Transformer**: Combines self-attention with SE(3)-equivariant fiber features (Fuchs et al., NeurIPS 2020). More expressive than EGNN but more expensive.
- **Invariant Point Attention (IPA)**: AlphaFold2's structure module. Attends over 3D points in local frames. Could replace the structure module in our Transformer. [IT004]
- **GNN + Transformer hybrid**: Use GNN for local structure refinement and Transformer for global context. Potential architecture for IT005+. [IT004]
