import calendar
from datetime import datetime, date, timedelta 
from dateutil.relativedelta import relativedelta
import time

def date1_less_than_date2(date1: str, date2: str) -> bool:
    """
        Input: date string in the format yyyymmdd
        Output: bool
    """
    d1 = datetime.strptime(date1, "%Y%m%d")
    d2 = datetime.strptime(date2, "%Y%m%d")
    return d1 < d2

def get_next_date(d: str) -> str:
    """
        Input: date string in the format yyyymmdd
        Output: day after the input date in yyyymmdd format
    """

    # Parse incoming date string
    dt = datetime.strptime(d, "%Y%m%d")
    # Add one day
    next_dt = dt + timedelta(days=1)
    # Return in the same format
    return next_dt.strftime("%Y%m%d")

def last_date_of_current_month() -> str:
    """
        Returns the date of the last day of the current month as a str in YYYYMMDD format 
    """
    today = date.today()
    year = today.year
    month = today.month
    last_day = calendar.monthrange(year, month)[1]
    last_date = date(year, month, last_day)

    return last_date.strftime("%Y%m%d")

def last_day_of_current_year() -> date:
    """
        Output: a Date object representing the last date of the current year
    """
    today = date.today()
    # last day of current year is always 12/31, duh
    last_day = date(today.year, 12, 31)
    return last_day

