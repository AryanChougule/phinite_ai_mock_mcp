from backend import MockPhiniteBackend
from models import WorkflowNode, WorkflowEdge


def seed_backend(backend):

    workflow = backend.create_workflow(
        name="Customer Support Agent",
        nodes=[
            WorkflowNode(
                id="input_1",
                type="input",
                name="Customer Ticket",
                config={
                    "schema": {
                        "ticket": "string"
                    }
                }
            ),

            WorkflowNode(
                id="classifier_1",
                type="agent",
                name="Ticket Classifier",
                config={
                    "model": "mock-gpt",
                    "prompt": "Classify the customer ticket."
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
                name="Human Approval",
                config={
                    "required": True
                }
            ),

            WorkflowNode(
                id="output_1",
                type="output",
                name="Customer Response",
                config={}
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


if __name__ == "__main__":

    backend = MockPhiniteBackend()

    seed_backend(backend)

    print("Seed complete.")