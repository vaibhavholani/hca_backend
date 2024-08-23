from dateutil import parser
from datetime import datetime
     

def parse_date(date_string, day_first=None):

    if type(date_string) == datetime:
        return date_string
    
    try:
        parsed_date = parser.parse(date_string, dayfirst=day_first)
        return parsed_date
    except Exception as e:
        print("Error parsing date:", e)
        return None

def sql_date(date: datetime):
        return date.strftime("%Y-%m-%d")

def user_date(date: datetime):
        return date.strftime("DD/MM/YYYY")