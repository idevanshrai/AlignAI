#!/usr/bin/env bash
# exit on error
set -o errexit

# Install Python dependencies
pip install --upgrade pip
pip install -r backend/requirements.txt

# Create necessary directories if they don't exist
mkdir -p backend/logs

# Set permissions
chmod +x backend/gunicorn_config.py

python -m nltk.downloader punkt
python -m nltk.downloader stopwords
python -m nltk.downloader averaged_perceptron_tagger