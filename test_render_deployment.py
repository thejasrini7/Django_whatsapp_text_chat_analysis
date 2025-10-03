#!/usr/bin/env python
"""
Deployment verification script for WhatsApp Analytics application.
This script checks if all necessary components for deployment are in place.
"""

import os
import sys
from pathlib import Path

def check_file_exists(file_path, description):
    """Check if a file exists and print status."""
    if os.path.exists(file_path):
        print(f"✓ {description} - Found")
        return True
    else:
        print(f"✗ {description} - Missing")
        return False

def check_directory_exists(dir_path, description):
    """Check if a directory exists and print status."""
    if os.path.exists(dir_path) and os.path.isdir(dir_path):
        print(f"✓ {description} - Found")
        return True
    else:
        print(f"✗ {description} - Missing")
        return False

def main():
    """Main verification function."""
    print("=== WhatsApp Analytics Deployment Verification ===\n")
    
    # Get the base directory (current directory)
    base_dir = Path(__file__).resolve().parent
    
    # Files to check
    files_to_check = [
        ("requirements.txt", "Python requirements file"),
        ("requirements_simple.txt", "Simple requirements file"),
        ("render.yaml", "Render deployment configuration"),
        ("build.sh", "Build script"),
        ("Procfile", "Heroku deployment file"),
        ("runtime.txt", "Heroku Python version specification"),
        ("Dockerfile", "Docker deployment file"),
        (".dockerignore", "Docker ignore file"),
        ("gunicorn.conf.py", "Gunicorn configuration"),
        ("manage_render.py", "Render management script"),
        (".env.example", "Environment variables example"),
    ]
    
    # Directories to check
    dirs_to_check = [
        ("myproject", "Django project directory"),
        ("chatapp", "Main application directory"),
        ("static", "Static files directory"),
        ("media", "Media files directory"),
        ("chatapp/templates", "Templates directory"),
    ]
    
    # Check files
    print("Checking required files:")
    all_files_found = True
    for file_name, description in files_to_check:
        file_path = base_dir / file_name
        if not check_file_exists(file_path, description):
            all_files_found = False
    
    print()
    
    # Check directories
    print("Checking required directories:")
    all_dirs_found = True
    for dir_name, description in dirs_to_check:
        dir_path = base_dir / dir_name
        if not check_directory_exists(dir_path, description):
            all_dirs_found = False
    
    print()
    
    # Check Django settings files
    print("Checking Django settings:")
    settings_files = [
        ("myproject/settings.py", "Development settings"),
        ("myproject/settings_render.py", "Render/production settings"),
        ("myproject/wsgi_render.py", "Render WSGI configuration"),
    ]
    
    all_settings_found = True
    for file_name, description in settings_files:
        file_path = base_dir / file_name
        if not check_file_exists(file_path, description):
            all_settings_found = False
    
    print()
    
    # Overall status
    if all_files_found and all_dirs_found and all_settings_found:
        print("✓ All deployment requirements satisfied!")
        print("\nNext steps:")
        print("1. Set up your environment variables (SECRET_KEY, GEMINI_API_KEY)")
        print("2. Choose your deployment platform:")
        print("   - Render: Use the render.yaml configuration")
        print("   - Heroku: Use the Procfile")
        print("   - Docker: Use the Dockerfile")
        print("3. Deploy your application!")
        return 0
    else:
        print("✗ Some deployment requirements are missing!")
        print("Please check the missing files/directories above and ensure they are created.")
        return 1

if __name__ == "__main__":
    sys.exit(main())