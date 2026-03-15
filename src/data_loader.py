"""
Data loading utilities for Stanford RNA 3D Folding 2 competition
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import Bio
from Bio import SeqIO
import warnings


class RNADataLoader:
    """Loader for RNA competition data"""
    
    def __init__(self, data_dir: str = "../data/raw"):
        """
        Initialize data loader
        
        Args:
            data_dir: Path to raw data directory
        """
        self.data_dir = Path(data_dir)
        
    def load_sample_submission(self) -> pd.DataFrame:
        """Load sample submission file"""
        path = self.data_dir / "sample_submission.csv"
        if not path.exists():
            raise FileNotFoundError(f"Sample submission not found at {path}")
        return pd.read_csv(path)
    
    def load_msa_file(self, msa_id: str) -> List[Dict]:
        """
        Load a specific MSA file
        
        Args:
            msa_id: MSA file ID (e.g., '157D')
            
        Returns:
            List of sequences from MSA
        """
        msa_path = self.data_dir / "MSA" / f"{msa_id}.MSA.fasta"
        if not msa_path.exists():
            raise FileNotFoundError(f"MSA file not found: {msa_path}")
        
        sequences = []
        for record in SeqIO.parse(msa_path, "fasta"):
            sequences.append({
                "id": record.id,
                "sequence": str(record.seq),
                "description": record.description
            })
        
        return sequences
    
    def list_msa_files(self) -> List[str]:
        """List all available MSA files"""
        msa_dir = self.data_dir / "MSA"
        if not msa_dir.exists():
            return []
        
        return [f.stem.replace(".MSA", "") for f in msa_dir.glob("*.fasta")]
    
    def get_msa_stats(self, msa_id: str) -> Dict:
        """
        Get statistics for an MSA file
        
        Args:
            msa_id: MSA file ID
            
        Returns:
            Dictionary with MSA statistics
        """
        sequences = self.load_msa_file(msa_id)
        
        if not sequences:
            return {}
        
        seq_lengths = [len(seq["sequence"]) for seq in sequences]
        
        return {
            "num_sequences": len(sequences),
            "min_length": min(seq_lengths),
            "max_length": max(seq_lengths),
            "mean_length": np.mean(seq_lengths),
            "median_length": np.median(seq_lengths),
            "unique_chars": len(set("".join([seq["sequence"] for seq in sequences])))
        }
    
    def load_training_data(self) -> Optional[pd.DataFrame]:
        """Load training data if available"""
        train_path = self.data_dir / "train.csv"
        if train_path.exists():
            return pd.read_csv(train_path)
        return None
    
    def load_test_data(self) -> Optional[pd.DataFrame]:
        """Load test data if available"""
        test_path = self.data_dir / "test.csv"
        if test_path.exists():
            return pd.read_csv(test_path)
        return None


def create_data_summary(data_dir: str = "../data/raw") -> pd.DataFrame:
    """
    Create summary of all MSA files
    
    Args:
        data_dir: Path to raw data directory
        
    Returns:
        DataFrame with MSA file statistics
    """
    loader = RNADataLoader(data_dir)
    msa_files = loader.list_msa_files()
    
    summary_data = []
    for msa_id in msa_files[:50]:  # Limit to first 50 for speed
        try:
            stats = loader.get_msa_stats(msa_id)
            if stats:
                stats["msa_id"] = msa_id
                summary_data.append(stats)
        except Exception as e:
            warnings.warn(f"Error processing {msa_id}: {e}")
    
    return pd.DataFrame(summary_data)


if __name__ == "__main__":
    # Example usage
    loader = RNADataLoader()
    
    print("Available MSA files:", len(loader.list_msa_files()))
    
    # Load sample submission
    sample = loader.load_sample_submission()
    print(f"Sample submission shape: {sample.shape}")
    print(f"Columns: {sample.columns.tolist()}")
    
    # Get stats for first MSA
    msa_files = loader.list_msa_files()
    if msa_files:
        stats = loader.get_msa_stats(msa_files[0])
        print(f"\nStats for {msa_files[0]}:")
        for key, value in stats.items():
            print(f"  {key}: {value}")