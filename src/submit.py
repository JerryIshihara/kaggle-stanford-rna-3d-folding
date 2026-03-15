"""
Submission script for Stanford RNA 3D Folding 2 competition
"""

import torch
import numpy as np
import pandas as pd
from pathlib import Path
import argparse
import yaml
import sys

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from src.models.baseline import create_model
from src.data_loader import RNADataLoader


def load_model(model_path, config):
    """Load trained model"""
    device = torch.device("cuda" if torch.cuda.is_available() and config.get("use_cuda", True) else "cpu")
    
    # Create model
    model = create_model(
        model_type=config.get("model_type", "rnn"),
        input_dim=config.get("input_dim", 4),
        hidden_dim=config.get("hidden_dim", 128),
        output_dim=config.get("output_dim", 3)
    ).to(device)
    
    # Load weights
    checkpoint = torch.load(model_path, map_location=device)
    model.load_state_dict(checkpoint['model_state_dict'])
    model.eval()
    
    print(f"Model loaded from {model_path}")
    print(f"Validation loss: {checkpoint.get('val_loss', 'N/A')}")
    
    return model, device


def predict(model, sequences, device, batch_size=32):
    """Generate predictions for sequences"""
    model.eval()
    all_predictions = []
    
    # Map nucleotides to indices
    nuc_to_idx = {'A': 0, 'C': 1, 'G': 2, 'U': 3, 'T': 3}
    
    with torch.no_grad():
        for i in range(0, len(sequences), batch_size):
            batch_seqs = sequences[i:i+batch_size]
            
            # Convert sequences to indices
            batch_indices = []
            max_len = max(len(seq) for seq in batch_seqs)
            
            for seq in batch_seqs:
                indices = [nuc_to_idx.get(nuc, 0) for nuc in seq]
                # Pad to max length
                indices = indices + [0] * (max_len - len(indices))
                batch_indices.append(indices)
            
            # Convert to tensor
            batch_tensor = torch.tensor(batch_indices, dtype=torch.long).to(device)
            
            # Generate predictions
            predictions = model(batch_tensor)
            
            # Convert to numpy and remove padding
            pred_np = predictions.cpu().numpy()
            for j, seq in enumerate(batch_seqs):
                seq_len = len(seq)
                all_predictions.append(pred_np[j, :seq_len, :])
    
    return all_predictions


def create_submission_file(predictions, output_path="submission.csv"):
    """Create submission file in Kaggle format"""
    # TODO: Update this based on actual submission format
    # This is a template - needs to be adjusted based on competition requirements
    
    submission_data = []
    
    for i, pred in enumerate(predictions):
        # Flatten predictions
        flat_pred = pred.flatten()
        
        # Create row for submission
        # Format depends on competition requirements
        row = {
            'id': f'pred_{i:04d}',
            'prediction': ' '.join([f'{x:.6f}' for x in flat_pred])
        }
        submission_data.append(row)
    
    # Create DataFrame
    submission_df = pd.DataFrame(submission_data)
    
    # Save to CSV
    submission_df.to_csv(output_path, index=False)
    print(f"Submission file saved to {output_path}")
    
    return submission_df


def main(config):
    """Main submission function"""
    
    # Load model
    model_path = Path(config.get("model_path", "models/best_model.pth"))
    if not model_path.exists():
        raise FileNotFoundError(f"Model not found at {model_path}")
    
    model, device = load_model(model_path, config)
    
    # Load test data
    # TODO: Replace with actual test data loading
    print("Loading test data...")
    
    # For now, create dummy test sequences
    num_test = config.get("num_test_samples", 100)
    test_sequences = []
    
    for i in range(num_test):
        # Create random RNA sequence
        seq_len = np.random.randint(50, 150)
        seq = ''.join(np.random.choice(['A', 'C', 'G', 'U'], seq_len))
        test_sequences.append(seq)
    
    print(f"Loaded {len(test_sequences)} test sequences")
    
    # Generate predictions
    print("Generating predictions...")
    predictions = predict(
        model, 
        test_sequences, 
        device,
        batch_size=config.get("batch_size", 32)
    )
    
    print(f"Generated {len(predictions)} predictions")
    
    # Create submission file
    output_dir = Path(config.get("output_dir", "submissions"))
    output_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")
    output_path = output_dir / f"submission_{timestamp}.csv"
    
    submission_df = create_submission_file(predictions, output_path)
    
    # Print submission summary
    print("\n" + "="*50)
    print("SUBMISSION SUMMARY")
    print("="*50)
    print(f"Model: {config.get('model_type', 'rnn')}")
    print(f"Test samples: {len(test_sequences)}")
    print(f"Submission file: {output_path}")
    print(f"File size: {output_path.stat().st_size / 1024:.2f} KB")
    print("\nFirst few rows of submission:")
    print(submission_df.head())
    
    # Instructions for Kaggle submission
    print("\n" + "="*50)
    print("KAGGLE SUBMISSION INSTRUCTIONS")
    print("="*50)
    print("To submit to Kaggle, run:")
    print(f"kaggle competitions submit -c stanford-rna-3d-folding-2 \\")
    print(f"  -f {output_path} \\")
    print(f"  -m 'Submission {timestamp}: {config.get('model_type', 'rnn')} model'")
    
    return output_path


def load_config(config_path):
    """Load configuration from YAML file"""
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    return config


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create submission for RNA 3D structure prediction")
    parser.add_argument("--config", type=str, default="configs/submit_config.yaml",
                       help="Path to configuration file")
    parser.add_argument("--model_path", type=str, help="Path to model checkpoint")
    parser.add_argument("--output_dir", type=str, help="Output directory for submission")
    
    args = parser.parse_args()
    
    # Load config
    config_path = Path(args.config)
    if config_path.exists():
        config = load_config(config_path)
    else:
        config = {}
    
    # Override with command line arguments
    if args.model_path:
        config["model_path"] = args.model_path
    if args.output_dir:
        config["output_dir"] = args.output_dir
    
    # Set defaults
    defaults = {
        "model_type": "rnn",
        "input_dim": 4,
        "hidden_dim": 128,
        "output_dim": 3,
        "use_cuda": True,
        "batch_size": 32,
        "num_test_samples": 100,
        "output_dir": "submissions",
        "model_path": "models/best_model.pth"
    }
    
    for key, value in defaults.items():
        if key not in config:
            config[key] = value
    
    # Run submission
    try:
        output_path = main(config)
        print(f"\nSubmission created successfully: {output_path}")
    except Exception as e:
        print(f"Error creating submission: {e}")
        sys.exit(1)