from models import Workflow


def validate_workflow(workflow: Workflow) -> dict:

    errors = []
    warnings = []

    node_ids = [node.id for node in workflow.nodes]

    # Duplicate IDs
    if len(node_ids) != len(set(node_ids)):
        errors.append("Workflow contains duplicate node IDs.")

    valid_ids = set(node_ids)

    # Check edges
    for edge in workflow.edges:

        if edge.source not in valid_ids:
            errors.append(
                f"Edge references unknown source node: {edge.source}"
            )

        if edge.target not in valid_ids:
            errors.append(
                f"Edge references unknown target node: {edge.target}"
            )

    # Empty workflow
    if not workflow.nodes:
        errors.append("Workflow must contain at least one node.")

    # Input
    inputs = [
        node for node in workflow.nodes
        if node.type == "input"
    ]

    if not inputs:
        warnings.append(
            "Workflow does not contain an input node."
        )

    # Output
    outputs = [
        node for node in workflow.nodes
        if node.type == "output"
    ]

    if not outputs:
        warnings.append(
            "Workflow does not contain an output node."
        )

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings
    }