from typing import Optional
from pydantic import BaseModel


class DependencyTreeConfig(BaseModel):
    CH_URL: str
    DATABASES: Optional[str] = None
    FILE_OUTPUT: Optional[str] = None
    EXCLUDED_DATABASES: Optional[str] = None
    LOG_LEVEL: Optional[str] = "INFO"
    TABLES: Optional[str] = None
    IGNORE_VALIDATION: Optional[bool] = None
