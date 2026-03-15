# Stanford RNA 3D Folding 2 - Kaggle Competition

## 🧬 Competition Overview

**Competition:** Stanford RNA 3D Folding 2  
**Deadline:** March 25, 2026  
**Prize Pool:** $75,000 USD  
**Category:** Featured  
**Current Teams:** ~1,990  
**Competition URL:** https://www.kaggle.com/competitions/stanford-rna-3d-folding-2

## 🎯 Problem Statement

Predict the 3D structure of RNA molecules from their nucleotide sequences. This is a fundamental challenge in computational biology with applications in drug discovery, disease understanding, and synthetic biology.

### Key Challenge
RNA molecules fold into complex 3D structures that determine their biological function. Predicting these structures from sequence alone remains a difficult problem in bioinformatics.

## 📊 Evaluation Metric

The competition uses **Root Mean Square Deviation (RMSD)** between predicted and actual atomic coordinates to evaluate submissions. Lower RMSD values indicate better predictions.

## 📁 Dataset Structure

The dataset includes:
- **MSA files**: Multiple Sequence Alignment files for evolutionary information
- **RNA sequences**: Primary nucleotide sequences
- **3D structures**: Ground truth atomic coordinates for training

### File Structure:
```
MSA/           # Multiple Sequence Alignment files (.fasta)
train/         # Training data
test/          # Test data for submission
sample_submission.csv  # Submission format
```

## 🚀 Getting Started

### 1. Prerequisites
```bash
# Install required packages
pip install kaggle numpy pandas biopython scikit-learn torch
```

### 2. Download Data
```bash
# After joining competition on Kaggle website
kaggle competitions download -c stanford-rna-3d-folding-2
unzip stanford-rna-3d-folding-2.zip
```

### 3. Basic Exploration
```python
import pandas as pd
import numpy as np

# Load sample submission to understand format
sample = pd.read_csv('sample_submission.csv')
print(sample.head())
```

## 🏗️ Project Structure

```
kaggle-stanford-rna-3d-folding/
├── README.md                 # This file
├── data/                     # Competition data (gitignored)
├── notebooks/                # Jupyter notebooks for exploration
├── src/                      # Source code
│   ├── data_loader.py       # Data loading utilities
│   ├── preprocessing.py     # Data preprocessing
│   ├── models/              # Model architectures
│   └── evaluation.py        # Evaluation metrics
├── experiments/             # Experiment tracking
└── submissions/            # Submission files
```

## 🔬 Technical Approaches

### Potential Methods:
1. **Deep Learning Models**: Graph Neural Networks (GNNs), Transformers
2. **Physics-Based Methods**: Molecular dynamics simulations
3. **Hybrid Approaches**: Combining evolutionary information with deep learning
4. **Ensemble Methods**: Combining multiple prediction methods

### Key Features:
- Evolutionary information from MSA
- Secondary structure predictions
- Energy minimization constraints
- Geometric constraints (bond lengths, angles)

## 📈 Baseline Approaches

1. **Simple Baseline**: Use existing tools like RNAfold/ViennaRNA for secondary structure
2. **Template-Based**: Find similar structures in PDB database
3. **Machine Learning**: Train on known RNA structures from PDB

## 🎮 Competition Timeline

- **Start**: January 2026
- **Deadline**: March 25, 2026
- **Final Submission**: March 25, 2026 (23:59 UTC)

## 🏆 Prizes

- **1st Place**: $30,000
- **2nd Place**: $20,000  
- **3rd Place**: $15,000
- **4th-10th Place**: $10,000 total

## 🔗 Useful Resources

### Documentation
- [Kaggle Competition Page](https://www.kaggle.com/competitions/stanford-rna-3d-folding-2)
- [RNA 3D Structure Prediction Review](https://www.nature.com/articles/s41576-019-0203-6)
- [RosettaRNA Documentation](https://www.rosettacommons.org/docs/latest/application_documentation/rna/rosetta-rna)

### Tools & Libraries
- [ViennaRNA](https://www.tbi.univie.ac.at/RNA/) - RNA secondary structure prediction
- [Rosetta](https://www.rosettacommons.org/) - Molecular modeling suite
- [Biopython](https://biopython.org/) - Biological computation in Python
- [PyTorch Geometric](https://pytorch-geometric.readthedocs.io/) - GNNs for molecular data

### Datasets
- [Protein Data Bank (PDB)](https://www.rcsb.org/) - Repository of 3D biological structures
- [RNAcentral](https://rnacentral.org/) - Non-coding RNA sequences

## 👥 Team Collaboration

This repository is set up for collaborative work on the competition. Use branches for different approaches and merge successful experiments.

### Git Workflow:
```bash
# Create feature branch
git checkout -b feature/new-model

# Work on changes
# ...

# Commit and push
git add .
git commit -m "Add new model architecture"
git push origin feature/new-model

# Create pull request when ready
```

## 📝 Submission Instructions

1. Generate predictions in the required format
2. Create submission file `submission.csv`
3. Submit via Kaggle CLI:
   ```bash
   kaggle competitions submit -c stanford-rna-3d-folding-2 -f submission.csv -m "Description"
   ```

## 🚨 Important Notes

- **Data Privacy**: Competition data should not be shared publicly
- **Compute Resources**: RNA 3D prediction can be computationally intensive
- **Validation**: Use proper cross-validation to avoid overfitting
- **Ensembling**: Consider ensemble methods for final submission

---

**Good luck with the competition!** 🧬🚀

*Last updated: March 15, 2026*