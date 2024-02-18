from typing import List, Any
import typer
from entsopy.utils.const import *
from entsopy.components.table import create_table
from rich import print
import json
from rich.prompt import Prompt


def input_areas(area: str) -> list[Any]:
    """
    Prompts the user to input areas based on the given area type.

    Args:
        area (str): The type of area to select.

    Returns:
        list[Any]: A list of selected areas.

    """
    end = False
    selected_areas = []
    element = ""
    areas = []

    if area == "CTA":
        f = open(DIRS["areas_control_area"], "r")
        element = "control area"
    elif area == "BZN":
        f = open(DIRS["areas_bidding_zone"], "r")
        element = "bidding zone"
    elif area == "BZNS":
        f = open(DIRS["areas_border_bidding_zone"], "r")
        element = "border bidding zone"
    elif area == "MBAS":
        f = open(DIRS["areas_border_market_balancing_area"], "r")
        element = "border market balance area"

    areas = json.load(f)

    table = create_table(
        [f"{element.capitalize()}", "Code", "Key"],
        title=f"Select the [b]{element}[/b] of the data you want to download from the list below",
        rows=areas,
    )
    print(table)

    while not end:
        key = str(
            Prompt.ask(
                f"Insert the [b gold1]{element}[/b gold1] of the data you want to download",
                choices=[str(x["key"]) for x in areas],
            )
        ).lower()

        for area in areas:
            if key == area["key"]:
                tmp_area = area

        if tmp_area:
            selected_areas.append(tmp_area)
            areas = [area for area in areas if area["key"] != tmp_area["key"]]

            if len(areas) > 0:
                end = not (typer.confirm(f"Do you want to add another {element}?"))

                if not end:
                    table = create_table(
                        ["Control Area", "Code"],
                        title=f"Select one of the remaining {element} of the data you want to download from the list below",
                        rows=areas,
                    )
            else:
                print(f"No more {element}s available !")
                end = True

        else:
            print(
                f"[b][red]The {element} you inserted is not available![/red][b] Insert another one."
            )

    return selected_areas
