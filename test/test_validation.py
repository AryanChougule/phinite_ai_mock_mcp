from models import (
    Workflow,
    WorkflowNode,
    WorkflowEdge
)

from validation import validate_workflow


def test_valid_workflow():

    workflow = Workflow(
        id="workflow_1",
        name="Test Workflow",

        nodes=[
            WorkflowNode(
                id="input_1",
                type="input",
                name="Input"
            ),

            WorkflowNode(
                id="output_1",
                type="output",
                name="Output"
            )
        ],

        edges=[
            WorkflowEdge(
                source="input_1",
                target="output_1"
            )
        ]
    )

    result = validate_workflow(workflow)

    assert result["valid"] is True
    assert result["errors"] == []


def test_unknown_edge_target():

    workflow = Workflow(
        id="workflow_2",
        name="Invalid Workflow",

        nodes=[
            WorkflowNode(
                id="input_1",
                type="input",
                name="Input"
            )
        ],

        edges=[
            WorkflowEdge(
                source="input_1",
                target="does_not_exist"
            )
        ]
    )

    result = validate_workflow(workflow)

    assert result["valid"] is False

    assert any(
        "does_not_exist" in error
        for error in result["errors"]
    )


def test_empty_workflow():

    workflow = Workflow(
        id="workflow_3",
        name="Empty Workflow"
    )

    result = validate_workflow(workflow)

    assert result["valid"] is False

    assert any(
        "at least one node" in error
        for error in result["errors"]
    )


def test_duplicate_node_ids():

    workflow = Workflow(
        id="workflow_4",
        name="Duplicate Nodes",

        nodes=[
            WorkflowNode(
                id="node_1",
                type="input",
                name="Input"
            ),

            WorkflowNode(
                id="node_1",
                type="output",
                name="Output"
            )
        ]
    )

    result = validate_workflow(workflow)

    assert result["valid"] is False

    assert any(
        "duplicate" in error.lower()
        for error in result["errors"]
    )