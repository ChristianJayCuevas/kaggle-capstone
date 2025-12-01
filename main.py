import os
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langgraph.types import Command

# Load environment variables from .env file
load_dotenv()

# Validate API key is set
# Validate API key is set
if not os.getenv("GOOGLE_API_KEY"):
    print("=" * 70)
    print("❌ ERROR: GOOGLE_API_KEY not found!")
    print("=" * 70)
    print("\nPlease set your Google API key:")
    print("\n1. Get your API key from: https://aistudio.google.com/app/apikey")
    print("2. Edit the .env file and add your key:")
    print("   nano .env")
    print("\n3. Or set it as an environment variable:")
    print("   export GOOGLE_API_KEY='AIza...'")
    print("\n" + "=" * 70)
    exit(1)

from graph.graph import app
from external_crm_mock.mock import crm


if __name__ == "__main__":
    # Setup thread for persistence
    thread_config = {"configurable": {"thread_id": "onboarding_session_enhanced"}}

    print("=" * 70)
    print("🚀 STARTING TALENTFLOW - MULTI-DEPARTMENT ONBOARDING SYSTEM")
    print("=" * 70)

    # Comprehensive onboarding request
    initial_input = {
        "messages": [
            HumanMessage(content="Onboard Sarah Johnson as a Senior Engineer. Email: sarah.johnson@company.com")
        ]
    }

    print("\n📋 Processing onboarding request for Sarah Johnson...")
    print("-" * 70)

    # 1. Initial Run (User Request)
    # Expected: HR → Legal → Finance → IT (pause) → Facilities → Training
    for event in app.stream(initial_input, thread_config):
        pass  # Stream output is handled by print statements in nodes

    # 2. Inspect State
    state = app.get_state(thread_config)
    if state.next:
        print("\n" + "=" * 70)
        print("⚠️  WORKFLOW IS PAUSED - AWAITING HUMAN INPUT")
        print("=" * 70)
        print(f"📍 Paused at: {state.next}")
        print(f"📊 Steps completed: {state.values.get('current_step', 0)}/{len(state.values.get('plan', []))}")
        print(f"🔍 Status: {state.values.get('status', 'unknown')}")

        # 3. Resume (Simulate Admin Override)
        print("\n" + "-" * 70)
        print("👨‍💼 ADMIN ACTION: Providing Override Code 'ADMIN_OVERRIDE'...")
        print("-" * 70 + "\n")

        # Resume the workflow
        for event in app.stream(Command(resume="ADMIN_OVERRIDE"), thread_config):
            pass

    print("\n" + "=" * 70)
    print("🏁 WORKFLOW COMPLETE - ONBOARDING FINISHED")
    print("=" * 70)

    # Display final CRM state
    print("\n📊 FINAL CRM STATE:")
    print("-" * 70)
    print(f"\n👥 Employees: {len(crm.db['employees'])} registered")
    for emp in crm.db['employees']:
        print(f"   • {emp['name']} - {emp['role']} ({emp['email']})")

    print(f"\n📋 Contracts: {len(crm.db['contracts'])} generated")
    for contract in crm.db['contracts']:
        print(f"   • {contract['id']}: {contract['employee']} ({contract['type']})")

    print(f"\n💰 Finance:")
    print(f"   • HR Budget: ${crm.db['budgets']['hr']}")
    print(f"   • IT Budget: ${crm.db['budgets']['it']}")
    print(f"   • Facilities Budget: ${crm.db['budgets']['facilities']}")
    print(f"   • Training Budget: ${crm.db['budgets']['training']}")

    print(f"\n💻 IT Inventory:")
    for device, stock in crm.db['inventory'].items():
        print(f"   • {device}: {stock} units")

    print(f"\n🏢 Facilities:")
    if crm.db['desk_assignments']:
        for employee, desk in crm.db['desk_assignments'].items():
            print(f"   • {employee}: {desk}")
    if crm.db['access_badges']:
        for employee, badge_info in crm.db['access_badges'].items():
            print(f"   • {employee}: {badge_info['badge_id']} ({badge_info['access_level']})")

    print(f"\n📚 Training:")
    for course, info in crm.db['training_courses'].items():
        print(f"   • {course}: {info['enrolled']}/{info['capacity']} enrolled")

    print("\n" + "=" * 70)
    print("✅ TalentFlow Multi-Department Demo Complete!")
    print("=" * 70)
