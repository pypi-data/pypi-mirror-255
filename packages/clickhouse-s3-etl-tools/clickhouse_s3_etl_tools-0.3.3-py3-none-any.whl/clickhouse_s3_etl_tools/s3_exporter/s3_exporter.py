from clickhouse_s3_etl_tools.schema.schema_configs import Configuration
from clickhouse_s3_etl_tools import (
    MAX_PERCENTAGE_DIFF_EXTRACT,
    METADATA_COLUMNS_LIST_V2,
)
from clickhouse_s3_etl_tools.connectors.clickhouse_connector import ClickHouseConnector
from clickhouse_s3_etl_tools.connectors.s3_connector import S3Connector
from clickhouse_s3_etl_tools.logger import get_logger
from clickhouse_s3_etl_tools.schema.schema_table_metadata import MetadataConfig
from clickhouse_s3_etl_tools.utils import (
    build_s3_source,
    check_rows_mismatch,
    timing_decorator,
    build_where_condition,
    get_metadata_file_name,
    get_partition_export_file_name,
    get_full_table_export_file_name,
    get_partition_key
)

logger = get_logger(__name__)

# Constants for SQL Statements
SAVE_PARQUET_SCHEMA_SQL = """
    INSERT INTO FUNCTION
        {s3_source}
   SELECT {columns_list}
   FROM system.tables 
   WHERE
        name = '{table_name}'
        AND database = '{database}'
   SETTINGS s3_truncate_on_insert = 1;
"""

SAVE_PARQUET_SQL = """
    INSERT INTO FUNCTION
        {s3_source}
        {partition_statement}
    SELECT {columns_list}
    FROM {database}.`{table}`
    WHERE {partition_key} between '{range_start}' and '{range_end}'
    SETTINGS s3_truncate_on_insert = 1;
"""

SAVE_WHOLE_TABLE_SQL = """
    INSERT INTO FUNCTION
        {s3_source}
    SELECT {columns_list}
    FROM {database}.`{table}`
    {where_condition}
    SETTINGS s3_truncate_on_insert = 1;
"""

GROUP_BY_PARTS_SQL = """SELECT
                             COUNT() as value,
                             {partition_key} as partition
                       FROM {database}.{table_name}
                       {where_condition}
                       GROUP BY {partition_key}
                       """

SQL_COUNT_ROWS = """
    SELECT count(*) as total_rows
    FROM {s3_source}
"""


def save_table_metadata(
        config: Configuration, conn: ClickHouseConnector, metadata: MetadataConfig
) -> None:
    """
    Save metadata of the table to S3 in Parquet format.

    Parameters:
    - config (Configuration): The configuration object.
    - conn (ClickHouseConnector): The ClickHouse connector.

    Returns:
    None
    """
    s3_source: str = build_s3_source(config, get_metadata_file_name(config))
    columns_list = METADATA_COLUMNS_LIST_V2.replace(
        "total_rows,", f"{metadata.total_rows} as total_rows,"
    )

    save_parquet_metadata = SAVE_PARQUET_SCHEMA_SQL.format(
        s3_source=s3_source,
        columns_list=columns_list,
        table_name=config.table.TABLE_NAME,
        database=config.table.DATABASE,
    )

    conn.execute_query_and_log(save_parquet_metadata)


def fetch_number_rows_from_s3(config: Configuration, conn: ClickHouseConnector) -> int:
    """
    Fetch the number of rows from the specified S3 path.

    Parameters:
        config (Configuration): The configuration object.
        conn (ClickHouseConnector): The ClickHouse connection object.

    Returns:
        int: The total number of rows.
    """
    s3_source: str = build_s3_source(config, f"{config.table.TABLE_NAME}*.parquet")

    query = SQL_COUNT_ROWS.format(s3_source=s3_source)

    res = conn.execute_query_and_log(query)
    return next((column[0] for column in res if res), None)


def save_parquet_data(
        config: Configuration,
        conn: ClickHouseConnector,
        partition_key: str,
        partition_statement: str = "",
        range_start: str = "",
        range_end: str = "",
        columns_list: str = "",
) -> None:
    """
    Save Parquet data to S3.

    Parameters:
    - config (Configuration): The configuration object.
    - conn (ClickHouseConnector): The ClickHouse connector.
    - partition_key (str): The partition key.
    - partition_statement (str): The partition statement.
    - range_start (str): The starting range for partition.
    - range_end (str): The ending range for partition.
    - columns_list(str)

    Returns:
    None
    """
    s3_source: str = build_s3_source(
        config, get_partition_export_file_name(config, _partition_id="{_partition_id}")
    )
    save_parquet_sql = SAVE_PARQUET_SQL.format(
        s3_source=s3_source,
        partition_statement=partition_statement,
        columns_list=columns_list,
        database=config.table.DATABASE,
        table=config.table.TABLE_NAME,
        partition_key=partition_key,
        range_start=range_start.replace("'", "''")
        if isinstance(range_start, str)
        else range_start,
        range_end=range_end.replace("'", "''")
        if isinstance(range_end, str)
        else range_end,
    )

    conn.execute_query_and_log(save_parquet_sql)


def save_whole_table(
        config: Configuration, conn: ClickHouseConnector, columns_list: str
) -> None:
    """
    Save the entire table to S3 in Parquet format.

    Parameters:
    - config (Configuration): The configuration object.
    - conn (ClickHouseConnector): The ClickHouse connector.

    Returns:
    None
    """
    s3_source: str = build_s3_source(config, get_full_table_export_file_name(config))
    save_parquet_sql = SAVE_WHOLE_TABLE_SQL.format(
        s3_source=s3_source,
        columns_list=columns_list,
        database=config.table.DATABASE,
        table=config.table.TABLE_NAME,
        where_condition=""
    )

    conn.execute_query_and_log(save_parquet_sql)


@timing_decorator
def export_to_s3(config: Configuration) -> None:
    """
    Export data from ClickHouse to S3 in Parquet format.

    Parameters:
    - config (Configuration): The configuration object.

    Returns:
    None
    """
    max_rows_per_group = config.BATCH_SIZE
    partition_statement = ""
    with (
        ClickHouseConnector(config.clickhouse.CH_URL_SOURCE) as ch_conn,
        S3Connector(config.s3) as s3_conn,
    ):
        ch_conn.check_if_table_exists(config.table.DATABASE, config.table.TABLE_NAME)

        s3_conn.drop_table_directory_if_exists(
            f"{config.table.DATABASE}/{config.table.TABLE_NAME}"
        )

        metadata: MetadataConfig = ch_conn.get_table_metadata(
            config.table.DATABASE, config.table.TABLE_NAME
        )
        partition_key: str = get_partition_key(config, metadata)

        if metadata.engine.lower() == "log":
            metadata.total_rows = ch_conn.get_table_number_rows(
                config.table.DATABASE, config.table.TABLE_NAME
            )

        logger.info(f"A number of rows in clickhouse: {metadata.total_rows}")

        if config.SAVE_ONLY_METADATA:
            logger.info(f"Saving only metadata --save-only-metadata is True")

        elif metadata.engine.lower() in [
            "join",
            "view",
            "merge",
            "null",
            "materializedview",
        ]:
            logger.info(f"Engine {metadata.engine} has no rows ")

        else:
            columns_list: str = ch_conn.get_column_list(
                config.table.DATABASE, config.table.TABLE_NAME
            )

            if partition_key and partition_key != "tuple()":
                partition_statement = f"PARTITION BY {partition_key}"

            if partition_statement and metadata.total_rows > max_rows_per_group:
                partitions_group = ch_conn.fetch_rows_by_cumulative_sum(
                    GROUP_BY_PARTS_SQL.format(
                        partition_key=partition_key,
                        table_name=config.table.TABLE_NAME,
                        database=config.table.DATABASE,
                        where_condition=build_where_condition(config, partition_key),
                    ),
                    max_rows_per_group,
                )
                for part_tuple in partitions_group:
                    range_start, range_end, _ = part_tuple
                    logger.info(
                        f"Fetch by {partition_key} "
                        f"from {range_start} to {range_end}, "
                        f"a number of rows is {part_tuple[2]}"
                    )
                    save_parquet_data(
                        config,
                        ch_conn,
                        partition_key,
                        partition_statement,
                        range_start.replace("'", "''")
                        if isinstance(range_start, str)
                        else range_start,
                        range_end.replace("'", "''")
                        if isinstance(range_end, str)
                        else range_end,
                        columns_list,
                    )
            else:
                save_whole_table(config, ch_conn, columns_list)

    if (
            metadata.engine.lower()
            not in [
        "join",
        "view",
        "merge",
        "null",
        "materializedview",
    ]
            and not config.SAVE_ONLY_METADATA
            and not config.PARTITION_VALUE_FROM
    ):
        number_rows_s3: int = fetch_number_rows_from_s3(config, ch_conn)
        logger.info(f"The number rows in s3 is {number_rows_s3}")
        check_rows_mismatch(
            number_rows_s3, metadata.total_rows, MAX_PERCENTAGE_DIFF_EXTRACT
        )
        metadata.total_rows = number_rows_s3

    logger.debug("Save metadata for table")

    save_table_metadata(config, ch_conn, metadata)
