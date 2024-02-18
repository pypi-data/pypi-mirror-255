from enum import Enum

class ConnectorType(Enum):
    AWS_S3: str
    AZURE_BLOB: str
    GCS: str
    FILE: str
    MYSQL: str
    AZURE_SQL: str
    BIGQUERY: str
    SNOWFLAKE: str
