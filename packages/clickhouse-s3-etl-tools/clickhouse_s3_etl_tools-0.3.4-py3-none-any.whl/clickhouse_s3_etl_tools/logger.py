import logging
import sys
from typing import Union

from clickhouse_s3_etl_tools import APP_LOGGER_NAME


def setup_applevel_logger(
    log_level: str, file_name: Union[str, None] = None
) -> logging.Logger:
    logger = logging.getLogger(APP_LOGGER_NAME)
    logger.setLevel(log_level)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)
    logger.handlers.clear()
    logger.addHandler(stream_handler)
    if file_name:
        file_handler = logging.FileHandler(file_name)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


def get_logger(module_name: str) -> logging.Logger:
    logger = logging.getLogger(APP_LOGGER_NAME).getChild(module_name)

    # Set propagate to False to avoid duplicate log messages

    return logger
