import logging
import os

import pytest
import copy
from conftest import (
    initialize_tests,
    create_and_fill_table,
    create_bucket_clear_directory,
    create_view,
    create_database,
    check_number_and_sum,
    create_table_with_invalid_column_name,
    create_view_depended_of_diff_databases,
    TABLE_NAME,
)
from clickhouse_s3_etl_tools.s3_exporter.s3_exporter import export_to_s3
from clickhouse_s3_etl_tools.s3_to_clickhouse_transfer.s3_to_clickhouse_transfer import (
    transfer_s3_to_clickhouse,
)
from clickhouse_s3_etl_tools.schema.schema_configs import Configuration
from clickhouse_s3_etl_tools.connectors.s3_connector import S3Connector
from clickhouse_s3_etl_tools.connectors.clickhouse_connector import ClickHouseConnector


#
@pytest.mark.parametrize(
    "create_and_fill_table, create_bucket_clear_directory",
    [pytest.param(None, None, marks=pytest.mark.dependency(name="test_export_common"))],
    indirect=["create_and_fill_table", "create_bucket_clear_directory"],
)
def test_export(create_and_fill_table, create_bucket_clear_directory, initialize_tests):
    export_to_s3(initialize_tests)


@pytest.mark.parametrize(
    "create_and_fill_table, create_bucket_clear_directory",
    [
        pytest.param(
            "test_by_part",
            "test_by_part",
            marks=pytest.mark.dependency(name="test_export_by_part"),
        )
    ],
    indirect=["create_and_fill_table", "create_bucket_clear_directory"],
)
def test_export_by_not_part_field(
    initialize_tests, create_and_fill_table, create_bucket_clear_directory
):
    config: Configuration = copy.deepcopy(initialize_tests)
    config.table.TABLE_NAME = "test_by_part"
    config.PARTITION_KEY = "column2"
    export_to_s3(config)


@pytest.mark.parametrize(
    "create_view, create_bucket_clear_directory",
    [
        pytest.param(
            "_view_suffix",
            f"{TABLE_NAME}_view_suffix",
            marks=pytest.mark.dependency(name="test_export_view"),
        )
    ],
    indirect=["create_view", "create_bucket_clear_directory"],
)
def test_export_view(create_view, create_bucket_clear_directory, initialize_tests):
    config_: Configuration = copy.deepcopy(initialize_tests)
    config_.table.TABLE_NAME = config_.table.TABLE_NAME + "_view_suffix"
    export_to_s3(config_)
    # only metadata exists
    with S3Connector(config_.s3) as s3_conn:
        s3_path_folder: str = f"{config_.table.DATABASE}/{config_.table.TABLE_NAME}"
        meta_path: str = (
            f"{s3_path_folder}/__metadata__{config_.table.TABLE_NAME}.parquet"
        )
        file_list = s3_conn.get_file_list(s3_path_folder)
        assert meta_path in file_list, f"No {meta_path} in s3 folder for metadata"
        assert (
            len(file_list) == 1
        ), f"Only {meta_path} should be in folder for {config_.table.TABLE_NAME}"


@pytest.mark.dependency(depends=["test_export_common"], name="test_transfer_common")
def test_transfer(initialize_tests):
    config = initialize_tests
    transfer_s3_to_clickhouse(initialize_tests)
    check_number_and_sum(config)


@pytest.mark.dependency(depends=["test_export_by_part"])
def test_transfer_by_part(initialize_tests):
    config: Configuration = copy.deepcopy(initialize_tests)
    config.table.TABLE_NAME = "test_by_part"
    transfer_s3_to_clickhouse(config)
    check_number_and_sum(config)


@pytest.mark.dependency(depends=["test_export_view", "test_transfer_common"])
def test_transfer_by_view(initialize_tests):
    config: Configuration = copy.deepcopy(initialize_tests)
    config.table.TABLE_NAME = config.table.TABLE_NAME + "_view_suffix"
    transfer_s3_to_clickhouse(config)
    check_number_and_sum(config)


@pytest.mark.parametrize("create_cascade_tables", ["table_cascade"], indirect=True)
def test_transfer_by_null(create_cascade_tables, initialize_tests):
    config: Configuration = copy.deepcopy(initialize_tests)
    config.table.TABLE_NAME = "table_cascade_null"
    export_to_s3(config)
    transfer_s3_to_clickhouse(config)
    check_number_and_sum(config)


@pytest.mark.parametrize(
    "create_table_with_invalid_column_name", ["table_invalid_name"], indirect=True
)
def test_transfer_with_invalid_columns(
    create_table_with_invalid_column_name, initialize_tests
):
    config: Configuration = copy.deepcopy(initialize_tests)
    config.table.TABLE_NAME = "table_invalid_name"
    export_to_s3(config)
    transfer_s3_to_clickhouse(config)
    check_number_and_sum(config, column_sum="id")


@pytest.mark.parametrize(
    "create_and_fill_table, create_bucket_clear_directory",
    [pytest.param("test_clear", None)],
    indirect=["create_and_fill_table", "create_bucket_clear_directory"],
)
def test_s3_clear(
    create_and_fill_table, create_bucket_clear_directory, initialize_tests
):
    config: Configuration = copy.deepcopy(initialize_tests)
    config.table.TABLE_NAME = "test_clear"
    config.s3.PATH_S3 = config.s3.PATH_S3 + "/backup/test"
    export_to_s3(config)
    s3_path_folder: str = f"{config.table.DATABASE}/test_clear"
    with S3Connector(config.s3) as s3_conn:
        file_list = s3_conn.get_file_list(s3_path_folder)
        assert len(file_list) > 0, f"Directory should'nt be empty"
        s3_conn.drop_table_directory_if_exists(s3_path_folder)
        file_list = s3_conn.get_file_list(s3_path_folder)
        assert len(file_list) == 0, f"Directory  have to be empty"


@pytest.mark.parametrize(
    "create_and_fill_table, create_bucket_clear_directory",
    [pytest.param("test_clear_no_sub_path", None)],
    indirect=["create_and_fill_table", "create_bucket_clear_directory"],
)
def test_s3_clear_no_sub_path(
    create_and_fill_table, create_bucket_clear_directory, initialize_tests
):
    config: Configuration = copy.deepcopy(initialize_tests)
    config.table.TABLE_NAME = "test_clear_no_sub_path"
    export_to_s3(config)
    s3_path_folder: str = f"{config.table.DATABASE}/test_clear_no_sub_path"
    with S3Connector(config.s3) as s3_conn:
        file_list = s3_conn.get_file_list(s3_path_folder)
        assert len(file_list) > 0, f"Directory should'nt be empty"
        s3_conn.drop_table_directory_if_exists(s3_path_folder)
        file_list = s3_conn.get_file_list(s3_path_folder)
        assert len(file_list) == 0, f"Directory  have to be empty"


@pytest.mark.parametrize(
    "create_bucket_clear_directory, create_view_depended_of_diff_databases",
    [pytest.param("test_multiple_dependencies", "test_multiple_dependencies")],
    indirect=[
        "create_view_depended_of_diff_databases",
        "create_bucket_clear_directory",
    ],
)
def test_multiple_dependences(
    create_view_depended_of_diff_databases,
    create_bucket_clear_directory,
    initialize_tests,
):
    config: Configuration = copy.deepcopy(initialize_tests)
    config.table.TABLE_NAME = "test_multiple_dependencies"
    config.DATABASES_MAP = "black:test2,white:test2"
    export_to_s3(config)
    transfer_s3_to_clickhouse(config)

    with ClickHouseConnector(config.clickhouse.CH_URL_DESTINATION) as conn:
        assert (
            conn.get_table_metadata(
                config.table.DATABASE_DESTINATION, config.table.TABLE_NAME
            ).create_table_query
            == "CREATE MATERIALIZED VIEW test2.test_multiple_dependencies (`id` Int32, `column1` String) ENGINE = MergeTree PARTITION BY tuple() ORDER BY id SETTINGS index_granularity = 8192 AS SELECT t.id, t.column1 FROM test2.test AS t LEFT JOIN test2.test AS t2 ON t.id = t2.id LIMIT 5"
            == "CREATE MATERIALIZED VIEW test2.test_multiple_dependencies (`id` Int32, `column1` String) ENGINE = MergeTree PARTITION BY tuple() ORDER BY id SETTINGS index_granularity = 8192 AS SELECT t.id, t.column1 FROM test2.test AS t LEFT JOIN test2.test AS t2 ON t.id = t2.id LIMIT 5"
        )
