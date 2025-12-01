import json
import random
from typing import Dict, Any
from langchain_core.tools import tool

class MockCorporateCRM:
    """
    Simulates a database and external APIs.
    Includes logic to force a 'Soft Failure' (Out of Stock).
    """
    def __init__(self):
        self.db = {
            "employees": [],
            "inventory": {
                "macbook_pro": 0,      # <--- MACBOOK IS 0 TO TRIGGER PAUSE
                "dell_xps": 5,
                "thinkpad_t14": 3,
                "ipad_pro": 10,
                "monitor_27inch": 8
            },
            "budgets": {
                "hr": 50000,
                "it": 30000,
                "facilities": 20000,
                "training": 15000
            },
            "desk_assignments": {},
            "access_badges": {},
            "training_courses": {
                "compliance_101": {"capacity": 50, "enrolled": 35},
                "security_basics": {"capacity": 30, "enrolled": 28},
                "onboarding_orientation": {"capacity": 100, "enrolled": 45}
            },
            "contracts": []
        }

    def create_employee(self, name: str, role: str, email: str) -> str:
        self.db["employees"].append({"name": name, "role": role, "email": email})
        return f"SUCCESS: Created HR profile for {name} ({role})."

    def provision_hardware(self, device: str, override_auth: str = None) -> str:
        stock = self.db["inventory"].get(device, 0)

        # LOGIC: If out of stock and no auth provided, return specific flag
        if stock < 1:
            if override_auth == "ADMIN_OVERRIDE":
                return f"SUCCESS: Admin Override accepted. Backordered {device} assigned."
            return "ERROR_OUT_OF_STOCK"

        self.db["inventory"][device] -= 1
        return f"SUCCESS: Assigned {device} from inventory."

    def approve_budget(self, department: str, amount: float, purpose: str) -> str:
        """Approve budget allocation for a department"""
        if department not in self.db["budgets"]:
            return f"ERROR: Department '{department}' not found."

        available = self.db["budgets"][department]
        if amount > available:
            return f"ERROR_INSUFFICIENT_BUDGET: Requested ${amount}, but only ${available} available."

        self.db["budgets"][department] -= amount
        return f"SUCCESS: Approved ${amount} for {department} - {purpose}. Remaining budget: ${self.db['budgets'][department]}"

    def setup_expense_account(self, employee_name: str, limit: float) -> str:
        """Setup expense account for employee"""
        return f"SUCCESS: Expense account created for {employee_name} with ${limit} monthly limit."

    def generate_contract(self, employee_name: str, role: str, contract_type: str = "full-time") -> str:
        """Generate employment contract"""
        contract_id = f"CONTRACT-{len(self.db['contracts']) + 1:04d}"
        contract = {
            "id": contract_id,
            "employee": employee_name,
            "role": role,
            "type": contract_type
        }
        self.db["contracts"].append(contract)
        return f"SUCCESS: Generated {contract_type} contract {contract_id} for {employee_name}."

    def compliance_check(self, employee_name: str, check_type: str = "background") -> str:
        """Run compliance checks"""
        # Simulate random check results
        if random.random() > 0.1:  # 90% pass rate
            return f"SUCCESS: {check_type.title()} check passed for {employee_name}."
        return f"PENDING: {check_type.title()} check for {employee_name} requires manual review."

    def assign_desk(self, employee_name: str, floor: int, desk_number: str) -> str:
        """Assign desk to employee"""
        location = f"Floor-{floor}-Desk-{desk_number}"
        if location in self.db["desk_assignments"].values():
            return f"ERROR: Desk {location} already assigned."

        self.db["desk_assignments"][employee_name] = location
        return f"SUCCESS: Assigned {location} to {employee_name}."

    def issue_access_badge(self, employee_name: str, access_level: str = "standard") -> str:
        """Issue access badge"""
        badge_id = f"BADGE-{len(self.db['access_badges']) + 1:05d}"
        self.db["access_badges"][employee_name] = {
            "badge_id": badge_id,
            "access_level": access_level
        }
        return f"SUCCESS: Issued badge {badge_id} with {access_level} access to {employee_name}."

    def enroll_training(self, employee_name: str, course_name: str) -> str:
        """Enroll employee in training course"""
        if course_name not in self.db["training_courses"]:
            return f"ERROR: Course '{course_name}' not found."

        course = self.db["training_courses"][course_name]
        if course["enrolled"] >= course["capacity"]:
            return f"ERROR_COURSE_FULL: {course_name} is at capacity ({course['capacity']}/{course['capacity']})."

        course["enrolled"] += 1
        return f"SUCCESS: Enrolled {employee_name} in {course_name}. ({course['enrolled']}/{course['capacity']})"

    def schedule_orientation(self, employee_name: str, date: str) -> str:
        """Schedule new employee orientation"""
        return f"SUCCESS: Scheduled orientation for {employee_name} on {date}."

# Initialize Singleton
crm = MockCorporateCRM()

# ============= HR TOOLS =============
@tool
def hr_create_profile(name: str, role: str, email: str):
    """Creates an employee profile in the HR system."""
    return crm.create_employee(name, role, email)

# ============= IT TOOLS =============
@tool
def it_provision_device(device: str, override_auth: str = None):
    """Provisions a laptop. If out of stock, requires override_auth."""
    return crm.provision_hardware(device, override_auth)

# ============= FINANCE TOOLS =============
@tool
def finance_approve_budget(department: str, amount: float, purpose: str):
    """Approves budget allocation for a department. Returns error if insufficient funds."""
    return crm.approve_budget(department, amount, purpose)

@tool
def finance_setup_expense_account(employee_name: str, monthly_limit: float):
    """Sets up an expense account for an employee with specified monthly limit."""
    return crm.setup_expense_account(employee_name, monthly_limit)

# ============= LEGAL TOOLS =============
@tool
def legal_generate_contract(employee_name: str, role: str, contract_type: str = "full-time"):
    """Generates an employment contract. Contract types: full-time, part-time, contractor."""
    return crm.generate_contract(employee_name, role, contract_type)

@tool
def legal_compliance_check(employee_name: str, check_type: str = "background"):
    """Runs compliance checks. Types: background, reference, credential."""
    return crm.compliance_check(employee_name, check_type)

# ============= FACILITIES TOOLS =============
@tool
def facilities_assign_desk(employee_name: str, floor: int, desk_number: str):
    """Assigns a desk to an employee. Returns error if desk is already taken."""
    return crm.assign_desk(employee_name, floor, desk_number)

@tool
def facilities_issue_badge(employee_name: str, access_level: str = "standard"):
    """Issues an access badge. Access levels: standard, elevated, admin."""
    return crm.issue_access_badge(employee_name, access_level)

# ============= TRAINING TOOLS =============
@tool
def training_enroll_course(employee_name: str, course_name: str):
    """Enrolls employee in a training course. Returns error if course is full."""
    return crm.enroll_training(employee_name, course_name)

@tool
def training_schedule_orientation(employee_name: str, orientation_date: str):
    """Schedules new employee orientation on the specified date."""
    return crm.schedule_orientation(employee_name, orientation_date)
