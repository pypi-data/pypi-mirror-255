from rich.panel import Panel
from entsopy.utils.const import *
from rich import print


def panel_success(
    message: str = f"File [file_name] sucessfully downloaded", file_name: str = ""
) -> None:
    """
    Display a success message with an optional file name.

    Args:
        message (str): The success message to display. The placeholder [file_name] can be used to indicate where the file name should be inserted.
        file_name (str, optional): The name of the file that was successfully downloaded. Defaults to "".

    Returns:
        None
    """

    if file_name != "":
        message = message.replace("[file_name]", file_name)

    print(
        Panel(
            f"[b][green]{message}[/green][/b]",
            highlight=True,
        )
    )
    return
