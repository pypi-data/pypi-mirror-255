from pydantic import BaseModel
from typing import Optional


class MetadataConfig(BaseModel):
    """
    Pydantic model for metadata configuration.

    Attributes:
        create_table_query (str): SQL query for table creation.
        engine (str): Database engine.
        partition_key (str): Key used for partitioning.
        total_rows (int): Total number of rows.
        total_bytes (int): Total size in bytes.
    """

    create_table_query: str
    engine: str
    partition_key: str
    total_rows: int
    total_bytes: int
    engine_full: Optional[str] = None
