#!/usr/bin/env python3
"""
Pipeline runner for Stanford RNA 3D Folding 2.

Single entry point for the agent to train, validate, predict, and generate
submission files. Run from the project root:

    python scripts/run_pipeline.py train --config configs/train_config.yaml
    python scripts/run_pipeline.py validate --checkpoint checkpoints/IT002_best.pt
    python scripts/run_pipeline.py predict --checkpoint checkpoints/IT002_best.pt
    python scripts/run_pipeline.py submit --checkpoint checkpoints/IT002_best.pt
"""

import argparse
import sys
import json
from pathlib import Path
from datetime import datetime

import yaml
import numpy as np
import torch
from torch.utils.data import DataLoader

# Ensure project root is on the path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from data_processor.loader import RNADataLoader, encode_sequence
from data_processor.dataset import RNAStructureDataset, RNATestDataset, collate_rna
from inferencer.baseline_model import create_model
from inferencer.predict import load_checkpoint, predict_sequences
from optimizer.trainer import Trainer
from optimizer.losses import get_loss_fn
from validator.metrics import rmsd, rmsd_per_sample, aggregate_scores, evaluate_fold, evaluate_cv
from validator.splitter import get_splitter


def load_config(path: str) -> dict:
    with open(path) as f:
        return yaml.safe_load(f) or {}


# ---------------------------------------------------------------------------
# Train
# ---------------------------------------------------------------------------

def cmd_train(args):
    """Train a model and save checkpoints."""
    config = load_config(args.config) if args.config else {}

    config.setdefault("model_type", "rnn")
    config.setdefault("learning_rate", 1e-3)
    config.setdefault("num_epochs", 50)
    config.setdefault("batch_size", 32)
    config.setdefault("patience", 10)
    config.setdefault("loss", "rmsd")
    config.setdefault("gradient_clip", 1.0)
    config.setdefault("checkpoint_dir", "checkpoints")
    config.setdefault("iteration_id", args.iteration_id or "IT000")
    config.setdefault("data_dir", "data/raw")
    config.setdefault("split_strategy", "kfold")
    config.setdefault("n_splits", 5)

    if args.iteration_id:
        config["iteration_id"] = args.iteration_id

    print(f"=== Training Pipeline ===")
    print(f"  Model type  : {config['model_type']}")
    print(f"  Loss        : {config['loss']}")
    print(f"  Iteration   : {config['iteration_id']}")
    print(f"  Epochs      : {config['num_epochs']}")
    print(f"  Batch size  : {config['batch_size']}")
    print()

    loader = RNADataLoader(config["data_dir"])

    try:
        train_df = loader.load_train()
    except FileNotFoundError:
        print("WARNING: Real training data not found. Using dummy data for pipeline validation.")
        return _train_dummy(config)

    # ---- real data path (adapt columns once competition format is confirmed) ----
    sequences = train_df["sequence"].tolist()
    # Coordinate parsing depends on actual column format; placeholder below
    if "coordinates" in train_df.columns:
        from data_processor.loader import parse_coordinates
        coordinates = [parse_coordinates(c) for c in train_df["coordinates"]]
    else:
        print("WARNING: No 'coordinates' column found. Using random dummy targets.")
        coordinates = [np.random.randn(len(s), 3).astype(np.float32) for s in sequences]

    ids = train_df["id"].tolist() if "id" in train_df.columns else None

    splitter = get_splitter(config["split_strategy"])

    if config["split_strategy"] == "kfold":
        folds = splitter(len(sequences), n_splits=config["n_splits"])
    else:
        folds = splitter(len(sequences), n_splits=config["n_splits"])

    fold_results = []

    for fold_idx, (train_idx, val_idx) in enumerate(folds):
        print(f"\n--- Fold {fold_idx} ({len(train_idx)} train / {len(val_idx)} val) ---")

        train_seqs = [sequences[i] for i in train_idx]
        train_coords = [coordinates[i] for i in train_idx]
        val_seqs = [sequences[i] for i in val_idx]
        val_coords = [coordinates[i] for i in val_idx]
        train_ids = [ids[i] for i in train_idx] if ids else None
        val_ids = [ids[i] for i in val_idx] if ids else None

        train_ds = RNAStructureDataset(train_seqs, train_coords, ids=train_ids)
        val_ds = RNAStructureDataset(val_seqs, val_coords, ids=val_ids)

        train_loader = DataLoader(train_ds, batch_size=config["batch_size"], shuffle=True, collate_fn=collate_rna)
        val_loader = DataLoader(val_ds, batch_size=config["batch_size"], shuffle=False, collate_fn=collate_rna)

        fold_config = {**config, "iteration_id": f"{config['iteration_id']}_fold{fold_idx}"}
        model = create_model(config["model_type"])
        trainer = Trainer(model, fold_config)
        result = trainer.fit(train_loader, val_loader)
        fold_results.append(result)

    cv_losses = [r["best_val_loss"] for r in fold_results]
    print(f"\n=== CV Results ===")
    print(f"  Fold losses : {[f'{v:.6f}' for v in cv_losses]}")
    print(f"  CV Mean     : {np.mean(cv_losses):.6f}")
    print(f"  CV Std      : {np.std(cv_losses):.6f}")

    return {"fold_results": fold_results, "cv_mean": float(np.mean(cv_losses)), "cv_std": float(np.std(cv_losses))}


def _train_dummy(config: dict) -> dict:
    """Fallback: train on random dummy data to validate pipeline mechanics."""
    n = config.get("num_dummy_samples", 100)
    seq_len = config.get("dummy_seq_len", 50)

    sequences = ["".join(np.random.choice(list("ACGU"), seq_len)) for _ in range(n)]
    coordinates = [np.random.randn(seq_len, 3).astype(np.float32) for _ in range(n)]

    split = int(n * 0.8)
    train_ds = RNAStructureDataset(sequences[:split], coordinates[:split])
    val_ds = RNAStructureDataset(sequences[split:], coordinates[split:])

    train_loader = DataLoader(train_ds, batch_size=config["batch_size"], shuffle=True, collate_fn=collate_rna)
    val_loader = DataLoader(val_ds, batch_size=config["batch_size"], shuffle=False, collate_fn=collate_rna)

    model = create_model(config["model_type"])
    trainer = Trainer(model, config)
    result = trainer.fit(train_loader, val_loader)

    print(f"\n=== Dummy Training Complete ===")
    print(f"  Best val loss: {result['best_val_loss']:.6f}")
    print(f"  Epochs run   : {result['epochs_run']}")
    print(f"  Checkpoint   : {result['best_checkpoint']}")
    return result


# ---------------------------------------------------------------------------
# Validate
# ---------------------------------------------------------------------------

def cmd_validate(args):
    """Evaluate a checkpoint against validation data."""
    config = load_config(args.config) if args.config else {}
    config.setdefault("model_type", "rnn")
    config.setdefault("data_dir", "data/raw")
    config.setdefault("batch_size", 32)

    print(f"=== Validation ===")
    print(f"  Checkpoint: {args.checkpoint}")

    model = load_checkpoint(args.checkpoint, model_type=config["model_type"])
    device = next(model.parameters()).device
    loader = RNADataLoader(config["data_dir"])

    try:
        train_df = loader.load_train()
    except FileNotFoundError:
        print("ERROR: Training data not found. Cannot validate.")
        return

    sequences = train_df["sequence"].tolist()
    if "coordinates" in train_df.columns:
        from data_processor.loader import parse_coordinates
        coordinates = [parse_coordinates(c) for c in train_df["coordinates"]]
    else:
        print("ERROR: No coordinates column. Cannot validate.")
        return

    ids = train_df["id"].tolist() if "id" in train_df.columns else [str(i) for i in range(len(sequences))]

    predictions = predict_sequences(model, sequences, ids=ids, batch_size=config["batch_size"], device=device)
    targets = {sid: coordinates[i] for i, sid in enumerate(ids)}

    per_sample = rmsd_per_sample(predictions, targets)
    agg = aggregate_scores(per_sample)

    print(f"\n=== Validation Results ===")
    for k, v in agg.items():
        print(f"  {k}: {v}")

    return agg


# ---------------------------------------------------------------------------
# Predict
# ---------------------------------------------------------------------------

def cmd_predict(args):
    """Generate predictions on test data."""
    config = load_config(args.config) if args.config else {}
    config.setdefault("model_type", "rnn")
    config.setdefault("data_dir", "data/raw")
    config.setdefault("batch_size", 32)

    print(f"=== Prediction ===")
    print(f"  Checkpoint: {args.checkpoint}")

    model = load_checkpoint(args.checkpoint, model_type=config["model_type"])
    loader = RNADataLoader(config["data_dir"])

    try:
        test_df = loader.load_test()
    except FileNotFoundError:
        print("ERROR: Test data not found.")
        return

    sequences = test_df["sequence"].tolist()
    ids = test_df["id"].tolist() if "id" in test_df.columns else [str(i) for i in range(len(sequences))]

    predictions = predict_sequences(model, sequences, ids=ids, batch_size=config["batch_size"])

    print(f"  Generated predictions for {len(predictions)} samples.")
    return predictions


# ---------------------------------------------------------------------------
# Submit
# ---------------------------------------------------------------------------

def cmd_submit(args):
    """Generate a Kaggle submission CSV."""
    config = load_config(args.config) if args.config else {}
    config.setdefault("model_type", "rnn")
    config.setdefault("data_dir", "data/raw")
    config.setdefault("batch_size", 32)

    predictions = cmd_predict(args)
    if predictions is None:
        return

    import pandas as pd

    output_dir = Path(args.output_dir or "submissions")
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = output_dir / f"submission_{timestamp}.csv"

    rows = []
    for sid, coords in predictions.items():
        flat = " ".join(f"{v:.6f}" for v in coords.flatten())
        rows.append({"id": sid, "prediction": flat})

    df = pd.DataFrame(rows)
    df.to_csv(output_path, index=False)

    print(f"\n=== Submission Created ===")
    print(f"  File  : {output_path}")
    print(f"  Rows  : {len(df)}")
    print(f"  Size  : {output_path.stat().st_size / 1024:.1f} KB")
    print(f"\nTo submit:")
    print(f"  kaggle competitions submit -c stanford-rna-3d-folding-2 -f {output_path} -m 'description'")

    return output_path


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Stanford RNA 3D Folding 2 — Pipeline Runner")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # train
    p_train = subparsers.add_parser("train", help="Train model with CV")
    p_train.add_argument("--config", type=str, default=None)
    p_train.add_argument("--iteration-id", type=str, default=None)

    # validate
    p_val = subparsers.add_parser("validate", help="Evaluate checkpoint")
    p_val.add_argument("--checkpoint", type=str, required=True)
    p_val.add_argument("--config", type=str, default=None)

    # predict
    p_pred = subparsers.add_parser("predict", help="Generate predictions")
    p_pred.add_argument("--checkpoint", type=str, required=True)
    p_pred.add_argument("--config", type=str, default=None)

    # submit
    p_sub = subparsers.add_parser("submit", help="Generate submission CSV")
    p_sub.add_argument("--checkpoint", type=str, required=True)
    p_sub.add_argument("--config", type=str, default=None)
    p_sub.add_argument("--output-dir", type=str, default=None)

    args = parser.parse_args()

    commands = {
        "train": cmd_train,
        "validate": cmd_validate,
        "predict": cmd_predict,
        "submit": cmd_submit,
    }

    result = commands[args.command](args)

    if result and isinstance(result, dict):
        print(f"\n=== Summary (JSON) ===")
        print(json.dumps({k: v for k, v in result.items() if k != "fold_results"}, indent=2, default=str))


if __name__ == "__main__":
    main()
