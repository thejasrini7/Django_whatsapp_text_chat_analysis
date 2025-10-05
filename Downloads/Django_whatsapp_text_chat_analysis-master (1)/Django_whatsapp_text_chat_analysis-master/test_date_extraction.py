import re

def test_date_extraction(question):
    print(f"Testing date extraction for: {question}")
    
    # Look for date patterns (support multiple formats)
    date_patterns = [
        r'(\d{1,2})[/-](\d{1,2})[/-](\d{4})',  # DD/MM/YYYY or MM/DD/YYYY or DD-MM-YYYY
        r'(\d{1,2})[/-](\d{1,2})[/-](\d{2})',   # DD/MM/YY or MM/DD/YY or DD-MM-YY
    ]
    
    for pattern in date_patterns:
        match = re.search(pattern, question)
        if match:
            groups = match.groups()
            print(f"Pattern matched: {pattern}")
            print(f"Groups: {groups}")
            if len(groups) == 3:
                part1, part2, year = groups
                print(f"Parts: {part1}, {part2}, {year}")
                
                # Handle 2-digit years
                if len(year) == 2:
                    year = f"20{year}" if int(year) < 50 else f"19{year}"
                
                # For the format 7/02/2024, we need to determine if it's DD/MM/YYYY or MM/DD/YYYY
                # Let's use the same heuristic as in utils.py
                try:
                    a = int(part1)
                    b = int(part2)
                    if a > 12:
                        # First number > 12, so it must be DD/MM
                        day = part1
                        month = part2
                    elif b > 12:
                        # Second number > 12, so it must be MM/DD
                        month = part1
                        day = part2
                    else:
                        # Both <= 12, default to DD/MM (international format)
                        day = part1
                        month = part2
                except ValueError:
                    # If conversion fails, default to DD/MM
                    day = part1
                    month = part2
                
                print(f"Interpreted as: day={day}, month={month}, year={year}")
                
                # Validate the date parts
                try:
                    day_int = int(day)
                    month_int = int(month)
                    year_int = int(year)
                    
                    # Basic validation
                    if 1 <= day_int <= 31 and 1 <= month_int <= 12:
                        result = {
                            'date': f"{year_int}-{month_int:02d}-{day_int:02d}",
                            'type': 'specific_date'
                        }
                        print(f"Final result: {result}")
                        return result
                except ValueError:
                    # If conversion fails, continue to next pattern
                    continue
    
    print("No date found")
    return None

# Test with the problematic question
test_date_extraction("list the messages done on 7/02/2024")