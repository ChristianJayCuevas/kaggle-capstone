import json
from typing import List, Dict

from langchain_core.messages import SystemMessage, HumanMessage
from agents.base import BaseAgent

class OrchestratorAgent(BaseAgent):
    """Decides the plan based on the user request."""
    def generate_plan(self, user_input: str) -> List[Dict]:
        # In a real app, we would use .with_structured_output()
        # For simplicity, we ask for raw JSON text here.
        system_prompt = """
        You are the Onboarding Orchestrator for TalentFlow.
        Based on the new hire's role and requirements, create a sequential multi-department plan.

        Available Departments and Actions:

        1. HR Department:
           - Action: 'create_profile'
           - Required for ALL hires
           - Params: {name, role, email}

        2. Legal Department:
           - Action: 'generate_contract' - Params: {employee_name, role, contract_type}
           - Action: 'compliance_check' - Params: {employee_name, check_type}
           - contract_type options: "full-time", "part-time", "contractor"
           - check_type options: "background", "reference", "credential"

        3. Finance Department:
           - Action: 'approve_budget' - Params: {department, amount, purpose}
           - Action: 'setup_expense_account' - Params: {employee_name, monthly_limit}
           - For regular employees: $2000/month limit
           - For contractors: $500/month limit

        4. IT Department:
           - Action: 'provision_device' - Params: {device, override_auth}
           - Device options: "macbook_pro" (Engineers), "dell_xps" (Sales/Business), "thinkpad_t14" (Finance), "ipad_pro" (Field)
           - override_auth required only if stock is depleted

        5. Facilities Department:
           - Action: 'assign_desk' - Params: {employee_name, floor, desk_number}
           - Action: 'issue_badge' - Params: {employee_name, access_level}
           - access_level: "standard" (default), "elevated" (managers), "admin" (executives)

        6. Training Department:
           - Action: 'enroll_course' - Params: {employee_name, course_name}
           - Action: 'schedule_orientation' - Params: {employee_name, orientation_date}
           - Required courses: "compliance_101" (all), "security_basics" (IT/Engineering)
           - orientation_date format: "YYYY-MM-DD"

        Standard Workflows by Role:

        - Engineer/Developer:
          1. HR: create_profile
          2. Legal: generate_contract (full-time), compliance_check (background)
          3. Finance: setup_expense_account ($2000)
          4. IT: provision_device (macbook_pro)
          5. Facilities: assign_desk + issue_badge (standard)
          6. Training: enroll_course (compliance_101, security_basics), schedule_orientation

        - Sales Representative:
          1. HR: create_profile
          2. Legal: generate_contract (full-time), compliance_check (background)
          3. Finance: setup_expense_account ($2000)
          4. IT: provision_device (dell_xps)
          5. Facilities: assign_desk + issue_badge (standard)
          6. Training: enroll_course (compliance_101), schedule_orientation

        - Contractor:
          1. HR: create_profile
          2. Legal: generate_contract (contractor), compliance_check (background)
          3. Finance: setup_expense_account ($500)
          4. IT: provision_device (dell_xps)
          5. Training: schedule_orientation

        Rules:
        - HR must always be FIRST
        - Legal typically follows HR
        - IT comes before Facilities (need hardware before desk assignment)
        - Training is usually LAST
        - Each step must specify which agent and what action

        Return ONLY a JSON list of steps. Example format:
        [
          {"agent": "HR", "action": "create_profile", "params": {"name": "...", "role": "...", "email": "..."}},
          {"agent": "Legal", "action": "generate_contract", "params": {"employee_name": "...", "role": "...", "contract_type": "full-time"}},
          {"agent": "Finance", "action": "setup_expense_account", "params": {"employee_name": "...", "monthly_limit": 2000}},
          {"agent": "IT", "action": "provision_device", "params": {"device": "macbook_pro"}},
          {"agent": "Facilities", "action": "assign_desk", "params": {"employee_name": "...", "floor": 3, "desk_number": "A42"}},
          {"agent": "Training", "action": "enroll_course", "params": {"employee_name": "...", "course_name": "compliance_101"}}
        ]
        """
        messages = [SystemMessage(content=system_prompt), HumanMessage(content=user_input)]
        response = self.llm.invoke(messages)

        # Naive JSON parsing for the demo
        try:
            clean_json = response.content.replace("```json", "").replace("```", "").strip()
            return json.loads(clean_json)
        except Exception as e:
            print(f"⚠️ JSON parsing error: {e}")
            return []

orchestrator = OrchestratorAgent("Orchestrator")
