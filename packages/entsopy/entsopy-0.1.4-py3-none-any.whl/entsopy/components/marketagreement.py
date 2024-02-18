from rich.prompt import Prompt
from entsopy.utils.const import *
from entsopy.components.table import create_table
from rich import print
import json
from rich import print
from entsopy.utils.utils import extract_code_from_key


def input_market_agreement(is_type: bool = False) -> str:
    """
    Prompts the user to select a market agreement and returns the corresponding code.

    Args:
        is_type (bool, optional): Specifies whether the market agreement is of type or contract. Defaults to False.

    Returns:
        str: The code of the selected market agreement.
    """
    element = ""
    data = []
    if is_type:
        f = open(DIRS["type_market_agreement_type"], "r")
        element = "Type Market Agreement"
    else:
        f = open(DIRS["type_market_agreement_contract"], "r")
        element = "Contract Market Agreement"
    data = json.load(f)

    table = create_table(
        [f"{element.capitalize()}", "Code" "Key"],
        title=f"Select the [b]{element}[/b] of the data you want to download from the list below",
        rows=data,
    )
    print(table)

    selected_market_agreement = str(
        Prompt.ask(
            f"Insert the {element} you want to download data from\n",
            choices=[str(x["key"]) for x in data],
        )
    ).lower()

    market_agreement = extract_code_from_key(data, selected_market_agreement)

    return market_agreement
