#!/usr/bin/env python3
"""
Test script to verify date filtering with actual message dates
"""

import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from chatapp.utils import filter_messages_by_date
from chatapp.views import load_all_chats

def test_date_filtering():
    """Test date filtering with actual message dates"""
    
    print("Testing date filtering with actual message dates...")
    print("=" * 50)
    
    # Load chat data
    chat_data = load_all_chats()
    
    # Check the Unofficial Aids C group
    group_name = 'Whatsapp Chat With Unofficial Aids C'
    if group_name not in chat_data:
        print(f"Group '{group_name}' not found")
        return
    
    messages = chat_data[group_name]['messages']
    print(f"Found {len(messages)} messages")
    
    # Test filtering with a date range that should contain messages
    # Based on our debug output, messages are from 2023-09-20 to 2025-09-23
    print("\nTesting date filtering...")
    
    # Test 1: Wide date range that should include all messages
    filtered = filter_messages_by_date(messages, '2023-01-01', '2026-01-01')
    print(f"Messages in wide date range (2023-01-01 to 2026-01-01): {len(filtered)}")
    
    # Test 2: Date range that matches what the frontend was previously using
    filtered_old = filter_messages_by_date(messages, '2024-06-01', '2024-12-31')
    print(f"Messages in old default range (2024-06-01 to 2024-12-31): {len(filtered_old)}")
    
    # Test 3: Date range that should contain messages based on debug output
    filtered_new = filter_messages_by_date(messages, '2023-09-20', '2025-09-23')
    print(f"Messages in actual range (2023-09-20 to 2025-09-23): {len(filtered_new)}")
    
    if len(filtered_new) > 0:
        print("✓ Date filtering is working correctly with proper date range")
    else:
        print("✗ Date filtering is not working correctly")
        
    if len(filtered_old) == 0 and len(filtered_new) > 0:
        print("✓ This confirms the issue: old default dates don't overlap with actual message dates")

if __name__ == "__main__":
    test_date_filtering()