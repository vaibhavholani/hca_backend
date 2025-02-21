from dateutil import parser
from datetime import datetime

def parse_date(date_string, day_first=None):
    """Parses a date string or datetime object and returns a datetime; prints an error if parsing fails."""
    if type(date_string) == datetime:
        return date_string
    try:
        parsed_date = parser.parse(date_string, dayfirst=day_first)
        return parsed_date
    except Exception as e:
        print('Error parsing date:', e)
        return None

def sql_date(date: datetime):
    """Formats a datetime object into a SQL date string in the format YYYY-MM-DD."""
    return date.strftime('%Y-%m-%d')

def user_date(date: datetime):
    """Formats a datetime object into a user-friendly date string in the format DD/MM/YYYY."""
    return date.strftime('DD/MM/YYYY')