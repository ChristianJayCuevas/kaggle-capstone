import json
from langgraph.types import interrupt

from graph.state import AgentState
from agents.orchestrator import orchestrator
from agents.worker import (
    hr_agent,
    it_agent,
    finance_agent,
    legal_agent,
    facilities_agent,
    training_agent
)
from external_crm_mock.mock import (
    hr_create_profile,
    it_provision_device,
    finance_approve_budget,
    finance_setup_expense_account,
    legal_generate_contract,
    legal_compliance_check,
    facilities_assign_desk,
    facilities_issue_badge,
    training_enroll_course,
    training_schedule_orientation
)


def node_orchestrator(state: AgentState):
    """The Brain: Generates the workflow plan."""
    print("\n--- 🧠 ORCHESTRATOR: Generating Plan ---")
    user_req = state["messages"][-1].content
    plan = orchestrator.generate_plan(user_req)
    print(f"Plan created with {len(plan)} steps.")
    return {"plan": plan, "current_step": 0, "status": "executing"}


def node_router(state: AgentState):
    """Decides which agent works next or if we are done."""
    idx = state["current_step"]
    plan = state["plan"]

    if idx >= len(plan):
        return {"status": "done"}

    step = plan[idx]
    print(f"\n--- 🔄 ROUTING: Step {idx + 1}/{len(plan)} -> {step['agent']} Agent ---")

    # Return nothing creates a pass-through to the Conditional Edge
    return {"status": "working"}

def node_hr_worker(state: AgentState):
    """Executes HR tasks."""
    idx = state["current_step"]
    step = state["plan"][idx]

    # Construct instruction from plan
    instruction = f"Execute: {step['action']} with params {json.dumps(step['params'])}"
    result = hr_agent.process_step(instruction)

    # Simply Execute the tool call (Simplified for demo)
    # In full production, we'd loop the tool execution.
    for tool_call in result.tool_calls:
        if tool_call['name'] == 'hr_create_profile':
            output = hr_create_profile.invoke(tool_call)
            print(f"✅ HR Output: {output}")

    return {"current_step": idx + 1, "messages": [result]}

def node_it_worker(state: AgentState):
    """Executes IT tasks. HANDLES HITL INTERRUPTION."""
    idx = state["current_step"]
    step = state["plan"][idx]

    # Check if we are resuming from an interrupt with new data
    override_code = None
    # If the tool previously failed, we might have injected an override code via Command
    # (Simplified logic: we just check if we are retrying)

    instruction = f"Execute: {step['action']} with params {json.dumps(step['params'])}"

    # 1. Ask LLM what to do
    ai_msg = it_agent.process_step(instruction)

    # 2. Execute Tool
    for tool_call in ai_msg.tool_calls:
        if tool_call['name'] == 'it_provision_device':
            output = it_provision_device.invoke(tool_call)

            # --- 🛑 INTERRUPT LOGIC ---
            if output == "ERROR_OUT_OF_STOCK":
                print("🛑 CRITICAL: IT Agent reports Out of Stock.")
                print("⏸️  PAUSING WORKFLOW. Waiting for Admin...")

                # Interrupt execution. The graph stops here.
                # When resumed, the value provided by Command(resume="...") is returned.
                human_input = interrupt("Out of Stock. Please provide Admin Override Code.")

                print(f"▶️  RESUMING: Received code '{human_input}'")

                # Retry with the code provided by the human
                retry_output = it_provision_device.invoke({
                    "device": tool_call['args']['device'],
                    "override_auth": human_input
                })
                print(f"✅ IT Output (Retry): {retry_output}")
            else:
                print(f"✅ IT Output: {output}")

    return {"current_step": idx + 1, "messages": [ai_msg]}

def node_finance_worker(state: AgentState):
    """Executes Finance tasks."""
    idx = state["current_step"]
    step = state["plan"][idx]

    instruction = f"Execute: {step['action']} with params {json.dumps(step['params'])}"
    ai_msg = finance_agent.process_step(instruction)

    # Execute tool calls
    for tool_call in ai_msg.tool_calls:
        if tool_call['name'] == 'finance_approve_budget':
            output = finance_approve_budget.invoke(tool_call)
            print(f"✅ Finance Output: {output}")
        elif tool_call['name'] == 'finance_setup_expense_account':
            output = finance_setup_expense_account.invoke(tool_call)
            print(f"✅ Finance Output: {output}")

    return {"current_step": idx + 1, "messages": [ai_msg]}

def node_legal_worker(state: AgentState):
    """Executes Legal tasks."""
    idx = state["current_step"]
    step = state["plan"][idx]

    instruction = f"Execute: {step['action']} with params {json.dumps(step['params'])}"
    ai_msg = legal_agent.process_step(instruction)

    # Execute tool calls
    for tool_call in ai_msg.tool_calls:
        if tool_call['name'] == 'legal_generate_contract':
            output = legal_generate_contract.invoke(tool_call)
            print(f"✅ Legal Output: {output}")
        elif tool_call['name'] == 'legal_compliance_check':
            output = legal_compliance_check.invoke(tool_call)
            print(f"✅ Legal Output: {output}")

    return {"current_step": idx + 1, "messages": [ai_msg]}

def node_facilities_worker(state: AgentState):
    """Executes Facilities tasks."""
    idx = state["current_step"]
    step = state["plan"][idx]

    instruction = f"Execute: {step['action']} with params {json.dumps(step['params'])}"
    ai_msg = facilities_agent.process_step(instruction)

    # Execute tool calls
    for tool_call in ai_msg.tool_calls:
        if tool_call['name'] == 'facilities_assign_desk':
            output = facilities_assign_desk.invoke(tool_call)
            print(f"✅ Facilities Output: {output}")
        elif tool_call['name'] == 'facilities_issue_badge':
            output = facilities_issue_badge.invoke(tool_call)
            print(f"✅ Facilities Output: {output}")

    return {"current_step": idx + 1, "messages": [ai_msg]}

def node_training_worker(state: AgentState):
    """Executes Training tasks."""
    idx = state["current_step"]
    step = state["plan"][idx]

    instruction = f"Execute: {step['action']} with params {json.dumps(step['params'])}"
    ai_msg = training_agent.process_step(instruction)

    # Execute tool calls
    for tool_call in ai_msg.tool_calls:
        if tool_call['name'] == 'training_enroll_course':
            output = training_enroll_course.invoke(tool_call)
            print(f"✅ Training Output: {output}")
        elif tool_call['name'] == 'training_schedule_orientation':
            output = training_schedule_orientation.invoke(tool_call)
            print(f"✅ Training Output: {output}")

    return {"current_step": idx + 1, "messages": [ai_msg]}
