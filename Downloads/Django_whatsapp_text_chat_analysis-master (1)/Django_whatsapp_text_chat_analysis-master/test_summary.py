#!/usr/bin/env python3
"""
Test script to verify the enhanced summary generation functions
"""

import os
import sys
import django

# Fix console encoding for Windows
if sys.platform == "win32":
    import codecs
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
    sys.stderr = codecs.getwriter("utf-8")(sys.stderr.detach())

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from chatapp.summary_generator import generate_brief_summary, generate_weekly_summary, calculate_date_range

def test_summary_functions():
    """Test the enhanced summary functions"""
    
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
    
    print("Testing Enhanced Summary Functions")
    print("=" * 50)
    
    # Test date range calculation
    date_range = calculate_date_range(test_messages)
    print(f"Date range: {date_range} days")
    print(f"Is short period (<=7 days): {date_range <= 7}")
    print()
    
    # Test brief summary
    print("Testing Brief Summary:")
    print("-" * 30)
    brief_summary = generate_brief_summary(test_messages)
    print(brief_summary)
    print()
    
    # Test weekly summary
    print("Testing Weekly Summary:")
    print("-" * 30)
    weekly_summaries = generate_weekly_summary(test_messages, '2025-06-20', '2025-06-25')
    for i, week in enumerate(weekly_summaries, 1):
        print(f"Week {i}: {week['date_range']}")
        print(f"Messages: {week['message_count']}, Participants: {week['participant_count']}")
        print(f"Summary: {week['summary'][:200]}...")
        print()
    
    print("Test completed successfully!")

if __name__ == "__main__":
    test_summary_functions()
