#!/usr/bin/env bash
# exit on error
set -o errexit

echo "Current directory: $(pwd)"
echo "Directory contents:"
ls -la

# Install Python dependencies
pip install --upgrade pip
cd backend
pip install -r requirements.txt

# Create necessary directories if they don't exist
mkdir -p logs

# Create gunicorn config
echo "Creating gunicorn_config.py..."
cat > gunicorn_config.py << 'EOL'
import multiprocessing

# Worker configuration
workers = 1  # Reduce number of workers to minimize memory usage
threads = 2  # Use threads instead of processes for better memory sharing
worker_class = 'gthread'  # Use threads
worker_connections = 1000

# Timeouts
timeout = 300  # Increase timeout to 5 minutes for model loading
graceful_timeout = 300

# Memory optimization
max_requests = 1000
max_requests_jitter = 50

# Logging
accesslog = '-'
errorlog = '-'
loglevel = 'info'

# Process naming
proc_name = 'alignai_backend'

# Prevent worker timeout during model loading
preload_app = True

# Bind to PORT from environment variable
bind = "0.0.0.0:10000"
EOL

chmod +x gunicorn_config.py

echo "Directory contents after setup:"
ls -la

# Install NLTK data
python -m nltk.downloader punkt
python -m nltk.downloader stopwords
python -m nltk.downloader averaged_perceptron_tagger

echo "Build script completed successfully"