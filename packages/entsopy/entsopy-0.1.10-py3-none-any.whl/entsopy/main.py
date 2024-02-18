import os
from typing import Annotated
import typer
from entsopy.components.panels.fail import panel_fail
from entsopy.components.panels.success import panel_success
from entsopy.components.welcome import welcome_panel
from entsopy.components.domain import input_domain
from entsopy.components.home import home
from entsopy.components.welcome import welcome_panel
import dotenv
from entsopy.components.securitytoken import input_security_token
from entsopy.components.logging.logtable import logtable
from entsopy.utils.const import *
from entsopy.components.downloaddirectory import input_download_directory
from entsopy.utils.utils import is_debug_active
from entsopy.logger.logger import LOGGER
from entsopy.classes.httpsclient import HttpsClient
import traceback

""" Main module of the app. """


app = typer.Typer(
    help="""Welcome to ENTSOPY your assistant for dowloading data from entso-e transparency platform.""",
)


@app.command(help="Start Entsopy Cli app.")
def start():
        
    print("10 entsopy cli app started.")
    
    try:
        env_file_path = ".env"
        if not os.path.exists(env_file_path):
            with open(env_file_path, "w") as file:
                file.write("# .env file created")
                print("10.1 .env file created")

        dotenv_file = dotenv.find_dotenv()
        dotenv.load_dotenv(dotenv_file)

        token = "a364d79f-a534-4aea-b0db-c76565e74d06"
        download_dir = ""
        
        # if token is None:
        #     token = input_security_token()
        #     os.environ["SECURITY_TOKEN"] = f"${token}"
        #     dotenv.set_key(dotenv_file, "SECURITY_TOKEN", os.environ["SECURITY_TOKEN"])

        # if download_dir is None:
        #     download_dir = input_download_directory()
        #     os.environ["DOWNLOAD_DIR"] = f"{download_dir}"
        #     dotenv.set_key(dotenv_file, "DOWNLOAD_DIR", os.environ["DOWNLOAD_DIR"])

        client = HttpsClient(token)

        welcome_panel()

        domain = input_domain()

        res = home(client=client, domain=domain, download_dir=download_dir)

        if res:
            panel_success(file_name=res)
        else:
            panel_fail()

    except Exception as e:
        panel_fail("Error!", f"{e}. \n \n {traceback.format_exc()}")
        LOGGER.info(f"ERROR: {e}.\nTraceback: {traceback.format_exc()}")


@app.command(
    "reset",
    help="Reset the security token, target download directory or clear the log file.\nArgs aviable: security-token, download-dir, log, all.",
)
def reset(
    command: Annotated[
        str,
        typer.Argument(help="The name of reset action to perform."),
    ] = "",
):
    if command == "security-token" or command == "all":
        input_security_token()
        panel_success("Security token successfully replaced and log file cleared.")
    elif command == "download-dir" or command == "all":
        os.environ["DOWNLOAD_DIR"] = ""
        panel_success("Download directory successfully reset.")
    elif command == "log" or command == "all":
        open(DIRS["log"], "w").close()
        panel_success("Log file succesfully cleared")
    else:
        panel_fail("Command not recognized. Type reset --help for more info.")


@app.command(
    "log",
    help="Manage logs. Args aviable: show, clear.",
)
def log(
    command: Annotated[
        str,
        typer.Argument(help="The name of thea action to perform related to logs."),
    ] = "show",
):
    if command == "clear":
        open(DIRS["log"], "w").close()
        panel_success("Log file cleared")
    else:
        logtable("log")


if __name__ == "__main__":
    if is_debug_active():
        typer.run(start)
    else:
        app()
