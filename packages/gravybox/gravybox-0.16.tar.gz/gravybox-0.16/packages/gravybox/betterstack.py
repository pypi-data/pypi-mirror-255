import logging
import os

from logtail import LogtailHandler

LOGGER_IS_NOT_INITIALIZED = True


def collect_logger():
    logger = logging.getLogger(__name__)
    global LOGGER_IS_NOT_INITIALIZED
    if LOGGER_IS_NOT_INITIALIZED:
        LOGGER_IS_NOT_INITIALIZED = False
        source_token = os.getenv("SOURCE_TOKEN")
        if source_token is None:
            logger.info("initialized local logger")
        else:
            handler = LogtailHandler(source_token=source_token)
            logger.setLevel(logging.INFO)
            log_format = logging.Formatter("%(message)s")
            handler.setFormatter(log_format)
            logger.handlers = []
            logger.addHandler(handler)
            logger.info("initialized betterstack logger")
    return logger
