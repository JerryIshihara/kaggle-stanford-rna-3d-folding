"""
Training loop for RNA 3D structure prediction.

Supports configurable loss, gradient clipping, LR scheduling, early stopping,
and checkpoint saving with iteration-level traceability.
"""

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from pathlib import Path
from typing import Dict, Optional
from tqdm import tqdm

from optimizer.losses import get_loss_fn


class Trainer:
    """Encapsulates the training loop, validation, scheduling, and checkpointing.

    Parameters
    ----------
    model : nn.Module
    config : dict with keys such as ``learning_rate``, ``weight_decay``,
        ``num_epochs``, ``patience``, ``gradient_clip``, ``loss``,
        ``checkpoint_dir``, ``iteration_id``, etc.
    device : torch.device or None (auto-selects CUDA if available).
    """

    def __init__(
        self,
        model: nn.Module,
        config: Dict,
        device: Optional[torch.device] = None,
    ):
        self.model = model
        self.config = config
        self.device = device or torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model.to(self.device)

        self.loss_fn = get_loss_fn(config.get("loss", "rmsd"))

        self.optimizer = optim.Adam(
            model.parameters(),
            lr=config.get("learning_rate", 1e-3),
            weight_decay=config.get("weight_decay", 1e-4),
        )
        self.scheduler = optim.lr_scheduler.ReduceLROnPlateau(
            self.optimizer,
            mode="min",
            factor=config.get("scheduler_factor", 0.5),
            patience=config.get("scheduler_patience", 5),
        )

        self.num_epochs = config.get("num_epochs", 50)
        self.patience = config.get("patience", 10)
        self.gradient_clip = config.get("gradient_clip", 1.0)
        self.checkpoint_dir = Path(config.get("checkpoint_dir", "checkpoints"))
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        self.iteration_id = config.get("iteration_id", "IT000")

        self.best_val_loss = float("inf")
        self.patience_counter = 0
        self.history: Dict[str, list] = {"train_loss": [], "val_loss": []}

    def _train_epoch(self, loader: DataLoader) -> float:
        self.model.train()
        total_loss = 0.0
        total_samples = 0

        for batch in tqdm(loader, desc="  train", leave=False):
            seq = batch["seq_indices"].to(self.device)
            coords = batch["coordinates"].to(self.device)
            mask = batch["mask"].to(self.device)

            self.optimizer.zero_grad()
            preds = self.model(seq, mask=mask)
            loss = self.loss_fn(preds, coords, mask=mask)
            loss.backward()

            if self.gradient_clip > 0:
                nn.utils.clip_grad_norm_(self.model.parameters(), self.gradient_clip)

            self.optimizer.step()

            bs = seq.size(0)
            total_loss += loss.item() * bs
            total_samples += bs

        return total_loss / max(total_samples, 1)

    @torch.no_grad()
    def _validate(self, loader: DataLoader) -> float:
        self.model.eval()
        total_loss = 0.0
        total_samples = 0

        for batch in tqdm(loader, desc="  val  ", leave=False):
            seq = batch["seq_indices"].to(self.device)
            coords = batch["coordinates"].to(self.device)
            mask = batch["mask"].to(self.device)

            preds = self.model(seq, mask=mask)
            loss = self.loss_fn(preds, coords, mask=mask)

            bs = seq.size(0)
            total_loss += loss.item() * bs
            total_samples += bs

        return total_loss / max(total_samples, 1)

    def _save_checkpoint(self, tag: str, val_loss: float, epoch: int):
        path = self.checkpoint_dir / f"{self.iteration_id}_{tag}.pt"
        torch.save(
            {
                "epoch": epoch,
                "model_state_dict": self.model.state_dict(),
                "optimizer_state_dict": self.optimizer.state_dict(),
                "val_loss": val_loss,
                "config": self.config,
                "iteration_id": self.iteration_id,
                "model_kwargs": {
                    k: v
                    for k, v in self.config.items()
                    if k in ("num_tokens", "embed_dim", "hidden_dim", "num_layers", "dropout", "output_dim")
                },
            },
            path,
        )
        return path

    def fit(self, train_loader: DataLoader, val_loader: DataLoader) -> Dict:
        """Run the full training loop.

        Returns a summary dict with best_val_loss, epochs_run, and checkpoint path.
        """
        best_ckpt_path = None

        for epoch in range(1, self.num_epochs + 1):
            train_loss = self._train_epoch(train_loader)
            val_loss = self._validate(val_loader)

            self.scheduler.step(val_loss)
            self.history["train_loss"].append(train_loss)
            self.history["val_loss"].append(val_loss)

            lr = self.optimizer.param_groups[0]["lr"]
            print(
                f"Epoch {epoch:3d}/{self.num_epochs}  "
                f"train_loss={train_loss:.6f}  val_loss={val_loss:.6f}  lr={lr:.2e}"
            )

            if val_loss < self.best_val_loss:
                self.best_val_loss = val_loss
                self.patience_counter = 0
                best_ckpt_path = self._save_checkpoint("best", val_loss, epoch)
                print(f"  -> new best ({val_loss:.6f}), saved to {best_ckpt_path}")
            else:
                self.patience_counter += 1
                if self.patience_counter >= self.patience:
                    print(f"  Early stopping after {epoch} epochs.")
                    break

        self._save_checkpoint("final", val_loss, epoch)

        return {
            "best_val_loss": self.best_val_loss,
            "epochs_run": epoch,
            "best_checkpoint": str(best_ckpt_path) if best_ckpt_path else None,
            "history": self.history,
        }
