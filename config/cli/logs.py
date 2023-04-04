import logging
import logging.handlers
import sys


def _get_app_logger():
    logger = logging.getLogger("neoteroi-conf")
    logger.setLevel(logging.INFO)
    logger.addHandler(logging.StreamHandler(sys.stdout))
    return logger


logger = _get_app_logger()
