#!/usr/bin/env python3
"""
Test script to verify the dynamic topic generation functionality
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

from chatapp.summary_generator import generate_fallback_summary, generate_brief_summary

def test_dynamic_topics():
    """Test the dynamic topic generation functionality"""
    
    # Sample messages for testing with diverse content
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
        },
        {
            'timestamp': '23/06/2025, 2:00 PM',
            'sender': 'Sf Kalpanjay Nathe',
            'message': 'मी तुमच्या मदतीसाठी उपलब्ध आहे. आपण कधी भेटू शकता?'
        },
        {
            'timestamp': '24/06/2025, 3:30 PM',
            'sender': 'User3',
            'message': 'आजच्या सभेची वेळ ४:०० वाजता आहे. कृपया सर्व उपस्थित राहावे.'
        },
        {
            'timestamp': '25/06/2025, 4:00 PM',
            'sender': 'User4',
            'message': 'मला आजची सभा उपस्थित राहता येणार नाही. कारण माझे बास्टीत पाऊस पडत आहे.'
        },
        {
            'timestamp': '26/06/2025, 5:00 PM',
            'sender': 'User5',
            'message': 'कृपया सर्वांनी आपले निर्णय आजच्या सभेपूर्वी द्यावेत. आम्ही आजच निर्णय घेणार आहोत.'
        }
    ]
    
    print("Testing Dynamic Topic Generation")
    print("=" * 50)
    
    # Test fallback summary
    print("Testing Fallback Summary:")
    print("-" * 30)
    fallback_summary = generate_fallback_summary(test_messages)
    print(fallback_summary)
    print()
    
    # Count the number of topics in the summary
    topic_count = fallback_summary.count("Topic")
    print(f"Number of topics generated: {topic_count}")
    print(f"Expected: Dynamic number based on content (should be 5-7 for this test)")
    print()
    
    # Test brief summary
    print("Testing Brief Summary:")
    print("-" * 30)
    brief_summary = generate_brief_summary(test_messages)
    print(brief_summary[:500] + "..." if len(brief_summary) > 500 else brief_summary)
    print()
    
    print("Test completed successfully!")

if __name__ == "__main__":
    test_dynamic_topics()