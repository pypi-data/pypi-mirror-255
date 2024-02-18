import sys
from datetime import datetime

log_file = "log.txt"

def log(message, category):
    caller = sys._getframe().f_back.f_code.co_name # Get the name of the function that called the logger.

    # Get the current timestamp.
    timestamp = datetime.now()
    timestamp_iso8601 = timestamp.strftime('%Y-%m-%dT%H:%M:%S.%f%z')

    # Add a "icon" that quickly accustoms the user to a logcategory, using a switch-case style solution.
    category_dict = {
        'warning': '[!?]',
        'error': '[!]',
        'info': '[i]',
        'debug': '[D]',
        'data': '[-]',
    }
    category_icon = category_dict.get(category, category)
    
    # Log to file:
    logfile_appender = open(log_file, "a")
    logfile_appender.write(f"{timestamp_iso8601} {category_icon} '{caller}': {message}" )

    # Log to screen:
    print(f"{timestamp} {category_icon} '{caller}': {message}" )