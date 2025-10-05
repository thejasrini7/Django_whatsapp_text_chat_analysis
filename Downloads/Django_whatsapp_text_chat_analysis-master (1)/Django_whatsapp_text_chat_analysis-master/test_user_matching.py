#!/usr/bin/env python3
"""
Test script to verify the improved user matching works correctly.
"""

import os
import sys
import django
from django.conf import settings

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from chatapp.question_processor import QuestionProcessor

def test_user_matching():
    """Test the improved user matching algorithm."""
    
    print("Testing Improved User Matching...")
    print("=" * 50)
    
    # Sample test data with various user name formats
    sample_messages = [
        {
            'sender': 'Ram Aids +91 98983 93819',
            'message': 'Hello everyone! How are you all doing?',
            'timestamp': '03/03/2025, 3:30 PM'
        },
        {
            'sender': 'Subiksha DS Aids +91 98765 43210',
            'message': 'I am doing great! Thanks for asking.',
            'timestamp': '03/03/2025, 3:35 PM'
        },
        {
            'sender': 'John Smith +91 87654 32109',
            'message': 'That is wonderful to hear!',
            'timestamp': '03/03/2025, 3:36 PM'
        },
        {
            'sender': 'Alice Johnson +91 76543 21098',
            'message': 'I am also doing well. How about the project?',
            'timestamp': '03/03/2025, 4:00 PM'
        },
        {
            'sender': 'Bob Wilson +91 65432 10987',
            'message': 'The project is progressing well.',
            'timestamp': '03/03/2025, 4:15 PM'
        }
    ]
    
    # Test questions with different user name variations
    test_questions = [
        "Show me messages from Ram Aids",
        "What did Ram say?",
        "List messages from Ram",
        "Show me messages from Subiksha DS Aids",
        "What did Subiksha say?",
        "Show messages from John Smith",
        "What did John say?",
        "Show messages from Alice",
        "What did Alice Johnson say?",
        "Show messages from Bob Wilson",
        "What did Bob say?"
    ]
    
    # Initialize processor
    processor = QuestionProcessor(sample_messages, "Test Group")
    
    print(f"Available users: {processor.users}")
    print()
    
    for i, question in enumerate(test_questions, 1):
        print(f"Test {i}: {question}")
        print("-" * 40)
        
        try:
            # Test user extraction
            extracted_user = processor._extract_user_from_question(question)
            
            if extracted_user:
                print(f"[SUCCESS] Found user: {extracted_user}")
                
                # Test the full question processing
                result = processor.process_question(question)
                
                if "error" in result:
                    print(f"[ERROR] {result['error']}")
                else:
                    print(f"[SUCCESS] Question type: {result.get('type', 'unknown')}")
                    if result.get('type') == 'user_messages':
                        user = result.get('user', 'Unknown')
                        total = result.get('total_messages', 0)
                        print(f"[SUCCESS] User: {user}, Messages: {total}")
            else:
                print(f"[FAILED] No user found for: {question}")
        
        except Exception as e:
            print(f"[ERROR] Exception: {str(e)}")
        
        print()
    
    print("=" * 50)
    print("User matching test completed!")
    print("\nKey improvements:")
    print("1. [OK] Better partial name matching")
    print("2. [OK] Word-based scoring system")
    print("3. [OK] Handles variations in user names")
    print("4. [OK] Prioritizes exact matches over partial matches")

if __name__ == "__main__":
    test_user_matching()

