from typing import List, Tuple, Union

import clickhouse_driver
from clickhouse_s3_etl_tools import (
    METADATA_COLUMNS_LIST_V1,
    METADATA_COLUMNS_LIST_V2,
    MAX_TABLE_SIZE_TO_DROP_TABLE_MB,
    MAX_PERCENTAGE_DIFF_TRANSFORM,
)
from clickhouse_s3_etl_tools.connectors.clickhouse_connector import ClickHouseConnector
from clickhouse_s3_etl_tools.connectors.s3_connector import S3Connector
from clickhouse_s3_etl_tools.exceptions.exception import (
    ClickHouseColumnsDeclarationErrorS3,
    TransferErrorAlreadyExists,
    ExtractMetadataError,
)
from clickhouse_s3_etl_tools.logger import get_logger
from clickhouse_s3_etl_tools.schema.schema_configs import Configuration
from clickhouse_s3_etl_tools.schema.schema_table_metadata import MetadataConfig
from clickhouse_s3_etl_tools.utils import (
    check_rows_mismatch,
    build_s3_source,
    build_s3_path,
    build_where_condition_s3,
    get_metadata_file_name,
    get_partition_from_export_file_name,
    update_create_table_query,
    timing_decorator,
    get_partition_key
)

logger = get_logger(__name__)

SQL_FETCH_METADATA = """
    SELECT {columns_list}
    FROM {s3_source}
"""

SQL_INSERT_TO_CH = """
    INSERT INTO {database_destination}.`{table_name}`
    SELECT *
    FROM {s3_source}
"""

SQL_INSERT_TO_CH_BY_RANGE = """
    INSERT INTO {database_destination}.`{table_name}`
    SELECT {columns_list}
    FROM {s3_source}
    WHERE _file between '{range_start}' and '{range_end}'
 """

GROUP_BY_PARTS_SQL = """SELECT count() as value,
                              _file AS partition
                        FROM {s3_source}
                        {where_condition}
                        GROUP BY _file
                        ORDER BY _file
                       """

FILE_LISTS = """SELECT _file
                FROM {s3_source}
                GROUP BY _file
                ORDER BY _file
            """


def check_partition_value_from(
        partition_value_from: str, config: Configuration, conn: ClickHouseConnector
):
    if config.PARTITION_VALUE_FROM:
        s3_source: str = build_s3_source(
            config, f"{config.table.TABLE_NAME}*.parquet"
        )
        logger.debug(FILE_LISTS.format(s3_source=s3_source))
        res = conn.execute(FILE_LISTS.format(s3_source=s3_source))
        parts_list = [get_partition_from_export_file_name(config, f[0]) for f in res]
        if partition_value_from not in parts_list:
            raise Exception(f"{partition_value_from} is not valid value for partitions try values like {parts_list[0:3]}")


def check_on_cluster(metadata: MetadataConfig, config: Configuration):
    if (
            "replicated" in metadata.engine.lower()
            and "on cluster" not in config.get_on_cluster().lower()
    ):
        logger.warning(
            "Your table is replicated. ? Forgot specified 'cluster_name' ?? "
        )
        # raise OnClusterClickhouseError(
        #     table=config.table.TABLE_NAME,
        #     database=config.table.DATABASE,
        #     cluster=config.CLUSTER_NAME,
        #     message="Your table is replicated. Specify 'cluster_name'",
        # )


def drop_and_create_table(config: Configuration, conn: ClickHouseConnector) -> None:
    """
    Drop the table if it exists and fetch metadata to create the table if it does not exist.

    Parameters:
        config (Configuration): The configuration object.
        conn (ClickHouseConnector): The ClickHouse connection object.
    """
    if config.DROP_DESTINATION_TABLE_IF_EXISTS and not config.PARTITION_VALUE_FROM:
        logger.debug("Check if the table exists")
        if conn.check_if_table_exists(
                database=config.table.DATABASE_DESTINATION,
                table_name=config.table.TABLE_NAME,
                raise_error=False,
        ):
            drop_table_if_exists(config, conn)

        logger.debug("Check if the table is dropped")
        if conn.check_if_table_exists(
                database=config.table.DATABASE_DESTINATION,
                table_name=config.table.TABLE_NAME,
                raise_error=False,
        ):
            raise TransferErrorAlreadyExists(
                config.table.TABLE_NAME, config.table.DATABASE_DESTINATION
            )

    create_table_if_not_exists(config, conn)


def drop_table_if_exists(
        config: Configuration,
        conn: ClickHouseConnector,
) -> None:
    """
    Drop the table if it exists.

    Parameters:
        config (Configuration): The configuration object.
        conn (ClickHouseConnector): The ClickHouse connection object.
    """
    metadata_dest: MetadataConfig = conn.get_table_metadata(
        config.table.DATABASE_DESTINATION, config.table.TABLE_NAME
    )
    logger.info(
        f"Size of destination table is {metadata_dest.total_bytes / 1024 / 1024} MB"
    )
    if metadata_dest.total_bytes / 1024 / 1024 < MAX_TABLE_SIZE_TO_DROP_TABLE_MB:
        logger.info("DROP TABLE")
        conn.drop_table(
            database=config.table.DATABASE_DESTINATION,
            table_name=config.table.TABLE_NAME,
            on_cluster=config.get_on_cluster(),
        )
    else:
        logger.info("DROP TABLE BY PARTITIONS")
        conn.drop_all_partitions(
            database=config.table.DATABASE_DESTINATION,
            table_name=config.table.TABLE_NAME,
            on_cluster=config.get_on_cluster(),
            max_size_befor_drop_mb=MAX_TABLE_SIZE_TO_DROP_TABLE_MB,
        )


def create_table_if_not_exists(
        config: Configuration, conn: ClickHouseConnector
) -> None:
    """
    Fetch metadata and create the table if it does not exist.

    Parameters:
        config (Configuration): The configuration object.
        conn (ClickHouseConnector): The ClickHouse connection object.
    """

    if not conn.check_if_table_exists(
            database=config.table.DATABASE_DESTINATION,
            table_name=config.table.TABLE_NAME,
            raise_error=False,
    ):
        logger.debug(f"ENGINE {config.ENGINE_FULL}")
        metadata: MetadataConfig = fetch_metadata_from_s3(config, conn)
        if (metadata.engine_full or "") != "" and (config.ENGINE_FULL or "" != ""):
            engine_full_to_replace: Tuple[str, str] = (
                metadata.engine_full,
                config.ENGINE_FULL,
            )
            logger.debug(f"ENGINE {engine_full_to_replace}")
        else:
            engine_full_to_replace = None

        create_table_query = update_create_table_query(
            metadata.create_table_query,
            config.table,
            config.CLUSTER_NAME,
            config.DATABASES_MAP,
            engine_full_to_replace,
        )

        conn.execute_query_and_log(create_table_query)


def fetch_metadata_from_s3(
        config: Configuration, conn: ClickHouseConnector
) -> MetadataConfig:
    """
    Fetch metadata information from the specified S3 path.

    Parameters:
        config (Configuration): The configuration object.
        conn (ClickHouseConnector): The ClickHouse connection object.

    Returns:
        Optional[MetadataConfig]: The metadata configuration if available, else None.
    """
    s3_source: str = build_s3_source(config, get_metadata_file_name(config))

    query: str = SQL_FETCH_METADATA.format(
        columns_list=METADATA_COLUMNS_LIST_V2, s3_source=s3_source
    )

    try:
        res = conn.execute_query_and_log(query)

    except clickhouse_driver.errors.ServerException as e:
        try:
            logger.debug("changing column list for the engine")
            query = SQL_FETCH_METADATA.format(
                columns_list=METADATA_COLUMNS_LIST_V1, s3_source=s3_source
            )
            res = conn.execute_query_and_log(query)

        except clickhouse_driver.errors.ServerException as e:
            s3_path: str = build_s3_path(
                config, f"__metadata__{config.table.TABLE_NAME}.parquet"
            )

            raise ExtractMetadataError(
                table=config.table.TABLE_NAME,
                database=config.table.DATABASE,
                columns_list=METADATA_COLUMNS_LIST_V1,
                s3_path=s3_path,
            ) from e

    columns = res[0]
    return MetadataConfig(
        create_table_query=str(columns[0]),
        engine=str(columns[1]),
        partition_key=str(columns[2]),
        total_rows=int(columns[3] or 0),
        total_bytes=int(columns[4] or 0),
        engine_full=str(columns[5] or 0) if len(columns) > 5 else "",
    )


def insert_to_ch_whole_table(config: Configuration, conn: ClickHouseConnector):
    """
    Insert all data from S3 to ClickHouse.

    Parameters:
        config (Configuration): The configuration object.
        conn (ClickHouseConnector): The ClickHouse connection object.
    """
    s3_source: str = build_s3_source(config, f"{config.table.TABLE_NAME}*.parquet")

    query = SQL_INSERT_TO_CH.format(
        s3_source=s3_source,
        database_destination=config.table.DATABASE_DESTINATION,
        table_name=config.table.TABLE_NAME,
    )
    try:
        conn.execute_query_and_log(query)
    except ClickHouseColumnsDeclarationErrorS3:
        config.USE_S3_CLUSTER = False
        insert_to_ch_whole_table(config, conn)


def insert_to_ch_by_range(
        config: Configuration,
        conn: ClickHouseConnector,
        range_start: str = "",
        range_end: str = "",
):
    """
    Insert data from S3 to ClickHouse within a specified range.

    Parameters:
        config (Configuration): The configuration object.
        conn (ClickHouseConnector): The ClickHouse connection object.
        range_start (str): The start of the range.
        range_end (str): The end of the range.
    """
    s3_source: str = build_s3_source(config, f"{config.table.TABLE_NAME}*.parquet")

    save_parquet_sql = SQL_INSERT_TO_CH_BY_RANGE.format(
        s3_source=s3_source,
        access_key=config.s3.S3_ACCESS_KEY,
        secret_key=config.s3.S3_SECRET_KEY,
        columns_list=conn.get_column_list(
            config.table.DATABASE_DESTINATION, config.table.TABLE_NAME
        ),
        table_name=config.table.TABLE_NAME,
        database_destination=config.table.DATABASE_DESTINATION,
        range_start=range_start.replace("'", "''"),
        range_end=range_end.replace("'", "''"),
    )

    try:
        conn.execute_query_and_log(save_parquet_sql)
    except ClickHouseColumnsDeclarationErrorS3:
        config.USE_S3_CLUSTER = False
        insert_to_ch_by_range(
            config,
            conn,
            range_start,
            range_end,
        )


@timing_decorator
def transfer_s3_to_clickhouse(config: Configuration):
    """
    Transfer data from S3 to ClickHouse.

    Parameters:
        config (Configuration): The configuration object.
    """
    with (
        ClickHouseConnector(config.clickhouse.CH_URL_DESTINATION) as conn,
        S3Connector(config.s3) as s3_conn,
    ):
        s3_conn.do_nothing()
        logger.debug(config.PARTITION_VALUE_FROM)
        check_partition_value_from(config.PARTITION_VALUE_FROM, config, conn)
        if (
                not config.DROP_DESTINATION_TABLE_IF_EXISTS
                and conn.check_if_table_exists(
            database=config.table.DATABASE_DESTINATION,
            table_name=config.table.TABLE_NAME,
            raise_error=False,
        )
                and not config.PARTITION_VALUE_FROM
        ):
            raise TransferErrorAlreadyExists(
                config.table.TABLE_NAME, config.table.DATABASE_DESTINATION
            )

        logger.info("Fetch metadata from s3")
        metadata: MetadataConfig = fetch_metadata_from_s3(config, conn)
        partition_key: str = get_partition_key(config, metadata)
        check_on_cluster(metadata, config)

        drop_and_create_table(config, conn)

        if metadata.engine.lower() in [
            "join",
            "view",
            "merge",
            "null",
            "materializedview",
        ]:
            logger.info(
                f"Engine {metadata.engine} doesn't require to be transferred to clickhouse"
            )
        else:
            number_rows: int = metadata.total_rows
            max_rows_per_group = config.BATCH_SIZE
            logger.info(f"The number rows in s3 is {number_rows}")

            partition_statement: Union[str, None] = None
            if partition_key and partition_key != "tuple()":
                partition_statement = f"PARTITION BY {partition_key}"

            if partition_statement and number_rows > max_rows_per_group:
                s3_source: str = build_s3_source(
                    config, f"{config.table.TABLE_NAME}*.parquet"
                )

                partitions_group = conn.fetch_rows_by_cumulative_sum(
                    GROUP_BY_PARTS_SQL.format(
                        s3_source=s3_source,
                        where_condition=build_where_condition_s3(
                            config, partition_key
                        ),
                    ),
                    max_rows_per_group,
                )
                for part_tuple in partitions_group:
                    range_start, range_end, _ = part_tuple
                    logger.info(
                        f"Transfer by file_name from {range_start} to {range_end}, a number of rows is {part_tuple[2]}"
                    )
                    insert_to_ch_by_range(
                        config,
                        conn,
                        range_start.replace("'", "''"),
                        range_end.replace("'", "''"),
                    )
            else:
                insert_to_ch_whole_table(config, conn)

        metadata_dest: MetadataConfig = conn.get_table_metadata(
            config.table.DATABASE_DESTINATION, config.table.TABLE_NAME
        )

        if metadata.engine.lower() == "log":
            metadata.total_rows = conn.get_table_number_rows(
                config.table.DATABASE_DESTINATION, config.table.TABLE_NAME
            )

        logger.info(
            f"A number of rows in clickhouse destination: {metadata_dest.total_rows}"
        )

        if metadata.engine.lower() not in ["materializedview"] and not config.PARTITION_VALUE_FROM:
            check_rows_mismatch(
                s3_row_count=metadata.total_rows,
                clickhouse_row_count=metadata_dest.total_rows,
                max_percentage_diff=MAX_PERCENTAGE_DIFF_TRANSFORM,
                is_export=False,
            )
