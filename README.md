# TalentFlow

TalentFlow is a lightweight demonstration of an onboarding workflow built with LangGraph. It shows how to coordinate multiple agents and how to pause execution for human input. All external systems are mocked.

# Requirements

Python 3.8+
Google Gemini API key

# Installation

Clone the repository

Install dependencies:

pip install -r requirements.txt

Set your Google API key. Get one at https://aistudio.google.com/app/apikey

Using a .env file:

echo "GOOGLE_API_KEY=your-key" > .env

Or export it:

export GOOGLE_API_KEY="your-key"

# Running the Demo
python main.py


The demo uses the gemini 2.5 flash model.

What the System Does

The Orchestrator generates an onboarding plan. Six worker agents handle HR, Legal, Finance, IT, Facilities and Training. Each task is executed through mock tools. When a blocking condition occurs, the workflow pauses and waits for human input. The IT device provisioning step uses this pause to request an override code when inventory is empty.

State is stored with LangGraph's in memory checkpointer so the workflow can resume cleanly.

File Structure
agents/                Agent logic
graph/                 Workflow graph and state
external_crm_mock/     Mock department and CRM tools
main.py                Entry point
requirements.txt
README.md

Mock Capabilities

HR: create employee profile
IT: provision hardware with optional override
Finance: set expense accounts
Legal: generate contracts and run checks
Facilities: assign desks and badges
Training: enroll courses and schedule orientation

All tools are simulated. No external actions occur.

Purpose

TalentFlow is intended as a reference for building agent workflows with human intervention points using LangGraph.
