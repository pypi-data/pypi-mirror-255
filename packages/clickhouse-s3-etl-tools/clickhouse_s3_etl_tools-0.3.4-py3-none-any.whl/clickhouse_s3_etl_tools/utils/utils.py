import json
import re
import time
from typing import Tuple

import sqlparse
from clickhouse_s3_etl_tools.logger import get_logger
from clickhouse_s3_etl_tools.schema.schema_configs import (
    TableConfiguration,
    Configuration,
)
from clickhouse_s3_etl_tools.schema.schema_table_metadata import MetadataConfig
from clickhouse_s3_etl_tools.exceptions.exception import RowsMismatchError

logger = get_logger(__name__)


def save_dict_as_json(dictionary, file_path):
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(dictionary, file, indent=4, ensure_ascii=False)


def get_metadata_file_name(config: Configuration) -> str:
    return f"__metadata__{config.table.TABLE_NAME}.parquet"


def get_partition_export_file_name(config: Configuration, _partition_id: str) -> str:
    return f"{config.table.TABLE_NAME}{_partition_id}.parquet"


def get_full_table_export_file_name(config: Configuration) -> str:
    return f"{config.table.TABLE_NAME}_all.parquet"


def get_partition_from_export_file_name(config: Configuration, file_name) -> str:
    return file_name.replace(config.table.TABLE_NAME, "").replace(".parquet", "")


def get_partition_key(config: Configuration, metadata: MetadataConfig) -> str:
    return config.PARTITION_KEY if config.PARTITION_KEY else metadata.partition_key


def check_rows_mismatch(
        s3_row_count: int,
        clickhouse_row_count: int,
        max_percentage_diff: float,
        is_export: bool = True,
) -> None:
    """
     Check if there is a mismatch in the number of rows between ClickHouse and S3.

     Parameters:
     - s3_row_count (int): The number of rows in S3.
     - clickhouse_row_count (int): The total number
     Raises:
    - RowsMismatchError: If the conditions for row mismatch are met.
    """

    row_difference: int = abs((s3_row_count - clickhouse_row_count))

    if s3_row_count == clickhouse_row_count:
        mismatch_percentage = 0
    elif is_export:
        mismatch_percentage = (
            row_difference / s3_row_count * 100 if s3_row_count != 0 else 100
        )
    else:
        mismatch_percentage = (
            row_difference / clickhouse_row_count * 100
            if clickhouse_row_count != 0
            else 100
        )

    if mismatch_percentage > max_percentage_diff:
        raise RowsMismatchError(
            s3_row_count, clickhouse_row_count, max_percentage_diff, mismatch_percentage
        )


def prettify_sql(sql_query):
    parsed = sqlparse.format(sql_query, reindent=True)
    return parsed


def timing_decorator(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        logger.info(
            f"Execution started at {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start_time))}"
        )

        result = func(*args, **kwargs)

        end_time = time.time()
        logger.info(
            f"Execution finished at {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(end_time))}"
        )

        execution_time = end_time - start_time
        hours, remainder = divmod(execution_time, 3600)
        minutes, seconds = divmod(remainder, 60)
        milliseconds = (execution_time - int(execution_time)) * 1000

        logger.info(
            f"Total execution time: {int(hours)}h {int(minutes)}m {int(seconds)}s {int(milliseconds)}ms"
        )

        return result

    return wrapper


def update_create_table_query(
        create_table_query: str,
        table: TableConfiguration,
        cluster_name: str = None,
        databases_map: str = None,
        engine_full_to_replace: Tuple[str, str] = None,
) -> str:
    logger.debug(engine_full_to_replace)
    logger.debug(engine_full_to_replace or "" != "")
    if engine_full_to_replace or "" != "":
        create_table_query = create_table_query.replace(
            engine_full_to_replace[0], engine_full_to_replace[1]
        )

    create_table_query = create_table_query.replace(
        f"{table.DATABASE}.", f"{table.DATABASE_DESTINATION}."
    )

    def _replace_databases(query: str) -> str:
        if databases_map:
            placeholders: list[Tuple] = [
                (f"{db.split(':')[0]}.", f"{db.split(':')[1]}.")
                for db in databases_map.split(",")
            ]
            for placeholder, replacement in placeholders:
                query = query.replace(placeholder, replacement)

        return query

    def _replace_on_cluster(query: str) -> str:
        placeholders = [
            (
                f"{table.DATABASE_DESTINATION}.{table.TABLE_NAME}",
                Configuration._get_on_cluster(cluster_name),
            ),
            (
                f"{table.DATABASE_DESTINATION}.`{table.TABLE_NAME}`",
                Configuration._get_on_cluster(cluster_name),
            ),
        ]

        for placeholder, replacement in placeholders:
            query = query.replace(placeholder, f"{placeholder} {replacement}", 1)

        return query

    def _replace_replicated_engine(create_table_query):
        pattern = r"(.*?)Replicated([A-Za-z0-9]*)MergeTree(.*?)"
        replacement = r"\1\2MergeTree\3"
        result = re.sub(pattern, replacement, create_table_query)
        return result

    def _add_replicated_to_engine(create_table_query):
        pattern = r"(\b(?:Aggregating|Collapsing|Replacing|VersionedCollapsing|Graphite|Summing)?MergeTree)\((.*?)\)"

        def repl(match):
            engine, args = match.groups()
            return f"Replicated{engine}({args})"

        return re.sub(pattern, repl, create_table_query)

    def _replace_merge_tree(query: str) -> str:
        if "CollapsingMergeTree" in query:
            pattern = (
                r"CollapsingMergeTree\((.*?)\s*(?:,\s*[^,\n]+\s*)*?,\s*([^,\n]+)\s*\)"
            )
            repl = r"CollapsingMergeTree(\2)"
        elif "ReplacingMergeTree" in query:
            pattern = (
                r"ReplacingMergeTree\((.*?)\s*(?:,\s*[^,\n]+\s*)*?,\s*([^,\n]+)\s*\)"
            )
            repl = r"ReplacingMergeTree(\2)"
        else:
            pattern = r"MergeTree\([^)]*\)"
            repl = "MergeTree()"

        query = re.sub(pattern, repl, query)

        if not cluster_name:
            logger.debug(query)
            query = _replace_replicated_engine(query)

        return query

    if cluster_name:
        create_table_query = _replace_on_cluster(create_table_query)
        if "Replicated" not in create_table_query:
            create_table_query = _add_replicated_to_engine(create_table_query)
    if databases_map:
        create_table_query = _replace_databases(create_table_query)

    create_table_query = _replace_merge_tree(create_table_query)
    if cluster_name and not re.search(r"MergeTree\([^)]*\)", create_table_query):
        create_table_query = create_table_query.replace(
            "MergeTree", "ReplicatedMergeTree()"
        )

    return create_table_query


def build_where_condition(config: Configuration, partition_key: str) -> str:
    logger.debug(f"config.PARTITION_VALUE_FROM {config.PARTITION_VALUE_FROM}")
    if (partition_key or "tuple()" != "tuple()") and config.PARTITION_VALUE_FROM:
        return f" WHERE {partition_key} >= '{config.PARTITION_VALUE_FROM}'"
    else:
        return ""


def build_where_condition_s3(config: Configuration, partition_key: str) -> str:
    file_from: str = get_partition_export_file_name(config, config.PARTITION_VALUE_FROM)

    if (partition_key or "tuple()" != "tuple()") and config.PARTITION_VALUE_FROM:
        return f" WHERE _file >= '{file_from}'"
    else:
        return ""


def build_s3_path(config: Configuration, filename: str) -> str:
    return f"{config.s3.PATH_S3}/{config.table.DATABASE}/{config.table.TABLE_NAME}/{filename}"


def build_s3_source(config: Configuration, filename: str) -> str:
    """
    Build the S3 source path or S3 Cluster source based on the configuration.

    Args:
        config (Configuration): The configuration object.
        filename (str): The filename for the S3 source.

    Returns:
        str: The constructed S3 source path or S3 Cluster source.
    """
    s3_path = build_s3_path(config, filename)
    if config.USE_S3_CLUSTER:
        return f"""s3Cluster(
        '{config.CLUSTER_NAME}',
        '{s3_path}',
        '{config.s3.S3_ACCESS_KEY}',
        '{config.s3.S3_SECRET_KEY}',
        'Parquet'
    )"""
    return f"""s3(
        '{s3_path}',
        '{config.s3.S3_ACCESS_KEY}',
        '{config.s3.S3_SECRET_KEY}',
        'Parquet'
    )"""
