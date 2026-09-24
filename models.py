from typing import Literal
from pydantic import BaseModel, Field


NodeType = Literal[
    "input",
    "agent",
    "tool",
    "condition",
    "approval",
    "output"
]

class Tool(BaseModel):
    id: str
    name: str
    description: str
    type: Literal["http", "webhook", "function", "database"] = "http"
    status: Literal["draft", "configured"] = "draft"
    config: dict = Field(default_factory=dict)

class Agent(BaseModel):
    id: str
    name: str
    description: str
    status: Literal["draft", "published"] = "draft"
    workflow_id: str | None = None


class WorkflowNode(BaseModel):
    id: str
    type: NodeType
    name: str
    config: dict = Field(default_factory=dict)


class WorkflowEdge(BaseModel):
    source: str
    target: str


class Workflow(BaseModel):
    id: str
    name: str

    version: int = 1

    nodes: list[WorkflowNode] = Field(default_factory=list)
    edges: list[WorkflowEdge] = Field(default_factory=list)

    status: Literal["draft", "published"] = "draft"


class Approval(BaseModel):
    id: str
    workflow_id: str
    status: Literal["pending", "approved", "rejected"] = "pending"
    requested_by: str = "claude"
    comment: str | None = None


class AuditEvent(BaseModel):
    id: str
    action: str
    resource_type: str
    resource_id: str
    actor: str
    details: dict = Field(default_factory=dict)