from models import (
    Agent,
    Workflow,
    WorkflowNode,
    WorkflowEdge,
    Approval,
    AuditEvent,
    Tool
)


class MockPhiniteBackend:

    def __init__(self):

        self.agents: dict[str, Agent] = {}
        self.workflows: dict[str, Workflow] = {}

        self.tools: dict[str, Tool] = {}
        self.tool_counter = 0
        
        self.approvals: dict[str, Approval] = {}
        self.audit_logs: list[AuditEvent] = []

        self.workflow_versions: dict[str, list[Workflow]] = {}

        self.agent_counter = 0
        self.workflow_counter = 0
        self.node_counter = 0
        self.approval_counter = 0
        self.audit_counter = 0

    # --------------------------------------------------
    # Audit
    # --------------------------------------------------

    def audit(
        self,
        action: str,
        resource_type: str,
        resource_id: str,
        details: dict | None = None
    ):

        self.audit_counter += 1

        event = AuditEvent(
            id=f"audit_{self.audit_counter}",
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            actor="claude",
            details=details or {}
        )

        self.audit_logs.append(event)

    # --------------------------------------------------
    # Agents
    # --------------------------------------------------

    def list_agents(self):

        return list(self.agents.values())

    def get_agent(self, agent_id: str):

        if agent_id not in self.agents:
            raise ValueError(
                f"Agent '{agent_id}' not found."
            )

        return self.agents[agent_id]

    def create_agent(
        self,
        name: str,
        description: str,
        workflow_id: str | None = None
    ):

        self.agent_counter += 1

        agent = Agent(
            id=f"agent_{self.agent_counter}",
            name=name,
            description=description,
            workflow_id=workflow_id,
            status="draft"
        )

        self.agents[agent.id] = agent

        self.audit(
            "create",
            "agent",
            agent.id
        )

        return agent

    # --------------------------------------------------
    # Workflows
    # --------------------------------------------------

    def list_workflows(self):

        return list(self.workflows.values())

    def get_workflow(self, workflow_id: str):

        if workflow_id not in self.workflows:
            raise ValueError(
                f"Workflow '{workflow_id}' not found."
            )

        return self.workflows[workflow_id]

    def create_workflow(
        self,
        name: str,
        nodes: list[WorkflowNode],
        edges: list[WorkflowEdge]
    ):

        self.workflow_counter += 1

        workflow = Workflow(
            id=f"workflow_{self.workflow_counter}",
            name=name,
            nodes=nodes,
            edges=edges,
            version=1,
            status="draft"
        )

        self.workflows[workflow.id] = workflow

        self.workflow_versions[workflow.id] = [
            workflow.model_copy(deep=True)
        ]

        self.audit(
            "create",
            "workflow",
            workflow.id
        )

        return workflow

    def save_workflow(self, workflow: Workflow):

        if workflow.id not in self.workflows:
            raise ValueError(
                f"Workflow '{workflow.id}' not found."
            )

        workflow.version += 1

        self.workflows[workflow.id] = workflow

        self.workflow_versions.setdefault(
            workflow.id,
            []
        ).append(
            workflow.model_copy(deep=True)
        )

        self.audit(
            "update",
            "workflow",
            workflow.id,
            {
                "version": workflow.version
            }
        )

        return workflow

    # --------------------------------------------------
    # Nodes
    # --------------------------------------------------

    def add_edge(
        self,
        workflow_id: str,
        source: str,
        target: str
    ):

        workflow = self.get_workflow(
            workflow_id
        )

        valid_ids = {
            node.id
            for node in workflow.nodes
        }

        if source not in valid_ids:
            raise ValueError(
                f"Unknown source node: {source}"
            )

        if target not in valid_ids:
            raise ValueError(
                f"Unknown target node: {target}"
            )

        edge = WorkflowEdge(
            source=source,
            target=target
        )

        workflow.edges.append(edge)

        self.save_workflow(workflow)

        return edge

    # --------------------------------------------------
    # Versions
    # --------------------------------------------------

    def get_versions(self, workflow_id: str):

        if workflow_id not in self.workflow_versions:
            raise ValueError(
                f"Workflow '{workflow_id}' not found."
            )

        return self.workflow_versions[workflow_id]

    # --------------------------------------------------
    # Approvals
    # --------------------------------------------------

    def request_approval(
        self,
        workflow_id: str,
        comment: str | None = None
    ):

        self.get_workflow(workflow_id)

        self.approval_counter += 1

        approval = Approval(
            id=f"approval_{self.approval_counter}",
            workflow_id=workflow_id,
            status="pending",
            comment=comment
        )

        self.approvals[approval.id] = approval

        self.audit(
            "request_approval",
            "workflow",
            workflow_id,
            {
                "approval_id": approval.id
            }
        )

        return approval

    def approve(
        self,
        approval_id: str
    ):

        if approval_id not in self.approvals:
            raise ValueError(
                f"Approval '{approval_id}' not found."
            )

        approval = self.approvals[approval_id]

        approval.status = "approved"

        self.audit(
            "approve",
            "approval",
            approval_id
        )

        return approval

    # --------------------------------------------------
    # Publishing
    # --------------------------------------------------

    def publish_workflow(
        self,
        workflow_id: str
    ):

        workflow = self.get_workflow(workflow_id)

        approvals = [
            a
            for a in self.approvals.values()
            if a.workflow_id == workflow_id
        ]

        approved = any(
            a.status == "approved"
            for a in approvals
        )

        if not approved:
            raise ValueError(
                "Workflow cannot be published without approval."
            )

        workflow.status = "published"

        self.audit(
            "publish",
            "workflow",
            workflow_id,
            {
                "version": workflow.version
            }
        )

        return workflow

    # --------------------------------------------------
    # Audit
    # --------------------------------------------------

    def get_audit_logs(self):

        return self.audit_logs
    
    # --------------------------------------------------
    # Tool
    # --------------------------------------------------
    
    def list_tools(self):

        return list(self.tools.values())


    def get_tool(self, tool_id: str):

        if tool_id not in self.tools:
            raise ValueError(
                f"Tool '{tool_id}' not found."
            )

        return self.tools[tool_id]


    def create_tool(
        self,
        name: str,
        description: str,
        tool_type: str = "http"
    ):

        self.tool_counter += 1

        tool = Tool(
            id=f"tool_{self.tool_counter}",
            name=name,
            description=description,
            type=tool_type,
            status="draft"
        )

        self.tools[tool.id] = tool

        self.audit(
            "create",
            "tool",
            tool.id,
            {
                "name": name,
                "type": tool_type
            }
        )

        return tool


    def configure_tool(
        self,
        tool_id: str,
        config: dict
    ):

        tool = self.get_tool(tool_id)

        tool.config = config
        tool.status = "configured"

        self.audit(
            "configure",
            "tool",
            tool_id,
            {
                "config": config
            }
        )

        return tool