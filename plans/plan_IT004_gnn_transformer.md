# Plan — IT004: GNN and Transformer Models for RNA 3D Structure Prediction

## Iteration ID
IT004

## Title
GNN and Transformer architectures — implementation and pipeline integration

## Target Module(s)
`inferencer/` (primary), `data_processor/` (secondary), `scripts/run_pipeline.py`, `configs/`

## Hypothesis
Graph Neural Network and Transformer architectures will improve RNA 3D coordinate prediction over the current RNN/CNN baselines by:
1. **GNN**: Capturing non-local structural interactions through graph message passing with backbone, skip-connection, and k-NN edges
2. **Transformer**: Learning global pairwise nucleotide relationships through self-attention, proven effective in RhoFold+, trRosettaRNA, and RibonanzaNet

Both models should integrate seamlessly with the existing training pipeline (Trainer, losses, metrics, CV splitter) and demonstrate functional end-to-end training on dummy data.

## Files to Create/Modify

### New Files
| File | Purpose |
|------|---------|
| `inferencer/gnn_model.py` | GNN model: RNA graph construction + EGNN-style message-passing network |
| `inferencer/transformer_model.py` | Transformer model: multi-head self-attention encoder for sequence-to-coordinate prediction |
| `configs/train_gnn_config.yaml` | GNN-specific training configuration |
| `configs/train_transformer_config.yaml` | Transformer-specific training configuration |

### Modified Files
| File | Change |
|------|--------|
| `inferencer/baseline_model.py` | Register GNN and Transformer in MODEL_REGISTRY |
| `inferencer/predict.py` | Support new model types in `load_checkpoint` |
| `scripts/run_pipeline.py` | Import and support new model types |

## Exact Functions/Features

### GNN Model (`inferencer/gnn_model.py`)

1. **`build_rna_graph(seq_indices, mask, k_neighbors=10)`**
   - Constructs edge_index tensor from: backbone edges (i, i+1), skip-connection edges (i, i+k), k-NN edges (from initial coordinate estimates or distance heuristic)
   - Returns edge_index (2, E), edge_attr (E, edge_feat_dim)

2. **`EGNNLayer(node_dim, edge_dim, coord_dim=3)`**
   - Single EGNN message-passing layer
   - Message function: combines node features + edge features + distance
   - Coordinate update: equivariant position shift based on messages
   - Node update: aggregate messages + MLP

3. **`RNAGraphModel(num_tokens, embed_dim, hidden_dim, num_layers, ...)`**
   - Full GNN model: embedding → graph construction → EGNN layers → coordinate output
   - Forward: seq_indices, mask → (B, L, 3) coordinates
   - Compatible with existing Trainer interface

### Transformer Model (`inferencer/transformer_model.py`)

1. **`SinusoidalPositionalEncoding(d_model, max_len)`**
   - Standard sin/cos positional encoding (not learned, for length generalization)

2. **`TransformerEncoderLayer(d_model, nhead, dim_feedforward, dropout)`**
   - Pre-norm Transformer layer with multi-head self-attention + FFN
   - Causal masking disabled (bidirectional attention for structure prediction)

3. **`RNATransformerModel(num_tokens, d_model, nhead, num_layers, ...)`**
   - Full model: token embedding + sinusoidal PE → Transformer encoder → linear head → (B, L, 3)
   - Attention mask from padding mask
   - Compatible with existing Trainer interface

### Pipeline Integration

1. **MODEL_REGISTRY update**: Add `"gnn": RNAGraphModel, "transformer": RNATransformerModel`
2. **create_model update**: Factory supports all four model types
3. **Config files**: Separate YAML configs with model-specific hyperparameters

## Expected Metric Impact

On dummy data (pipeline validation):
- Both models should converge to comparable loss as RNN/CNN baselines
- Training completes in seconds on CPU with dummy data

On real data (projection):
- GNN: 0.05-0.15 RMSD improvement over RNN baseline
- Transformer: 0.05-0.20 RMSD improvement over RNN baseline

## Evaluation Plan

1. **Smoke test**: `python scripts/run_pipeline.py train --config configs/train_gnn_config.yaml`
2. **Smoke test**: `python scripts/run_pipeline.py train --config configs/train_transformer_config.yaml`
3. **Verify**: Both models train without errors, loss decreases, checkpoints are saved
4. **Compare**: Training curves and final val_loss across all four model types (RNN, CNN, GNN, Transformer)

## Rollback Plan
- New files are additive (new model files, new configs)
- Existing model registry is extended, not replaced
- If either model fails, remove its entry from MODEL_REGISTRY and delete its file
- No existing functionality is modified

## Linked Research File
[research/research_IT004_gnn_transformer.md](../research/research_IT004_gnn_transformer.md)

---

*Plan created: March 19, 2026*
