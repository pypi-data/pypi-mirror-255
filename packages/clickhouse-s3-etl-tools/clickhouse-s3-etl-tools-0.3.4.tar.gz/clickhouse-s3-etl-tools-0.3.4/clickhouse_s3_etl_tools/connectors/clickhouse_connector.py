from bisect import bisect_left
from typing import List, Tuple, Union, Dict, Optional
from urllib.parse import urlparse, parse_qs

import time
import clickhouse_driver
from clickhouse_s3_etl_tools import (
    NUM_PARTITIONS_DROP_IN_QUERY,
    NUMB_RECONNECT_ATTEMPTS_CH,
    MAX_PARTITIONS_PER_INSERT_BLOCK,
    DELAY_BETWEEN_DROP_PARTITIONS_SEC,
)
from clickhouse_s3_etl_tools.connectors.my_clickhouse_balanced import Client
from clickhouse_s3_etl_tools.exceptions.exception import (
    TableNotFoundError,
    ClickHouseError,
    TableSizeExceedsMaxException,
    ClickHouseColumnsDeclarationErrorS3,
)
from clickhouse_s3_etl_tools.logger import get_logger
from clickhouse_s3_etl_tools.schema.schema_table_metadata import MetadataConfig
from clickhouse_s3_etl_tools.utils.utils import prettify_sql

logger = get_logger(__name__)


class ClickHouseConnector:
    """Connector for interacting with ClickHouse databases.

    Args:
        db_url (str): The URL of the ClickHouse database.

    Methods:
        __enter__(): Enter method for context management.
        __exit__(exc_type, exc_val, exc_tb): Exit method for context management.
        execute_query_and_log(sql: str): Execute a query and log it.
        get_schema(database: str, table_name: str) -> dict | None: Get the schema for a ClickHouse table.
        get_column_list(database: str, table_name: str) -> str: Get the column list for a ClickHouse table.
        get_partitions(database: str, table_name: str) -> List[Union[str, int]] | None: Get the partitions for a ClickHouse table.
        drop_partition(database: str, table_name: str, partition: Union[str, int], on_cluster: str = "") -> bool:
            Drop a partition from a ClickHouse table.
        drop_all_partitions(database: str, table_name: str, on_cluster: str = "", max_size_befor_drop_mb: int = 70000) -> bool:
            Drop all partitions from a ClickHouse table.
        get_table_metadata(database: str, table_name: str) -> MetadataConfig | None: Get metadata for a ClickHouse table.
        check_if_table_exists(database: str, table_name: str, raise_error: bool = True) -> bool:
            Check if a ClickHouse table exists.
        fetch_rows_by_cumulative_sum(query: str, max_rows_per_group: int) -> List[Tuple]: Fetch rows from ClickHouse based on cumulative sum.
        drop_table(database: str, table_name: str, on_cluster: str = "") -> bool: Drop a ClickHouse table.
    """

    def __init__(self, db_url: str):
        """Initialize the ClickHouseConnector."""
        self.db_url = db_url
        self.client = None

    def __enter__(self):
        """Enter method for context management."""
        url = urlparse(self.db_url)
        conn_params = {
            "host": url.hostname,
            "port": url.port or 9000,
            "database": url.path.lstrip("/"),
            "user": url.username,
            "password": url.password,
            "alt_hosts": str(",".join(parse_qs(url.query).get("alt_hosts", []))),
            "reconnect_attempts": NUMB_RECONNECT_ATTEMPTS_CH,
            "settings": {
                "max_partitions_per_insert_block": MAX_PARTITIONS_PER_INSERT_BLOCK
            },
        }

        self.client = Client(**conn_params)
        try:
            self.client.execute("select 1")
        except clickhouse_driver.errors.ServerException as e:
            raise ClickHouseError(
                url=self.db_url, message="Cannot connect to Clickhouse"
            ) from e

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit method for context management."""
        if self.client is not None:
            self.client.disconnect()

    def execute(self, sql):
        """Custom execution"""
        try:
            return self.client.execute(sql)
        except clickhouse_driver.errors.ServerException as e:
            if (
                "columns declaration list" in e.message
            ):  # bug of clickhouse for s3 cluster https://github.com/ClickHouse/ClickHouse/issues/54615
                raise ClickHouseColumnsDeclarationErrorS3(
                    url=self.db_url,
                    message="Old bug in clickhouse have to change S3Cluster to S3",
                )
            raise clickhouse_driver.errors.ServerException(e.message) from e

    def execute_query_and_log(self, sql: str):
        """Execute a query and log it."""
        logger.debug(prettify_sql(sql))
        return self.execute(sql)

    def get_schema(self, database: str, table_name: str) -> Union[Dict[str, str], None]:
        """Get the schema for a ClickHouse table.

        Args:
            database (str): The name of the database.
            table_name (str): The name of the table.

        Returns:
            dict | None: A dictionary representing the table schema.

        Raises:
            ClickHouseError: If an error occurs while fetching the schema.
        """
        try:
            schema_stat = f"""SELECT name, type
                              FROM system.columns
                              WHERE table = '{table_name}'
                                    AND database = '{database}'"""

            columns = self.execute_query_and_log(schema_stat)
        except Exception as e:
            logger.error(f"Error fetching schema for {table_name}: {e}")
            return None
        return {column[0]: column[1] for column in columns} if columns else None

    def get_partitions(
        self, database: str, table_name: str
    ) -> Union[List[Union[str, int]], None]:
        """Get the partitions for a ClickHouse table.

        Args:
            database (str): The name of the database.
            table_name (str): The name of the table.

        Returns:
            List[Union[str, int]] | None: A list of partition values.

        Raises:
            ClickHouseError: If an error occurs while fetching partitions.
        """
        partitions_info = self.execute_query_and_log(
            f"""select distinct partition 
                from system.parts where table = '{table_name}' 
                and database = '{database}' """
        )
        return [column[0] for column in partitions_info] if partitions_info else None

    def get_partitions_names(
        self, database: str, table_name: str
    ) -> Union[List[Union[str, int]], None]:
        """Get the partitions for a ClickHouse table.

        Args:
            database (str): The name of the database.
            table_name (str): The name of the table.

        Returns:
            List[Union[str, int]] | None: A list of partition values.

        Raises:
            ClickHouseError: If an error occurs while fetching partitions.
        """
        partitions_info = self.execute_query_and_log(
            f"""select distinct name
                from system.parts where table = '{table_name}' 
                and database = '{database}' """
        )
        return [column[0] for column in partitions_info] if partitions_info else None

    def get_table_metadata(self, database: str, table_name: str) -> MetadataConfig:
        """Get metadata for a ClickHouse table.

        Args:
            database (str): The name of the database.
            table_name (str): The name of the table.

        Returns:
            MetadataConfig | None: Metadata information.

        Raises:
            ClickHouseError: If an error occurs while fetching metadata.
        """
        metadata_stat = f"""SELECT  create_table_query,
                                    engine,
                                    partition_key,
                                    total_rows,
                                    total_bytes,
                                    engine_full
                             FROM system.tables
                             WHERE table = '{table_name}'
                             AND database = '{database}'"""

        res: List[Tuple[str, str, str, int, int, str]] = self.execute_query_and_log(
            metadata_stat
        )

        columns: Tuple[str, str, str, int, int, str] = res[0]

        return MetadataConfig(
            create_table_query=str(columns[0]),
            engine=str(columns[1]),
            partition_key=str(columns[2]),
            total_rows=int(columns[3] or 0),
            total_bytes=int(columns[4] or 0),
            engine_full=str(columns[5] or ""),
        )

    def check_if_table_exists(
        self, database: str, table_name: str, raise_error: bool = True
    ) -> bool:
        """Check if a ClickHouse table exists.

        Args:
            database (str): The name of the database.
            table_name (str): The name of the table.
            raise_error (bool): Whether to raise an error if the table doesn't exist.

        Returns:
            bool: True if the table exists, False otherwise.

        Raises:
            TableNotFoundError: If the table doesn't exist and raise_error is True.
            ClickHouseError: If an error occurs while checking table existence.
        """
        create_table_stat = f"""SELECT 1
                                 FROM system.tables
                                 WHERE table = '{table_name}'
                                    AND database = '{database}'"""

        res: list = self.execute_query_and_log(create_table_stat)
        if not res:
            if raise_error:
                raise TableNotFoundError(table_name, database)
            return False
        return True

    def fetch_rows_by_cumulative_sum(
        self, query: str, max_rows_per_group: int
    ) -> List[Tuple]:
        """Fetch rows from ClickHouse based on cumulative sum.

        Args:
            query (str): The query to fetch rows.
            max_rows_per_group (int): Maximum number of rows per group.

        Returns:
            List[Tuple]: List of tuples representing rows.

        Raises:
            ClickHouseError: If an error occurs while fetching rows.
        """
        query = f"""
            SELECT
                partition as partition,
                SUM(value) OVER (ORDER BY partition) AS cumulative_sum
            FROM (
                {query}
            )
        """

        result = self.execute_query_and_log(query)
        cumulative_sums = list(result)

        rows = []

        start_index = 0

        while start_index < len(cumulative_sums):
            if start_index != 0:
                target_cumulative_sum = (
                    cumulative_sums[start_index][1] + max_rows_per_group
                )
            else:
                target_cumulative_sum = max_rows_per_group

            end_index = bisect_left(
                [x[1] for x in cumulative_sums], target_cumulative_sum
            )
            if end_index > 0:
                end_index -= 1

            if end_index == len(cumulative_sums):
                end_index -= 1

            if start_index > 0:
                selected_group_sum = (
                    cumulative_sums[end_index][1] - cumulative_sums[start_index - 1][1]
                )
            else:
                selected_group_sum = cumulative_sums[end_index][1]

            rows.append(
                (
                    cumulative_sums[start_index][0],
                    cumulative_sums[end_index][0],
                    selected_group_sum,
                )
            )
            start_index = end_index + 1

        return rows

    def drop_partition(
        self,
        database: str,
        table_name: str,
        partition: Union[str, int],
        on_cluster: str = "",
    ) -> bool:
        """Drop a partition from a ClickHouse table.

        Args:
            database (str): The name of the database.
            table_name (str): The name of the table.
            partition (Union[str, int]): The partition to drop.
            on_cluster (str): The cluster name.

        Returns:
            bool: True if the partition was dropped successfully, False otherwise.

        Raises:
            ClickHouseError: If an error occurs while dropping the partition.
        """
        drop_partition_query = f"ALTER TABLE {database}.{table_name} {on_cluster} DROP PARTITION '{partition}' "
        self.execute_query_and_log(drop_partition_query)
        return True

    def drop_all_partitions(
        self,
        database: str,
        table_name: str,
        on_cluster: str = "",
        max_size_befor_drop_mb: int = 70000,
    ) -> bool:
        """Drop all partitions from a ClickHouse table.

        Args:
            database (str): The name of the database.
            table_name (str): The name of the table.
            on_cluster (str): The cluster name.

        Returns:
            bool: True if all partitions were dropped successfully, False otherwise.

        Raises:
            ClickHouseError: If an error occurs while dropping partitions.
            :param database:
            :param table_name:
            :param on_cluster:
            :param max_size_befor_drop_mb:
        """

        m: MetadataConfig = self.get_table_metadata(database, table_name)
        size_mb: float = m.total_bytes / 1024 / 1024
        logger.debug(
            f"Size of the table is {size_mb:.2f} MB, a number of rows is {m.total_rows}"
        )

        # Get the list of existing partitions
        partitions = self.get_partitions_names(database, table_name)

        if not partitions or len(partitions) <= 1:
            if size_mb > max_size_befor_drop_mb:
                raise TableSizeExceedsMaxException(
                    table_name, database, size_mb, max_size_befor_drop_mb
                )

            else:
                return self.drop_table(database, table_name, on_cluster)

        # Drop partitions iteratively in batches of 10

        for i in range(0, len(partitions), NUM_PARTITIONS_DROP_IN_QUERY):
            if size_mb > max_size_befor_drop_mb:
                batch = partitions[i : i + NUM_PARTITIONS_DROP_IN_QUERY]
                drop_partition_query = (
                    f"ALTER TABLE {database}.`{table_name}` {on_cluster} "
                    + ", ".join([f"DROP PART '{p}'" for p in batch])
                )
                self.execute_query_and_log(drop_partition_query)

            logger.debug(f"Sleep {DELAY_BETWEEN_DROP_PARTITIONS_SEC} secs")
            time.sleep(DELAY_BETWEEN_DROP_PARTITIONS_SEC)

            m = self.get_table_metadata(database, table_name)
            size_mb = m.total_bytes / 1024 / 1024
            logger.debug(
                f"Size of the table is {size_mb:.2f} MB, a number of rows is {m.total_rows}"
            )

        logger.info(f"All partitions dropped successfully for table '{table_name}'.")
        return self.drop_table(database, table_name, on_cluster)

    def drop_table(self, database: str, table_name: str, on_cluster: str = "") -> bool:
        """Drop a ClickHouse table.

        Args:
            database (str): The name of the database.
            table_name (str): The name of the table.
            on_cluster (str): The cluster name.

        Returns:
            bool: True if the table was dropped successfully, False otherwise.
        """
        drop_table_query = (
            f"""DROP TABLE IF EXISTS {database}.`{table_name}` {on_cluster}"""
        )
        self.execute_query_and_log(drop_table_query)
        return True

    def get_column_list(self, database: str, table_name: str) -> str:
        """Get the column list for a ClickHouse table.

        Args:
            database (str): The name of the database.
            table_name (str): The name of the table.

        Returns:
            str: The formatted column list.
        """
        schema = self.get_schema(database, table_name)

        columns_list = ",\n".join(
            [
                f'toString("{k}") as {k}'
                if "UUID" in v or "AggregateFunction" in v
                else f'"{k}"'
                for (k, v) in schema.items()
            ]
        )
        return columns_list

    def get_table_number_rows(self, database: str, table_name: str) -> int:
        """Get the number of rows in a specified table.

        Args:
            database (str): The name of the database.
            table_name (str): The name of the table.

        Returns:
            int: The number of rows in the specified table.

        Raises:
            ClickHouseError: If an error occurs while fetching the number of rows.
        """
        number_rows_stat = f"SELECT COUNT(*) FROM {database}.{table_name}"
        return self.execute_query_and_log(number_rows_stat)[0][0]
