import json
from typing import Literal
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import interrupt

from graph.state import AgentState
from graph.node import (
    node_orchestrator,
    node_router,
    node_hr_worker,
    node_it_worker,
    node_finance_worker,
    node_legal_worker,
    node_facilities_worker,
    node_training_worker
)


workflow = StateGraph(AgentState)

# Add all agent nodes
workflow.add_node("orchestrator", node_orchestrator)
workflow.add_node("router", node_router)
workflow.add_node("hr_agent", node_hr_worker)
workflow.add_node("it_agent", node_it_worker)
workflow.add_node("finance_agent", node_finance_worker)
workflow.add_node("legal_agent", node_legal_worker)
workflow.add_node("facilities_agent", node_facilities_worker)
workflow.add_node("training_agent", node_training_worker)

# Edges
workflow.add_edge(START, "orchestrator")
workflow.add_edge("orchestrator", "router")

# Conditional Routing Logic - Now handles all 6 departments
def route_next(state: AgentState) -> Literal["hr_agent", "it_agent", "finance_agent", "legal_agent", "facilities_agent", "training_agent", END]:
    if state["status"] == "done":
        return END

    # Look at the plan to decide next node
    current_step = state["plan"][state["current_step"]]
    agent_name = current_step["agent"]

    # Map agent names to node names
    agent_routing = {
        "HR": "hr_agent",
        "IT": "it_agent",
        "Finance": "finance_agent",
        "Legal": "legal_agent",
        "Facilities": "facilities_agent",
        "Training": "training_agent"
    }

    return agent_routing.get(agent_name, END)

workflow.add_conditional_edges("router", route_next)

# Connect all agents back to router
workflow.add_edge("hr_agent", "router")
workflow.add_edge("it_agent", "router")
workflow.add_edge("finance_agent", "router")
workflow.add_edge("legal_agent", "router")
workflow.add_edge("facilities_agent", "router")
workflow.add_edge("training_agent", "router")

# Compile with Memory (Required for Pause/Resume)
checkpointer = MemorySaver()
app = workflow.compile(checkpointer=checkpointer)
