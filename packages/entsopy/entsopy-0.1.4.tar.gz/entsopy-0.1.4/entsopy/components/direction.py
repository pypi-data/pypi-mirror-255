from rich.prompt import Prompt
from entsopy.utils.const import *
from entsopy.components.table import create_table
from rich import print
import json


def input_direction() -> str:
    """
    Prompts the user to select a direction from a list of options and returns the selected direction.

    Returns:
        str: The selected direction.
    """
    element = "Direction"
    data = json.load(open(DIRS["type_directions"], "r"))

    table = create_table(
        [f"{element}", "Code", "Key"],
        title=f"Select the [b]{element}[/b] of the data you want to download from the list below",
        rows=data,
    )
    print(table)

    direction = str(
        Prompt.ask(
            f"Insert the [b gold1]{element}[/b gold1] of the data you want to download",
            choices=[str(x["key"]) for x in data],
        )
    ).lower()

    return direction
