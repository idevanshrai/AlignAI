import multiprocessing
import os

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
port = os.environ.get('PORT', '10000')
bind = f"0.0.0.0:{port}" 