import logging
from logging.handlers import SysLogHandler

from watchsync.__version__ import APP_NAME

logger = logging.getLogger(APP_NAME)

formatter = logging.Formatter("%(name)s: %(levelname)s - %(message)s")
handler = SysLogHandler(address="/dev/log")
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)
