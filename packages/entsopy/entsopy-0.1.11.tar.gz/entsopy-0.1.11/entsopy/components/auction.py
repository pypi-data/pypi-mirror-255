from entsopy.utils.const import *
from entsopy.components.table import create_table
from rich import print
import json
from rich.prompt import Prompt
from entsopy.utils.utils import extract_code_from_key
from importlib import resources


def input_auction_type(is_category: bool = False) -> str:
    element = "Auction Type"
    if is_category:
        f = resources.open_text("entsopy.data.types", "auctions_type.json")
        element = "Auction Category"
    else:
        f = resources.open_text("entsopy.data.types", "auctions_category.json")
        element = "Auction Type"

    data = json.load(f)

    table = create_table(
        [f"{element}", "Code", "Key"],
        title=f"Select the [b]{element}[/b] of the data you want to download from the list below",
        rows=data,
    )
    print(table)

    selected_auction = str(
        Prompt.ask(
            f"Insert the [b gold1]{element}[/b gold1] of the data you want to download",
            choices=[str(x["key"]) for x in data],
        )
    ).lower()

    auction = extract_code_from_key(data, selected_auction)
    return auction
