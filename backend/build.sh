#!/usr/bin/env bash
# exit on error
set -o errexit

echo "Starting build process..."
echo "Current directory: $(pwd)"
echo "Python version:"
python --version

# Install Python dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create necessary directories
echo "Creating required directories..."
mkdir -p logs

# Install NLTK data
echo "Downloading NLTK data..."
python -m nltk.downloader -d ./nltk_data punkt stopwords averaged_perceptron_tagger

# Set environment variables
echo "Setting up environment..."
export PYTHONPATH="${PYTHONPATH}:${PWD}"
export NLTK_DATA="${PWD}/nltk_data"

echo "Build script completed successfully"