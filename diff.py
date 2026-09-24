from models import Workflow


def workflow_diff(
    old: Workflow,
    new: Workflow
):

    old_nodes = {
        node.id: node
        for node in old.nodes
    }

    new_nodes = {
        node.id: node
        for node in new.nodes
    }

    added_nodes = [
        node.model_dump()
        for node_id, node in new_nodes.items()
        if node_id not in old_nodes
    ]

    removed_nodes = [
        node.model_dump()
        for node_id, node in old_nodes.items()
        if node_id not in new_nodes
    ]

    old_edges = {
        f"{edge.source}->{edge.target}"
        for edge in old.edges
    }

    new_edges = {
        f"{edge.source}->{edge.target}"
        for edge in new.edges
    }

    return {
        "added_nodes": added_nodes,
        "removed_nodes": removed_nodes,
        "added_edges": list(
            new_edges - old_edges
        ),
        "removed_edges": list(
            old_edges - new_edges
        )
    }