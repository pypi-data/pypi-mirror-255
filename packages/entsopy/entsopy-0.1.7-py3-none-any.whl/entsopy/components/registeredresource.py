from rich.prompt import Prompt
from entsopy.utils.const import *
from entsopy.components.table import create_table
from rich import print
from rich import print


def input_registeredsource() -> str:
    """
    Prompts the user to input the EIC code of the Registered Resource they want to download data from.

    Returns:
        str: The EIC code of the Registered Resource.
    """
    element = "EIC code"
    data = []

    ask_text = (
        f"Insert the [b gold1]{element}[/b gold1] of the Registered Resource you want to download data from\n. \nYou can find the list of approved EIC codes here: [link=https://www.entsoe.eu/data/energy-identification-codes-eic/eic-approved-codes/]entsoe.eu/data/energy-identification-codes-eic/eic-approved-codes[/link]",
    )

    registered_source = str(Prompt.ask(ask_text)).lower()

    return registered_source
