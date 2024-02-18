import argparse
import os

from clickhouse_s3_etl_tools import (
    DEFAULT_VALUE_BATCH_SIZE,
    DEFAULT_VALUE_LOG_LEVEL,
)
from clickhouse_s3_etl_tools.schema.schema_configs import Configuration


def get_configuration() -> Configuration:
    parser = argparse.ArgumentParser(
        description="Script processes exporting data from ClickHouse instance to S3. "
        "Specify S3 and ClickHouse connection details, table configuration, and other options."
    )

    # Define command-line arguments

    parser.add_argument("--ch-url-source", type=str, help="ClickHouse Source URL")

    parser.add_argument("--s3-access-key", type=str, help="S3 Access Key")
    parser.add_argument("--s3-secret-key", type=str, help="S3 Secret Key")
    parser.add_argument("--s3-path", type=str, help="S3 Path")

    parser.add_argument("--table-name", type=str, help="Table Name")
    parser.add_argument("--database", type=str, help="Database")
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
        "--save-only-metadata",
        action="store_true",
        help="Save only data metadata without the body",
    )

    parser.add_argument(
        "--partition-value-from",
        type=str,
        help="Partition value from for increment extraction",
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
            "CH_URL_SOURCE": args.ch_url_source or os.getenv("CH_URL_SOURCE"),
            "CH_URL_DESTINATION": "not_available",
        },
        "table": {
            "TABLE_NAME": args.table_name or os.getenv("TABLE_NAME"),
            "DATABASE": args.database or os.getenv("DATABASE"),
            "DATABASE_DESTINATION": "not_available",
        },
        "BATCH_SIZE": args.batch_size,
        "LOG_LEVEL": args.log_level,
        "PARTITION_KEY": args.partition_key or os.getenv("PARTITION_KEY"),
        "SAVE_ONLY_METADATA": args.save_only_metadata,
        "PARTITION_VALUE_FROM": args.partition_value_from,
    }

    # Create Configuration instance
    return Configuration(**raw_config)
