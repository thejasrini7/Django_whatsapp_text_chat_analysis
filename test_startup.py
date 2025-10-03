#!/usr/bin/env python
"""
Test script to verify that the Django WhatsApp application can start correctly
"""

import os
import sys
import django
from django.conf import settings
from django.test.utils import get_runner

def test_django_startup():
    """Test that Django can start correctly"""
    try:
        # Configure Django settings
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings_render')
        django.setup()
        
        # Test importing key components
        from django.urls import reverse
        from chatapp.views import index, home
        from chatapp.models import ChatFile
        
        print("✅ Django startup test passed!")
        print("✅ Views imported successfully!")
        print("✅ Models imported successfully!")
        
        return True
    except Exception as e:
        print(f"❌ Django startup test failed: {e}")
        return False

def test_gemini_initialization():
    """Test that Gemini can be initialized without ClientOptions errors"""
    try:
        # Test importing and initializing Gemini without ClientOptions
        from chatapp.summary_generator import model as summary_model
        from chatapp.sentiment_analyzer import model as sentiment_model
        
        print("✅ Gemini initialization test passed!")
        print(f"✅ Summary generator model: {summary_model is not None}")
        print(f"✅ Sentiment analyzer model: {sentiment_model is not None}")
        
        return True
    except Exception as e:
        print(f"❌ Gemini initialization test failed: {e}")
        return False

def test_settings():
    """Test that settings are correctly configured"""
    try:
        # Test key settings
        from myproject.settings_render import ALLOWED_HOSTS, CSRF_TRUSTED_ORIGINS
        
        print("✅ Settings test passed!")
        print(f"✅ ALLOWED_HOSTS: {ALLOWED_HOSTS}")
        print(f"✅ CSRF_TRUSTED_ORIGINS: {CSRF_TRUSTED_ORIGINS}")
        
        # Check if our Render domain is in the allowed hosts
        render_domain = "django-whatsapp-text-chat-analysis.onrender.com"
        if render_domain in ALLOWED_HOSTS:
            print("✅ Render domain is in ALLOWED_HOSTS")
        else:
            print("⚠️  Render domain is NOT in ALLOWED_HOSTS")
            
        return True
    except Exception as e:
        print(f"❌ Settings test failed: {e}")
        return False

def main():
    """Main test function"""
    print("=== Django WhatsApp Application Startup Test ===\n")
    
    tests = [
        ("Settings Test", test_settings),
        ("Django Startup Test", test_django_startup),
        ("Gemini Initialization Test", test_gemini_initialization),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        print("-" * (len(test_name) + 1))
        result = test_func()
        results.append(result)
    
    print("\n=== Test Summary ===")
    if all(results):
        print("🎉 All tests passed! The application should start correctly.")
        return 0
    else:
        print("❌ Some tests failed. Please check the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())