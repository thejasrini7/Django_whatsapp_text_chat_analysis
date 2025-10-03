#!/bin/bash
# Build script for Render deployment

echo "Starting build process..."

# Install dependencies
pip install -r requirements.txt

# Create necessary directories
mkdir -p static staticfiles media

# Collect static files
python manage_render.py collectstatic --noinput

# Run migrations
python manage_render.py migrate

echo "Build process completed!"