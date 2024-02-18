from rich.prompt import Prompt
from entsopy.utils.const import *
from entsopy.components.table import create_table
from rich import print
import json
from rich import print
from entsopy.utils.utils import extract_code_from_key


def input_market_product(is_standard: bool = True) -> str:
    """
    Prompts the user to select a market product and returns the corresponding code.

    Args:
        is_standard (bool, optional): Specifies whether the market product is standard or original. Defaults to True.

    Returns:
        str: The code of the selected market product.
    """

    element = ""
    data = []
    if is_standard:
        element = "Standard Market Product"
    else:
        element = "Original Market Product"
    data = json.load(open(DIRS["type_market_product"], "r"))

    table = create_table(
        [f"{element.capitalize()}", "Code" "Key"],
        title=f"Select the [b]{element}[/b] of the data you want to download from the list below",
        rows=data,
    )
    print(table)

    selected_market_product = str(
        Prompt.ask(
            f"Insert the {element} you want to download data from\n",
            choices=[str(x["key"]) for x in data],
        )
    ).lower()

    market_product = extract_code_from_key(data, selected_market_product)

    return market_product
