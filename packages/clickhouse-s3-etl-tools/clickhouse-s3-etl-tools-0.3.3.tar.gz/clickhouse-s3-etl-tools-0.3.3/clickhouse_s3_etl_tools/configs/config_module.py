import os
from clickhouse_s3_etl_tools.schema.schema_configs import Configuration

from clickhouse_s3_etl_tools import (
    DEFAULT_VALUE_BATCH_SIZE,
    DEFAULT_VALUE_LOG_LEVEL,
    DEFAULT_VALUE_DROP_DESTINATION_TABLE_IF_EXISTS,
)


def get_configuration() -> Configuration:
    raw_config = {
        "s3": {
            "S3_ACCESS_KEY": os.getenv("S3_ACCESS_KEY"),
            "S3_SECRET_KEY": os.getenv("S3_SECRET_KEY"),
            "PATH_S3": os.getenv("PATH_S3"),
        },
        "clickhouse": {
            "CH_URL_SOURCE": os.getenv("CH_URL_SOURCE"),
            "CH_URL_DESTINATION": os.getenv("CH_URL_DESTINATION"),
        },
        "table": {
            "TABLE_NAME": os.getenv("TABLE_NAME"),
            "DATABASE": os.getenv("DATABASE"),
            "DATABASE_DESTINATION": os.getenv("DATABASE_DESTINATION"),
        },
        "BATCH_SIZE": int(os.getenv("BATCH_SIZE") or DEFAULT_VALUE_BATCH_SIZE),
        "LOG_LEVEL": os.getenv("LOG_LEVEL") or DEFAULT_VALUE_LOG_LEVEL,
        "DROP_DESTINATION_TABLE_IF_EXISTS": os.getenv(
            "DROP_DESTINATION_TABLE_IF_EXISTS"
        )
        or DEFAULT_VALUE_DROP_DESTINATION_TABLE_IF_EXISTS,
        "CLUSTER_NAME": os.getenv("CLUSTER_NAME"),
        "USE_S3_CLUSTER": os.getenv("USE_S3_CLUSTER") or False,
        "PARTITION_KEY": os.getenv("PARTITION_KEY"),
    }

    return Configuration(**raw_config)
