from mcp.server.fastmcp import FastMCP
from backend import MockPhiniteBackend
from models import WorkflowNode, WorkflowEdge
from validation import validate_workflow


mcp = FastMCP("Phinite MCP")

backend = MockPhiniteBackend()



from models import WorkflowNode, WorkflowEdge


def initialize_demo_data():

    workflow = backend.create_workflow(
        name="Customer Support Agent",

        nodes=[
            WorkflowNode(
                id="input_1",
                type="input",
                name="Customer Ticket"
            ),

            WorkflowNode(
                id="classifier_1",
                type="agent",
                name="Ticket Classifier",
                config={
                    "model": "mock-gpt"
                }
            ),

            WorkflowNode(
                id="knowledge_1",
                type="tool",
                name="Knowledge Base",
                config={
                    "tool": "knowledge_search"
                }
            ),

            WorkflowNode(
                id="approval_1",
                type="approval",
                name="Human Approval"
            ),

            WorkflowNode(
                id="output_1",
                type="output",
                name="Customer Response"
            )
        ],

        edges=[
            WorkflowEdge(
                source="input_1",
                target="classifier_1"
            ),
            WorkflowEdge(
                source="classifier_1",
                target="knowledge_1"
            ),
            WorkflowEdge(
                source="knowledge_1",
                target="approval_1"
            ),
            WorkflowEdge(
                source="approval_1",
                target="output_1"
            )
        ]
    )

    backend.create_agent(
        name="Customer Support Agent",
        description="Handles customer support tickets.",
        workflow_id=workflow.id
    )


initialize_demo_data()

# ======================================================
# AGENTS
# ======================================================

@mcp.tool()
def add_workflow_edge(
    workflow_id: str,
    source: str,
    target: str
) -> dict:
    """
    Connect two nodes in a workflow.
    """

    edge = backend.add_edge(
        workflow_id=workflow_id,
        source=source,
        target=target
    )

    workflow = backend.get_workflow(
        workflow_id
    )

    validation = validate_workflow(
        workflow
    )

    return {
        "success": True,
        "edge": edge.model_dump(),
        "workflow": workflow.model_dump(),
        "validation": validation
    }
    
@mcp.tool()
def list_tools() -> list[dict]:
    """
    List tools available in the Phinite workspace.
    """

    return [
        tool.model_dump()
        for tool in backend.list_tools()
    ]

@mcp.tool()
def get_tool(tool_id: str) -> dict:
    """
    Get the configuration of a specific tool.
    """

    return backend.get_tool(
        tool_id
    ).model_dump()
    
@mcp.tool()
def create_tool(
    name: str,
    description: str,
    tool_type: str = "http"
) -> dict:
    """
    Create a new draft tool.

    Supported tool types:
    - http
    - webhook
    - function
    - database
    """

    allowed_types = {
        "http",
        "webhook",
        "function",
        "database"
    }

    if tool_type not in allowed_types:
        return {
            "success": False,
            "error": (
                f"Unsupported tool type: {tool_type}. "
                f"Supported types: {sorted(allowed_types)}"
            )
        }

    tool = backend.create_tool(
        name=name,
        description=description,
        tool_type=tool_type
    )

    return {
        "success": True,
        "tool": tool.model_dump()
    }

@mcp.tool()
def configure_tool(
    tool_id: str,
    config: dict
) -> dict:
    """
    Configure an existing tool.

    For HTTP tools, config can contain:
    method, url, headers, query_params, body_schema,
    response_schema, authentication.
    """

    tool = backend.configure_tool(
        tool_id=tool_id,
        config=config
    )

    return {
        "success": True,
        "tool": tool.model_dump()
    }
    
    
@mcp.tool()
def get_workflow_schema() -> dict:
    """
    Return the supported Phinite workflow node types.
    """

    return {
        "node_types": [
            {
                "type": "input",
                "description": "Receives workflow input."
            },
            {
                "type": "agent",
                "description": "Executes an AI agent."
            },
            {
                "type": "tool",
                "description": "Calls an external tool or integration."
            },
            {
                "type": "condition",
                "description": "Branches based on a condition."
            },
            {
                "type": "approval",
                "description": "Requires human approval."
            },
            {
                "type": "output",
                "description": "Returns workflow output."
            }
        ]
    }
    
@mcp.tool()
def test_workflow(
    workflow_id: str,
    input_data: dict
) -> dict:
    """
    Execute a workflow in mock/test mode.
    No production actions are performed.
    """

    workflow = backend.get_workflow(
        workflow_id
    )

    validation = validate_workflow(
        workflow
    )

    if not validation["valid"]:
        return {
            "success": False,
            "validation": validation
        }

    execution = []

    for node in workflow.nodes:

        execution.append({
            "node_id": node.id,
            "node_name": node.name,
            "type": node.type,
            "status": "success"
        })

    return {
        "success": True,
        "mode": "test",
        "workflow_id": workflow_id,
        "input": input_data,
        "execution": execution,
        "output": {
            "message": "Mock workflow execution completed."
        }
    }    

@mcp.tool()
def list_agents() -> list[dict]:
    """
    List all agents in the current Phinite workspace.
    """

    return [
        agent.model_dump()
        for agent in backend.list_agents()
    ]


@mcp.tool()
def get_agent(agent_id: str) -> dict:
    """
    Get the configuration and status of a specific agent.
    """

    return backend.get_agent(
        agent_id
    ).model_dump()


@mcp.tool()
def create_agent(
    name: str,
    description: str,
    workflow_id: str | None = None
) -> dict:
    """
    Create a new draft agent.
    """

    agent = backend.create_agent(
        name=name,
        description=description,
        workflow_id=workflow_id
    )

    return {
        "success": True,
        "agent": agent.model_dump()
    }


# ======================================================
# WORKFLOWS
# ======================================================

@mcp.tool()
def list_workflows() -> list[dict]:
    """
    List workflows in the workspace.
    """

    return [
        workflow.model_dump()
        for workflow in backend.list_workflows()
    ]


@mcp.tool()
def get_workflow(
    workflow_id: str
) -> dict:
    """
    Get a complete workflow graph.
    """

    return backend.get_workflow(
        workflow_id
    ).model_dump()


@mcp.tool()
def create_workflow_draft(
    name: str,
    nodes: list[dict],
    edges: list[dict]
) -> dict:
    """
    Create a new workflow draft.

    Nodes must contain:
    id, type, name, config.

    Edges must contain:
    source, target.
    """

    workflow_nodes = [
        WorkflowNode(**node)
        for node in nodes
    ]

    workflow_edges = [
        WorkflowEdge(**edge)
        for edge in edges
    ]

    workflow = backend.create_workflow(
        name=name,
        nodes=workflow_nodes,
        edges=workflow_edges
    )

    validation = validate_workflow(
        workflow
    )

    return {
        "success": True,
        "workflow": workflow.model_dump(),
        "validation": validation
    }


@mcp.tool()
def add_workflow_node(
    workflow_id: str,
    node_type: str,
    name: str,
    config: dict | None = None
) -> dict:
    """
    Add a node to an existing workflow.
    """

    node = backend.add_node(
        workflow_id=workflow_id,
        node_type=node_type,
        name=name,
        config=config
    )

    workflow = backend.get_workflow(
        workflow_id
    )

    validation = validate_workflow(
        workflow
    )

    return {
        "success": True,
        "node": node.model_dump(),
        "workflow": workflow.model_dump(),
        "validation": validation
    }


# ======================================================
# VALIDATION
# ======================================================

@mcp.tool()
def validate_workflow_tool(
    workflow_id: str
) -> dict:
    """
    Validate a workflow before it is published.
    """

    workflow = backend.get_workflow(
        workflow_id
    )

    return {
        "workflow_id": workflow_id,
        "version": workflow.version,
        **validate_workflow(workflow)
    }


# ======================================================
# VERSIONING
# ======================================================

@mcp.tool()
def get_workflow_versions(
    workflow_id: str
) -> list[dict]:
    """
    Get all saved versions of a workflow.
    """

    versions = backend.get_versions(
        workflow_id
    )

    return [
        {
            "version": workflow.version,
            "workflow": workflow.model_dump()
        }
        for workflow in versions
    ]


# ======================================================
# APPROVAL
# ======================================================

@mcp.tool()
def request_publish_approval(
    workflow_id: str,
    comment: str | None = None
) -> dict:
    """
    Request human approval before publishing a workflow.
    """

    validation = validate_workflow_tool(
        workflow_id
    )

    if not validation["valid"]:
        return {
            "success": False,
            "reason": "Workflow validation failed.",
            "validation": validation
        }

    approval = backend.request_approval(
        workflow_id,
        comment
    )

    return {
        "success": True,
        "approval": approval.model_dump()
    }


@mcp.tool()
def approve_publish(
    approval_id: str
) -> dict:
    """
    Approve a pending workflow publication.
    """

    approval = backend.approve(
        approval_id
    )

    return {
        "success": True,
        "approval": approval.model_dump()
    }


# ======================================================
# PUBLISH
# ======================================================

@mcp.tool()
def publish_workflow(
    workflow_id: str
) -> dict:
    """
    Publish an approved workflow.
    """

    validation = validate_workflow_tool(
        workflow_id
    )

    if not validation["valid"]:
        return {
            "success": False,
            "reason": "Validation failed.",
            "validation": validation
        }

    workflow = backend.publish_workflow(
        workflow_id
    )

    return {
        "success": True,
        "workflow": workflow.model_dump()
    }


# ======================================================
# AUDIT
# ======================================================

@mcp.tool()
def get_audit_logs() -> list[dict]:
    """
    Return the audit trail of MCP operations.
    """

    return [
        event.model_dump()
        for event in backend.get_audit_logs()
    ]


# ======================================================
# SERVER
# ======================================================

if __name__ == "__main__":
    mcp.run(
        transport="stdio"
    )