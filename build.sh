#!/bin/bash
# Build script for Render deployment

echo "Starting build process..."

# Install dependencies
<<<<<<< HEAD
pip install -r requirements.txt
=======
pip install -r requirements_render.txt
>>>>>>> 49340df8744b6570747d6bd4d9b58a8af76954d8

# Create necessary directories
mkdir -p static staticfiles media

# Collect static files
python manage_render.py collectstatic --noinput

# Run migrations
python manage_render.py migrate

echo "Build process completed!"