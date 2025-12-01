# TalentFlow - AI-Powered Employee Onboarding System

A mock demonstration of a LangGraph-based employee onboarding workflow with Human-in-the-Loop (HITL) interruption capabilities.

## 🎯 Overview

TalentFlow is a multi-agent AI system that orchestrates employee onboarding across **six departments** (HR, Legal, Finance, IT, Facilities, and Training). It showcases:

- **Multi-Agent Architecture**: Orchestrator agent plans workflows, 6 worker agents execute department-specific tasks
- **Human-in-the-Loop (HITL)**: Workflow pauses when manual intervention is required (e.g., out-of-stock hardware)
- **State Persistence**: Uses LangGraph's checkpointing to save/resume workflow state
- **Mock External Systems**: Simulates real-world CRM, inventory, budgets, and departmental APIs

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         Main.py                              │
│                  (Workflow Orchestration)                    │
└────────────────────────┬────────────────────────────────────┘
                         │
        ┌────────────────┴────────────────┐
        │      LangGraph Workflow         │
        │   (graph/graph.py + state.py)   │
        └────────────────┬────────────────┘
                         │
        ┌────────────────┴────────────────────────────┐
        │              Graph Nodes                     │
        │            (graph/node.py)                   │
        │                                              │
        │  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
        │  │Orchestr- │  │  Router  │  │  6 Worker│  │
        │  │  ator    │  │          │  │  Nodes   │  │
        │  └──────────┘  └──────────┘  └──────────┘  │
        └─────────────────┬────────────────────────────┘
                          │
        ┌─────────────────┴──────────────────┐
        │           Agents Layer             │
        │      (agents/orchestrator.py,      │
        │         agents/worker.py)          │
        │                                    │
        │  6 Agents: HR, Legal, Finance,     │
        │  IT, Facilities, Training          │
        └─────────────────┬──────────────────┘
                          │
        ┌─────────────────┴──────────────────┐
        │      External CRM Mock             │
        │   (external_crm_mock/mock.py)      │
        │                                    │
        │  15+ Department Tools:             │
        │  • HR: Create profiles             │
        │  • IT: Provision devices           │
        │  • Finance: Budgets, expenses      │
        │  • Legal: Contracts, compliance    │
        │  • Facilities: Desks, badges       │
        │  • Training: Courses, orientation  │
        └────────────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Google Gemini API key (free tier available)

### Installation

1. **Clone/Navigate to the repository**
   ```bash
   cd /home/christian/kaggle-capstone
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set your Google Gemini API key**

   Get your free API key from: https://aistudio.google.com/app/apikey

   Then either:

   **Option A: Using .env file (recommended)**
   ```bash
   # Edit the .env file and add your API key
   nano .env
   # Replace 'your-google-gemini-api-key-here' with your actual key
   ```

   **Option B: Using environment variable**
   ```bash
   export GOOGLE_API_KEY='your-api-key-here'
   ```

### Running the Demo

```bash
python main.py
```

**Note:** The system uses **gemini-1.5-flash** (Google's free tier model) by default.

## 📖 How It Works

### Workflow Flow

1. **User Request**: "Onboard Sarah Johnson as a Senior Engineer. Email: sarah.johnson@company.com"

2. **Orchestrator Agent**: Generates a comprehensive 6-department plan
   - Step 1: HR creates employee profile
   - Step 2: Legal generates contract + runs background check
   - Step 3: Finance sets up expense account
   - Step 4: IT provisions MacBook Pro
   - Step 5: Facilities assigns desk + issues badge
   - Step 6: Training enrolls in courses + schedules orientation

3. **HR Worker**: Executes successfully
   - Creates profile in mock CRM

4. **Legal Worker**: Executes successfully
   - Generates full-time employment contract
   - Runs background compliance check

5. **Finance Worker**: Executes successfully
   - Sets up $2000/month expense account

6. **IT Worker**: Detects out-of-stock condition
   - MacBook Pro inventory = 0
   - Workflow **PAUSES** via `interrupt()`
   - Requests admin override code

7. **Human Input**: Admin provides override "ADMIN_OVERRIDE"

8. **Workflow Resumes**: IT worker completes with override
   - Backordered device assigned

9. **Facilities Worker**: Executes successfully
   - Assigns desk (Floor 3, Desk A42)
   - Issues access badge with standard access

10. **Training Worker**: Executes successfully
    - Enrolls in compliance_101 course
    - Schedules orientation for new hire

11. **Completion**: All 6 departments report success

### Key Demonstration: HITL Interruption

The system demonstrates **soft failure handling**:

```python
# In node_it_worker (graph/node.py)
output = it_provision_device.invoke(tool_call)

if output == "ERROR_OUT_OF_STOCK":
    # 🛑 PAUSE WORKFLOW
    human_input = interrupt("Out of Stock. Please provide Admin Override Code.")

    # When resumed, retry with human-provided code
    retry_output = it_provision_device.invoke({
        "device": "macbook_pro",
        "override_auth": human_input  # "ADMIN_OVERRIDE"
    })
```

## 🧪 Checkpointer Verification

### How Checkpointing Works

LangGraph's `MemorySaver` checkpointer enables:

1. **State Persistence**: Saves workflow state after each node execution
2. **Resumption**: Restores state when workflow resumes after interruption
3. **Thread Management**: Each workflow has a unique `thread_id`

### Verification Points

✅ **Checkpointer Initialization** (`graph/graph.py`)
```python
from langgraph.checkpoint.memory import MemorySaver

checkpointer = MemorySaver()
app = workflow.compile(checkpointer=checkpointer)
```

✅ **Thread Configuration** (`main.py`)
```python
thread_config = {"configurable": {"thread_id": "onboarding_session_1"}}
```

✅ **State Inspection**
```python
state = app.get_state(thread_config)
if state.next:
    print("Workflow is PAUSED")
```

✅ **Resume with Command**
```python
app.stream(Command(resume="ADMIN_OVERRIDE"), thread_config)
```

### Testing Checkpointer

Run `python main.py` and observe:

1. Workflow starts streaming events
2. Console shows "⏸️ PAUSING WORKFLOW"
3. State inspection reveals `state.next = ['it_agent']`
4. Resume command triggers continuation
5. Workflow completes successfully

**Expected Output:**
```
🚀 STARTING TALENTFLOW...
--- 🧠 ORCHESTRATOR: Generating Plan ---
Plan created with 2 steps.
✅ HR Output: SUCCESS: Created HR profile for John Doe (Engineer).
🛑 CRITICAL: IT Agent reports Out of Stock.
⏸️ PAUSING WORKFLOW. Waiting for Admin...

⚠️ Workflow is PAUSED waiting for input.
Next step in graph: ('it_agent',)

👨‍💻 USER ACTION: Providing Override Code 'ADMIN_OVERRIDE'...
▶️ RESUMING: Received code 'ADMIN_OVERRIDE'
✅ IT Output (Retry): SUCCESS: Admin Override accepted. Backordered macbook_pro assigned.

🏁 WORKFLOW COMPLETE.
```

## 🛠️ Available Mock Tools

### HR Department
- `hr_create_profile(name, role, email)` - Create employee profile

### IT Department
- `it_provision_device(device, override_auth)` - Provision hardware
  - Devices: `macbook_pro`, `dell_xps`, `thinkpad_t14`, `ipad_pro`, `monitor_27inch`

### Finance Department
- `finance_approve_budget(department, amount, purpose)` - Approve budget allocation
- `finance_setup_expense_account(employee_name, monthly_limit)` - Setup expense account

### Legal Department
- `legal_generate_contract(employee_name, role, contract_type)` - Generate employment contract
- `legal_compliance_check(employee_name, check_type)` - Run compliance checks

### Facilities Department
- `facilities_assign_desk(employee_name, floor, desk_number)` - Assign workspace
- `facilities_issue_badge(employee_name, access_level)` - Issue access badge

### Training Department
- `training_enroll_course(employee_name, course_name)` - Enroll in training
  - Courses: `compliance_101`, `security_basics`, `onboarding_orientation`
- `training_schedule_orientation(employee_name, orientation_date)` - Schedule orientation

## 📂 Project Structure

```
kaggle-capstone/
├── agents/
│   ├── __init__.py
│   ├── base.py              # BaseAgent class
│   ├── orchestrator.py      # Planning agent
│   └── worker.py            # Execution agents (HR, IT)
├── graph/
│   ├── graph.py             # LangGraph workflow definition
│   ├── node.py              # Node functions (orchestrator, router, workers)
│   └── state.py             # AgentState TypedDict
├── external_crm_mock/
│   └── mock.py              # Mock CRM with 15+ tools
├── main.py                  # Entry point with HITL demo
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## 🔑 Key Concepts

### State Management
The `AgentState` tracks:
- `messages`: Conversation history
- `plan`: Generated workflow steps
- `current_step`: Execution progress
- `status`: Workflow state (planning/executing/paused/done)
- `last_error`: Error tracking for HITL

### Interrupt Mechanism
```python
from langgraph.types import interrupt

# Pause workflow and request human input
user_input = interrupt(prompt="Provide override code")

# Resume with:
app.stream(Command(resume="user_provided_value"), thread_config)
```

### Conditional Routing
The router node uses conditional edges to direct flow:
```python
def route_next(state) -> Literal["hr_agent", "it_agent", END]:
    if state["status"] == "done":
        return END

    current_step = state["plan"][state["current_step"]]
    if current_step["agent"] == "HR":
        return "hr_agent"
    elif current_step["agent"] == "IT":
        return "it_agent"
```

## 🧩 Extending the System

### Adding New Departments

1. **Add tools to `mock.py`**:
   ```python
   @tool
   def marketing_create_campaign(employee_name: str):
       return crm.create_marketing_campaign(employee_name)
   ```

2. **Create worker agent** in `agents/worker.py`:
   ```python
   marketing_agent = WorkerAgent("Marketing", [marketing_create_campaign])
   ```

3. **Add node** in `graph/node.py`:
   ```python
   def node_marketing_worker(state: AgentState):
       # Similar to node_hr_worker
   ```

4. **Update graph** in `graph/graph.py`:
   ```python
   workflow.add_node("marketing_agent", node_marketing_worker)
   # Add to conditional edges in route_next
   ```

## 🐛 Troubleshooting

### "ModuleNotFoundError: No module named 'langgraph'"
```bash
pip install langgraph langchain-google-genai langchain-core python-dotenv
```

### "GOOGLE_API_KEY not set"
Get your free API key from https://aistudio.google.com/app/apikey and either:
```bash
export GOOGLE_API_KEY='your-key-here'
```
Or add it to the `.env` file

### Workflow doesn't pause
- Check `inventory["macbook_pro"] = 0` in `mock.py`
- Ensure `interrupt()` is imported in `graph/node.py`

### "Rate limit exceeded" or quota errors
- Gemini free tier has rate limits
- Wait a few seconds between runs
- Consider upgrading to paid tier for production use

## 📝 Notes

- **This is a MOCK system**: All tools simulate external APIs, no real actions occur
- **Demo Purpose**: Designed to showcase LangGraph HITL capabilities
- **State Persistence**: Uses in-memory `MemorySaver`, resets on restart
- **Production Considerations**: Replace `MemorySaver` with `PostgresSaver` or `RedisSaver` for persistence

## 📄 License

This is a demonstration project for educational purposes.

---

**Ready to see HITL in action?** Run `python main.py` and watch the workflow pause when MacBook inventory hits zero! 🚀
