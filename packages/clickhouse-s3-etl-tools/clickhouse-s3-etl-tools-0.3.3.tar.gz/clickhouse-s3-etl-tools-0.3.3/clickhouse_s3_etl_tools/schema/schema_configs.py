from typing import Optional

from pydantic import BaseModel, PositiveInt, ValidationInfo, field_validator


class ClickHouseConfig(BaseModel):
    """
    Pydantic model for ClickHouse configuration.

    Attributes:
        CH_URL_SOURCE (Optional[str]): ClickHouse source URL.
        CH_URL_DESTINATION (Optional[str]): ClickHouse destination URL.
    """

    CH_URL_SOURCE: str
    CH_URL_DESTINATION: str


class S3Config(BaseModel):
    """
    Pydantic model for S3 configuration.

    Attributes:
        S3_ACCESS_KEY (str): S3 access key.
        S3_SECRET_KEY (str): S3 secret key.
        PATH_S3 (str): S3 path.
    """

    S3_ACCESS_KEY: str
    S3_SECRET_KEY: str
    PATH_S3: str


class TableConfiguration(BaseModel):
    """
    Pydantic model for table configuration.

    Attributes:
        TABLE_NAME (str): Table name.
        DATABASE (str): Database name.
        DATABASE_DESTINATION (str): Destination database name.
    """

    TABLE_NAME: str
    DATABASE: str
    DATABASE_DESTINATION: str


class Configuration(BaseModel):
    """
    Pydantic model for the overall configuration.

    Attributes:
        s3 (S3Config): S3 configuration.
        clickhouse (ClickHouseConfig): ClickHouse configuration.
        table (TableConfiguration): Table configuration.
        LOG_LEVEL (str): Logging level (default: INFO).
        BATCH_SIZE (PositiveInt): Batch size for processing (default: 100000000).
        DROP_DESTINATION_TABLE_IF_EXISTS (bool): Whether to drop the destination table if it exists (default: False).
        CLUSTER_NAME (str): Directive for cluster configuration (default: "").
        DATABASES_MAP(str)
    """

    s3: S3Config
    clickhouse: ClickHouseConfig
    table: TableConfiguration
    LOG_LEVEL: Optional[str] = "INFO"
    BATCH_SIZE: Optional[PositiveInt] = 100000000
    DROP_DESTINATION_TABLE_IF_EXISTS: Optional[bool] = False
    CLUSTER_NAME: Optional[str] = None
    USE_S3_CLUSTER: Optional[bool] = False
    SAVE_ONLY_METADATA: Optional[bool] = False
    PARTITION_KEY: Optional[str] = None
    DATABASES_MAP: Optional[str] = None
    ENGINE_FULL: Optional[str] = None

    @classmethod
    def _get_on_cluster(cls, cluster_name: str):
        if not cluster_name or cluster_name == "":
            return ""
        return f"ON CLUSTER '{cluster_name}'"

    def get_on_cluster(self):
        return Configuration._get_on_cluster(self.CLUSTER_NAME)

    @field_validator('DATABASES_MAP')
    @classmethod
    def validate_databases_map(cls, value: str, info: ValidationInfo) -> str:
        # Split the value by commas
        if value:
            pairs = value.split(',')

            for pair in pairs:
                # Split each pair by colon
                databases = pair.split(':')

                # Ensure each pair has two elements
                assert len(databases) == 2, f'pair in {info.field_name} must be like database_str:database_dst'

        return value
