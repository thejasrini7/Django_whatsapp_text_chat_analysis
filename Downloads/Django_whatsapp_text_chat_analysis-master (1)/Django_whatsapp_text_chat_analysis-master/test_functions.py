#!/usr/bin/env python3
"""
Test script to verify that the summary functions are working correctly
"""

import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from chatapp.summary_generator import generate_weekly_summary, generate_brief_summary

def test_functions():
    """Test the summary functions directly"""
    
    # Sample messages for testing
    test_messages = [
        {
            'timestamp': '20/06/2025, 9:00 AM',
            'sender': 'Alice',
            'message': 'Hello everyone! How are you doing today?'
        },
        {
            'timestamp': '21/06/2025, 10:30 AM',
            'sender': 'Bob',
            'message': 'I am doing great! Just finished the project.'
        },
        {
            'timestamp': '22/06/2025, 11:15 AM',
            'sender': 'Charlie',
            'message': 'That is awesome! Can you share the details?'
        }
    ]
    
    print("Testing Summary Functions")
    print("=" * 30)
    
    try:
        # Test weekly summary
        print("Testing weekly summary...")
        weekly_summaries = generate_weekly_summary(test_messages, '2025-06-20', '2025-06-25')
        print(f"Generated {len(weekly_summaries)} weekly summaries")
        
        if len(weekly_summaries) > 0:
            print("✓ Weekly summary function is working")
            for i, week in enumerate(weekly_summaries):
                print(f"  Week {i+1}: {week['message_count']} messages, {week['participant_count']} participants")
        else:
            print("✗ Weekly summary function returned no results")
            
    except Exception as e:
        print(f"Error testing weekly summary: {e}")
        import traceback
        traceback.print_exc()
    
    try:
        # Test brief summary
        print("\nTesting brief summary...")
        brief_summary = generate_brief_summary(test_messages)
        print(f"Generated brief summary: {brief_summary[:100]}...")
        
        if brief_summary:
            print("✓ Brief summary function is working")
        else:
            print("✗ Brief summary function returned no results")
            
    except Exception as e:
        print(f"Error testing brief summary: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_functions()