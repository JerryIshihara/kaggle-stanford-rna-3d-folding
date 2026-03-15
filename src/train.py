"""
Training script for Stanford RNA 3D Folding 2 competition
"""

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, Dataset
import numpy as np
import pandas as pd
from pathlib import Path
import argparse
import yaml
from tqdm import tqdm
import wandb
import sys
import os

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from src.models.baseline import create_model
from src.data_loader import RNADataLoader


class RNADataset(Dataset):
    """Dataset for RNA structure prediction"""
    
    def __init__(self, sequences, structures, transform=None):
        """
        Initialize dataset
        
        Args:
            sequences: List of RNA sequences
            structures: List of 3D structures
            transform: Optional transformations
        """
        self.sequences = sequences
        self.structures = structures
        self.transform = transform
        
        # Map nucleotides to indices
        self.nuc_to_idx = {'A': 0, 'C': 1, 'G': 2, 'U': 3, 'T': 3}
        
    def __len__(self):
        return len(self.sequences)
    
    def __getitem__(self, idx):
        sequence = self.sequences[idx]
        structure = self.structures[idx]
        
        # Convert sequence to indices
        seq_indices = torch.tensor([self.nuc_to_idx.get(nuc, 0) for nuc in sequence], 
                                  dtype=torch.long)
        
        # Convert structure to tensor
        struct_tensor = torch.tensor(structure, dtype=torch.float32)
        
        if self.transform:
            seq_indices, struct_tensor = self.transform(seq_indices, struct_tensor)
        
        return seq_indices, struct_tensor


def train_epoch(model, dataloader, criterion, optimizer, device, epoch):
    """Train for one epoch"""
    model.train()
    total_loss = 0
    total_samples = 0
    
    pbar = tqdm(dataloader, desc=f"Epoch {epoch} [Train]")
    for batch_idx, (sequences, structures) in enumerate(pbar):
        sequences = sequences.to(device)
        structures = structures.to(device)
        
        # Forward pass
        optimizer.zero_grad()
        predictions = model(sequences)
        
        # Calculate loss
        loss = criterion(predictions, structures)
        
        # Backward pass
        loss.backward()
        optimizer.step()
        
        # Update statistics
        batch_size = sequences.size(0)
        total_loss += loss.item() * batch_size
        total_samples += batch_size
        
        # Update progress bar
        pbar.set_postfix({
            'loss': f'{loss.item():.4f}',
            'avg_loss': f'{total_loss/total_samples:.4f}'
        })
        
        # Log to wandb
        if wandb.run is not None:
            wandb.log({
                'train_loss': loss.item(),
                'train_avg_loss': total_loss/total_samples,
                'batch': batch_idx + epoch * len(dataloader)
            })
    
    return total_loss / total_samples


def validate(model, dataloader, criterion, device):
    """Validate model"""
    model.eval()
    total_loss = 0
    total_samples = 0
    
    with torch.no_grad():
        pbar = tqdm(dataloader, desc="[Val]")
        for sequences, structures in pbar:
            sequences = sequences.to(device)
            structures = structures.to(device)
            
            # Forward pass
            predictions = model(sequences)
            
            # Calculate loss
            loss = criterion(predictions, structures)
            
            # Update statistics
            batch_size = sequences.size(0)
            total_loss += loss.item() * batch_size
            total_samples += batch_size
            
            # Update progress bar
            pbar.set_postfix({
                'loss': f'{loss.item():.4f}',
                'avg_loss': f'{total_loss/total_samples:.4f}'
            })
    
    return total_loss / total_samples


def main(config):
    """Main training function"""
    
    # Set device
    device = torch.device("cuda" if torch.cuda.is_available() and config.get("use_cuda", True) else "cpu")
    print(f"Using device: {device}")
    
    # Initialize wandb
    if config.get("use_wandb", False):
        wandb.init(
            project=config.get("wandb_project", "rna-3d-folding"),
            config=config
        )
    
    # Create model
    model = create_model(
        model_type=config.get("model_type", "rnn"),
        input_dim=config.get("input_dim", 4),
        hidden_dim=config.get("hidden_dim", 128),
        output_dim=config.get("output_dim", 3)
    ).to(device)
    
    print(f"Model created with {sum(p.numel() for p in model.parameters()):,} parameters")
    
    # Create optimizer
    optimizer = optim.Adam(
        model.parameters(),
        lr=config.get("learning_rate", 1e-3),
        weight_decay=config.get("weight_decay", 1e-4)
    )
    
    # Create scheduler
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(
        optimizer,
        mode='min',
        factor=config.get("scheduler_factor", 0.5),
        patience=config.get("scheduler_patience", 5),
        verbose=True
    )
    
    # Loss function
    criterion = nn.MSELoss()
    
    # Load data
    # TODO: Replace with actual data loading
    print("Loading data...")
    
    # For now, create dummy data
    num_samples = config.get("num_samples", 100)
    seq_len = config.get("seq_len", 50)
    
    # Create dummy sequences and structures
    dummy_sequences = []
    dummy_structures = []
    
    for _ in range(num_samples):
        # Random sequence
        seq = ''.join(np.random.choice(['A', 'C', 'G', 'U'], seq_len))
        dummy_sequences.append(seq)
        
        # Random 3D coordinates
        coords = np.random.randn(seq_len, 3).astype(np.float32)
        dummy_structures.append(coords)
    
    # Split into train/val
    split_idx = int(num_samples * 0.8)
    train_sequences = dummy_sequences[:split_idx]
    train_structures = dummy_structures[:split_idx]
    val_sequences = dummy_sequences[split_idx:]
    val_structures = dummy_structures[split_idx:]
    
    # Create datasets
    train_dataset = RNADataset(train_sequences, train_structures)
    val_dataset = RNADataset(val_sequences, val_structures)
    
    # Create dataloaders
    train_loader = DataLoader(
        train_dataset,
        batch_size=config.get("batch_size", 16),
        shuffle=True,
        num_workers=config.get("num_workers", 2)
    )
    
    val_loader = DataLoader(
        val_dataset,
        batch_size=config.get("batch_size", 16),
        shuffle=False,
        num_workers=config.get("num_workers", 2)
    )
    
    print(f"Train samples: {len(train_dataset)}, Val samples: {len(val_dataset)}")
    
    # Training loop
    best_val_loss = float('inf')
    patience_counter = 0
    
    for epoch in range(config.get("num_epochs", 50)):
        print(f"\n{'='*50}")
        print(f"Epoch {epoch+1}/{config.get('num_epochs', 50)}")
        print(f"{'='*50}")
        
        # Train
        train_loss = train_epoch(model, train_loader, criterion, optimizer, device, epoch+1)
        
        # Validate
        val_loss = validate(model, val_loader, criterion, device)
        
        # Update scheduler
        scheduler.step(val_loss)
        
        # Log epoch results
        print(f"\nEpoch {epoch+1} Summary:")
        print(f"  Train Loss: {train_loss:.6f}")
        print(f"  Val Loss:   {val_loss:.6f}")
        
        if wandb.run is not None:
            wandb.log({
                'epoch': epoch,
                'train_loss_epoch': train_loss,
                'val_loss_epoch': val_loss,
                'learning_rate': optimizer.param_groups[0]['lr']
            })
        
        # Save best model
        if val_loss < best_val_loss:
            best_val_loss = val_loss
            patience_counter = 0
            
            # Save model
            model_path = Path(config.get("model_save_dir", "models")) / "best_model.pth"
            model_path.parent.mkdir(parents=True, exist_ok=True)
            
            torch.save({
                'epoch': epoch,
                'model_state_dict': model.state_dict(),
                'optimizer_state_dict': optimizer.state_dict(),
                'val_loss': val_loss,
                'config': config
            }, model_path)
            
            print(f"  Best model saved to {model_path}")
        else:
            patience_counter += 1
            print(f"  No improvement for {patience_counter} epochs")
            
            # Early stopping
            if patience_counter >= config.get("patience", 10):
                print(f"Early stopping at epoch {epoch+1}")
                break
    
    # Save final model
    final_model_path = Path(config.get("model_save_dir", "models")) / "final_model.pth"
    torch.save({
        'epoch': config.get("num_epochs", 50),
        'model_state_dict': model.state_dict(),
        'optimizer_state_dict': optimizer.state_dict(),
        'val_loss': val_loss,
        'config': config
    }, final_model_path)
    
    print(f"\nTraining complete!")
    print(f"Best validation loss: {best_val_loss:.6f}")
    print(f"Final model saved to {final_model_path}")
    
    # Finish wandb
    if wandb.run is not None:
        wandb.finish()


def load_config(config_path):
    """Load configuration from YAML file"""
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    return config


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train RNA 3D structure prediction model")
    parser.add_argument("--config", type=str, default="configs/train_config.yaml",
                       help="Path to configuration file")
    parser.add_argument("--model_type", type=str, choices=["rnn", "cnn"],
                       help="Model type (overrides config)")
    parser.add_argument("--batch_size", type=int, help="Batch size (overrides config)")
    parser.add_argument("--learning_rate", type=float, help="Learning rate (overrides config)")
    parser.add_argument("--num_epochs", type=int, help="Number of epochs (overrides config)")
    
    args = parser.parse_args()
    
    # Load config
    config_path = Path(args.config)
    if config_path.exists():
        config = load_config(config_path)
    else:
        config = {}
    
    # Override with command line arguments
    if args.model_type:
        config["model_type"] = args.model_type
    if args.batch_size:
        config["batch_size"] = args.batch_size
    if args.learning_rate:
        config["learning_rate"] = args.learning_rate
    if args.num_epochs:
        config["num_epochs"] = args.num_epochs
    
    # Set defaults
    defaults = {
        "model_type": "rnn",
        "input_dim": 4,
        "hidden_dim": 128,
        "output_dim": 3,
        "batch_size": 16,
        "learning_rate": 1e-3,
        "num_epochs": 50,
        "weight_decay": 1e-4,
        "use_cuda": True,
        "use_wandb": False,
        "wandb_project": "rna-3d-folding",
        "model_save_dir": "models",
        "patience": 10,
        "scheduler_factor": 0.5,
        "scheduler_patience": 5,
        "num_samples": 100,
        "seq_len": 50,
        "num_workers": 2
    }
    
    for key, value in defaults.items():
        if key not in config:
            config[key] = value
    
    # Run training
    main(config)