import os
import sys
import django
from django.conf import settings

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from chatapp.views import load_all_chats
from chatapp.utils import parse_timestamp

def main():
    print("Loading chat data...")
    chat_data = load_all_chats()
    
    if not chat_data:
        print("No chat data found")
        return
    
    group_name = 'Whatsapp Chat With ✨ai Souls✨'
    if group_name not in chat_data:
        print(f"Group {group_name} not found")
        return
    
    messages = chat_data[group_name]['messages']
    print(f"Total messages: {len(messages)}")
    
    # Check for specific date: 2024-02-07
    target_date = '2024-02-07'
    print(f"\nSearching for messages on {target_date}...")
    
    date_messages = []
    for msg in messages:
        timestamp = parse_timestamp(msg['timestamp'])
        if timestamp:
            msg_date = timestamp.strftime('%Y-%m-%d')
            if msg_date == target_date:
                date_messages.append(msg)
    
    print(f"Found {len(date_messages)} messages on {target_date}")
    
    if date_messages:
        print("\nMessages found:")
        for i, msg in enumerate(date_messages):
            print(f"{i+1}. {msg['timestamp']} - {msg['sender']}: {msg['message'][:100]}...")
    else:
        print("No messages found for that date.")
        
        # Let's check what February dates we do have in 2024
        feb_2024_messages = []
        for msg in messages:
            timestamp = parse_timestamp(msg['timestamp'])
            if timestamp:
                if timestamp.year == 2024 and timestamp.month == 2:
                    feb_2024_messages.append((timestamp, msg))
        
        if feb_2024_messages:
            print("\nAvailable February 2024 dates:")
            feb_dates = set()
            for timestamp, msg in feb_2024_messages:
                feb_dates.add(timestamp.strftime('%Y-%m-%d'))
            for date in sorted(feb_dates):
                print(f"  {date}")

if __name__ == "__main__":
    main()