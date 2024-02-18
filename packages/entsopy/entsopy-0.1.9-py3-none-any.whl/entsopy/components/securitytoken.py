from rich.prompt import Prompt


def input_security_token() -> str:
    """
    Prompts the user to input a security token and saves it in a .env file.

    Returns:
        str: The security token inserted by the user.
    """

    security_token = str(
        Prompt.ask(
            f"Insert your security token. You can ask for one at [link=https://transparency.entsoe.eu/content/static_content/Static%20content/web%20api/Guide.html#_authentication_and_authorisation]this link[/link]",
        )
    ).lower()

    return security_token
