import enum
from typing import Dict


class FeatureType(enum.Enum):
    """Feature type for contribution requests."""

    ORIGINAL = "ORIGINAL"
    TRANSFORMED = "TRANSFORMED"


class Format(enum.Enum):
    """Data formats for source/sink."""

    BIGQUERY = "Google BigQuery table"
    CSV = "CSV file"
    JDBC_QUERY = "SQL query through JDBC connection"
    JDBC_TABLE = "SQL table through JDBC connection"
    ORC = "ORC file"
    PARQUET = "Parquet file"
    SNOWFLAKE_QUERY = "Snowflake query"
    SNOWFLAKE_TABLE = "Snowflake table"


format_map: Dict[Format, Dict[str, str]] = {
    Format.BIGQUERY: {"format": "bigquery"},
    Format.CSV: {"format": "csv", "header": "true", "inferschema": "true"},
    Format.JDBC_QUERY: {"format": "jdbc"},
    Format.JDBC_TABLE: {"format": "jdbc"},
    Format.ORC: {"format": "orc"},
    Format.PARQUET: {"format": "parquet"},
    Format.SNOWFLAKE_QUERY: {"format": "net.snowflake.spark.snowflake"},
    Format.SNOWFLAKE_TABLE: {"format": "net.snowflake.spark.snowflake"},
}


class WriteMode(enum.Enum):
    """Write modes for sink."""

    APPEND = "Append to existing files"
    ERROR = "Error if exists"
    IGNORE = "Ignore if exists"
    OVERWRITE = "Overwrite existing files"


write_mode_map: Dict[WriteMode, str] = {
    WriteMode.APPEND: "append",
    WriteMode.ERROR: "error",
    WriteMode.IGNORE: "ignore",
    WriteMode.OVERWRITE: "overwrite",
}
