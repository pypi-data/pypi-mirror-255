import logging
from entsopy.utils.const import *

logging.basicConfig(
    filename=DIRS["log"],
    format="[%(asctime)s] %(message)s",
    filemode="a+",
    force=True,
)
LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)
