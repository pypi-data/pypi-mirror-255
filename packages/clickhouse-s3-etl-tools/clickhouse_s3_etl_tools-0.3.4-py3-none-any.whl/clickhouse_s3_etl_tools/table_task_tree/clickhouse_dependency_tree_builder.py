from typing import List, Dict, Tuple, Any
from urllib.parse import urlparse
from clickhouse_driver import Client


def get_key(database: str, table_name: str) -> str:
    """
    Generate a unique key for a table based on its database and name.

    Args:
        database (str): The name of the database.
        table_name (str): The name of the table.

    Returns:
        str: The generated key.
    """
    return f"{database}.{table_name}"


def process_dependencies(
    table_config: Dict[str, Any],
    table_node: str,
    parents_by_id: Dict[str, str],
    trigger_with_parent: Dict[str, str],
    excluded_databases: List[str],
) -> None:
    """
    Process dependencies for a table and update dictionaries.

    Args:
        table_config (Dict[str, Any]): Configuration of the table.
        table_node (str): The unique key representing the table.
        parents_by_id (Dict[str, str]): Dictionary of parent-child relationships.
        trigger_with_parent (Dict[str, str]): Dictionary of trigger relationships.
        excluded_databases (List[str]):
    """
    global_root = "Global.root"
    parents_by_id.setdefault(table_node, global_root)

    for dep_db, dep_table in zip(
        table_config["DEPENDENCIES_DATABASE"], table_config["DEPENDENCIES_TABLE"]
    ):
        if dep_db not in excluded_databases:
            table_node_dep = get_key(table_name=dep_table, database=dep_db)
            parents_by_id[table_node_dep] = table_node

    if (
        table_config["EXTRACTED_TABLE_NAME"] != ""
        and table_config["ENGINE"] == "MaterializedView"
    ):
        handle_materialized_view_dependency(
            table_config, table_node, trigger_with_parent
        )

    if table_config["EXTRACTED_TABLE_NAME_FROM"] != "" and table_config["ENGINE"] in (
        "View",
        "MaterializedView",
    ):
        handle_view_dependency(
            table_config, table_node, parents_by_id, excluded_databases
        )


def handle_materialized_view_dependency(
    table_config: Dict[str, Any], table_node: str, trigger_with_parent: Dict[str, str]
) -> None:
    """
    Handle materialized view dependencies.

    Args:
        table_config (Dict[str, Any]): Configuration of the table.
        table_node (str): The unique key representing the table.
        trigger_with_parent (Dict[str, str]): Dictionary of trigger relationships.
    """
    db_ext, table_ext = table_config["EXTRACTED_TABLE_NAME"].split(".")
    table_node_ext = get_key(table_name=table_ext, database=db_ext)
    trigger_with_parent[table_node] = table_node_ext


def handle_view_dependency(
    table_config: Dict[str, Any],
    table_node: str,
    parents_by_id: Dict[str, str],
    excluded_databases: List[str],
) -> None:
    """
    Handle view dependencies.

    Args:
        table_config (Dict[str, Any]): Configuration of the table.
        table_node (str): The unique key representing the table.
        parents_by_id (Dict[str, str]): Dictionary of parent-child relationships.
        excluded_databases (List[str]):
    """
    db_view, table_view = table_config["EXTRACTED_TABLE_NAME_FROM"].split(".")
    if db_view not in excluded_databases:
        table_node_view = get_key(table_name=table_view, database=db_view)
        parents_by_id[table_node] = table_node_view


def validate_tables_and_dependencies(
    parents_by_id: Dict[str, str], tables: List[Dict[str, Any]]
) -> None:
    """
    Validate tables and their dependencies.

    Args:
        parents_by_id (Dict[str, str]): Dictionary of parent-child relationships.
        tables (List[Dict[str, Any]]): List of table configurations.

    Raises:
        AssertionError: If there are inconsistencies in tables and dependencies.
    """
    table_names_databases = [
        get_key(table_name=table["TABLE_NAME"], database=table["DATABASE"])
        for table in tables
    ]
    dependency_ids = list(parents_by_id.keys())
    difference = set(dependency_ids) - set(table_names_databases)
    difference_ = set(table_names_databases) - set(dependency_ids)

    # Create a list of problematic tables
    problematic_tables = [
        (x, d) for d in difference for x, node in parents_by_id.items() if node == d
    ]

    # Generate an error message with information about problematic tables
    error_message = "Inconsistent tables and dependency tree:\n"
    error_message += "\n".join(
        [
            f"{dependency_id} is in the tree but not in the tables list.\n"
            f"This table {table} depends on {dependency_id}, but {dependency_id} doesn't exist."
            for table, dependency_id in problematic_tables
        ]
    )

    # Check for problematic tables and raise an assertion error if any
    assert not problematic_tables, error_message
    assert len(difference_) == 0, difference_
    assert (
        len(difference) == 0
    ), f"{difference} was not found in tables list. Whether database '{difference.pop().split('.')[0]}' is in the tables list"
    assert len(tables) == len(set(parents_by_id.keys()))


def update_dependency_dict(
    dict_for_update: Dict[str, str], main_dict: Dict[str, str]
) -> Dict[str, str]:
    """
    Update the main dependency dictionary with the entries from another dictionary.

    Args:
        dict_for_update (Dict[str, str]): The dictionary to update from.
        main_dict (Dict[str, str]): The main dictionary to update.

    Returns:
        Dict[str, str]: The updated main dictionary.
    """
    main_dict_copy: Dict[str, str] = {}
    dict_for_update_reverse = {value: key for key, value in dict_for_update.items()}

    for node, parent in main_dict.items():
        if node in main_dict_copy:
            parent = main_dict_copy[node]

            if (
                parent in dict_for_update_reverse
                and dict_for_update_reverse[parent] != node
            ):
                main_dict_copy[node] = dict_for_update_reverse[parent]

        if node in dict_for_update and node not in main_dict_copy:
            parent_trigger_node = dict_for_update[node]

            for node_, parent_ in main_dict.items():
                if node_ == node:
                    main_dict_copy[node] = parent_trigger_node
                    main_dict_copy[parent_trigger_node] = parent_

            for node_, parent_ in main_dict.items():
                if parent_ == parent_trigger_node:
                    if node_ in dict_for_update:
                        parent_trigger_node_ = dict_for_update[node_]
                        main_dict_copy[node_] = parent_trigger_node_
                        main_dict_copy[parent_trigger_node_] = node
                    else:
                        main_dict_copy[node_] = node
                    main_dict_copy[node] = parent_

        elif node not in main_dict_copy:
            main_dict_copy[node] = parent

    return main_dict_copy


def get_dict_dependencies(
    url: str,
    databases: List[str],
    excluded_databases: List[str] = None,
    tables: List[str] = None,
    ignore_validation: bool = False,
) -> Tuple[Dict[str, str], List[Dict[str, Any]]]:
    """
    Retrieve dependencies between tables from ClickHouse.

    Args:
        url (str): The URL of the ClickHouse instance.
        databases (List[str]): List of databases to consider.

    Returns:
        Tuple[Dict[str, str], List[Dict[str, Any]]]: Tuple containing the dictionary representing dependencies
        between tables and a list of table configurations.
        excluded_databases: do not show database
        table: if specified show dependencies only for one table

    """
    url_ = urlparse(url)
    conn_params = {
        "host": url_.hostname,
        "port": url_.port or 9000,
        "database": url_.path.lstrip("/"),
        "user": url_.username,
        "password": url_.password,
    }

    client = Client(**conn_params)

    query = f"""SELECT  table, 
                        database, 
                        ifNull(total_rows,0) as total_rows,
                        dependencies_database, 
                        dependencies_table, 
                        engine,
                        arrayElement(extractAll(create_table_query, 'TO (\\S+)'), 1) AS extracted_table_name, 
                        replace(arrayElement(extractAll(as_select, 'FROM (\\S+)'), -1), ')', '') AS extracted_table_name_from
              FROM system.tables 
              WHERE 1 = 1
              """
    if not excluded_databases:
        excluded_databases = []

    if databases:
        databases_str = ",".join([f"'{d}'" for d in databases])
        query += f" AND  database in ({databases_str}) "

    if tables:
        tables_str = ",".join([f"'{d}'" for d in tables])
        query += f" AND table in ({tables_str}) "

    result = client.execute(query)

    parents_by_id: Dict[str, str] = {}
    trigger_with_parent: Dict[str, str] = {}
    tables: List[Dict[str, Any]] = []

    for row in result:
        table_config = {
            "TABLE_NAME": row[0],
            "DATABASE": row[1],
            "TOTAL_ROWS": row[2],
            "DEPENDENCIES_DATABASE": row[3],
            "DEPENDENCIES_TABLE": row[4],
            "ENGINE": row[5],
            "EXTRACTED_TABLE_NAME": row[6],
            "EXTRACTED_TABLE_NAME_FROM": row[7],
        }

        tables.append(table_config)
        table_node = get_key(
            table_name=table_config["TABLE_NAME"], database=table_config["DATABASE"]
        )
        process_dependencies(
            table_config,
            table_node,
            parents_by_id,
            trigger_with_parent,
            excluded_databases,
        )

    parents_by_id = update_dependency_dict(trigger_with_parent, parents_by_id)
    if not ignore_validation:
        validate_tables_and_dependencies(parents_by_id, tables)

    return parents_by_id, tables
