#!/bin/bash

# Setup script for Stanford RNA 3D Folding 2 competition

echo "Setting up Stanford RNA 3D Folding 2 competition environment..."

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "Installing requirements..."
pip install -r requirements.txt

# Create data directory
echo "Creating data directory structure..."
mkdir -p data/{raw,processed,external}
mkdir -p data/raw/{train,test,msa}

echo ""
echo "Setup complete!"
echo ""
echo "Next steps:"
echo "1. Download competition data:"
echo "   kaggle competitions download -c stanford-rna-3d-folding-2"
echo "2. Unzip data to data/raw/"
echo "3. Start exploring with notebooks/exploration.ipynb"
echo ""
echo "Activate virtual environment: source venv/bin/activate"