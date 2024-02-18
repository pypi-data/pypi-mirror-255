import logging
import pytest
from dotenv import load_dotenv
from clickhouse_s3_etl_tools.utils import update_create_table_query
from clickhouse_s3_etl_tools.configs.config_module import get_configuration
from clickhouse_s3_etl_tools.schema.schema_configs import TableConfiguration

load_dotenv(".env-test")


def test_update_create_table_query_collapsed():
    table: TableConfiguration = TableConfiguration(
        **{"TABLE_NAME": "table1", "DATABASE": "test", "DATABASE_DESTINATION": "test2"}
    )
    ddl_test = """CREATE TABLE test.table1 (`column1` Int64) ENGINE = ReplicatedCollapsingMergeTree('path', '{replica}', Sign)"""
    assert (
        update_create_table_query(ddl_test, table)
        == """CREATE TABLE test2.table1 (`column1` Int64) ENGINE = CollapsingMergeTree(Sign)"""
    )


def test_create_table_query_replicated_collapsed():
    table: TableConfiguration = TableConfiguration(
        **{"TABLE_NAME": "table1", "DATABASE": "test", "DATABASE_DESTINATION": "test2"}
    )
    ddl_test = """CREATE TABLE test.table1 (`column1` Int64) ENGINE = ReplicatedCollapsingMergeTree('path', '{replica}', Sign)"""
    assert (
        update_create_table_query(ddl_test, table, "{cluster}")
        == """CREATE TABLE test2.table1 ON CLUSTER '{cluster}' (`column1` Int64) ENGINE = ReplicatedCollapsingMergeTree(Sign)"""
    )


def test_update_replicated_to_reg():
    table: TableConfiguration = TableConfiguration(
        **{"TABLE_NAME": "table1", "DATABASE": "test", "DATABASE_DESTINATION": "test2"}
    )
    ddl_test = """CREATE TABLE test.table1 (`column1` Int64) ENGINE = ReplicatedMergeTree('patsgsgsg')"""

    assert (
        update_create_table_query(ddl_test, table)
        == """CREATE TABLE test2.table1 (`column1` Int64) ENGINE = MergeTree()"""
    )


def test_update_replicated_to_reg_second():
    table: TableConfiguration = TableConfiguration(
        **{"TABLE_NAME": "table1", "DATABASE": "test", "DATABASE_DESTINATION": "test2"}
    )

    ddl_test = "CREATE TABLE netology.orders_rick (`orders_order_id` Int32, `orders_user_id` Int32, `orders_programs_title` Nullable(String), `orders_programs_urlcode` Nullable(String), `urlcode_start_date` Date, `urlcode_finish_date` Nullable(Date), `type_users` String, `payment_id` Nullable(Int32), `buyer_id` Nullable(Int32), `revenue` Nullable(Float32), `orders_price` Nullable(Float32), `orders_add_date` Date, `orders_pay_date` Nullable(Date), `_min_pay_date` Nullable(Date), `orders_status` Nullable(Int32), `users_reg_date` Nullable(Date), `rick_order_id` Int32, `rick_user_ids` String, `rick_client_id` String, `rick_channel_group` String, `rick_channel_grouping` String, `rick_channel_type` String, `rick_source_medium` String, `rick_real_source_medium` String, `rick_campaign` String, `rick_keyword` String, `rick_date` Nullable(Date), `rick_sess_count` Int64, `rick_actions` String, `FCC_date` Nullable(Date), `FCC_sess_num` Int64, `FCC_channel_group` String, `FCC_channel_grouping` String, `FCC_channel_type` String, `FCC_source_medium` String, `FCC_campaign` String, `FCC_keyword` String, `rick_user_id` Int32, `is_many_users` String, `FCU_client_id` String, `FCU_date` Nullable(Date), `FCU_sess_num` Int64, `FCU_channel_group` String, `FCU_channel_grouping` String, `FCU_channel_type` String, `FCU_source_medium` String, `FCU_campaign` String, `FCU_keyword` String) ENGINE = ReplicatedMergeTree('/clickhouse/tables/45dfb642-aefd-405c-85df-b642aefd205c/{shard}', \
                '{replica}') PARTITION BY tuple() ORDER BY orders_order_id SETTINGS index_granularity = 8192"
    assert (
        update_create_table_query(ddl_test, table)
        == "CREATE TABLE netology.orders_rick (`orders_order_id` Int32, `orders_user_id` Int32, `orders_programs_title` Nullable(String), `orders_programs_urlcode` Nullable(String), `urlcode_start_date` Date, `urlcode_finish_date` Nullable(Date), `type_users` String, `payment_id` Nullable(Int32), `buyer_id` Nullable(Int32), `revenue` Nullable(Float32), `orders_price` Nullable(Float32), `orders_add_date` Date, `orders_pay_date` Nullable(Date), `_min_pay_date` Nullable(Date), `orders_status` Nullable(Int32), `users_reg_date` Nullable(Date), `rick_order_id` Int32, `rick_user_ids` String, `rick_client_id` String, `rick_channel_group` String, `rick_channel_grouping` String, `rick_channel_type` String, `rick_source_medium` String, `rick_real_source_medium` String, `rick_campaign` String, `rick_keyword` String, `rick_date` Nullable(Date), `rick_sess_count` Int64, `rick_actions` String, `FCC_date` Nullable(Date), `FCC_sess_num` Int64, `FCC_channel_group` String, `FCC_channel_grouping` String, `FCC_channel_type` String, `FCC_source_medium` String, `FCC_campaign` String, `FCC_keyword` String, `rick_user_id` Int32, `is_many_users` String, `FCU_client_id` String, `FCU_date` Nullable(Date), `FCU_sess_num` Int64, `FCU_channel_group` String, `FCU_channel_grouping` String, `FCU_channel_type` String, `FCU_source_medium` String, `FCU_campaign` String, `FCU_keyword` String) ENGINE = MergeTree() PARTITION BY tuple() ORDER BY orders_order_id SETTINGS index_granularity = 8192"
    )


def test_update_replicated_to_replicated():
    table: TableConfiguration = TableConfiguration(
        **{"TABLE_NAME": "table1", "DATABASE": "test", "DATABASE_DESTINATION": "test2"}
    )
    ddl_test = """CREATE TABLE test.table1 (`column1` Int64) ENGINE = ReplicatedMergeTree('patsgsgsg')"""

    assert (
        update_create_table_query(ddl_test, table, "{cluster}")
        == """CREATE TABLE test2.table1 ON CLUSTER '{cluster}' (`column1` Int64) ENGINE = ReplicatedMergeTree()"""
    )


def test_regular_to_replicated():
    table: TableConfiguration = TableConfiguration(
        **{"TABLE_NAME": "table1", "DATABASE": "test", "DATABASE_DESTINATION": "test2"}
    )
    ddl_test = (
        """CREATE TABLE test.table1 (`column1` Int64) ENGINE = MergeTree('patsgsgsg')"""
    )

    assert (
        update_create_table_query(ddl_test, table, "{cluster}")
        == """CREATE TABLE test2.table1 ON CLUSTER '{cluster}' (`column1` Int64) ENGINE = ReplicatedMergeTree()"""
    )


def test_regular_to_replicated_collapsed():
    table: TableConfiguration = TableConfiguration(
        **{"TABLE_NAME": "table1", "DATABASE": "test", "DATABASE_DESTINATION": "test2"}
    )
    ddl_test = """CREATE TABLE test.table1 (`column1` Int64) ENGINE = CollapsingMergeTree('patsgsgsg')"""

    assert (
        update_create_table_query(ddl_test, table, "{cluster}")
        == """CREATE TABLE test2.table1 ON CLUSTER '{cluster}' (`column1` Int64) ENGINE = ReplicatedCollapsingMergeTree('patsgsgsg')"""
    )


def test_regular_to_replicated_2():
    table: TableConfiguration = TableConfiguration(
        **{"TABLE_NAME": "table1", "DATABASE": "test", "DATABASE_DESTINATION": "test2"}
    )
    ddl_test = """CREATE TABLE test.table1 (`column1` Int64) ENGINE = MergeTree"""

    assert (
        update_create_table_query(ddl_test, table, "{cluster}")
        == """CREATE TABLE test2.table1 ON CLUSTER '{cluster}' (`column1` Int64) ENGINE = ReplicatedMergeTree()"""
    )


def test_depended_talbe():
    table: TableConfiguration = TableConfiguration(
        **{"TABLE_NAME": "table1", "DATABASE": "test", "DATABASE_DESTINATION": "test2"}
    )

    ddl_test = """CREATE MATERIALIZED VIEW test.table1
(
    `sid_long` String,
    `date` Date
)
ENGINE = MergeTree
PARTITION BY tuple()
ORDER BY (sid_long, date)
SETTINGS index_granularity = 8192 AS
SELECT
    sid_long,
    date
FROM test11.clickstream"""

    assert (
        update_create_table_query(ddl_test, table, databases_map="test11:test2")
        == """CREATE MATERIALIZED VIEW test2.table1
(
    `sid_long` String,
    `date` Date
)
ENGINE = MergeTree
PARTITION BY tuple()
ORDER BY (sid_long, date)
SETTINGS index_granularity = 8192 AS
SELECT
    sid_long,
    date
FROM test2.clickstream"""
    )


def test_name_exists_in_ddl_():
    table: TableConfiguration = TableConfiguration(
        **{
            "TABLE_NAME": "accounts_account_users",
            "DATABASE": "test",
            "DATABASE_DESTINATION": "test2",
        }
    )

    ddl_test = """CREATE VIEW test.accounts_account_users  (`account_id` String, `user_id` String) AS
                    SELECT account_id,
                    user_id
                    FROM
                    (SELECT JSONExtractString(data, 'user_id') AS user_id,
                    JSONExtractString(data, 'account_id') AS account_id,
                    JSONExtractInt(data, '__ts_ms') AS __ts_ms,
                    JSONExtractString(data, '__deleted') AS deleted, timestamp
                    FROM test.accounts_account_users_events) WHERE deleted = 'false'
"""
    assert (
        update_create_table_query(ddl_test, table, cluster_name="{cluster}")
        .replace("\n", "")
        .replace(" ", "")
        == """CREATE VIEW test2.accounts_account_users ON CLUSTER'{cluster}'   (`account_id` String, `user_id` String) AS
    SELECT account_id,
    user_id
    FROM
    (SELECT JSONExtractString(data, 'user_id') AS user_id,
    JSONExtractString(data, 'account_id') AS account_id,
    JSONExtractInt(data, '__ts_ms') AS __ts_ms,
    JSONExtractString(data, '__deleted') AS deleted, timestamp
    FROM test2.accounts_account_users_events) WHERE deleted = 'false'
 """.replace(
            "\n", ""
        ).replace(
            " ", ""
        )
    )


def test_replace_engine_full():
    table: TableConfiguration = TableConfiguration(
        **{
            "TABLE_NAME": "accounts_account_users",
            "DATABASE": "test",
            "DATABASE_DESTINATION": "test2",
        }
    )

    ddl_test = """CREATE TABLE netology.clickstream (`client_id` String, `tracker_id` String) ENGINE = ReplicatedMergeTree() PARTITION BY toYYYYMMDD(date) ORDER BY ts_captured TTL date + toIntervalMonth(12) TO VOLUME 'object_storage' SETTINGS index_granularity = 8192"""
    engine_from = "ReplicatedMergeTree() PARTITION BY toYYYYMMDD(date) ORDER BY ts_captured TTL date + toIntervalMonth(12) TO VOLUME 'object_storage' SETTINGS index_granularity = 8192"
    assert (
        update_create_table_query(
            ddl_test,
            table,
            cluster_name="{cluster}",
            engine_full_to_replace=(
                engine_from,
                "ReplicatedMergeTree() PARTITION BY toYYYYMMDD(date) ORDER BY ts_captured",
            ),
        )
        == "CREATE TABLE netology.clickstream (`client_id` String, `tracker_id` String) ENGINE = ReplicatedMergeTree() PARTITION BY toYYYYMMDD(date) ORDER BY ts_captured"
    )
