import argparse
import os

from clickhouse_s3_etl_tools import (
    DEFAULT_VALUE_BATCH_SIZE,
    DEFAULT_VALUE_LOG_LEVEL,
    DEFAULT_ENGINE_FULL,
)
from clickhouse_s3_etl_tools.schema.schema_configs import Configuration

from clickhouse_s3_etl_tools.logger import get_logger

logger = get_logger(__name__)


def get_configuration() -> Configuration:
    parser = argparse.ArgumentParser(
        description="Script processes data from S3 and transfers it to ClickHouse instance. "
                    "Specify S3 and ClickHouse connection details, table configuration, and other options."
    )

    # Define command-line arguments

    parser.add_argument(
        "--ch-url-destination", type=str, help="ClickHouse Destination URL"
    )

    parser.add_argument("--s3-access-key", type=str, help="S3 Access Key")
    parser.add_argument("--s3-secret-key", type=str, help="S3 Secret Key")
    parser.add_argument("--s3-path", type=str, help="S3 Path")

    parser.add_argument("--table-name", type=str, help="Table Name")
    parser.add_argument("--database", type=str, help="Database")
    parser.add_argument("--database-destination", type=str, help="Destination Database")

    parser.add_argument(
        "--partition-key", type=str, help="Partition key if you want to use custom"
    )

    parser.add_argument(
        "--batch-size", type=int, default=DEFAULT_VALUE_BATCH_SIZE, help="Batch Size"
    )
    parser.add_argument(
        "--log-level", type=str, default=DEFAULT_VALUE_LOG_LEVEL, help="Log Level"
    )

    parser.add_argument(
        "--drop-destination-table-if-exists",
        action="store_true",
        help="Drop destination table if exists",
    )

    parser.add_argument(
        "--use-s3-cluster",
        action="store_true",
        help="Use S3cluster",
    )

    parser.add_argument(
        "--cluster-name",
        type=str,
        help="Directive for cluster configuration (default: " ")",
    )

    parser.add_argument(
        "--databases-map",
        type=str,
        help="Mapping for database sources and destination. Format database_src1:database_dst1,"
             "database_src2:database_dst2",
    )

    parser.add_argument(
        "--engine-full",
        type=str,
        default=DEFAULT_ENGINE_FULL,
        help="Full engine if you want to replace create table query engine full with your custom",
    )

    parser.add_argument(
        "--partition-value-from",
        type=str,
        help="Partition value from for increment transfer",
    )

    # Parse command-line arguments
    args = parser.parse_args()

    # Construct raw config dictionary
    raw_config = {
        "s3": {
            "S3_ACCESS_KEY": args.s3_access_key or os.getenv("S3_ACCESS_KEY"),
            "S3_SECRET_KEY": args.s3_secret_key or os.getenv("S3_SECRET_KEY"),
            "PATH_S3": args.s3_path or os.getenv("PATH_S3"),
        },
        "clickhouse": {
            "CH_URL_SOURCE": "not_available",
            "CH_URL_DESTINATION": args.ch_url_destination
                                  or os.getenv("CH_URL_DESTINATION"),
        },
        "table": {
            "TABLE_NAME": args.table_name or os.getenv("TABLE_NAME"),
            "DATABASE": args.database or os.getenv("DATABASE"),
            "DATABASE_DESTINATION": args.database_destination
                                    or os.getenv("DATABASE_DESTINATION"),
        },
        "BATCH_SIZE": args.batch_size,
        "LOG_LEVEL": args.log_level,
        "DROP_DESTINATION_TABLE_IF_EXISTS": args.drop_destination_table_if_exists,
        "CLUSTER_NAME": args.cluster_name or os.getenv("CLUSTER_NAME"),
        "USE_S3_CLUSTER": args.use_s3_cluster or os.getenv("USE_S3_CLUSTER"),
        "PARTITION_KEY": args.partition_key or os.getenv("PARTITION_KEY"),
        "DATABASES_MAP": args.databases_map,
        "ENGINE_FULL": args.engine_full,
        "PARTITION_VALUE_FROM": args.partition_value_from,
    }
    logger.debug(raw_config)
    # Create Configuration instance
    return Configuration(**raw_config)
