from datetime import datetime

# Module to convert datetime string from database to string in NZ format

def datetime_to_nz(datetime_dt):
    return datetime_dt.strftime('%d %B %Y %I:%M %p')