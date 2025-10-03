import re
from datetime import datetime, timedelta
import google.generativeai as genai
from dotenv import load_dotenv
import os
import time
import logging
from django.conf import settings
from .utils import filter_messages_by_date, parse_timestamp

load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)

# Global model variable
model = None

def initialize_gemini_model():
    """Initialize the Gemini model with proper error handling"""
    global model
    
    # Get API key
    api_key = os.getenv("GEMINI_API_KEY") or getattr(settings, "GEMINI_API_KEY", None)
    if not api_key:
        logger.warning("GEMINI_API_KEY not found in environment or settings")
        return False
    
    try:
        # Configure Gemini AI (using direct module access to avoid linter errors)
        genai.configure(api_key=api_key, client_options={"client_class": genai.ClientOptions})  # type: ignore
        
        # Initialize the model with fallback
        try:
            model = genai.GenerativeModel('gemini-2.5-flash')  # type: ignore
        except Exception as e:
            logger.warning(f"Could not initialize gemini-2.5-flash, falling back to gemini-2.0-flash: {e}")
            try:
                model = genai.GenerativeModel('gemini-2.0-flash')  # type: ignore
            except Exception as e2:
                logger.warning(f"Could not initialize gemini-2.0-flash, falling back to gemini-flash-latest: {e2}")
                try:
                    model = genai.GenerativeModel('gemini-flash-latest')  # type: ignore
                except Exception as e3:
                    logger.warning(f"Could not initialize gemini-flash-latest, falling back to gemini-pro-latest: {e3}")
                    model = genai.GenerativeModel('gemini-pro-latest')  # type: ignore
        
        return True
    except Exception as e:
        logger.error(f"Failed to initialize Gemini model: {e}")
        return False

# Initialize the model when module is loaded
initialize_gemini_model()

def generate_fallback_summary(messages):
    """Generate structured summary with actual message content when AI is unavailable"""
    if not messages:
        return "**ACTIVITY OVERVIEW**: No messages during this week\n**MAIN DISCUSSION TOPICS**: No conversations recorded"
    
    # Basic statistics
    total_messages = len(messages)
    users = set(msg['sender'] for msg in messages)
    user_count = len(users)
    
    # Most active user
    user_msg_count = {}
    for msg in messages:
        user = msg['sender']
        user_msg_count[user] = user_msg_count.get(user, 0) + 1
    
    most_active_user = max(user_msg_count.items(), key=lambda x: x[1]) if user_msg_count else None
    
    # Extract actual message content (not system messages)
    actual_messages = []
    file_names = []
    conversation_snippets = []
    
    for msg in messages:
        message_text = msg['message']
        message_lower = message_text.lower()
        
        # Skip system messages
        if any(term in message_lower for term in ['media omitted', 'security code changed', 'tap to learn more', 'this message was deleted', 'messages and calls are end-to-end encrypted']):
            continue
            
        # Look for file names and documents
        if any(ext in message_lower for ext in ['.pdf', '.doc', '.jpg', '.png', '.mp4', '.xlsx']):
            file_names.append(message_text.strip())
        
        # Collect meaningful conversation content
        if len(message_text.strip()) >= 10:  # Meaningful messages
            conversation_snippets.append(f"{msg['sender']}: {message_text.strip()[:100]}..." if len(message_text) > 100 else f"{msg['sender']}: {message_text.strip()}")
            actual_messages.append(message_text)
    
    # Build structured summary with actual content
    summary_parts = []
    
    # Activity Overview
    summary_parts.append(f"**ACTIVITY OVERVIEW**: {total_messages} messages from {user_count} participants during this week")
    
    # Key Participants
    if most_active_user:
        percentage = round((most_active_user[1] / total_messages) * 100)
        summary_parts.append(f"**KEY PARTICIPANTS**: {most_active_user[0]} was most active with {most_active_user[1]} messages ({percentage}% of activity)")
    
    # Main Discussion Topics with actual content
    if file_names or conversation_snippets:
        summary_parts.append("**MAIN DISCUSSION TOPICS**:")
        
        topic_count = 1
        # Add file/document sharing topics
        for file_name in file_names[:3]:  # Show up to 3 files
            summary_parts.append(f"- Topic {topic_count}: Document shared - \"{file_name}\"")
            topic_count += 1
        
        # Add conversation content from ALL participants, not just most active
        participant_messages = {}
        for snippet in conversation_snippets[:15]:  # Get more messages
            participant = snippet.split(':')[0]
            if participant not in participant_messages:
                participant_messages[participant] = []
            participant_messages[participant].append(snippet)
        
        # Distribute topics across different participants dynamically based on content
        max_topics = min(len(participant_messages), 10)  # Dynamically adjust based on participants, up to 10
        topic_index = 1
        for participant, messages in list(participant_messages.items()):
            if topic_index <= max_topics:
                sample_msg = messages[0] if messages else f"{participant}: [No detailed message]"
                summary_parts.append(f"- Topic {topic_index}: {sample_msg}")
                topic_index += 1
    else:
        # If no meaningful content found, show the actual raw messages to debug
        if len(messages) > 0:
            sample_messages = []
            for i, msg in enumerate(messages[:5]):  # Show first 5 messages for debugging
                sample_messages.append(f"{msg['sender']}: {msg['message'][:100]}")
            
            summary_parts.append("**MAIN DISCUSSION TOPICS**:")
            for i, sample in enumerate(sample_messages, 1):
                summary_parts.append(f"- Topic {i}: {sample}")
        else:
            summary_parts.append("**MAIN DISCUSSION TOPICS**: No messages found")
    
    # Social Dynamics with actual interaction content
    if user_count > 1 and conversation_snippets:
        summary_parts.append(f"**SOCIAL DYNAMICS**: Active interaction among {user_count} participants with meaningful exchanges")
        if len(conversation_snippets) >= 2:
            summary_parts.append(f"Sample interaction: {conversation_snippets[0]}")
    elif user_count > 1:
        summary_parts.append(f"**SOCIAL DYNAMICS**: Group interaction among {user_count} participants")
    else:
        summary_parts.append("**SOCIAL DYNAMICS**: Individual activity only")
    
    return '\n'.join(summary_parts)

def generate_with_gemini(prompt):
    """Generate content using Google Gemini AI SDK"""
    global model
    
    # Check if model is available
    if not model:
        # Try to reinitialize
        if not initialize_gemini_model():
            return "API_ERROR"
    
    if not model:
        return "API_ERROR"
        
    try:
        # Generate content with proper configuration
        response = model.generate_content(prompt)
        # Ensure we return a string
        if hasattr(response, 'text'):
            return str(response.text)
        else:
            return str(response)
    except Exception as e:
        logger.error(f"Gemini API error: {e}")
        # Check if it's a quota exceeded error
        error_str = str(e).lower()
        if "429" in error_str or "quota" in error_str or "limit" in error_str:
            return "QUOTA_EXCEEDED"
        return "API_ERROR"

# Using parse_timestamp from utils.py

def generate_total_summary(messages):
    if not messages:
        return "No messages found in the selected date range."
    
    chat_text = "\n".join([f"{msg['sender']}: {msg['message']}" for msg in messages])
    
    try:
        prompt = "Generate a brief summary in 3-4 bullet points. Focus only on the most important topics and key events. Keep it concise and easy to understand. Use **bold** for important terms, *italic* for emphasis, and <span style='color:red'>red text</span> for critical information.\n\n" + chat_text
        response = generate_with_gemini(prompt)
        
        # Check if API quota exceeded or error occurred
        if response == "QUOTA_EXCEEDED":
            return generate_fallback_summary(messages)
        elif response == "API_ERROR":
            return "Summary temporarily unavailable due to technical issues."
        else:
            return response
    except Exception as e:
        return f"Error generating summary: {str(e)}"

def generate_user_messages(messages):
    """Generate enhanced user messages with meaningful content and timestamps"""
    if not messages:
        return []
    
    # Filler words to remove
    filler_words = {
        'ok', 'okay', 'okk', 'okkkk', 'hmm', 'hmmm', 'yes', 'yeah', 'yep', 'yup', 
        'no', 'nope', 'ha', 'haha', 'lol', 'lmao', 'hehe', 'hi', 'hello', 'hey', 
        'bye', 'byee', 'thanks', 'thank', 'welcome', 'sure', 'fine', 'good', 
        'nice', 'great', 'cool', 'awesome', 'alright', 'right', 'correct'
    }
    
    # System message patterns to exclude
    system_message_patterns = [
        'security code', 'tap to learn more', 'changed the subject', 'added', 'removed',
        'left the group', 'joined using', 'created group', 'media omitted', 
        'this message was deleted', 'changed this group', 'end-to-end encrypted'
    ]
    
    user_messages = []
    user_topics = {}  # Track topics per user
    
    for msg in messages:
        dt = parse_timestamp(msg['timestamp'])
        if dt:
            formatted_datetime = dt.strftime('%d %b %Y, %I:%M %p')
        else:
            formatted_datetime = msg['timestamp']
        
        user = msg['sender']
        message_text = msg['message'].strip()
        
        # Skip system messages more comprehensively
        is_system_message = any(pattern in message_text.lower() for pattern in system_message_patterns)
        if is_system_message:
            continue
            
        # Clean message by removing filler words
        words = message_text.split()
        cleaned_words = []
        for word in words:
            # Remove punctuation for comparison but keep in display
            word_clean = word.lower().strip('.,!?;:')
            if word_clean not in filler_words and len(word_clean) > 1:
                cleaned_words.append(word)
        
        # Only include messages with substantial content
        if len(cleaned_words) >= 2 or len(message_text) >= 15:
            cleaned_message = ' '.join(cleaned_words) if cleaned_words else message_text
            
            # Format message content for better readability
            formatted_message = format_message_content(cleaned_message)
            
            # Extract topics for this user
            if user not in user_topics:
                user_topics[user] = set()
            
            # Simple topic extraction
            significant_words = [w.lower() for w in cleaned_words if len(w) > 4 and w.isalpha()]
            user_topics[user].update(significant_words[:3])  # Add first 3 significant words
            
            user_messages.append({
                'sender': user,
                'cleaned_message': formatted_message,
                'formatted_datetime': formatted_datetime,
                'original_message': message_text,
                'message_length': len(formatted_message)
            })
    
    # Add topics to each message (dynamically adjust based on content)
    for msg in user_messages:
        user = msg['sender']
        msg['topics'] = list(user_topics.get(user, set()))[:min(7, max(3, len(user_topics.get(user, set()))))]  # Dynamic limit based on content
    
    # Sort by timestamp (most recent first)
    user_messages.sort(key=lambda x: x['formatted_datetime'], reverse=True)
    
    return user_messages

def format_message_content(message):
    """Format message content for better readability with bullet points"""
    if not message:
        return message
    
    # Remove escape characters
    message = message.replace('\\n', '\n').replace('\\t', ' ').replace(r'\[', '[').replace(r'\]', ']')
    message = re.sub(r'\\(.)', r'\1', message)  # Remove backslashes before special characters
    
    # If message contains structured content, format it with bullet points
    if any(indicator in message for indicator in ['*', '**', '१)', '२)', 'विषय', 'दिनांक']):
        # Split by common delimiters and create bullet points
        lines = message.replace('*', '').split()
        formatted_lines = []
        current_line = []
        
        for word in lines:
            # Check for numbered points
            if word.startswith(('१)', '२)', '३)', '४)', '५)', '1)', '2)', '3)', '4)', '5)')):
                if current_line:
                    formatted_lines.append(' '.join(current_line))
                    current_line = []
                formatted_lines.append(f"• {word}")
            elif word in ['विषय:-', 'दिनांक-', 'वार-', 'टिप-']:
                if current_line:
                    formatted_lines.append(' '.join(current_line))
                    current_line = []
                formatted_lines.append(f"• {word}")
            else:
                current_line.append(word)
        
        if current_line:
            formatted_lines.append(' '.join(current_line))
        
        # Join with proper line breaks
        return ' '.join(formatted_lines) if len(formatted_lines) <= 3 else '\n'.join(formatted_lines[:5]) + '...'
    
    # For regular messages, just clean up extra spaces
    return ' '.join(message.split())

def get_users_in_messages(messages):
    if not messages:
        return []
    users = set()
    for msg in messages:
        users.add(msg['sender'])
    
    return sorted(list(users))

def generate_user_messages_for_user(messages, user):
    if not messages:
        return []
    user_messages = []
    for msg in messages:
        if msg['sender'] == user:
            dt = parse_timestamp(msg['timestamp'])
            if dt:
                time_str = dt.strftime('%d %b %Y, %I:%M %p')
            else:
                time_str = msg['timestamp']
            
            user_messages.append({
                'timestamp': time_str,
                'message': msg['message']
            })
    
    return user_messages

def count_user_messages(messages, user):
    """Count the number of messages sent by a specific user"""
    if not messages or not user:
        return 0
    
    count = 0
    for msg in messages:
        if msg['sender'] == user:
            count += 1
    
    return count

def filter_messages_by_time_range(messages, start_time_str=None, end_time_str=None):
    """Filter messages by time range (simple implementation for fallback)"""
    if not messages:
        return []
    
    # For fallback purposes, we'll do a simple string-based filtering
    # In a production environment, you would want to parse timestamps properly
    filtered_messages = []
    
    for msg in messages:
        timestamp = msg['timestamp'].lower()
        
        # If no time range specified, include all messages
        if not start_time_str and not end_time_str:
            filtered_messages.append(msg)
            continue
        
        # Simple time range check (this is a basic implementation)
        include_message = True
        
        if start_time_str and start_time_str in timestamp:
            # This is a very basic check - in practice, you'd want proper datetime parsing
            filtered_messages.append(msg)
        elif end_time_str and end_time_str in timestamp:
            # This is a very basic check - in practice, you'd want proper datetime parsing
            filtered_messages.append(msg)
        elif not start_time_str and not end_time_str:
            filtered_messages.append(msg)
    
    # If we have specific time filtering needs that aren't met by the simple approach,
    # return all messages (the UI should handle proper filtering)
    return filtered_messages if filtered_messages else messages

def clean_summary_text(summary):
    """Clean and format structured summary text following memory specifications"""
    if not summary:
        return ""
    
    # If it's an error message or quota message, return it as-is
    if any(keyword in summary.lower() for keyword in ['error', 'unavailable', 'quota', 'limits']):
        return summary
    
    # Handle structured format with sections
    if "**ACTIVITY OVERVIEW**" in summary or "**MAIN DISCUSSION TOPICS**" in summary:
        # Clean up the structured format but preserve the sections
        lines = summary.split('\n')
        cleaned_lines = []
        for line in lines:
            line = line.strip()
            if line:
                # Skip system message references
                if any(term in line.lower() for term in ['media omitted', 'security code', 'tap to learn']):
                    continue
                # Remove escape characters and clean formatting
                line = line.replace('\\n', '\n').replace('\\t', ' ').replace(r'\[', '[').replace(r'\]', ']')
                line = re.sub(r'\\(.)', r'\1', line)  # Remove backslashes before special characters
                cleaned_lines.append(line)
        return '\n'.join(cleaned_lines)
    
    # Handle bullet point format (fallback)
    lines = summary.split('\n')
    cleaned_lines = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Skip lines that mention system messages
        if any(term in line.lower() for term in ['media omitted', 'security code', 'tap to learn', 'changed security', 'message deleted']):
            continue
        
        # Remove escape characters and clean formatting
        line = line.replace('\\n', '\n').replace('\\t', ' ').replace(r'\[', '[').replace(r'\]', ']')
        line = re.sub(r'\\(.)', r'\1', line)  # Remove backslashes before special characters
        
        # Process bullet points
        if line.startswith(('•', '-', '*')) or (len(line) >= 2 and line[0].isdigit() and line[1] == '.'):
            # Remove bullet character and clean
            if line[0].isdigit() and line[1] == '.':
                line = line[2:].lstrip()
            else:
                line = line[1:].lstrip()
            
            line = re.sub(r'\s+', ' ', line).strip()
            
            if line and len(line) > 5:
                line = line[0].upper() + line[1:] if line else line
                cleaned_lines.append(f"* {line}")
        else:
            # For non-bullet lines, clean and format
            line = re.sub(r'\s+', ' ', line).strip()
            if line and len(line) > 5:
                cleaned_lines.append(f"* {line}")
    
    # If no meaningful content found
    if not cleaned_lines:
        return "**MAIN DISCUSSION TOPICS**: Mostly media sharing and brief exchanges during this week"
    
    return '\n'.join(cleaned_lines)

def generate_weekly_summary(messages, start_date_str=None, end_date_str=None):
    """Generate comprehensive weekly summaries with detailed discussion points for filtered date range"""
    if not messages:
        return []
    
    # Parse start and end dates if provided
    start_date = None
    end_date = None
    if start_date_str:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
    if end_date_str:
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
        end_date = end_date.replace(hour=23, minute=59, second=59)
    
    # Filter messages by the provided date range first
    filtered_messages = []
    for msg in messages:
        msg_date = parse_timestamp(msg['timestamp'])
        if msg_date is None:
            continue
        if start_date and msg_date < start_date:
            continue
        if end_date and msg_date > end_date:
            continue
        filtered_messages.append(msg)
    
    # If start_date or end_date is not provided, determine from messages
    if not start_date or not end_date:
        message_dates = [parse_timestamp(msg['timestamp']) for msg in filtered_messages]
        # Filter out None values
        message_dates = [date for date in message_dates if date is not None]
        if message_dates:
            if not start_date:
                start_date = min(message_dates)
            if not end_date:
                end_date = max(message_dates)
        else:
            # No valid dates found
            return []
    
    # Generate all weeks in the date range
    weeks = {}
    
    # Start from the Monday of the week containing start_date
    current_week_start = start_date - timedelta(days=start_date.weekday())
    
    # Continue until we've covered the week containing end_date
    while current_week_start <= end_date:
        week_key = current_week_start.strftime('%Y-%m-%d')
        weeks[week_key] = []
        current_week_start += timedelta(days=7)
    
    # Assign messages to their respective weeks
    for msg in filtered_messages:
        dt = parse_timestamp(msg['timestamp'])
        if not dt:
            continue
            
        monday = dt - timedelta(days=dt.weekday())
        week_key = monday.strftime('%Y-%m-%d')
        if week_key in weeks:
            weeks[week_key].append(msg)
    
    weekly_summaries = []

    # Process all weeks in the date range
    for week_key in sorted(weeks.keys()):
        week_messages = weeks[week_key]
        
        # Basic statistics for this week
        total_messages = len(week_messages)
        users = set(msg['sender'] for msg in week_messages)
        user_count = len(users)
        
        # User activity analysis
        user_msg_count = {}
        for msg in week_messages:
            user = msg['sender']
            user_msg_count[user] = user_msg_count.get(user, 0) + 1
        
        # Sort users by activity
        sorted_users = sorted(user_msg_count.items(), key=lambda x: x[1], reverse=True)
        most_active_user = sorted_users[0] if sorted_users else None
        
        monday = datetime.strptime(week_key, '%Y-%m-%d')
        sunday = monday + timedelta(days=6)
        date_range = f"{monday.strftime('%d %b %Y')} to {sunday.strftime('%d %b %Y')}" 

        if total_messages == 0:
            # No messages in this week
            summary = "**ACTIVITY OVERVIEW**: No messages during this week\n**MAIN DISCUSSION TOPICS**: No conversations recorded"
        else:
            # Limit the chat text to prevent API timeouts and token limits
            week_text = "\n".join([f"{msg['sender']}: {msg['message']}" for msg in week_messages[:200]])  # Limit to 200 messages

            try:
                # Enhanced prompt to extract EXACT conversation content and quotes
                exact_content_prompt = f"""Analyze this week's WhatsApp conversation and create a detailed summary showing EXACTLY what was discussed with actual quotes and specific content.

**CRITICAL INSTRUCTIONS**:
1. Show ACTUAL messages, file names, and specific content shared
2. Include exact quotes in original language (Hindi/Marathi/English)
3. Mention specific documents, files, or links shared by name
4. Show real conversation content from ALL participants, not just the most active user
5. Include messages from different people - distribute topics across various participants
6. For Social Dynamics, describe what ALL people said to each other
7. Include specific advice, instructions, or information shared by anyone
8. DO NOT focus only on the most active user - show diversity of participants
9. DO NOT generalize - show the actual conversation content from everyone
10. For short periods (few messages), provide even MORE detail about each message

**REQUIRED STRUCTURE**:
**ACTIVITY OVERVIEW**: {total_messages} messages from {user_count} participants during this week

**KEY PARTICIPANTS**: [Most active member and their specific contributions with actual quotes]

**MAIN DISCUSSION TOPICS** (Show actual conversation topics from ALL participants, not just the most active - dynamically based on content diversity):
- Topic 1: [Any participant]: "[Actual quote from message]"
- Topic 2: [Different participant]: "[Exact message content in original language]"
- [Continue adding topics dynamically based on content variety and participant diversity]

**IMPORTANT EVENTS**: [Actual announcements, documents shared, or decisions made with exact content]

**COMMUNICATION PATTERNS**: [When specific conversations happened with timestamps]

**ACTION ITEMS**: [Exact instructions or tasks mentioned in messages with who mentioned them]

**SOCIAL DYNAMICS**: [What ALL participants said to each other - include quotes from different people]

**SPECIFIC CONTENT SHARED**: [List any files, links, or resources mentioned with exact names]

**QUESTIONS & ANSWERS**: [Show actual questions asked and any responses provided]

Week's conversation content:
{week_text}"""
                
                response = generate_with_gemini(exact_content_prompt)
                
                # Check if API quota exceeded or error occurred
                if response == "QUOTA_EXCEEDED":
                    summary = generate_fallback_summary(week_messages)
                elif response == "API_ERROR":
                    # Use fallback when API is unavailable
                    summary = generate_fallback_summary(week_messages)
                else:
                    summary = response
                    # Clean the summary text
                    summary = clean_summary_text(summary)

            except Exception as e:
                # Even if there's an error, we should still include this week in the results
                # Use fallback summary
                try:
                    summary = generate_fallback_summary(week_messages)
                except Exception as fallback_error:
                    summary = f"Error generating summary: {str(e)}. Fallback error: {str(fallback_error)}"
        
        weekly_summaries.append({
            'week_start': week_key,
            'date_range': date_range,
            'summary': summary,
            'message_count': total_messages,
            'participant_count': user_count,
            'most_active_user': most_active_user[0] if most_active_user else None
        })
    
    return weekly_summaries


def generate_daily_user_messages(messages):
    """Generate day-by-day user messages with short summaries"""
    if not messages:
        return []
    
    # Group messages by date

    daily_messages = {}
    for msg in messages:
        dt = parse_timestamp(msg['timestamp'])
        if not dt:
            continue
        date_key = dt.strftime('%Y-%m-%d')
        if date_key not in daily_messages:
            daily_messages[date_key] = []
        daily_messages[date_key].append(msg)
    
    daily_summaries = []
    for date_key, day_messages in sorted(daily_messages.items()):
        # Create short summary for the day
        day_text = "\n".join([f"{msg['sender']}: {msg['message']}" for msg in day_messages])
        
        try:
            prompt = "Generate a very brief daily summary in 1-2 bullet points. Focus only on key topics or events discussed that day. Each bullet point must start with '*' and be concise. Use **bold** for important terms, *italic* for emphasis, and <span style='color:red'>red text</span> for critical information.\n\n" + day_text
            response = generate_with_gemini(prompt)
            
            # Check if API quota exceeded or error occurred
            if response == "QUOTA_EXCEEDED":
                summary = generate_fallback_summary(day_messages)
            elif response == "API_ERROR":
                summary = "Summary temporarily unavailable due to technical issues."
            else:
                summary = response
                summary = clean_summary_text(summary)
        except Exception as e:
            summary = f"Error generating summary: {str(e)}"
        
        # Format date nicely
        date_obj = datetime.strptime(date_key, '%Y-%m-%d')
        formatted_date = date_obj.strftime('%d %b %Y')
        
        daily_summaries.append({
            'date': date_key,
            'formatted_date': formatted_date,
            'summary': summary,
            'message_count': len(day_messages),
            'messages': day_messages
        })
    
    return daily_summaries

def generate_user_wise_detailed_report(messages, user):
    """Generate detailed user-wise report with date and time for each message"""
    if not messages or not user:
        return []
    
    user_messages = []
    for msg in messages:
        if msg['sender'] == user:
            dt = parse_timestamp(msg['timestamp'])
            if dt:
                formatted_datetime = dt.strftime('%d %b %Y, %I:%M %p')
                date_only = dt.strftime('%d %b %Y')
                time_only = dt.strftime('%I:%M %p')
            else:
                formatted_datetime = msg['timestamp']
                date_only = msg['timestamp'].split(',')[0] if ',' in msg['timestamp'] else msg['timestamp']
                time_only = msg['timestamp'].split(',')[1].strip() if ',' in msg['timestamp'] else ""
            
            user_messages.append({
                'datetime': formatted_datetime,
                'date': date_only,
                'time': time_only,
                'message': msg['message']
            })
    
    return user_messages


def generate_comprehensive_summary(messages, start_date_str=None, end_date_str=None):
    """Generate a comprehensive summary combining multiple analysis types"""
    if not messages:
        return {
            'brief_summary': "No messages found in the selected date range.",
            'weekly_summaries': []
        }
    
    # Generate brief summary
    brief_summary = generate_brief_summary(messages)
    
    # Generate weekly summaries
    weekly_summaries = generate_weekly_summary(messages, start_date_str, end_date_str)
    
    return {
        'brief_summary': brief_summary,
        'weekly_summaries': weekly_summaries
    }

def calculate_date_range(messages):
    """Calculate the number of days between first and last message"""
    if not messages:
        return 0
    
    dates = []
    for msg in messages:
        dt = parse_timestamp(msg['timestamp'])
        if dt:
            dates.append(dt.date())
    
    if len(dates) < 2:
        return 1
    
    return (max(dates) - min(dates)).days + 1

# Generate brief summary
def generate_brief_summary(messages):
    """Generate a comprehensive brief summary with actionable insights for decision making"""
    if not messages:
        return "No messages found in the selected date range."

    # Basic statistics for enhanced insights
    total_messages = len(messages)
    users = set(msg['sender'] for msg in messages)
    user_count = len(users)

    # Most active user
    user_msg_count = {}
    for msg in messages:
        user = msg['sender']
        user_msg_count[user] = user_msg_count.get(user, 0) + 1

    most_active_user = max(user_msg_count.items(), key=lambda x: x[1]) if user_msg_count else None

    # Calculate activity patterns
    hourly_activity = {}
    daily_activity = {}
    for msg in messages:
        dt = parse_timestamp(msg['timestamp'])
        if dt:
            hour = dt.hour
            day = dt.strftime('%A')
            hourly_activity[hour] = hourly_activity.get(hour, 0) + 1
            daily_activity[day] = daily_activity.get(day, 0) + 1

    peak_hour = max(hourly_activity.items(), key=lambda x: x[1])[0] if hourly_activity else None
    peak_day = max(daily_activity.items(), key=lambda x: x[1])[0] if daily_activity else None

    # Enhanced analysis for short periods (7 days or less)
    date_range = calculate_date_range(messages)
    is_short_period = date_range <= 7
    
    # Extract detailed information
    file_shares = []
    links = []
    meetings = []
    decisions = []
    action_items = []
    questions = []
    announcements = []
    technical_discussions = []
    
    for msg in messages:
        message_text = msg['message'].lower()
        original_text = msg['message']
        sender = msg['sender']
        
        # Check for file shares
        if any(ext in message_text for ext in ['.pdf', '.doc', '.jpg', '.png', '.mp4', '.xlsx', '.docx', '.pptx']):
            file_shares.append(f"{sender}: {original_text}")
        
        # Check for links
        if 'http' in message_text or 'www.' in message_text:
            links.append(f"{sender}: {original_text}")
            
        # Check for meeting related keywords
        if any(keyword in message_text for keyword in ['meeting', 'call', 'zoom', 'teams', 'hangout', 'discuss', 'schedule', 'मिटिंग', 'दौरा']):
            meetings.append(f"{sender}: {original_text}")
            
        # Check for decision keywords
        if any(keyword in message_text for keyword in ['decided', 'decision', 'concluded', 'final', 'agreed']):
            decisions.append(f"{sender}: {original_text}")
            
        # Check for action items
        if any(keyword in message_text for keyword in ['need to', 'should', 'must', 'todo', 'action', 'complete', 'finish', 'करावे', 'करायचे']):
            action_items.append(f"{sender}: {original_text}")
        
        # Check for questions
        if '?' in original_text or any(word in message_text for word in ['what', 'how', 'why', 'when', 'where', 'which', 'who', 'काय', 'कसे', 'केव्हा']):
            questions.append(f"{sender}: {original_text}")
        
        # Check for announcements
        if any(word in message_text for word in ['announce', 'notice', 'alert', 'अलर्ट', 'सूचना', 'जाहिरात']):
            announcements.append(f"{sender}: {original_text}")
        
        # Check for technical discussions
        if any(word in message_text for word in ['technical', 'method', 'process', 'procedure', 'technique', 'तंत्रज्ञान', 'पद्धत']):
            technical_discussions.append(f"{sender}: {original_text}")

    try:
        # Create enhanced prompt based on period length
        chat_text = "\n".join([f"{msg['sender']}: {msg['message']}" for msg in messages[:200]])
        
        if is_short_period:
            # Enhanced analysis for short periods
            comprehensive_prompt = f"""Analyze this WhatsApp group conversation from the last {date_range} days and create a DETAILED brief summary with specific insights and actionable information.

**CRITICAL INSTRUCTIONS FOR SHORT PERIOD ANALYSIS**:
1. Extract EXACT quotes and specific content from messages
2. Identify specific problems, solutions, or advice mentioned
3. Show actual conversation flow and responses between participants
4. Include specific names, dates, times, and locations mentioned
5. Highlight any urgent or important information shared
6. Show what each participant contributed specifically

**REQUIRED STRUCTURE**:
<h2 style='color:green;'>📊 CONVERSATION OVERVIEW</h2>
==Total Messages: {total_messages} from {user_count} participants over {date_range} days==

<h2 style='color:green;'>👥 KEY PARTICIPANTS & CONTRIBUTIONS</h2>
==Most Active: {most_active_user[0] if most_active_user else 'N/A'} with {most_active_user[1] if most_active_user else 0} messages==
==Show what each participant specifically contributed with actual quotes==

<h2 style='color:green;'>⏰ ACTIVITY PATTERNS</h2>
==Peak Activity: {peak_hour if peak_hour is not None else 'N/A'}:00 hours on {peak_day if peak_day else 'N/A'}==
==Show specific times when important conversations happened==

<h2 style='color:green;'>💬 MAIN DISCUSSION TOPICS (with actual quotes)</h2>
==Provide key topics with EXACT quotes from messages in original language==
==Show the actual conversation flow and responses==Dynamic number of topics based on content diversity==

<h2 style='color:green;'>📁 IMPORTANT RESOURCES SHARED</h2>
==Files Shared: {len(file_shares)} | Links Shared: {len(links)}==
==List specific files and links mentioned with who shared them==

<h2 style='color:green;'>❓ QUESTIONS ASKED</h2>
==Show actual questions asked with who asked them and any answers provided==

<h2 style='color:green;'>📢 ANNOUNCEMENTS & ALERTS</h2>
==List specific announcements with exact content and who made them==

<h2 style='color:green;'>🔧 TECHNICAL DISCUSSIONS</h2>
==Show any technical advice, methods, or procedures discussed==

<h2 style='color:green;'>✅ ACTIONABLE INSIGHTS</h2>
==Decisions Made: {len(decisions)} | Action Items: {len(action_items)} | Meetings Planned: {len(meetings)}==
==Show specific decisions and action items with who mentioned them==

<h2 style='color:green;'>🎯 IMMEDIATE NEXT STEPS</h2>
==Based on the conversation, what should be done next?==

Conversation content:
{chat_text}"""
        else:
            # Standard analysis for longer periods
            comprehensive_prompt = f"""Analyze this WhatsApp group conversation and create a comprehensive brief summary that provides actionable insights for decision making.

**REQUIRED STRUCTURE**:
<h2 style='color:green;'>CONVERSATION OVERVIEW</h2>
==Total Messages: {total_messages} from {user_count} participants==

<h2 style='color:green;'>KEY PARTICIPANTS</h2>
==Most Active: {most_active_user[0] if most_active_user else 'N/A'} with {most_active_user[1] if most_active_user else 0} messages==

<h2 style='color:green;'>ACTIVITY PATTERNS</h2>
==Peak Activity: {peak_hour if peak_hour is not None else 'N/A'}:00 hours on {peak_day if peak_day else 'N/A'}==

<h2 style='color:green;'>MAIN DISCUSSION TOPICS</h2>
==Provide key topics discussed with brief descriptions==
==Dynamic number of topics based on content variety==

<h2 style='color:green;'>IMPORTANT RESOURCES</h2>
==Files Shared: {len(file_shares)} | Links Shared: {len(links)}==

<h2 style='color:green;'>ACTIONABLE INSIGHTS</h2>
==Decisions Made: {len(decisions)} | Action Items: {len(action_items)} | Meetings Planned: {len(meetings)}==

<h2 style='color:green;'>RECOMMENDATIONS</h2>
==Provide 2-3 actionable recommendations based on the conversation==

Conversation content:
{chat_text}"""

        response = generate_with_gemini(comprehensive_prompt)

        # Check if API quota exceeded or error occurred
        if response == "QUOTA_EXCEEDED":
            # Enhanced fallback summary with actual content for brief summary
            return generate_fallback_brief_summary(total_messages, user_count, most_active_user, peak_hour, peak_day, file_shares, links, meetings, decisions, action_items, messages, questions, announcements, technical_discussions, date_range)

        elif response == "API_ERROR":
            # Use fallback summary when API is unavailable
            return generate_fallback_brief_summary(total_messages, user_count, most_active_user, peak_hour, peak_day, file_shares, links, meetings, decisions, action_items, messages, questions, announcements, technical_discussions, date_range)
        else:
            # Clean the response to follow formatting preferences
            return response

    except Exception as e:
        # Even if there's an exception, provide a fallback summary
        return generate_fallback_brief_summary(total_messages, user_count, most_active_user, peak_hour, peak_day, file_shares, links, meetings, decisions, action_items, messages, questions, announcements, technical_discussions, date_range)

def generate_fallback_brief_summary(total_messages, user_count, most_active_user, peak_hour, peak_day, file_shares, links, meetings, decisions, action_items, messages=None, questions=None, announcements=None, technical_discussions=None, date_range=None):
    """Generate an enhanced fallback brief summary when AI is unavailable"""
    fallback_parts = []
    
    # Determine if this is a short period for enhanced analysis
    is_short_period = date_range and date_range <= 7

    # Overview with actual conversation analysis
    if is_short_period:
        fallback_parts.append("<h2 style='color:green;'>📊 CONVERSATION OVERVIEW</h2>")
        fallback_parts.append(f"==Total Messages: {total_messages} from {user_count} participants over {date_range} days==")
    else:
        fallback_parts.append("<h2 style='color:green;'>CONVERSATION OVERVIEW</h2>")
        fallback_parts.append(f"==Total Messages: {total_messages} from {user_count} participants==")

    # Most active user with their contributions
    if most_active_user:
        if is_short_period:
            fallback_parts.append("<h2 style='color:green;'>👥 KEY PARTICIPANTS & CONTRIBUTIONS</h2>")
            fallback_parts.append(f"==Most Active: {most_active_user[0]} with {most_active_user[1]} messages ({round((most_active_user[1]/total_messages)*100)}% of activity)==")
            # Add actual message content for short periods
            if messages:
                user_messages = [msg for msg in messages if msg['sender'] == most_active_user[0]]
                if user_messages:
                    fallback_parts.append("==Recent contributions from most active participant:==")
                    for i, msg in enumerate(user_messages[:3], 1):
                        content = msg['message'][:100] + "..." if len(msg['message']) > 100 else msg['message']
                        fallback_parts.append(f"=={i}. \"{content}\"==")
        else:
            fallback_parts.append("<h2 style='color:green;'>KEY PARTICIPANTS</h2>")
            fallback_parts.append(f"==Most Active: {most_active_user[0]} with {most_active_user[1]} messages ({round((most_active_user[1]/total_messages)*100)}% of activity)==")

    # Activity patterns
    if is_short_period:
        fallback_parts.append("<h2 style='color:green;'>⏰ ACTIVITY PATTERNS</h2>")
    else:
        fallback_parts.append("<h2 style='color:green;'>ACTIVITY PATTERNS</h2>")
    
    if peak_hour is not None:
        hour_12 = peak_hour % 12 or 12
        am_pm = "AM" if peak_hour < 12 else "PM"
        fallback_parts.append(f"==Peak Activity: {hour_12}:00 {am_pm} on {peak_day if peak_day else 'N/A'}==")
        if is_short_period and messages:
            # Show specific times when messages were sent
            times = []
            for msg in messages:
                dt = parse_timestamp(msg['timestamp'])
                if dt:
                    time_str = dt.strftime('%I:%M %p')
                    if time_str not in times:
                        times.append(time_str)
            if times:
                fallback_parts.append(f"==Messages sent at: {', '.join(times[:5])}==")
    else:
        fallback_parts.append("==No significant activity patterns identified==")

    # Main topics - extract from actual messages with more detail for short periods
    if is_short_period:
        fallback_parts.append("<h2 style='color:green;'>💬 MAIN DISCUSSION TOPICS (with actual quotes)</h2>")
        if messages:
            # Extract actual topics from messages
            topics = []
            for msg in messages[:5]:  # Show first 5 messages as topics
                content = msg['message'][:80] + "..." if len(msg['message']) > 80 else msg['message']
                topics.append(f"=={msg['sender']}: \"{content}\"==")
            if topics:
                fallback_parts.extend(topics)
            else:
                fallback_parts.append("==No substantial conversation topics identified==")
        else:
            fallback_parts.append("==No conversation content available==")
    else:
        fallback_parts.append("<h2 style='color:green;'>MAIN DISCUSSION TOPICS</h2>")
        if file_shares or links or meetings:
            topic_points = []
            if file_shares:
                topic_points.append(f"Document sharing: {len(file_shares)} files shared")
            if links:
                topic_points.append(f"Resource sharing: {len(links)} links shared")
            if meetings:
                topic_points.append(f"Coordination: {len(meetings)} meeting-related discussions")
            fallback_parts.append(f"=={'; '.join(topic_points)}==")
        else:
            fallback_parts.append("==General group conversation==")

    # Questions asked (for short periods)
    if is_short_period and questions:
        fallback_parts.append("<h2 style='color:green;'>❓ QUESTIONS ASKED</h2>")
        for i, question in enumerate(questions[:3], 1):
            fallback_parts.append(f"=={i}. {question}==")

    # Announcements (for short periods)
    if is_short_period and announcements:
        fallback_parts.append("<h2 style='color:green;'>📢 ANNOUNCEMENTS & ALERTS</h2>")
        for i, announcement in enumerate(announcements[:3], 1):
            fallback_parts.append(f"=={i}. {announcement}==")

    # Technical discussions (for short periods)
    if is_short_period and technical_discussions:
        fallback_parts.append("<h2 style='color:green;'>🔧 TECHNICAL DISCUSSIONS</h2>")
        for i, discussion in enumerate(technical_discussions[:3], 1):
            fallback_parts.append(f"=={i}. {discussion}==")

    # Important resources
    if is_short_period:
        fallback_parts.append("<h2 style='color:green;'>📁 IMPORTANT RESOURCES SHARED</h2>")
    else:
        fallback_parts.append("<h2 style='color:green;'>IMPORTANT RESOURCES</h2>")
    fallback_parts.append(f"==Files Shared: {len(file_shares)} | Links Shared: {len(links)}==")
    
    if is_short_period and (file_shares or links):
        if file_shares:
            fallback_parts.append("==Files mentioned:==")
            for file_share in file_shares[:3]:
                fallback_parts.append(f"==• {file_share}==")
        if links:
            fallback_parts.append("==Links shared:==")
            for link in links[:3]:
                fallback_parts.append(f"==• {link}==")

    # Actionable insights
    if is_short_period:
        fallback_parts.append("<h2 style='color:green;'>✅ ACTIONABLE INSIGHTS</h2>")
    else:
        fallback_parts.append("<h2 style='color:green;'>ACTIONABLE INSIGHTS</h2>")
    fallback_parts.append(f"==Decisions Made: {len(decisions)} | Action Items: {len(action_items)} | Meetings Planned: {len(meetings)}==")
    
    if is_short_period and (decisions or action_items):
        if decisions:
            fallback_parts.append("==Specific decisions mentioned:==")
            for decision in decisions[:3]:
                fallback_parts.append(f"==• {decision}==")
        if action_items:
            fallback_parts.append("==Action items identified:==")
            for action in action_items[:3]:
                fallback_parts.append(f"==• {action}==")

    # Recommendations
    if is_short_period:
        fallback_parts.append("<h2 style='color:green;'>🎯 IMMEDIATE NEXT STEPS</h2>")
    else:
        fallback_parts.append("<h2 style='color:green;'>RECOMMENDATIONS</h2>")
    
    recommendations = []
    if is_short_period:
        if total_messages < 5:
            recommendations.append("Consider encouraging more group participation")
        if questions and not any('answer' in str(messages).lower() for msg in messages):
            recommendations.append("Follow up on unanswered questions")
        if announcements:
            recommendations.append("Review and act on recent announcements")
        if not recommendations:
            recommendations.append("Continue monitoring group activity")
    else:
        if not meetings and user_count > 1:
            recommendations.append("Schedule a team meeting to discuss key topics")
        if len(file_shares) > 5:
            recommendations.append("Organize shared files in a central repository")
        if most_active_user and (most_active_user[1]/total_messages) > 0.4:
            recommendations.append("Encourage more balanced participation from all members")
        if not recommendations:
            recommendations.append("Continue current communication practices")
    
    fallback_parts.append(f"=={'; '.join(recommendations)}==")

    return '\n'.join(fallback_parts)


# Generate structured weekly summary
def generate_structured_summary(messages):
    try:
        model = genai.GenerativeModel(model_name="gemini-2.5-flash")  # type: ignore
        prompt = (
            "You are an expert WhatsApp chat analyst. Read the conversation messages provided "
            "in JSON-like list form and produce a rich weekly summary as a JSON object with "
            "these properties: activity_summary (string), key_topics (array of strings), "
            "notable_events (array of strings), social_dynamics (string), and "
            "recommended_actions (array of strings)."
            "Make sure each property is filled based only on evidence in the messages. "
            "If there is insufficient information for a property, set it to an empty string "
            "or an empty array as appropriate. Use concise language, but include concrete "
            "details like usernames, counts, dates, and times when available.\n\n"
            f"Messages: {messages}"
        )
        response = model.generate_content(
            prompt,
            generation_config={
                "temperature": 0.4,
                "max_output_tokens": 2048,
                "response_mime_type": "application/json"
            }
        )
        if hasattr(response, "text"):
            return response.text
        return str(response)
    except Exception as e:
        logger.error(f"Error generating structured summary: {e}")
        return {"status": "error", "message": str(e)}


# Generate answer to specific questions
def generate_question_answer(messages, question):
    """Generate an answer to a specific question based on chat messages"""
    try:
        # Prepare the chat context
        chat_context = "\n".join([f"{msg['sender']}: {msg['message']}" for msg in messages[:200]])  # Limit to 200 messages
        
        # Create a prompt for question answering with enhanced instructions
        prompt = f"""You are an expert WhatsApp chat analyzer. Based on the following WhatsApp chat conversation, please answer the question accurately and comprehensively.

Conversation context:
{chat_context}

Question: {question}

Instructions:
1. Analyze the conversation context carefully to find relevant information
2. Provide a clear, concise, and accurate answer based on the conversation
3. If the information is not available in the conversation, state that clearly
4. For questions about user activity, message counts, or statistics, provide specific numbers when available
5. For time-based questions, reference specific timestamps when relevant
6. Format your response clearly with appropriate headings and bullet points when needed

Please provide your answer:"""
        
        # Use the existing generate_with_gemini function
        response = generate_with_gemini(prompt)
        
        # Check for quota or API errors
        if response == "QUOTA_EXCEEDED":
            # Fallback answer using pattern matching
            return generate_fallback_answer(question, messages)
        elif response == "API_ERROR":
            return "Unable to generate answer due to technical issues. Please try again later."
        else:
            return response
            
    except Exception as e:
        logger.error(f"Error generating question answer: {e}")
        return {"status": "error", "message": str(e)}


def generate_fallback_answer(question, messages):
    """Generate a fallback answer when AI is unavailable"""
    if not messages:
        return "I don't have any messages to analyze for this question."
    
    question_lower = question.lower()
    
    # Analyze basic statistics
    total_messages = len(messages)
    users = set(msg['sender'] for msg in messages)
    user_count = len(users)
    
    # User activity analysis
    user_msg_count = {}
    for msg in messages:
        user = msg['sender']
        user_msg_count[user] = user_msg_count.get(user, 0) + 1
    
    most_active_user = max(user_msg_count.items(), key=lambda x: x[1]) if user_msg_count else None
    least_active_user = min(user_msg_count.items(), key=lambda x: x[1]) if user_msg_count else None
    
    # Extract meaningful content and filter system messages
    meaningful_messages = []
    meeting_messages = []
    file_messages = []
    topic_messages = []
    
    for msg in messages:
        message_text = msg['message'].strip()
        message_lower = message_text.lower()
        
        # Skip system messages
        if any(term in message_lower for term in ['security code', 'media omitted', 'tap to learn', 'left', 'added', 'removed']):
            continue
            
        # Collect meaningful messages
        if len(message_text) > 15:
            meaningful_messages.append(msg)
            
            # Look for meeting-related content
            if any(word in message_lower for word in ['meet', 'meeting', 'call', 'zoom', 'teams', 'hangout', 'discuss', 'schedule']):
                meeting_messages.append(msg)
                
            # Look for file/document sharing
            if any(ext in message_lower for ext in ['.pdf', '.doc', '.jpg', '.png', '.mp4', '.xlsx', '.jpeg', '.docx']):
                file_messages.append(msg)
                
            # Collect other substantial content
            if len(message_text) > 30:
                topic_messages.append(msg)
    
    # Handle different types of questions with improved pattern matching
    
    # User-specific message count questions
    if any(word in question_lower for word in ['how many', 'count', 'number of']) and 'message' in question_lower:
        # Extract user name from question (simple approach)
        # This is a basic implementation - in practice, you might want to use NLP for better entity extraction
        user_name = None
        # Look for common user name patterns
        for user in user_msg_count.keys():
            # Check if user name appears in the question
            if user.lower() in question_lower:
                user_name = user
                break
        
        if user_name:
            user_message_count = count_user_messages(messages, user_name)
            return f"📊 **Message Statistics for {user_name}:**\n\n• **Messages Sent**: {user_message_count}\n• **Percentage of Total**: {round((user_message_count/total_messages)*100, 1)}%"
        else:
            # Fall back to general statistics
            answer = f"📊 **Message Statistics:**\n\n"
            answer += f"• **Total Messages**: {total_messages}\n"
            answer += f"• **Total Users**: {user_count}\n"
            answer += f"• **Date Range**: {messages[0]['timestamp']} to {messages[-1]['timestamp']}\n"
            answer += f"• **Average per User**: {round(total_messages/user_count, 1)} messages\n"
            
            # Add most and least active users
            if most_active_user:
                answer += f"• **Most Active User**: {most_active_user[0]} ({most_active_user[1]} messages)\n"
            if least_active_user:
                answer += f"• **Least Active User**: {least_active_user[0]} ({least_active_user[1]} messages)\n"
            
            return answer
    
    # Meeting-related questions
    if any(word in question_lower for word in ['meet', 'meeting', 'call', 'schedule', 'appointment']):
        if meeting_messages:
            answer = "📅 **Meetings Found:**\n\n"
            for i, msg in enumerate(meeting_messages[:5], 1):  # Show up to 5 meetings
                meeting_content = msg['message'][:200] + "..." if len(msg['message']) > 200 else msg['message']
                answer += f"**{i}. Meeting on {msg['timestamp']}**\n"
                answer += f"👤 Organized by: {msg['sender']}\n"
                answer += f"📝 Details: {meeting_content}\n\n"
            return answer
        else:
            return "No meetings found in the conversation history."
    
    # Most active user questions
    elif (any(word in question_lower for word in ['most active', 'top user', 'highest activity']) or 
          (any(word in question_lower for word in ['who', 'active user']) and 'most' in question_lower)) and 'least' not in question_lower:
        if most_active_user:
            # Show top 3 users
            sorted_users = sorted(user_msg_count.items(), key=lambda x: x[1], reverse=True)
            answer = "👥 **Most Active Users:**\n\n"
            for i, (user, count) in enumerate(sorted_users[:3], 1):
                percentage = round((count/total_messages)*100, 1)
                answer += f"**{i}. {user}**: {count} messages ({percentage}%)\n"
            return answer
        else:
            return "Unable to determine user activity from the available data."
    
    # Least active user questions
    elif (any(word in question_lower for word in ['least active', 'lowest activity', 'inactive']) or 
          (any(word in question_lower for word in ['who', 'active user']) and 'least' in question_lower)):
        if least_active_user:
            # Show bottom 3 users (sorted by message count ascending)
            sorted_users = sorted(user_msg_count.items(), key=lambda x: x[1])
            answer = "👥 **Least Active Users:**\n\n"
            for i, (user, count) in enumerate(sorted_users[:3], 1):
                percentage = round((count/total_messages)*100, 1)
                answer += f"**{i}. {user}**: {count} messages ({percentage}%)\n"
            return answer
        else:
            return "Unable to determine user activity from the available data."
    
    # General statistics questions
    elif any(word in question_lower for word in ['how many', 'total', 'messages', 'count', 'number of', 'statistics', 'stats']):
        answer = f"📊 **Message Statistics:**\n\n"
        answer += f"• **Total Messages**: {total_messages}\n"
        answer += f"• **Total Users**: {user_count}\n"
        answer += f"• **Date Range**: {messages[0]['timestamp']} to {messages[-1]['timestamp']}\n"
        answer += f"• **Average per User**: {round(total_messages/user_count, 1)} messages\n"
        
        # Add most and least active users
        if most_active_user:
            answer += f"• **Most Active User**: {most_active_user[0]} ({most_active_user[1]} messages)\n"
        if least_active_user:
            answer += f"• **Least Active User**: {least_active_user[0]} ({least_active_user[1]} messages)\n"
        
        return answer
    
    # File/document sharing questions
    elif any(word in question_lower for word in ['file', 'document', 'pdf', 'shared', 'share', 'attachment']):
        if file_messages:
            answer = "📎 **Files/Documents Shared:**\n\n"
            for i, msg in enumerate(file_messages[:5], 1):
                answer += f"**{i}. {msg['timestamp']}**\n"
                answer += f"👤 Shared by: {msg['sender']}\n"
                answer += f"📄 File: {msg['message'][:100]}...\n\n"
            return answer
        else:
            return "No files or documents were shared."
    
    # Time range questions
    elif any(word in question_lower for word in ['show me', 'messages on', 'from', 'to', 'between']):
        # This is a basic implementation - in practice, you would want to parse dates properly
        # For now, we'll just indicate that time filtering should be done in the UI
        return "Please use the date filters in the UI to view messages for specific time ranges."
    
    # Specific date questions (e.g., "on 11/04/2024")
    elif re.search(r'\b(on|for)\s+\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b', question_lower):
        # Extract date from question
        date_match = re.search(r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b', question_lower)
        if date_match and messages:
            requested_date = date_match.group()
            # Format the date to match the message timestamps
            formatted_messages = []
            for msg in messages:
                # Check if the message timestamp contains the requested date
                if requested_date.replace('/', '-') in msg['timestamp'] or requested_date.replace('-', '/') in msg['timestamp']:
                    formatted_messages.append(msg)
            
            if formatted_messages:
                answer = f"📝 **Messages on {requested_date}:**\n\n"
                # Group messages by sender
                sender_messages = {}
                for msg in formatted_messages:
                    sender = msg['sender']
                    if sender not in sender_messages:
                        sender_messages[sender] = []
                    sender_messages[sender].append(msg)
                
                # List senders and their messages
                for sender, sender_msgs in sender_messages.items():
                    answer += f"**{sender}:**\n"
                    for msg in sender_msgs:
                        answer += f"  • {msg['message']}\n"
                    answer += "\n"
                return answer
            else:
                return f"No messages found for {requested_date}."
        else:
            return "Unable to parse the date from your question."
    
    # Time range questions (e.g., "from 3 pm to 8 pm")
    elif 'pm' in question_lower and ('from' in question_lower or 'between' in question_lower):
        # This would require more sophisticated time parsing
        return "I can see you're asking for a specific time range. Please use the time filters in the UI for more accurate results."
    
    # Topic/content questions
    elif any(word in question_lower for word in ['topic', 'discuss', 'about', 'content', 'summary', 'talk about', 'conversation']):
        if topic_messages:
            answer = "💬 **Main Discussion Topics:**\n\n"
            # Group messages by sender to show diverse content
            user_topics = {}
            for msg in topic_messages[:15]:
                user = msg['sender']
                if user not in user_topics:
                    user_topics[user] = []
                if len(user_topics[user]) < 4:  # Increased to 4 topics per user for better coverage
                    content = msg['message'][:120] + "..." if len(msg['message']) > 120 else msg['message']
                    user_topics[user].append({
                        'content': content,
                        'timestamp': msg['timestamp']
                    })
            
            topic_count = 1
            for user, topics in list(user_topics.items())[:min(8, len(user_topics))]:  # Dynamically show users based on content
                for topic in topics:
                    answer += f"**{topic_count}. {topic['timestamp']}**\n"
                    answer += f"👤 {user}: {topic['content']}\n\n"
                    topic_count += 1
                    if topic_count > 20:  # Increased to 20 topics total for better content coverage
                        break
                if topic_count > 20:
                    break
                    
            return answer
        else:
            return "The conversation appears to contain mostly brief exchanges."
    
    else:
        # General fallback with comprehensive overview
        answer = "📋 **Chat Overview:**\n\n"
        answer += f"• **{total_messages} messages** from **{user_count} users**\n"
        answer += f"• **Time Period**: {messages[0]['timestamp']} to {messages[-1]['timestamp']}\n"
        if meeting_messages:
            answer += f"• **{len(meeting_messages)} meetings** mentioned\n"
        if file_messages:
            answer += f"• **{len(file_messages)} files** shared\n"
        
        # Add user activity information
        if most_active_user:
            percentage = round((most_active_user[1]/total_messages)*100, 1)
            answer += f"• **Most Active User**: {most_active_user[0]} ({most_active_user[1]} messages, {percentage}% of total)\n"
        if least_active_user:
            percentage = round((least_active_user[1]/total_messages)*100, 1)
            answer += f"• **Least Active User**: {least_active_user[0]} ({least_active_user[1]} messages, {percentage}% of total)\n"
        
        return answer
