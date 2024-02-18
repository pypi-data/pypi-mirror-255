from rich.table import Table
from rich import print
from entsopy.utils.const import *
from entsopy.components.panels.fail import panel_fail


def logtable(
    filename: str,
) -> None:
    name = DIRS[f"{filename}"]
    rows = open(name, "r").readlines()

    if len(rows) <= 0:
        panel_fail(
            "No logs found...",
            f"Please make sure you have downloaded some data.",
        )
        return None

    else:
        table = Table(
            title="LOG FILE",
            expand=True,
            title_style="yellow bold",
            show_lines=True,
        )
        table.add_column("Date", justify="left")
        table.add_column("API Call", justify="left")

        for row in rows:
            date, api_call = row.split("] ")
            date = date.replace("[", "")
            api_call = api_call.replace("GET: ", "")
            table.add_row(date, api_call)

        print(table)
