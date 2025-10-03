#!/usr/bin/env python
"""
Test script to verify that the Django WhatsApp application is properly configured
"""

import os
import sys
import django
from django.conf import settings
from django.test.utils import get_runner

def test_django_setup():
    """Test that Django is properly configured"""
    try:
        # Configure Django settings
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings_render')
        django.setup()
        
        # Test importing key components
        from chatapp.views import index
        from chatapp.models import ChatFile
        from myproject.settings_render import SECRET_KEY
        
        print("✅ Django setup test passed!")
        print(f"✅ SECRET_KEY loaded: {bool(SECRET_KEY)}")
        print("✅ Views and models imported successfully!")
        
        return True
    except Exception as e:
        print(f"❌ Django setup test failed: {e}")
        return False

def test_requirements():
    """Test that all required packages are installed"""
    required_packages = [
        'django',
        'google.generativeai',
        'gunicorn',
        'whitenoise',
        'requests',
        'psycopg2',
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package} is installed")
        except ImportError as e:
            print(f"❌ {package} is missing: {e}")
            missing_packages.append(package)
    
    if not missing_packages:
        print("✅ All required packages are installed!")
        return True
    else:
        print(f"❌ Missing packages: {missing_packages}")
        return False

def test_file_structure():
    """Test that required directories exist"""
    required_dirs = [
        'chatapp',
        'myproject',
        'static',
        'staticfiles',
        'media',
        'chatapp/templates',
        'chatapp/static',
    ]
    
    missing_dirs = []
    for dir_name in required_dirs:
        if os.path.exists(dir_name) and os.path.isdir(dir_name):
            print(f"✅ {dir_name} directory exists")
        else:
            print(f"❌ {dir_name} directory is missing")
            missing_dirs.append(dir_name)
    
    if not missing_dirs:
        print("✅ All required directories exist!")
        return True
    else:
        print(f"❌ Missing directories: {missing_dirs}")
        return False

def main():
    """Main test function"""
    print("=== Django WhatsApp Application Deployment Test ===\n")
    
    tests = [
        ("File Structure Test", test_file_structure),
        ("Requirements Test", test_requirements),
        ("Django Setup Test", test_django_setup),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        print("-" * (len(test_name) + 1))
        result = test_func()
        results.append(result)
    
    print("\n=== Test Summary ===")
    if all(results):
        print("🎉 All tests passed! The application is ready for deployment.")
        return 0
    else:
        print("❌ Some tests failed. Please check the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())