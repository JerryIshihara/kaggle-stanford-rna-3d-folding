# Training Techniques and Evaluation

## Loss Functions [IT001, SUB001]

- **RMSD loss** [IT001]: Per-sample Root Mean Square Deviation. `rmsd = sqrt(mean(sum((pred - target)^2, dim=-1)))`. Supports padding mask. Directly aligned with structural comparison metrics.
- **Masked MSE loss** [IT001]: Mean squared error over valid (non-padded) positions only. Simpler gradient landscape than RMSD.
- **MSE on coordinates** [SUB001]: Used for refinement model training. Predicts delta corrections, loss = mean((template + delta - ground_truth)^2). Simpler proxy that works well in practice.

## Optimizers and Schedulers [IT001, SUB001]

- **Adam** [IT001, SUB001]: Default optimizer. lr=1e-3 (IT001 baseline), lr=3e-4 (SUB001 refinement). weight_decay=1e-4 (IT001), 1e-5 (SUB001).
- **ReduceLROnPlateau** [IT001]: Reduce LR by factor 0.5 when val_loss stops improving for 5 epochs. Good for uncertain convergence timelines.
- **CosineAnnealingLR** [SUB001]: Smoothly decays LR from initial to near-zero over T_max epochs. Better for fixed-epoch budgets. Used with T_max=25.
- **Gradient clipping** [IT001, SUB001]: max_norm=1.0. Prevents gradient explosions, especially important for coordinate regression where outlier residues can cause large gradients.

## Early Stopping [IT001]

- Monitor validation loss; stop if no improvement for `patience` epochs (default 10).
- Save best checkpoint based on val_loss.
- Prevents overfitting when training data is limited.

## Ensembling and Diversity [SUB001]

- **MC-dropout**: Keep dropout active during inference (model.train() mode). Each forward pass produces a slightly different prediction. Used to generate diverse structure predictions.
- **Input noise perturbation**: Add Gaussian noise (std=0.3 A) to template coordinates before refinement. Different noise samples produce different refined structures.
- **5-prediction strategy**: Competition requires 5 structures per target. Best-of-5 TM-score is the metric.
  - Structure 1: Clean prediction (no noise, no dropout)
  - Structures 2-3: MC-dropout + noise (std=0.3)
  - Structure 4: Low noise (std=0.15), no dropout
  - Structure 5: High noise (std=0.45) + MC-dropout

## Evaluation Metrics [IT001, IT002]

- **TM-score** [IT002 research]: The actual competition metric. Range 0.0-1.0, higher is better. Measures global fold similarity, less sensitive to local errors than RMSD. Length-normalized. Key insight: leaderboard scores are 0.45-0.55 range.
- **RMSD** [IT001]: Root Mean Square Deviation of atomic positions. Lower is better. Originally thought to be the competition metric (incorrect -- it is TM-score). Still useful as a training loss proxy.
- **Sequence identity** [IT002]: Fraction of aligned positions with matching nucleotides. Used to weight templates and filter poor matches.

## Feature Normalization [SUB002]

- **Coordinate normalization**: PDB coordinates range from roughly -100 to +100 Angstroms. Feeding raw coordinates into Conv1d layers (initialized with small random weights) causes numerical overflow. **Critical: always center and scale coordinates before neural network input.**
  - Implementation: `centroid = coords.mean(axis=0); scale = std(coords - centroid) + 1e-8; normed = (coords - centroid) / scale`
  - Denormalize after prediction: `coords = normed * scale + centroid`
  - Ground truth must be normalized with the **same** centroid and scale as the template (not independently), so the model learns relative corrections.

## Normalization Layers [SUB002]

- **BatchNorm1d pitfall**: With batch_size=1 (common when each training sample has different sequence length), BatchNorm computes statistics from a single sample. The running variance can become degenerate, leading to division by near-zero and inf/NaN outputs. **Never use BatchNorm1d when effective batch size is 1.**
- **InstanceNorm1d(affine=True)**: Computes statistics per-sample per-channel across the spatial dimension (sequence length). Works correctly regardless of batch size. The `affine=True` parameter adds learnable scale/shift, making it as expressive as BatchNorm without the batch dependency.
- **GroupNorm**: Another batch-size-independent alternative. Groups channels and normalizes within each group. Good middle ground between Instance and Layer normalization.
- **Source**: SUB001 post-mortem; loss was inf for all 25 epochs due to BatchNorm1d with B=1 combined with unnormalized coordinates.

## Cross-Validation [IT001]

- **Simple K-Fold**: Random splits. Fast but may have leakage if sequences are homologous.
- **Group K-Fold**: Split by sequence family/cluster to prevent leakage from homologous sequences appearing in both train and val.
- **Length-stratified K-Fold**: Ensure each fold has similar sequence length distribution. Important because longer sequences are harder to predict.
- **Status**: Defined in IT001 (validator/splitter.py), not yet exercised with real data.
