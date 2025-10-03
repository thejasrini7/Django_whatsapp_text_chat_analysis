#!/usr/bin/env python3
"""
Test script to verify weekly summary endpoint
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

def test_weekly_summary_endpoint():
    """Test the weekly summary endpoint"""
    
    base_url = 'http://127.0.0.1:8000'
    
    print("Testing weekly summary endpoint")
    print("=" * 30)
    
    # Test data
    test_data = {
        "group_name": "Whatsapp Chat With Sahyadri Arra15 Gr 1 2019",
        "summary_type": "weekly_summary",
        "start_date": "2024-03-22",
        "end_date": "2024-03-28"
    }
    
    try:
        response = requests.post(
            f'{base_url}/summarize/',
            headers={'Content-Type': 'application/json'},
            json=test_data
        )
        print(f"Weekly summary endpoint status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print("✓ Weekly summary endpoint is working")
                print(f"Response data keys: {list(data.keys())}")
                if 'weekly_summaries' in data:
                    print(f"Number of weekly summaries: {len(data['weekly_summaries'])}")
                    for i, week in enumerate(data['weekly_summaries']):
                        print(f"  Week {i+1}: {week['date_range']} - {week['message_count']} messages")
                        print(f"    Summary preview: {week['summary'][:100]}...")
                else:
                    print("No weekly summaries in response")
                    print(f"Available keys: {list(data.keys())}")
            except json.JSONDecodeError:
                print("✗ Response is not valid JSON")
                print(f"Response text: {response.text[:200]}...")
        else:
            print(f"✗ Weekly summary endpoint failed with status {response.status_code}")
            print(f"Response text: {response.text[:500]}...")
    except Exception as e:
        print(f"✗ Weekly summary endpoint failed: {e}")
        import traceback
        traceback.print_exc()
    
    print("\nWeekly summary endpoint testing completed")

if __name__ == "__main__":
    test_weekly_summary_endpoint()