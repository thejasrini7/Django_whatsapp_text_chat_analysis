#!/usr/bin/env python3
"""
Test script to verify summarize endpoint
"""

import os
import sys
import django
import json

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

import requests

def test_summarize_endpoint():
    """Test the summarize endpoint"""
    
    base_url = 'http://127.0.0.1:8000'
    
    print("Testing summarize endpoint")
    print("=" * 30)
    
    # Test data
    test_data = {
        "group_name": "Whatsapp Chat With Sahyadri Arra15 Gr 1 2019",
        "summary_type": "brief",
        "start_date": "2024-03-22",
        "end_date": "2024-03-28"
    }
    
    try:
        response = requests.post(
            f'{base_url}/summarize/',
            headers={'Content-Type': 'application/json'},
            json=test_data
        )
        print(f"Summarize endpoint status: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print("✓ Summarize endpoint is working")
                print(f"Response data keys: {list(data.keys())}")
                if 'summary' in data:
                    print(f"Summary preview: {data['summary'][:100]}...")
            except json.JSONDecodeError:
                print("✗ Response is not valid JSON")
                print(f"Response text: {response.text[:200]}...")
        else:
            print(f"✗ Summarize endpoint failed with status {response.status_code}")
            print(f"Response text: {response.text[:200]}...")
    except Exception as e:
        print(f"✗ Summarize endpoint failed: {e}")
        import traceback
        traceback.print_exc()
    
    print("\nSummarize endpoint testing completed")

if __name__ == "__main__":
    test_summarize_endpoint()