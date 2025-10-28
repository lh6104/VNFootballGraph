#!/bin/bash
# Setup script for Vietnamese Football Graph

echo "=========================================="
echo "Vietnamese Football Graph - Setup"
echo "=========================================="

# Check if conda is available
if ! command -v conda &> /dev/null; then
    echo "Error: conda not found. Please install Anaconda or Miniconda."
    exit 1
fi

# Activate datamining environment
echo ""
echo "Activating conda environment: datamining"
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate datamining

if [ $? -ne 0 ]; then
    echo "Error: Failed to activate datamining environment."
    echo "Please create it first: conda create -n datamining python=3.10"
    exit 1
fi

# Install Python dependencies
echo ""
echo "Installing Python dependencies..."
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "Error: Failed to install dependencies."
    exit 1
fi

echo ""
echo "=========================================="
echo "Setup complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Start Neo4j (if using Neo4j output)"
echo "2. Configure Neo4j credentials in src/config.py or set environment variables:"
echo "   export NEO4J_URI='bolt://localhost:7687'"
echo "   export NEO4J_USER='neo4j'"
echo "   export NEO4J_PASSWORD='your_password'"
echo ""
echo "3. Run the crawler:"
echo "   python -m src.main --seed 'Nguyễn Quang Hải (sinh 1997)' --depth 2"
echo ""
echo "4. Or try the examples:"
echo "   python example.py"
echo ""
