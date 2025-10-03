#!/usr/bin/env python3
"""
Test script to verify weekly summary and brief summary generation
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

from chatapp.summary_generator import generate_weekly_summary, generate_brief_summary
from chatapp.utils import parse_timestamp

def test_weekly_and_brief_summary():
    """Test the weekly summary and brief summary generation"""
    
    # Sample messages for testing
    test_messages = [
        {
            'timestamp': '20/06/2025, 9:00 AM',
            'sender': 'Sf Kalpanjay Nathe',
            'message': '‼️अलर्ट‼️ ह्या आठोड्यात सतत् पाऊस सारखी पाने ओली ,व मधे ऊन व पुढील काई दिवसाचा अंदाज बगता *१००% करप्'
        },
        {
            'timestamp': '21/06/2025, 10:30 AM',
            'sender': 'Far Gopalrao Dashrath Rayate - Shingave',
            'message': 'बागाचे अँगल करण्यासाठी माणसे असेल तर कॉन्टॅक्ट नंबर द्या .'
        },
        {
            'timestamp': '22/06/2025, 11:15 AM',
            'sender': 'Far Gopalrao Dashrath Rayate - Shingave',
            'message': 'कृपया मदत करा. मला तंत्रज्ञान माहिती हवी आहे.'
        }
    ]
    
    print("Testing Weekly Summary and Brief Summary Generation")
    print("=" * 50)
    
    # Test with specific date range
    start_date = '2025-06-20'
    end_date = '2025-06-25'
    
    print(f"Messages: {len(test_messages)}")
    print(f"Date range: {start_date} to {end_date}")
    
    try:
        # Test weekly summary
        print("\nTesting Weekly Summary:")
        print("-" * 30)
        weekly_summaries = generate_weekly_summary(test_messages, start_date, end_date)
        print(f"Generated {len(weekly_summaries)} weekly summaries")
        
        for i, week in enumerate(weekly_summaries, 1):
            print(f"\nWeek {i}:")
            print(f"  Week start: {week['week_start']}")
            print(f"  Date range: {week['date_range']}")
            print(f"  Messages: {week['message_count']}")
            print(f"  Participants: {week['participant_count']}")
            print(f"  Most active user: {week['most_active_user']}")
            print(f"  Summary preview: {week['summary'][:100]}...")
            
    except Exception as e:
        print(f"Error generating weekly summary: {e}")
        import traceback
        traceback.print_exc()
    
    try:
        # Test brief summary
        print("\nTesting Brief Summary:")
        print("-" * 30)
        brief_summary = generate_brief_summary(test_messages)
        print(f"Generated brief summary: {brief_summary[:200]}...")
        
    except Exception as e:
        print(f"Error generating brief summary: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_weekly_and_brief_summary()