#!/bin/bash

# Download script for Stanford RNA 3D Folding 2 competition data

set -e  # Exit on error

echo "Downloading Stanford RNA 3D Folding 2 competition data..."

# Check if kaggle is installed
if ! command -v kaggle &> /dev/null; then
    echo "Error: kaggle CLI is not installed."
    echo "Install with: pip install kaggle"
    exit 1
fi

# Check if user has joined the competition
echo "Checking competition access..."
if ! kaggle competitions list -s stanford-rna-3d-folding-2 &> /dev/null; then
    echo "Error: Cannot access competition. Make sure you:"
    echo "1. Have joined the competition at: https://www.kaggle.com/competitions/stanford-rna-3d-folding-2"
    echo "2. Have accepted the competition rules"
    echo "3. Have valid kaggle credentials"
    exit 1
fi

# Create data directory
DATA_DIR="data/raw"
mkdir -p "$DATA_DIR"

echo "Downloading competition data..."
kaggle competitions download -c stanford-rna-3d-folding-2 -p "$DATA_DIR"

echo "Extracting files..."
cd "$DATA_DIR"
unzip -o stanford-rna-3d-folding-2.zip

echo "Cleaning up..."
rm -f stanford-rna-3d-folding-2.zip

echo "Data downloaded successfully!"
echo ""
echo "Files downloaded to: $DATA_DIR"
echo ""
echo "To explore the data, run:"
echo "  jupyter notebook notebooks/exploration.ipynb"