import argparse

from clickhouse_s3_etl_tools.schema.schema_dependency_tree import DependencyTreeConfig


def get_configuration() -> DependencyTreeConfig:
    parser = argparse.ArgumentParser(
        description="The script returns the dependency tree of ClickHouse tables to a file or stdout. It also "
        "visualizes the tree in the console"
        "Specify ClickHouse connection details, databases list and file_output"
    )

    parser.add_argument("--ch-url", type=str, help="ClickHouse URL")

    parser.add_argument("--databases", type=str, help="Databases list")
    parser.add_argument("--file-output", type=str, help="File output for dict result")
    parser.add_argument(
        "--excluded-databases",
        type=str,
        help="A list of excluded databases for the parent " "dependency.",
    )
    parser.add_argument("--log-level", type=str, default="INFO", help="Log Level")
    parser.add_argument("--tables", type=str, help="Tables list")

    parser.add_argument(
        "--ignore-validation",
        action="store_true",
        help="Ignore validation after fetching data",
    )

    # Parse command-line arguments
    args = parser.parse_args()

    # Construct raw config dictionary
    raw_config = {
        "CH_URL": args.ch_url,
        "DATABASES": args.databases,
        "FILE_OUTPUT": args.file_output,
        "EXCLUDED_DATABASES": args.excluded_databases,
        "LOG_LEVEL": args.log_level,
        "TABLES": args.tables,
        "IGNORE_VALIDATION": args.ignore_validation,
    }

    return DependencyTreeConfig(**raw_config)
