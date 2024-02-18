import json
from rich.prompt import Prompt
from entsopy.components.table import create_table
from entsopy.utils.const import *
from rich import print
from importlib import resources
import os


def input_domain() -> str:
    """
    Prompts the user to select a domain from a list and returns the selected domain.

    Returns:
        str: The selected domain.
    """

    element = "domain"
    data = []
    data = json.load(resources.open_text("entsopy.data.types", "domains.json"))

    table = create_table(
        ["Domain", "Code", "Key to press"],
        title=f"Select the [b gold1]{element}[/b gold1] of the data you want to download from the list below",
        rows=data,
    )
    print(table)

    domain = str(
        Prompt.ask(
            f"Insert the [b gold1]{element}[/b gold1] you want to download data from\n",
            choices=[str(x["key"]) for x in data],
        )
    ).lower()

    return domain
