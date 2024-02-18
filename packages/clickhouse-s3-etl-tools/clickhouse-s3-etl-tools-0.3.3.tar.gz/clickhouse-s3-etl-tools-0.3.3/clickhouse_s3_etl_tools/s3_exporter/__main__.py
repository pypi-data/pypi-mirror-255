import logging

from clickhouse_s3_etl_tools.logger import setup_applevel_logger
from clickhouse_s3_etl_tools.s3_exporter.config_module import get_configuration
from clickhouse_s3_etl_tools.s3_exporter.s3_exporter import export_to_s3


def run_service():
    config = get_configuration()

    logger: logging.Logger = setup_applevel_logger(config.LOG_LEVEL)
    logger.info("Logger inited")
    logger.debug("App created")
    export_to_s3(config)
    logger.debug("App finished")


if __name__ == "__main__":
    run_service()
