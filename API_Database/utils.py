from dateutil import parser
from datetime import datetime

def parse_date(date_string):

    if type(date_string) == datetime:
        return date_string
    
    try:
        parsed_date = parser.parse(date_string)
        return parsed_date
    except Exception as e:
        print("Error parsing date:", e)
        return None