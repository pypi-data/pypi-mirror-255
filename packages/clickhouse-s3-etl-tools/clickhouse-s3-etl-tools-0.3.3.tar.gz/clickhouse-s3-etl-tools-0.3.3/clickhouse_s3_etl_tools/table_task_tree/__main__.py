import logging

from clickhouse_s3_etl_tools.logger import setup_applevel_logger
from clickhouse_s3_etl_tools.table_task_tree.config_module import get_configuration
from clickhouse_s3_etl_tools.table_task_tree.clickhouse_dependency_tree_builder import (
    get_dict_dependencies,
)
from clickhouse_s3_etl_tools.table_task_tree.tree_drawer import (
    print_dependency_tree,
    generate_tree,
)
from clickhouse_s3_etl_tools.schema.schema_dependency_tree import DependencyTreeConfig
from clickhouse_s3_etl_tools.utils import save_dict_as_json


def run_service():
    config: DependencyTreeConfig = get_configuration()

    logger: logging.Logger = setup_applevel_logger(config.LOG_LEVEL)
    logger.info("Logger inited")
    logger.debug("App created")
    databases: list[str] = config.DATABASES.split(",") if config.DATABASES else []
    tables: list[str] = config.TABLES.split(",") if config.TABLES else []
    excluded_databases: list[str] = (
        config.EXCLUDED_DATABASES.split(",") if config.EXCLUDED_DATABASES else []
    )
    parents_by_id, tables = get_dict_dependencies(
        config.CH_URL, databases, excluded_databases, tables, config.IGNORE_VALIDATION
    )
    logger.info(f"A number of table is {len(tables)}")
    if config.FILE_OUTPUT:
        save_dict_as_json(parents_by_id, config.FILE_OUTPUT)
    print_dependency_tree(generate_tree(parents_by_id)[0])
    logger.debug("App finished")


if __name__ == "__main__":
    run_service()
