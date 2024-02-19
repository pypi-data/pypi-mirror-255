from typing import Tuple

from anytree import Node as AnyNode, RenderTree
from clickhouse_s3_etl_tools.logger import get_logger

logger = get_logger(__name__)


def generate_tree(parents_by_id: dict) -> Tuple[AnyNode, dict[str, AnyNode]]:
    """
    Generate a tree structure from the dictionary of dependencies.

    Parameters:
    - parents_by_id: DependencyTableDict, the dictionary representing dependencies between tables.

    Returns:
    AnyNode: The root node of the generated tree.
    """
    root_id = "Global.root"
    global_node = AnyNode(root_id)
    nodes_by_id = {root_id: global_node}

    def set_parent(node_: str, parent_: str):
        if node_ in nodes_by_id:
            return nodes_by_id[node_]

        if parent_ in nodes_by_id and node_ not in nodes_by_id:
            nodes_by_id[node_] = AnyNode(node_, parent=nodes_by_id[parent_])
            return nodes_by_id[node_]

        if parent_ not in nodes_by_id:
            try:
                nodes_by_id[node_] = AnyNode(
                    node_,
                    parent=set_parent(parent_, parents_by_id[parent_]),
                )

            except KeyError as e:
                raise Exception(
                    f"The table {node_} depends of the table {parent_}. But this table doesn't exists"
                ) from e
            return nodes_by_id[node_]
        return nodes_by_id[node_]

    for node, parent in parents_by_id.items():
        set_parent(node, parent)

    return global_node, nodes_by_id


def print_dependency_tree(root):
    """
    Print the dependency tree.

    Parameters:
    - root: AnyNode, the root node of the tree.
    """
    for pre, _, node in RenderTree(root):
        print(pre, node.name)
