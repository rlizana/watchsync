import logging
from logging.handlers import SysLogHandler
import os

from watchsync.__version__ import APP_NAME

logger = logging.getLogger(APP_NAME)

formatter = logging.Formatter("%(name)s: %(levelname)s - %(message)s")

try:
    if os.path.exists("/dev/log"):
        handler = SysLogHandler(address="/dev/log")
    else:
        raise OSError
except OSError:
    handler = logging.StreamHandler()

handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)
