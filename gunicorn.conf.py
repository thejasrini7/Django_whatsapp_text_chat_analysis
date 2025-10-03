import multiprocessing
import os

<<<<<<< HEAD
# Memory-optimized worker configuration
workers = 1  # Use single worker to reduce memory usage
worker_class = 'sync'
worker_connections = 1000
timeout = 120
keepalive = 2

# Memory management
max_requests = 1000  # Restart worker after 1000 requests
max_requests_jitter = 50  # Add randomness to prevent all workers restarting at once
preload_app = True  # Load app before forking workers

# Logging
accesslog = '-'
errorlog = '-'
loglevel = 'info'
=======
# Ultra memory-optimized worker configuration for Render free tier
workers = 1  # Use single worker to reduce memory usage
worker_class = 'sync'
worker_connections = 25  # Further reduced to minimize memory footprint
timeout = 15  # Further reduced to prevent hanging processes
keepalive = 1

# Memory management
max_requests = 10  # Restart worker after 10 requests to prevent memory leaks
max_requests_jitter = 1  # Add randomness to prevent all workers restarting at once
preload_app = False  # Don't preload app to reduce memory usage

# Additional memory optimizations
threads = 1  # Use single thread to reduce memory usage
preload = False

# Reduce logging to save memory
accesslog = None  # Disable access logs
errorlog = '-'  # Keep error logs
loglevel = 'warning'  # Only log warnings and errors

# Limit request size to prevent memory issues
limit_request_line = 4096
limit_request_fields = 100
limit_request_field_size = 8190

# Bind to the port that Render expects
bind = '0.0.0.0:' + str(os.environ.get('PORT', 10000))
>>>>>>> 49340df8744b6570747d6bd4d9b58a8af76954d8
