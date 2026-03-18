"""
Inference wrapper for RNA 3D structure prediction.

Handles model loading, batched prediction, and coordinate post-processing.
"""

import torch
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional
from torch.utils.data import DataLoader

from inferencer.baseline_model import create_model
from data_processor.dataset import RNATestDataset, collate_rna


def load_checkpoint(
    checkpoint_path: str,
    model_type: str = "rnn",
    model_kwargs: Optional[Dict] = None,
    device: Optional[torch.device] = None,
) -> torch.nn.Module:
    """Load a trained model from a checkpoint file.

    Parameters
    ----------
    checkpoint_path : path to ``.pt`` file saved by the trainer.
    model_type : architecture name (``"rnn"`` or ``"cnn"``).
    model_kwargs : extra keyword arguments for the model constructor.
    device : target device; defaults to CUDA if available.

    Returns
    -------
    The model in eval mode on the target device.
    """
    if device is None:
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    checkpoint = torch.load(checkpoint_path, map_location=device)

    kwargs = model_kwargs or {}
    if "model_kwargs" in checkpoint:
        kwargs = {**checkpoint["model_kwargs"], **kwargs}

    model = create_model(model_type, **kwargs)
    model.load_state_dict(checkpoint["model_state_dict"])
    model.to(device)
    model.eval()
    return model


def predict_batch(
    model: torch.nn.Module,
    batch: Dict[str, torch.Tensor],
    device: torch.device,
) -> List[np.ndarray]:
    """Run inference on a single collated batch.

    Returns a list of numpy arrays, one per sample, each shaped ``(L_i, 3)``
    with padding stripped according to the real sequence length.
    """
    seq_indices = batch["seq_indices"].to(device)
    mask = batch["mask"].to(device)

    with torch.no_grad():
        preds = model(seq_indices, mask=mask)  # (B, max_len, 3)

    preds_np = preds.cpu().numpy()
    lengths = batch["lengths"].numpy()

    return [preds_np[i, : int(lengths[i])] for i in range(len(lengths))]


def predict_sequences(
    model: torch.nn.Module,
    sequences: List[str],
    ids: Optional[List[str]] = None,
    batch_size: int = 32,
    device: Optional[torch.device] = None,
) -> Dict[str, np.ndarray]:
    """Run inference on a list of RNA sequences.

    Returns a dict mapping sample ID to predicted coordinates ``(L, 3)``.
    """
    if device is None:
        device = next(model.parameters()).device

    dataset = RNATestDataset(sequences, ids=ids)
    loader = DataLoader(dataset, batch_size=batch_size, collate_fn=collate_rna, shuffle=False)

    results = {}
    for batch in loader:
        preds = predict_batch(model, batch, device)
        for sample_id, pred in zip(batch["ids"], preds):
            results[sample_id] = pred

    return results
