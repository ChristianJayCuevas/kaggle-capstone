from typing import List, Any
from langchain_core.messages import SystemMessage, HumanMessage, BaseMessage
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

from agents.base import BaseAgent

class WorkerAgent(BaseAgent):
    """Generic worker that executes tools."""
    def __init__(self, name: str, tools: List[Any]):
        super().__init__(name)
        self.tools = tools
        self.llm_with_tools = self.llm.bind_tools(tools)

    def process_step(self, instruction: str) -> Any:
        # Standard ReAct style invocation
        messages = [
            SystemMessage(content=f"You are the {self.name} Agent. Execute the requested task."),
            HumanMessage(content=instruction)
        ]
        return self.llm_with_tools.invoke(messages)

# ============= AGENT INSTANCES =============
hr_agent = WorkerAgent("HR", [hr_create_profile])
it_agent = WorkerAgent("IT", [it_provision_device])
finance_agent = WorkerAgent("Finance", [finance_approve_budget, finance_setup_expense_account])
legal_agent = WorkerAgent("Legal", [legal_generate_contract, legal_compliance_check])
facilities_agent = WorkerAgent("Facilities", [facilities_assign_desk, facilities_issue_badge])
training_agent = WorkerAgent("Training", [training_enroll_course, training_schedule_orientation])
