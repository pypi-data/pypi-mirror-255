import os
import logging
import pytest
from conftest import create_cascade_tables
from clickhouse_s3_etl_tools.table_task_tree.clickhouse_dependency_tree_builder import (
    get_dict_dependencies,
)
from clickhouse_s3_etl_tools.table_task_tree.tree_drawer import (
    print_dependency_tree,
    generate_tree,
)
from dotenv import load_dotenv

load_dotenv(".env-test")


@pytest.mark.parametrize("create_cascade_tables", ["table_cascade"], indirect=True)
def test_draw_tree(create_cascade_tables):
    parents_by_id, tables = get_dict_dependencies(
        url=os.getenv("CH_URL_SOURCE"), databases=[os.getenv("DATABASE")]
    )
    logging.info(parents_by_id)
    root, nodes_by_id = generate_tree(parents_by_id)

    print_dependency_tree(root)

    assert (
        nodes_by_id["test.table_cascade_null"].parent == nodes_by_id["Global.root"]
    ), "Error parent of test._trigger_table_cascade_null is not Global.root"

    assert (
        nodes_by_id["test.table_cascade_amt"].parent
        == nodes_by_id["test.table_cascade_null"]
    ), "Error parent of test.table_cascade_amt is not test.table_cascade_null"

    assert (
        nodes_by_id["test._trigger_table_cascade_amt"].parent
        == nodes_by_id["test.table_cascade_amt"]
    ), "Error parent of test._trigger_table_cascade_amt is not test.table_cascade_amt"

    assert (
        nodes_by_id["test.table_cascade_view"].parent
        == nodes_by_id["test._trigger_table_cascade_amt"]
    ), "Error parent of test.table_cascade_view is not test._trigger_table_cascade_amt"
