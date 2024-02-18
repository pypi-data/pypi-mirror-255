from rich import print
from tkinter import filedialog


def input_download_directory() -> str:
    """
    Prompts the user to choise a directory in which downloaded files will be saved.

    Returns:
        str: The directory choosed by the user.
    """

    dir = None

    while not dir:
        print(
            "Please select a [b]directory[/b] in which downloaded files will be saved."
        )
        dir = filedialog.askdirectory()
        if not dir:
            print(
                f"The [red][b]selected directory is not valid[/red][/b] ({dir}). Please try again."
            )

    return dir
