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

## Approaches Considered but Not Yet Implemented [IT002]

- **Transformer encoder**: Self-attention over sequence positions. Could capture long-range dependencies better than GRU/CNN. Needs more data.
- **Graph Neural Networks (SE(3)-equivariant)**: Operate on 3D coordinate graphs. Handle rotation/translation invariance natively. Tools: e3nn, EGNN.
- **Diffusion models**: Generate structures via iterative denoising. State-of-the-art for protein structure generation (RFdiffusion).
- **RoseTTAFold2 for RNA**: Adaptation of the protein structure prediction system. Uses MSA + templates + pair representations.
- **RNA-FM / ESMFold for RNA**: Foundation models pre-trained on large RNA sequence databases.
