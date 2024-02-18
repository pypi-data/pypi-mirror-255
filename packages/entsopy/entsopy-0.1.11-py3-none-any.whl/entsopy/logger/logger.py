import logging
from entsopy.utils.const import *
import os
from importlib import resources

# check if the log file exists, if not create it and write an empty string
if not os.path.exists(DIRS["log"]):
    with open(DIRS["log"], "w") as file:
        file.write("")

logging.basicConfig(
    filename=DIRS["log"],
    format="[%(asctime)s] %(message)s",
    filemode="a+",
    force=True,
)
LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)
