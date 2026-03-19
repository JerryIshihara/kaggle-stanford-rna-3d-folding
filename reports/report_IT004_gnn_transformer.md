# Report — IT004: GNN and Transformer Models for RNA 3D Structure Prediction

## Iteration ID
IT004

## Title
GNN and Transformer architectures — implementation and pipeline integration

## Target Module(s)
`inferencer/` (primary), `data_processor/` (secondary), `scripts/run_pipeline.py`, `configs/`

## Files Changed

| File | Action | Description |
|------|--------|-------------|
| `inferencer/gnn_model.py` | Created | E(n)-equivariant GNN with EGNN layers, RNA graph construction |
| `inferencer/transformer_model.py` | Created | Pre-norm Transformer encoder with pair bias, structure module |
| `configs/train_gnn_config.yaml` | Created | GNN-specific training configuration |
| `configs/train_transformer_config.yaml` | Created | Transformer-specific training configuration |
| `inferencer/baseline_model.py` | Modified | Extended MODEL_REGISTRY with lazy imports for GNN/Transformer |
| `optimizer/trainer.py` | Modified | Expanded checkpoint model_kwargs with GNN/Transformer params |
| `scripts/run_pipeline.py` | Modified | Added model kwargs extraction, pass to create_model |
| `research/research_IT004_gnn_transformer.md` | Created | Research document |
| `plans/plan_IT004_gnn_transformer.md` | Created | Implementation plan |

## Functions/Features Changed

### New — `inferencer/gnn_model.py`
| Function/Class | Description |
|----------------|-------------|
| `build_rna_graph()` | Constructs edge_index/edge_attr from backbone, skip-connection, k-NN edges |
| `EGNNLayer` | E(n)-equivariant message-passing layer with coordinate updates |
| `RNAGraphModel` | Full GNN model: embedding → graph → EGNN layers → coordinate head |

### New — `inferencer/transformer_model.py`
| Function/Class | Description |
|----------------|-------------|
| `SinusoidalPositionalEncoding` | Fixed sin/cos PE for length generalization |
| `PreNormTransformerLayer` | Pre-LN attention + FFN with optional pair bias |
| `PairRepresentation` | AlphaFold-style pairwise representation (outer product + relative PE) |
| `StructureModule` | MLP converting per-residue features to 3D coordinates |
| `RNATransformerModel` | Full Transformer: embedding → PE → encoder → structure module |

### Modified — `inferencer/baseline_model.py`
| Function | Change |
|----------|--------|
| `_get_full_registry()` | New helper for lazy-import model registry expansion |
| `create_model()` | Updated to use `_get_full_registry()`, supports 4 model types |

### Modified — `scripts/run_pipeline.py`
| Function | Change |
|----------|--------|
| `_model_kwargs()` | New helper to extract model constructor args from config |
| `cmd_train()` | Passes model kwargs to `create_model()` |
| `_train_dummy()` | Passes model kwargs to `create_model()` |

## Experiment Setup

- **Hardware**: CPU-only (cloud VM, no GPU)
- **Data**: Dummy random data (50 samples, sequence length 30)
- **Training**: Batch size 16, early stopping with patience 15
- **Loss**: RMSD loss
- **Validation**: Train/val split (80/20)

## Validation Setting
Dummy data pipeline validation — verifies end-to-end training mechanics, not predictive quality.

## Metrics

| Model | Params | Best Val Loss | Epochs | Train Time |
|-------|--------|---------------|--------|------------|
| RNN (baseline) | 610,115 | 1.788 | 11 | ~5s |
| CNN (baseline) | 584,643 | ~1.78 | ~11 | ~3s |
| **GNN** | **870,860** | **1.633** | **20** | **~10s** |
| **Transformer** | **1,517,683** | **1.648** | **18** | **~7s** |

### Observations
1. Both new models train and converge without errors
2. Both models show lower dummy val loss than RNN/CNN baselines (expected — more parameters fitting random data)
3. GNN training is slower per epoch due to graph construction overhead
4. Transformer training is faster per epoch than GNN despite more parameters
5. Both models produce well-formed (B, L, 3) coordinate outputs
6. Checkpoints are saved correctly with full model kwargs for reconstruction
7. Existing RNN/CNN models remain fully functional (backward compatible)

### Architecture Summary

**GNN (RNAGraphModel)**:
- EGNN-style equivariant message passing
- 3 edge types: backbone (sequential), skip-connection (i, i+k), k-NN (spatial proximity)
- Coordinate initialization from learned MLP, refined through message passing
- Final coordinate = EGNN output + learned correction head
- Equivariant to rotations and translations

**Transformer (RNATransformerModel)**:
- Pre-LayerNorm for stable training
- Pair bias in attention from AlphaFold-style outer product representation
- Sinusoidal PE (not learned) for length generalization
- Structure module: LN → MLP → coordinates
- 8-head attention, 512 FFN dim

## Outcome Classification
**PROMOTED** — Both architectures are functional, integrated, and ready for training on real data. The pipeline supports all four model types (rnn, cnn, gnn, transformer) seamlessly.

## Decision
Keep both models as core pipeline components. Both are ready for:
1. Training on real competition data when available
2. Feature engineering integration (IT003 features can feed into these models)
3. Hyperparameter tuning and architecture scaling
4. Ensemble with template-based predictions

## Follow-up Recommendations

### Immediate (IT005-IT006)
1. **IT005**: Integrate MSA/BPPM features from IT003 research as additional input to GNN/Transformer
2. **IT006**: Train on real data with k-fold CV; compare all 4 models + template

### Near-term
3. Implement pairwise distance loss (FAPE-style) alongside RMSD for better gradient signal
4. Add GNN edge features from BPPM matrix (pairwise base-pair probabilities as edge weights)
5. Experiment with Transformer pair representation fed by template distance matrices
6. Scale models: deeper layers, wider hidden dims (requires GPU)

### Competition Strategy
7. Ensemble GNN + Transformer + Template predictions with confidence weighting
8. Explore GNN for template-refinement: use template coords as initial node coordinates
9. Consider finetuning RNA-FM embeddings as input features (IT003d)

---

*Report created: March 19, 2026*
*Research: [research/research_IT004_gnn_transformer.md](../research/research_IT004_gnn_transformer.md)*
*Plan: [plans/plan_IT004_gnn_transformer.md](../plans/plan_IT004_gnn_transformer.md)*
