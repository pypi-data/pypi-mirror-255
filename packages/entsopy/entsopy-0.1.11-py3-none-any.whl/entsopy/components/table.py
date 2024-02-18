from rich.table import Table


def create_table(
    headers: list,
    title: str,
    rows: list,
) -> Table:
    """
    Create a table with the given headers, title, and rows.

    Args:
        headers (list): The list of column headers.
        title (str): The title of the table.
        rows (list): The list of rows, where each row is a dictionary.

    Returns:
        Table: The created table.

    """
    table = Table(
        *headers, expand=True, title=title, title_style="yellow bold", show_lines=True
    )

    for row in rows:
        table.add_row(
            row["name"],
            row["code"] if "code" in row else "",
            row["key"]
            if "is_available" in row and row["is_available"] == True
            else (row["key"] if "is_available" not in row else ":x:"),
        )

    return table
