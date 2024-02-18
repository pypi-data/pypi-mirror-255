from rich.panel import Panel
from rich import print


def panel_fail(
    message: str = "Something went wrong, file not downloaded",
    error_description: str = "No error description provided",
) -> None:
    """
    Display a failure panel with the provided message and error description.

    Args:
        message (str, optional): The message to display in the failure panel. Defaults to "Something went wrong, file not downloaded".
        error_description (str, optional): The description of the error. Defaults to "No error description provided".

    Returns:
        None
    """

    print(
        Panel(
            f"[b][red]{message}...[/red][/b]\nError: {error_description}.\n",
            title="[b][red]FATAL ERROR![/red][/b]",
            highlight=True,
            title_align="center",
        )
    )
    return
