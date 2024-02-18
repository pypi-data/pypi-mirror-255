import datetime
from matplotlib.dates import relativedelta


def check_date_not_tomorrow(date: datetime.datetime) -> bool:
    """
    Check if the given date is not tomorrow.

    Args:
        date (datetime.datetime): The date to check.

    Returns:
        bool: True if the date is not tomorrow, False otherwise.
    """
    today = datetime.datetime.today()
    if date > today:
        return False
    else:
        return True


def is_dates_diff_more_than_one_year(
    date1: datetime.datetime, date2: datetime.datetime
) -> bool:
    """
    Check if the difference between two dates is more than one year.

    Args:
        date1 (datetime.datetime): The first date.
        date2 (datetime.datetime): The second date.

    Returns:
        bool: True if the difference is more than one year, False otherwise.
    """
    if date2 - date1 > datetime.timedelta(days=365):
        return True
    else:
        return False


def calculate_dates_interval(
    date1: datetime.datetime, date2: datetime.datetime, time_type: str
) -> str:
    """
    Calculate the interval between two dates based on the given time type.

    Args:
        date1 (datetime.datetime): The first date.
        date2 (datetime.datetime): The second date.
        time_type (str): The type of time interval to calculate.

    Returns:
        str: The calculated time interval.
    """
    start_day = date1.strftime("%Y-%m-%d")

    if time_type == "yyyy-mm-dd":
        end_day = date2.strftime("%Y-%m-%d")
        time_interval = f"{start_day}T00:00Z/{end_day}T23:00Z"

    elif time_type == "yyyy-W":
        end_day = date2.strftime("%Y-%m-%d")
        time_interval = f"{start_day}T00:00Z/{end_day}T23:00Z"

    elif time_type == "yyyy-mm":
        end_day = (date2 + relativedelta(day=31)).strftime("%Y-%m-%d")
        start_day = (date1 - relativedelta(day=1)).strftime("%Y-%m-%d")
        time_interval = f"{start_day}T23:00Z/{end_day}T23:00Z"

    elif time_type == "yyyy":
        end_day = (date2 + relativedelta(yearday=365)).strftime("%Y-%m-%d")
        time_interval = f"{start_day}T23:00Z/{end_day}T23:00Z"

    return time_interval


def get_interval(date1: datetime.datetime, date2: datetime.datetime) -> str:
    """
    Get the interval between two dates in a specific format.

    Args:
        date1 (datetime.datetime): The first date.
        date2 (datetime.datetime): The second date.

    Returns:
        str: The interval between the two dates.
    """
    tmp_date1 = date1.strftime("%Y-%m-%dT%H:%MZ")
    tmp_date2 = date2.strftime("%Y-%m-%dT%H:%MZ")
    date = f"{tmp_date1}/{tmp_date2}"
    return date


def split_interval(interval: str) -> tuple:
    """
    Split the interval string into two datetime objects.

    Args:
        interval (str): The interval string.

    Returns:
        tuple: A tuple containing the two datetime objects.
    """
    dates = interval.split("/")
    date1 = datetime.datetime.strptime(dates[0], "%Y-%m-%dT%H:%MZ")
    date2 = datetime.datetime.strptime(dates[1], "%Y-%m-%dT%H:%MZ")
    return date1, date2


def get_format(time_type: str) -> str:
    """
    Get the date format based on the given time type.

    Args:
        time_type (str): The type of time interval.

    Returns:
        str: The date format.
    """
    time_format = ""
    if time_type == "yyyy-mm-dd":
        time_format = "%Y-%m-%d"
    elif time_type == "yyyy-W":
        time_format = "%Y-%W"
    elif time_type == "yyyy-mm":
        time_format = "%Y-%m"
    elif time_type == "yyyy-w":
        time_format = "%Y-%W"
    else:
        time_format = "%Y"

    return time_format


def date_diff(date1: datetime.datetime, date2: datetime.datetime) -> int:
    """
    Calculate the difference in days between two dates.

    Args:
        date1 (datetime.datetime): The first date.
        date2 (datetime.datetime): The second date.

    Returns:
        int: The difference in days.
    """
    diff = date2 - date1
    return diff.days


def get_week_boundrais(date: datetime.datetime, week_number: int) -> tuple:
    # calculate boundrais of the week_number-th week of the year
    year = date.year
    week = week_number
    initial_time_start = f"{year}-{week}-1"
    final_time_start = f"{year}-{week}-0"

    week_start = datetime.datetime.strptime(initial_time_start, "%Y-%W-%w")
    week_end = datetime.datetime.strptime(final_time_start, "%Y-%W-%w")

    return week_start, week_end


def count_weeks(start_date, end_date):
    """
    Counts the number of weeks between two dates.

    Args:
    start_date (datetime): The start date.
    end_date (datetime): The end date.

    Returns:
    int: The number of weeks between the two dates.
    """
    # Calculate the difference between the two dates
    delta = end_date - start_date

    # Divide the difference in days by 7 and round up to the nearest whole number
    number_of_weeks = (
        delta.days + 6
    ) // 7  # Adding 6 ensures that partial weeks are counted as full weeks

    return number_of_weeks
