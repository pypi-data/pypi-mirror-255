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
import configparser

""" Main module of the app. """


app = typer.Typer(
    help="""Welcome to ENTSOPY your assistant for dowloading data from entso-e transparency platform.""",
)


@app.command(help="Start Entsopy App")
def start():
    try:
        
        package_directory = os.path.dirname(__file__)
        config_file_path = f"{package_directory}/conf.ini"

        config = configparser.ConfigParser()
        config.read(config_file_path)
        
        #check if conf.ini file exists
        if not os.path.exists(config_file_path):
            with open(config_file_path, "w") as file:
                file.write("# conf.ini file created")
        
        config = configparser.ConfigParser()
        config.read(config_file_path)
        
        # check if conf.ini file has the required sections   
        if config.has_section('configuration') == False:
            # create the configuration section
            config.add_section('configuration')
            with open(config_file_path, 'w') as configfile:
                config.write(configfile)


        # check if conf.ini file has the required "security_token" and "download_dir" keys
        token = None
        if config.has_option('configuration', 'security_token'):
            token = config.get('configuration', 'security_token')

        download_dir = None
        if config.has_option('configuration', 'download_dir'):
            download_dir = config.get('configuration', 'download_dir')


        if token is None:
            token = input_security_token()
            # save token to conf.ini file
            config.set('configuration', 'security_token', token)
            

        if download_dir is None:
            download_dir = input_download_directory()
            # save download_dir to conf.ini file
            config.set('configuration', 'download_dir', download_dir)
            
        with open(config_file_path, 'w') as configfile:
            config.write(configfile)
            
        client = HttpsClient(token)

        welcome_panel()

        domain = input_domain()
        
        res = home(client=client, domain=domain, download_dir=download_dir)
        
        print (f"res: {res}")

        if res:
            panel_success(file_name=res)
        else:
            panel_fail()

    except Exception as e:
        panel_fail("Error!", f"{e}\n{traceback.format_exc()}.")
        LOGGER.info(f"ERROR: {e}.\nTraceback: {traceback.format_exc()}")


@app.command(
    "reset",
    help="Reset the security token, target download directory or clear the log file. Args aviable: security-token, download-dir, log, all.",
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
    short_help="Show logs of the app",
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
