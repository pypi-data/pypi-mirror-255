import datetime
from rich.prompt import Prompt
from entsopy.utils.date import *


def input_date(
    time_type: str,
) -> str:
    """
    Prompts the user to input a start date and an end date with the specified time format.
    Validates that the end date is greater than the start date.
    Calculates the dates interval based on the input dates and time type.

    Args:
        time_type (str): The format of the dates to be inputted.
        time_range (str, optional): The range of time for the dates. Defaults to "".

    Returns:
        str: The calculated dates interval.
    """

    time_format = get_format(time_type)
    element = "start date"
    date_1 = str(
        Prompt.ask(
            f"Insert the [b gold1]{element}[/b gold1] with the format {time_type}",
        )
    ).lower()

    if time_format == "%Y-%W":
        time_format = "%Y-%W-%w"
        date_1 = date_1 + "-1"

    date_1 = datetime.datetime.strptime(date_1, f"{time_format}")
    date_2 = date_1 - datetime.timedelta(days=1)

    if time_format == "%Y-%W-%w":
        time_format = "%Y-%W"

    element = "end date"
    while date_2 < date_1:
        date_2 = str(
            Prompt.ask(
                f"Insert the [b gold1]{element}[/b gold1] with the format {time_type}",
            )
        ).lower()
        if time_format == "%Y-%W":
            time_format = "%Y-%W-%w"
            date_2 = date_2 + "-0"

        date_2 = datetime.datetime.strptime(date_2, f"{time_format}")

        if date_1 > date_2:
            print(
                f"[b red]The end date must be greater than the start date[/b red]. Please insert again the end date."
            )

    dates_interval = calculate_dates_interval(date_1, date_2, time_type)
    return dates_interval
