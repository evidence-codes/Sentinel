# gunicorn_config.py
bind = "0.0.0.0:8000"  # Bind to all IP addresses on port 8000
workers = 3  # Number of worker processes
loglevel = "info"
errorlog = "-"  # Log errors to stderr
accesslog = "-"  # Log access to stdout