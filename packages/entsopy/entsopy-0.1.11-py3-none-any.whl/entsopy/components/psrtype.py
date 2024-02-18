from rich.prompt import Prompt
from entsopy.components.table import create_table
import json
from rich import print
from entsopy.utils.const import *
from entsopy.utils.utils import extract_code_from_key
from importlib import resources

def input_psrtype() -> str:
    """
    Prompts the user to select a PsrType from a list of options and returns the selected PsrType.

    Returns:
        str: The selected PsrType.
    """

    element = "PsrType"
    data = json.load(resources.open_text("entsopy.data.types", "psrtypes.json"))

    table = create_table(
        [f"{element}", "Code", "Key"],
        title=f"Select the [b]{element}[/b] of the data you want to download from the list below",
        rows=data,
    )
    print(table)

    selected_psr_type = str(
        Prompt.ask(
            f"Insert the [b gold1]{element}[/b gold1] of the data you want to download",
            choices=[str(x["key"]) for x in data],
        )
    ).lower()

    psr_type = extract_code_from_key(data, selected_psr_type)

    return psr_type
